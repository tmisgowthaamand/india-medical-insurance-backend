# MediCare+ Backend API 🚀

**AI-Powered Medical Insurance Dashboard - Backend Service**

A high-performance FastAPI backend service providing AI/ML capabilities, secure authentication, and comprehensive data management for medical insurance claim prediction and analysis.

## 🚀 Project Status: **COMPLETED** ✅

This is a fully functional, production-ready backend API deployed on Render with comprehensive features and bulletproof reliability.

## ✨ Core Features

### 🤖 **AI/ML Engine**
- Advanced insurance claim prediction models
- Real-time BMI analysis and health risk assessment
- Fast model training and retraining capabilities
- Scikit-learn integration with optimized algorithms

### 🔐 **Security & Authentication**
- JWT-based secure authentication system
- Role-based access control (Admin/User)
- Protected API endpoints
- Secure password hashing with bcrypt

### 💌 **Email Service Integration**
- Bulletproof Gmail SMTP integration
- Professional HTML email templates
- Prediction report delivery system
- Comprehensive error handling and retry mechanisms

### 📊 **Data Management**
- Supabase database integration
- Real-time statistics and analytics
- Dataset upload and management
- Claims analysis and insights

### ⚡ **Performance & Reliability**
- Optimized API response times
- Comprehensive error handling
- Health check monitoring
- Production-grade deployment configuration

## Deployment on Render

### Prerequisites

1. A Render account
2. A Supabase project with database setup
3. Environment variables configured

### Environment Variables

Set these environment variables in your Render service:

```bash
# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Authentication
JWT_SECRET_KEY=your_jwt_secret_key

# Email Service (Gmail SMTP)
GMAIL_EMAIL=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# CORS Configuration
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000

# Environment
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

## 🛠 API Endpoints

### **Authentication Endpoints**
- `POST /signup` - User registration with validation
- `POST /login` - User authentication with JWT
- `GET /me` - Get current user profile information

### **AI/ML Prediction Endpoints**
- `POST /predict` - Insurance claim prediction with BMI analysis
- `GET /model-info` - ML model information and performance metrics

### **Analytics & Statistics**
- `GET /stats` - Comprehensive dataset statistics
- `GET /claims-analysis` - Advanced claims analysis with visualizations

### **Email Service**
- `POST /send-prediction-email` - Send prediction reports via email
- `POST /test-email` - Test email functionality

### **Admin Endpoints** (Protected)
- `POST /admin/upload-dataset` - Upload new training datasets
- `POST /admin/retrain-model` - Retrain ML models with new data

### **System Endpoints**
- `GET /` - API information and status
- `GET /health` - Health check for monitoring

## 🏗 Technology Stack

### **Backend Framework**
- **FastAPI** - Modern, fast web framework for APIs
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic** - Data validation using Python type annotations

### **AI/ML Libraries**
- **Scikit-learn** - Machine learning algorithms
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing

### **Database & Storage**
- **Supabase** - PostgreSQL database with real-time features
- **JSON Storage** - Fallback local storage system

### **Email Service**
- **Gmail SMTP** - Professional email delivery
- **HTML Templates** - Rich email formatting
- **Retry Mechanisms** - Bulletproof delivery system

### **Security**
- **JWT** - JSON Web Tokens for authentication
- **bcrypt** - Password hashing
- **CORS** - Cross-origin resource sharing

## 💻 Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Development Server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8001
   ```

4. **API Documentation**:
   - Swagger UI: `http://localhost:8001/docs`
   - ReDoc: `http://localhost:8001/redoc`

## 🗄 Database Setup

### **Supabase Configuration**
1. Create a new Supabase project
2. Run the database migration scripts
3. Configure environment variables
4. Test connection with health endpoint

### **Required Tables**
- `users` - User authentication and profiles
- `predictions` - ML prediction history
- `datasets` - Training data management
- `model_metadata` - ML model information

## 🏆 Project Achievements

✅ **Production Deployment** - Successfully deployed on Render  
✅ **AI/ML Integration** - Advanced prediction algorithms  
✅ **Email Functionality** - Bulletproof Gmail SMTP service  
✅ **Database Integration** - Supabase PostgreSQL setup  
✅ **Security Implementation** - JWT authentication system  
✅ **Admin Panel API** - Complete administrative capabilities  
✅ **Performance Optimization** - Fast response times  
✅ **Error Handling** - Comprehensive error management  
✅ **API Documentation** - Auto-generated Swagger docs  

## 📞 Support

This is a completed, production-ready backend service. All features have been implemented and tested. For technical details, refer to the comprehensive API documentation available at `/docs` endpoint.
