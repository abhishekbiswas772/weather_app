from models.weather import Weather, CurrentConditions, Station
from extensions import db, get_redis_client
from dotenv import load_dotenv
import os
import httpx
import json
import asyncio


load_dotenv()


class WeatherService:
    def __init__(self, redis_client):
        self.db = db
        self.redis_client = redis_client
        self.weather_url = os.getenv("WEATHER_API_URL")
        self.weather_key = os.getenv("WEATHER_API_KEY")

    class WeatherException(Exception):
        pass

    @classmethod
    async def create(cls):
        redis_client = await get_redis_client()
        return cls(redis_client)

    def _save_weather_to_db(self, data):
        """Synchronous method to save weather data to database"""
        try:
            weather = Weather(
                query_cost=data.get('queryCost'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                resolved_address=data.get('resolvedAddress'),
                address=data.get('address'),
                timezone=data.get('timezone'),
                tzoffset=data.get('tzoffset'),
                description=data.get('description'),
                alerts=data.get('alerts')
            )

            self.db.session.add(weather)
            self.db.session.flush()  # Get the weather.id

            # Create CurrentConditions for current weather
            if data.get('currentConditions'):
                current = data['currentConditions']
                current_conditions = self._create_current_condition(current, weather.id, None)
                self.db.session.add(current_conditions)
                self.db.session.flush()
                weather.current_conditions_id = current_conditions.id

            # Create CurrentConditions for days and hours
            if data.get('days'):
                for day_data in data['days']:
                    day_condition = self._create_current_condition(day_data, weather.id, None)
                    self.db.session.add(day_condition)
                    self.db.session.flush()

                    # Create hourly conditions for this day
                    if day_data.get('hours'):
                        for hour_data in day_data['hours']:
                            hour_condition = self._create_current_condition(hour_data, weather.id, day_condition.id)
                            self.db.session.add(hour_condition)

            # Create Station objects
            if data.get('stations'):
                for station_key, station_data in data['stations'].items():
                    station = Station(
                        distance=station_data.get('distance'),
                        latitude=station_data.get('latitude'),
                        longitude=station_data.get('longitude'),
                        use_count=station_data.get('useCount'),
                        station_id=station_key,
                        name=station_data.get('name'),
                        quality=station_data.get('quality'),
                        contribution=station_data.get('contribution'),
                        weather_id=weather.id
                    )
                    self.db.session.add(station)

            # Commit to database
            self.db.session.commit()

            return weather

        except Exception as e:
            self.db.session.rollback()
            raise self.WeatherException(str(e))

    async def get_weather_details_from_api(self, long : float, lat: float) -> Weather:
        if not long:
            raise self.WeatherException("longitude is missing")

        if not lat:
            raise self.WeatherException("latitude is missing")

        if not self.weather_key:
            raise self.WeatherException("api key is missing")

        if not self.weather_url:
            raise self.WeatherException("weather url is missing")

        try:
            cache_key = f"weather:{lat}:{long}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)
            else:
                final_url = f"{self.weather_url}/rest/services/timeline/{long}%2C{lat}?unitGroup=us&key={self.weather_key}&contentType=json"
                async with httpx.AsyncClient() as client:
                    response = await client.get(final_url)

                if response.status_code == 200:
                    data = response.json()
                    await self.redis_client.setex(cache_key, 86400, json.dumps(data))
                else:
                    raise self.WeatherException(f"Weather cannot fetch, status code: {response.status_code}")

            # Run database operations in thread pool to avoid blocking
            weather = await asyncio.to_thread(self._save_weather_to_db, data)
            return weather

        except Exception as e:
            raise self.WeatherException(str(e))

    def _create_current_condition(self, data: dict, weather_id: str, parent_id: str = None):
        """Helper method to create CurrentConditions object from data"""
        from datetime import datetime

        # Parse datetime
        datetime_str = data.get('datetime')
        datetime_epoch = data.get('datetimeEpoch')

        if datetime_epoch:
            current_datetime = datetime.fromtimestamp(datetime_epoch)
        elif datetime_str:
            try:
                current_datetime = datetime.fromisoformat(datetime_str)
            except:
                current_datetime = datetime.now()
        else:
            current_datetime = datetime.now()

        return CurrentConditions(
            current_conditions_datetime=current_datetime,
            datetime_epoch=datetime_epoch or 0,
            temp=data.get('temp', 0.0),
            feelslike=data.get('feelslike', 0.0),
            humidity=data.get('humidity', 0.0),
            dew=data.get('dew', 0.0),
            precip=data.get('precip'),  # Can be None/null
            precipprob=data.get('precipprob', 0.0),
            snow=data.get('snow', 0.0),  # Changed to Float
            snowdepth=data.get('snowdepth', 0.0),  # Changed to Float
            preciptype=','.join(data.get('preciptype', [])) if data.get('preciptype') else None,
            windgust=data.get('windgust'),
            windspeed=data.get('windspeed', 0.0),
            winddir=data.get('winddir', 0.0),
            pressure=data.get('pressure', 0.0),
            visibility=data.get('visibility', 0.0),
            cloudcover=data.get('cloudcover', 0.0),
            solarradiation=data.get('solarradiation', 0.0),
            solarenergy=data.get('solarenergy', 0.0),
            uvindex=data.get('uvindex', 0),
            conditions=data.get('conditions', ''),
            icon=data.get('icon', ''),
            stations=data.get('stations'),
            source=data.get('source', ''),
            sunrise=self._parse_time_to_datetime(data.get('sunrise')) if data.get('sunrise') else None,
            sunrise_epoch=data.get('sunriseEpoch'),
            sunset=self._parse_time_to_datetime(data.get('sunset')) if data.get('sunset') else None,
            sunset_epoch=data.get('sunsetEpoch'),
            moonphase=data.get('moonphase'),
            tempmax=data.get('tempmax'),
            tempmin=data.get('tempmin'),
            feelslikemax=data.get('feelslikemax'),
            feelslikemin=data.get('feelslikemin'),
            precipcover=data.get('precipcover'),
            severerisk=data.get('severerisk'),
            description=data.get('description'),
            weather_id=weather_id,
            parent_id=parent_id
        )

    def _parse_time_to_datetime(self, time_str: str):
        """Parse time string to datetime object"""
        from datetime import datetime
        try:
            return datetime.strptime(time_str, "%H:%M:%S")
        except:
            return None


