# FoodSnap AI Backend

FastAPI backend service for FoodSnap AI application.

## Overview

This backend provides REST API endpoints for food image analysis and nutrition information. Built with FastAPI for high performance and automatic API documentation.

## Features

- ✅ FastAPI with automatic OpenAPI documentation
- ✅ CORS enabled for frontend integration
- ✅ Environment variable configuration
- ✅ Health check endpoints
- ✅ Structured folder organization
- 🚧 ML model integration (placeholder)
- 🚧 Nutrition API integration (placeholder)

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── README.md           # This file
├── model/              # ML models and utilities
│   └── __init__.py     # Package initialization
├── services/           # Business logic services
│   └── __init__.py     # Package initialization
└── utils/              # Utility functions
    └── __init__.py     # Package initialization
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Add USDA API key when ready to implement nutrition features
```

### 3. Run the Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Checks

- `GET /` - Basic health check with API info
- `GET /health` - Detailed health check with service status

### Documentation

- `GET /docs` - Swagger UI (interactive API docs)
- `GET /redoc` - ReDoc (alternative API documentation)

## Configuration

The server configuration is controlled by environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `USDA_API_KEY` | - | USDA API key for nutrition data |
| `LOG_LEVEL` | `info` | Logging level |

## Development Notes

### Adding New Features

1. **API Routes**: Create new route files in appropriate packages
2. **Services**: Implement business logic in `services/` package
3. **Models**: Add ML models in `model/` package
4. **Utils**: Add helper functions in `utils/` package

### Code Organization

- **main.py**: Application setup, middleware, basic endpoints
- **model/**: Machine learning models and inference logic
- **services/**: Business logic and external API integrations
- **utils/**: Helper functions, validators, utilities

## Future Implementation

The following features are planned for future iterations:

1. **ML Model Integration**
   - Food classification using ResNet50/MobileNetV2
   - Image preprocessing pipeline
   - Model inference endpoints

2. **Nutrition API Integration**
   - USDA FoodData Central API client
   - Nutrition data caching
   - Food database queries

3. **File Upload Handling**
   - Image validation and processing
   - Temporary file management
   - Error handling

4. **Database Integration**
   - User data storage
   - Analysis history
   - Caching layer

## Testing

```bash
# Run health check
curl http://localhost:8000/

# Run detailed health check
curl http://localhost:8000/health

# View API documentation
# Open http://localhost:8000/docs in browser
```

## Deployment

For production deployment:

1. Set `ENVIRONMENT=production`
2. Configure proper CORS origins
3. Add USDA API key
4. Use proper WSGI server (Gunicorn/Uvicorn)
5. Set up monitoring and logging

## License

This project is part of FoodSnap AI MVP.
