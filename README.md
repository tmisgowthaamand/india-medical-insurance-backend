# Medical Insurance ML Dashboard - Backend

This is the FastAPI backend for the Medical Insurance ML Dashboard, designed to be deployed on Render.

## Features

- FastAPI REST API
- Machine Learning model for insurance claim prediction
- User authentication with JWT
- Supabase database integration
- Claims analysis and statistics
- Admin panel functionality

## Deployment on Render

### Prerequisites

1. A Render account
2. A Supabase project with database setup
3. Environment variables configured

### Environment Variables

Set these environment variables in your Render service:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET_KEY=your_jwt_secret_key
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
ENVIRONMENT=production
```

### Deployment Steps

1. **Connect Repository**: Connect your GitHub repository to Render
2. **Create Web Service**: 
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.11
3. **Set Environment Variables**: Add all required environment variables
4. **Deploy**: Render will automatically deploy your service

### Health Check

The API includes a health check endpoint at `/health` for monitoring.

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /signup` - User registration
- `POST /login` - User login
- `GET /me` - Get current user info
- `POST /predict` - ML prediction
- `GET /stats` - Dataset statistics
- `GET /claims-analysis` - Claims analysis
- `GET /model-info` - Model information
- `POST /admin/upload-dataset` - Upload dataset (Admin)
- `POST /admin/retrain-model` - Retrain model (Admin)

### Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env` file
3. Run: `uvicorn app:app --reload`

### Database Setup

The application uses Supabase for data storage. Make sure to:

1. Create a Supabase project
2. Run the SQL schema from `supabase_schema.sql`
3. Set the connection details in environment variables

## Support

For issues and questions, please check the main project documentation.
