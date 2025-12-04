# SMRM Earthquake API

A FastAPI application for managing earthquake data from SMRM.

## Features

- RESTful API for earthquake data
- PostgreSQL database integration
- Data synchronization with external SMRM API
- Filtering and pagination support

## Requirements

### Local Development
- Python 3.8+
- PostgreSQL

### Docker Deployment
- Docker
- Docker Compose

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd smrm-db-fast-api
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

#### For Local Development

Create a `.env` file in the project root with the following content:

```
DATABASE_URL=postgresql://username:password@localhost:5432/smrm_db
API_URL=https://api.smrm.uz/api/earthquakes
```

Replace `username` and `password` with your PostgreSQL credentials.

#### For Docker Deployment

Environment variables are already configured in the `docker-compose.yml` file. If you need to modify them, edit the `environment` section in the file.

5. Create the database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE smrm_db;
```

## Running the Application

### Local Development

Run the application with:

```bash
python run.py
```

### Docker Deployment

1. Build and start the containers:

```bash
docker-compose up -d --build
```

2. To view logs:

```bash
docker-compose logs -f
```

3. To stop the containers:

```bash
docker-compose down
```

4. To stop the containers and remove volumes (this will delete all data):

```bash
docker-compose down -v
```

The API will be available at http://localhost:8005.

- API documentation: http://localhost:8005/docs
- Alternative documentation: http://localhost:8005/redoc

## API Endpoints

- `GET /api/earthquakes` - List earthquakes with filtering and pagination
- `GET /api/earthquakes/{id}` - Get a specific earthquake
- `POST /api/earthquakes` - Create a new earthquake
- `PUT /api/earthquakes/{id}` - Update an earthquake
- `DELETE /api/earthquakes/{id}` - Delete an earthquake
- `POST /api/earthquakes/sync` - Sync data from external SMRM API

## Query Parameters

The `GET /api/earthquakes` endpoint supports the following query parameters:

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10)
- `epicenter` - Filter by epicenter
- `from_date` / `to_date` - Filter by date range
- `from_magnitude` / `to_magnitude` - Filter by magnitude range
- `from_depth` / `to_depth` - Filter by depth range
- `from_latitude` / `to_latitude` - Filter by latitude range
- `from_longitude` / `to_longitude` - Filter by longitude range
- `sort` - Sort order (default: "datetime_desc")

## Example Usage

### Sync data from external API

```bash
curl -X POST "http://localhost:8005/api/earthquakes/sync?page=1&per_page=100"
```

### Get earthquakes with filters

```bash
curl "http://localhost:8005/api/earthquakes?epicenter=Afg&from_magnitude=5&page=1&per_page=10"
```
