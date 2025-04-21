# GeoPoints API

A robust RESTful API for managing geographic points of interest with spatial querying capabilities.

## Features

- **Geographic Data Management:** Create, read, update, and delete points of interest with geographic coordinates
- **Spatial Queries:** Find nearby points, nearest neighbors, and points within polygons
- **Categories:** Organize points into customizable categories 
- **Authentication:** Secure API with JWT-based authentication
- **Documentation:** Auto-generated OpenAPI documentation

## Technologies

- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL with PostGIS extension
- **ORM:** SQLAlchemy with GeoAlchemy2
- **Migrations:** Alembic
- **Authentication:** JWT with OAuth2
- **Containerization:** Docker & Docker Compose
- **Testing:** pytest

## Architecture

The application follows a layered architecture:

- **API Layer:** FastAPI routers and endpoints
- **Service Layer:** Business logic and data processing
- **Repository Layer:** Database access and queries
- **Model Layer:** SQLAlchemy models and database schema
- **Schema Layer:** Pydantic models for validation and serialization

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/RidwanWaheed/geopoints-api.git
   cd geopoints-api
   ```

2. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

3. Start the application:
   ```bash
   make run
   ```

4. Run database migrations:
   ```bash
   make migrate-db
   ```

5. The API will be available at [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
   - ReDoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

## API Usage

## Authentication & Authorization

1. Register a user:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "username": "user", "password": "StrongPassword123!"}'
   ```

2. Get an access token:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/token \
     -d "username=user@example.com&password=StrongPassword123!" \
     -H "Content-Type: application/x-www-form-urlencoded"
   ```

3. Use the token in subsequent requests:
   ```bash
   curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:8000/api/v1/points
   ```

**Note:** Some operations (like creating and deleting categories) require superuser privileges. To create a superuser account:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com", 
    "username": "admin", 
    "password": "AdminStrongPassword123!", 
    "is_superuser": true
  }'
```

The API implements rate limiting to prevent abuse. Different endpoints have different rate limits based on their resource requirements.

### Points of Interest

#### Create a Point

```bash
curl -X POST http://localhost:8000/api/v1/points \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Berlin Cathedral",
    "description": "Historic cathedral in Berlin",
    "latitude": 52.5192,
    "longitude": 13.4016,
    "category_id": 1
  }'
```

#### Get Nearby Points

```bash
curl "http://localhost:8000/api/v1/points/nearby?lat=52.5200&lng=13.4050&radius=1000"
```

#### Get Nearest Points

```bash
curl "http://localhost:8000/api/v1/points/nearest?lat=52.5200&lng=13.4050&limit=5"
```

#### Get Points Within Polygon

```bash
curl -X POST "http://localhost:8000/api/v1/points/within" \
  -H "Content-Type: application/json" \
  -d '{
    "polygon_wkt": "POLYGON((13.3 52.5, 13.3 52.55, 13.45 52.55, 13.45 52.5, 13.3 52.5))"
  }'
```

## Development

### Project Structure

```
geopoints-api/
├── alembic/              # Database migrations
├── app/                  # Application code
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Database repositories
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── spatial/          # Spatial utilities
├── tests/                # Automated tests
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Docker image specification
├── Makefile              # Development commands
└── README.md             # This file
```

### Available Commands

```bash
# Start the application
make run

# Stop the application
make down

# View logs
make logs

# Run migrations
make migrate-db

# Run tests
make test

# Format code
make format

# Open a shell in the API container
make enter-app

# Open a shell in the database container
make enter-db
```

## Testing

Run the test suite with:

```bash
make test
```

## Future Improvements

1. **Enhanced Spatial Features**
   - Support for more complex geometries (lines, polygons)
   - Route calculation between points

2. **Performance Optimizations**
   - Implement caching for frequently requested data
   - Add database indexing strategies for larger datasets

3. **Extended Authentication**
   - OAuth integration with popular providers
   - API key management for third-party applications

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- PostGIS for spatial database capabilities
- FastAPI for the powerful web framework
- SQLAlchemy and GeoAlchemy2 for ORM support
