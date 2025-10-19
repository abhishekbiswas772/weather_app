from enum import Enum
from datetime import datetime, timezone
from extensions import db
import uuid

class Conditions(Enum):
    CLEAR = "Clear"
    OVERCAST = "Overcast"
    PARTIALLY_CLOUDY = "Partially cloudy"


class Description(Enum):
    CLEAR_CONDITIONS_THROUGHOUT_THE_DAY = "Clear conditions throughout the day."
    PARTLY_CLOUDY_THROUGHOUT_THE_DAY = "Partly cloudy throughout the day."


class Icon(Enum):
    CLEAR_DAY = "clear-day"
    CLEAR_NIGHT = "clear-night"
    CLOUDY = "cloudy"
    FOG = "fog"
    PARTLY_CLOUDY_DAY = "partly-cloudy-day"
    PARTLY_CLOUDY_NIGHT = "partly-cloudy-night"


class Source(Enum):
    COMB = "comb"
    FCST = "fcst"
    OBS = "obs"


class ID(Enum):
    AV559 = "AV559"
    REMOTE = "remote"
    VIDP = "VIDP"


class CurrentConditions(db.Model):
    __tablename__ = 'current_conditions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    current_conditions_datetime = db.Column(db.DateTime, nullable=False)
    datetime_epoch = db.Column(db.Integer, nullable=False)
    temp = db.Column(db.Float, nullable=False)
    feelslike = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    dew = db.Column(db.Float, nullable=False)
    precip = db.Column(db.Float, nullable=True)  # Changed from Integer to Float
    precipprob = db.Column(db.Float, nullable=False)
    snow = db.Column(db.Float, nullable=False)  # Changed from Integer to Float
    snowdepth = db.Column(db.Float, nullable=False)  # Changed from Integer to Float
    preciptype = db.Column(db.String(50), nullable=True)
    windgust = db.Column(db.Float, nullable=True)
    windspeed = db.Column(db.Float, nullable=False)
    winddir = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.Float, nullable=False)
    cloudcover = db.Column(db.Float, nullable=False)
    solarradiation = db.Column(db.Float, nullable=False)
    solarenergy = db.Column(db.Float, nullable=False)
    uvindex = db.Column(db.Integer, nullable=False)
    conditions = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    stations = db.Column(db.JSON, nullable=True)
    source = db.Column(db.String(50), nullable=False)
    sunrise = db.Column(db.DateTime, nullable=True)
    sunrise_epoch = db.Column(db.Integer, nullable=True)
    sunset = db.Column(db.DateTime, nullable=True)
    sunset_epoch = db.Column(db.Integer, nullable=True)
    moonphase = db.Column(db.Float, nullable=True)
    tempmax = db.Column(db.Float, nullable=True)
    tempmin = db.Column(db.Float, nullable=True)
    feelslikemax = db.Column(db.Float, nullable=True)
    feelslikemin = db.Column(db.Float, nullable=True)
    precipcover = db.Column(db.Float, nullable=True)  # Changed from Integer to Float
    severerisk = db.Column(db.Float, nullable=True)  # Changed from Integer to Float
    description = db.Column(db.String(255), nullable=True)


    # Foreign keys
    weather_id = db.Column(db.String(36), db.ForeignKey('weather.id'), nullable=True)
    parent_id = db.Column(db.String(36), db.ForeignKey('current_conditions.id'), nullable=True)

    # Relationships
    hours = db.relationship('CurrentConditions', backref=db.backref('parent', remote_side=[id]), lazy=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self, include_hours=False):
        """Convert CurrentConditions to dictionary"""
        data = {
            'id': self.id,
            'datetime': self.current_conditions_datetime.isoformat() if self.current_conditions_datetime else None,
            'datetime_epoch': self.datetime_epoch,
            'temp': self.temp,
            'feelslike': self.feelslike,
            'humidity': self.humidity,
            'dew': self.dew,
            'precip': self.precip,
            'precipprob': self.precipprob,
            'snow': self.snow,
            'snowdepth': self.snowdepth,
            'preciptype': self.preciptype,
            'windgust': self.windgust,
            'windspeed': self.windspeed,
            'winddir': self.winddir,
            'pressure': self.pressure,
            'visibility': self.visibility,
            'cloudcover': self.cloudcover,
            'solarradiation': self.solarradiation,
            'solarenergy': self.solarenergy,
            'uvindex': self.uvindex,
            'conditions': self.conditions,
            'icon': self.icon,
            'stations': self.stations,
            'source': self.source,
            'sunrise': self.sunrise.isoformat() if self.sunrise else None,
            'sunrise_epoch': self.sunrise_epoch,
            'sunset': self.sunset.isoformat() if self.sunset else None,
            'sunset_epoch': self.sunset_epoch,
            'moonphase': self.moonphase,
            'tempmax': self.tempmax,
            'tempmin': self.tempmin,
            'feelslikemax': self.feelslikemax,
            'feelslikemin': self.feelslikemin,
            'precipcover': self.precipcover,
            'severerisk': self.severerisk,
            'description': self.description
        }

        if include_hours and self.hours:
            data['hours'] = [hour.to_dict(include_hours=False) for hour in self.hours]

        return data


class Station(db.Model):
    __tablename__ = 'station'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    distance = db.Column(db.Float, nullable=False)  # Changed from Integer to Float
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    use_count = db.Column(db.Integer, nullable=False)
    station_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    contribution = db.Column(db.Float, nullable=False)  # Changed from Integer to Float
    weather_id = db.Column(db.String(36), db.ForeignKey('weather.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Convert Station to dictionary"""
        return {
            'id': self.id,
            'distance': self.distance,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'use_count': self.use_count,
            'station_id': self.station_id,
            'name': self.name,
            'quality': self.quality,
            'contribution': self.contribution
        }


class Weather(db.Model):
    __tablename__ = 'weather'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_cost = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    resolved_address = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    timezone = db.Column(db.String(100), nullable=False)
    tzoffset = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    alerts = db.Column(db.JSON, nullable=True)
    days = db.relationship('CurrentConditions', foreign_keys=[CurrentConditions.weather_id], backref='weather', lazy=True)
    stations = db.relationship('Station', backref='weather', lazy=True)
    current_conditions_id = db.Column(db.String(36), db.ForeignKey('current_conditions.id'), nullable=True)
    current_conditions = db.relationship('CurrentConditions', foreign_keys=[current_conditions_id], post_update=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Convert Weather to dictionary"""
        # Get days (excluding current conditions to avoid duplication)
        days_list = []
        for day in self.days:
            if day.id != self.current_conditions_id:
                days_list.append(day.to_dict(include_hours=True))

        return {
            'id': self.id,
            'query_cost': self.query_cost,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'resolved_address': self.resolved_address,
            'address': self.address,
            'timezone': self.timezone,
            'tzoffset': self.tzoffset,
            'description': self.description,
            'alerts': self.alerts,
            'current_conditions': self.current_conditions.to_dict() if self.current_conditions else None,
            'days': days_list,
            'stations': [station.to_dict() for station in self.stations]
        }
