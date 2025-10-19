# Weather API Wrapper Service

A Flask-based REST API wrapper service for the Visual Crossing Weather API with built-in caching, rate limiting, and data persistence.

## Project Overview

This project is based on the [Weather API Wrapper Service](https://roadmap.sh/projects/weather-api-wrapper-service) challenge from roadmap.sh. It demonstrates building a production-ready API wrapper with caching, database persistence, and proper error handling.

## Features

- **Weather Data Retrieval**: Fetch current weather conditions, forecasts, and historical data using coordinates
- **Redis Caching**: 24-hour cache to minimize API calls and improve response times
- **PostgreSQL Database**: Persistent storage of weather data, conditions, and station information
- **Rate Limiting**: Built-in request rate limiting to prevent abuse
- **Async Support**: Fully asynchronous route handlers for better performance
- **API Documentation**: Swagger UI for interactive API documentation
- **Comprehensive Data Model**: Stores current conditions, daily/hourly forecasts, and weather stations

## Tech Stack

- **Framework**: Flask 2.0+ with async support
- **API Documentation**: Flask-Smorest (OpenAPI/Swagger)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **Rate Limiting**: Flask-Limiter
- **Environment Management**: python-dotenv
- **HTTP Client**: requests

## Prerequisites

- Python 3.12+
- PostgreSQL database
- Redis server
- Visual Crossing Weather API key ([Get one here](https://www.visualcrossing.com/weather-api))

## Installation

### 1. Clone the repository

```bash
cd weather_app
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
# Weather API Configuration
WEATHER_API_URL=https://weather.visualcrossing.com/VisualCrossingWebServices
WEATHER_API_KEY=your_visual_crossing_api_key_here

# API Configuration
API_VERSION=/api/v1

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# JWT Secret (for future authentication)
JWT_SECRET=your_secret_key_here
```

### 5. Set up Redis

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Windows:**
Download and install from [Redis Windows](https://github.com/microsoftarchive/redis/releases)

### 6. Set up PostgreSQL

Make sure you have a PostgreSQL database created and update the `DATABASE_URL` in your `.env` file.

## Running the Application

### Development Mode

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Access Swagger UI

Navigate to `http://localhost:5000/swagger-ui` for interactive API documentation.

## API Endpoints

### Get Weather Details

**Endpoint:** `GET /api/v1/weather`

**Request Body:**
```json
{
    "longitiude": -122.4194,
    "latitude": 37.7749
}
```

**Success Response (200):**
```json
{
    "status": true,
    "data": {
        "id": "uuid",
        "query_cost": 1,
        "latitude": 37.7749,
        "longitude": -122.4194,
        "resolved_address": "San Francisco, CA, United States",
        "timezone": "America/Los_Angeles",
        "description": "Clear conditions throughout the day.",
        "current_conditions": {
            "temp": 65.0,
            "feelslike": 63.0,
            "humidity": 70.0,
            "conditions": "Clear",
            "icon": "clear-day"
        }
    }
}
```

**Error Response (200):**
```json
{
    "status": false,
    "error": "longitiude is missing"
}
```

**Error Response (400):**
```json
{
    "status": false,
    "error": "Weather cannot fetch, status code: 401"
}
```

## Postman Collection

Import the `Weather_API.postman_collection.json` file into Postman to test the API endpoints with pre-configured requests and example responses.


## Database Schema

### Weather Table
- Stores main weather query information
- Contains query metadata, location, timezone
- References current conditions and daily forecasts

### CurrentConditions Table
- Stores weather conditions (current, daily, hourly)
- Self-referential relationship for day/hour hierarchy
- Contains temperature, humidity, precipitation, wind data

### Station Table
- Stores weather station information
- Contains station location, quality, contribution data

## Caching Strategy

- **Cache Key Format**: `weather:{latitude}:{longitude}`
- **TTL**: 24 hours (86400 seconds)
- **Cache Hit**: Returns cached data immediately
- **Cache Miss**: Fetches from Visual Crossing API, stores in cache and database

## Error Handling

The service includes comprehensive error handling:
- Missing coordinates validation
- API key validation
- Weather API error responses
- Database transaction rollbacks
- Redis connection failures

## Rate Limiting

Rate limiting is implemented using Flask-Limiter. Configure limits in the route handlers as needed.

## Development

### Database Migrations

The application automatically creates tables on startup using SQLAlchemy's `create_all()` method. For production, consider using Flask-Migrate (Alembic) for proper migrations.

### Adding New Features

1. Update models in `models/weather.py`
2. Add service methods in `service/weather_service.py`
3. Create route handlers in `routes/weather_routes.py`
4. Update Postman collection with new endpoints

## Production Deployment

For production deployment, consider:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up proper logging
3. Configure environment-specific settings
4. Use environment variables for secrets
5. Set up database migrations with Flask-Migrate
6. Configure Redis persistence
7. Implement authentication/authorization
8. Set up monitoring and alerting

## License

This project is created for educational purposes based on the roadmap.sh challenge.

## References

- [Project Challenge](https://roadmap.sh/projects/weather-api-wrapper-service)
- [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
