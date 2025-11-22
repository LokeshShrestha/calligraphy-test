# Quick Start Guide - Ranjana Calligraphy API

**Status**: ~75% Production Ready | [Full Assessment](PRODUCTION_READINESS.md)

## ⚡ 5-Minute Setup

### 1. Prerequisites
```bash
✅ Python 3.11+
✅ PostgreSQL database
✅ Google Gemini API key (free at: https://makersuite.google.com/app/apikey)
❌ Redis NOT required (despite what old docs say - Celery not configured)
```

### 2. Install & Configure
```bash
# Clone and setup
git clone <repo>
cd calligraphy-celerytest

# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Environment setup
copy .env.example .env
# Edit .env with your database credentials and Gemini API key

# Database
python manage.py migrate

# Run server
python manage.py runserver
```

### 3. Test It
```bash
# Visit: http://localhost:8000/admin
# API ready at: http://localhost:8000/api/
```

## 🎯 What Works Right Now

✅ **11 Working Endpoints**:
- Character recognition (99.5% accuracy)
- Similarity comparison (92.7% accuracy)
- AI-powered feedback (Gemini API)
- User authentication (JWT)
- History tracking with database persistence
- Statistics and analytics

✅ **Production-Ready Features**:
- Robust ML models (47MB + 25MB)
- Automatic image preprocessing
- Full CRUD operations
- PostgreSQL database
- JWT authentication
- CORS configured
- Gunicorn ready

## ⚠️ What Needs Work

❌ **Before Production**:
1. Security hardening (1 day):
   - Set DEBUG=False in .env
   - Remove SECRET_KEY from settings.py
   - Add rate limiting
   - Configure security headers

2. Logging setup (1 day):
   - Replace print() with proper logging
   - Add Sentry error tracking
   - Set up monitoring

3. Celery decision:
   - **Option A**: Implement properly (2 days) - for 10+ concurrent users
   - **Option B**: Remove references (1 hour) - for small scale

**Note**: Despite documentation mentioning Celery/async processing, it's NOT configured. API works synchronously.

## 📚 Key Files

```
README.md                    # Full documentation (comprehensive)
PRODUCTION_READINESS.md      # Detailed 75% assessment
api/views.py                 # 11 endpoint implementations
api/models.py                # Database schemas
calligrapy/settings.py       # Configuration
requirements.txt             # Dependencies
.env.example                 # Environment template
```

## 🔑 Environment Variables

```env
# Required
SECRET_KEY=your-secret-key-here
DEBUG=False  # For production
DB_NAME=your_db
DB_USER=postgres
DB_PASSWORD=your_pass
DB_HOST=localhost
DB_PORT=5432
GEMINI_API_KEY=your_api_key

# Optional
ALLOWED_HOSTS=yourdomain.com,localhost
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

## 🚀 Deploy Now (Quick)

### Render.com (Easiest)
1. Connect GitHub repo
2. Add environment variables in dashboard
3. Auto-deploys from main branch
4. Cost: $7-25/month

### Heroku
```bash
heroku create your-app
heroku addons:create heroku-postgresql:mini
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=xxx
heroku config:set GEMINI_API_KEY=xxx
git push heroku main
```

## 📊 API Quick Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/signup/` | POST | ❌ | Create account |
| `/api/signin/` | POST | ❌ | Get JWT tokens |
| `/api/predict/` | POST | ✅ | Recognize character |
| `/api/similarity/` | POST | ✅ | Compare handwriting |
| `/api/feedback/` | POST | ✅ | AI analysis |
| `/api/history/predictions/` | GET | ✅ | Get history |
| `/api/history/similarities/` | GET | ✅ | Get comparisons |
| `/api/history/similarities/<id>/` | DELETE | ✅ | Delete item |
| `/api/statistics/` | GET | ✅ | Get analytics |
| `/api/change-password/` | POST | ✅ | Update password |
| `/api/change-username/` | POST | ✅ | Update username |

**Authentication**: `Authorization: Bearer <access_token>`

## 🎓 Sample API Call

```bash
# 1. Sign up
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password2":"testpass123"}'

# 2. Sign in
curl -X POST http://localhost:8000/api/signin/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Response: {"refresh":"...","access":"..."}

# 3. Predict character
curl -X POST http://localhost:8000/api/predict/ \
  -H "Authorization: Bearer <access_token>" \
  -F "image=@character.png"

# Response: {"success":true,"predicted_class":12,"confidence":98.5,...}
```

## 🐛 Quick Troubleshooting

**"ModuleNotFoundError"**: 
```bash
pip install -r requirements.txt
```

**"Database connection failed"**:
```bash
# Check .env file has correct DB credentials
# Verify PostgreSQL is running
```

**"Reference image not found"**:
```bash
# Add 36 reference images to api/reference_images/
# Named: class_0.png through class_35.png
```

**"Gemini API error"**:
```bash
# Add GEMINI_API_KEY to .env
# Get free key: https://makersuite.google.com/app/apikey
```

## 📈 Performance Expectations

- **Character Recognition**: 1-3 seconds
- **Similarity (no AI)**: 2-4 seconds  
- **Similarity (with AI)**: 5-10 seconds
- **Concurrent Users**: 5-10 (synchronous) | 50+ (with Celery)
- **Database Queries**: <100ms

## 💡 Next Steps

1. **For Development**: You're ready! Start coding.
2. **For Testing**: Run `python manage.py test api.tests`
3. **For Production**: Read [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)
4. **For Scale**: Implement Celery (see Phase 3 in readiness doc)

## 🆘 Need Help?

- **Full Documentation**: See [README.md](README.md)
- **Production Assessment**: See [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)
- **Issues**: Check troubleshooting section in README

---

**Version**: 2.0  
**Models**: EfficientNet-B0 (99.5%) + Siamese Network (92.7%)  
**Classes**: 36 (0-35)  
**Status**: 75% Production Ready - Deploy after security fixes  
**Last Updated**: November 22, 2025
