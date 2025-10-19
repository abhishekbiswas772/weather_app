from flask_smorest import Blueprint
from extensions import limiter
from flask import jsonify, request
from dotenv import load_dotenv
from service.weather_service import WeatherService
import os

load_dotenv()

weather_blp = Blueprint("Weather",  __name__, description="weather service")
api_version = os.getenv("API_VERSION")
redis_url = os.getenv("REDIS_URL")
if not redis_url:
    raise ValueError("Redis url not found....")


@weather_blp.route(f"{api_version}/weather", methods = ["POST"])
async def get_weather_details():
    print("=== REQUEST RECEIVED ===")
    data = request.get_json()
    print(f"Data received: {data}")
    longitiude = float(data.get("longitiude"))
    latitude = float(data.get("latitude"))
    print(f"Long: {longitiude}, Lat: {latitude}")

    if not longitiude:
        return jsonify({
            "status" : False,
            "error" : "longitiude is missing"
        }), 200

    if not latitude:
        return jsonify({
            "status" : False,
            "error" : "latitude is missing"
        }), 200

    try:
        print("Creating weather service...")
        weather_service = await WeatherService.create()
        print("Weather service created, fetching weather...")
        weather = await weather_service.get_weather_details_from_api(
            long=longitiude,
            lat=latitude
        )
        print("Weather fetched, converting to dict...")
        result = weather.to_dict()
        print("Returning response...")
        return jsonify({"status": True, "data": result}), 200
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status" : False,
            "error" : str(e)
        }), 400