from flask import Flask
from flask_smorest import Api
from extensions import db, limiter
from dotenv import load_dotenv
from routes.weather_routes import weather_blp
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Weather REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")

    db.init_app(app)
    api = Api(app)
    limiter.init_app(app)
    

    with app.app_context():
        db.create_all()

    api.register_blueprint(weather_blp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
