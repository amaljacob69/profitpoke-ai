# ProfitPoke AI - Project Structure

## Overview
This is a Flask-based AI-powered stock recommendation application with Firebase hosting capabilities.

## Project Tree Structure

```
R1/
├── 📁 Core Application Files
│   ├── app.py                 # Main Flask application with routes and AI integration
│   ├── config.py              # Configuration settings and environment variables
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables (API keys)
│
├── 📁 Frontend Templates & Static Files
│   ├── templates/
│   │   └── index.html         # Main HTML template with form
│   ├── static/
│   │   ├── styles.css         # CSS styling (Bootstrap + custom)
│   │   └── scripts.js         # JavaScript functionality and AJAX calls
│   └── public/
│       └── 404.html           # Firebase 404 error page
│
├── 📁 Firebase Configuration
│   ├── firebase.json          # Firebase hosting configuration
│   ├── .firebaserc            # Firebase project configuration
│   └── .firebase/             # Firebase cache directory
│
├── 📁 Node.js/Firebase Tools
│   ├── package.json           # Node.js dependencies (Firebase tools)
│   ├── package-lock.json      # Dependency lock file
│   └── node_modules/          # Node.js packages
│
├── 📁 Python Environment
│   ├── .venv/                 # Python virtual environment
│   └── __pycache__/           # Python bytecode cache
│
└── 📁 Other Files
    ├── .gitignore             # Git ignore rules
    ├── app.log                # Application logs
    ├── PROJECT_STRUCTURE.md   # This file
    └── .DS_Store              # macOS system file
```

## Key Components

### Backend (Python/Flask)
- **app.py** - Main Flask application with:
  - Stock recommendation routes
  - Kite Connect integration
  - Grok AI integration
  - Rate limiting and caching
  - Form handling

- **config.py** - Configuration management:
  - Environment variable loading
  - API key configuration
  - Flask settings

- **.env** - Environment variables:
  - KITE_API_KEY
  - KITE_API_SECRET
  - GROK_API_KEY
  - FLASK_SECRET_KEY
  - REDIS_URL

### Frontend (HTML/CSS/JS)
- **templates/index.html** - Main webpage with:
  - Bootstrap styling
  - Stock recommendation form
  - Results display area
  - Modal for saved recommendations

- **static/styles.css** - Styling:
  - Custom CSS rules
  - Bootstrap overrides
  - Responsive design

- **static/scripts.js** - Frontend logic:
  - Form submission handling
  - AJAX calls to backend
  - Results display
  - Copy/save functionality

### Dependencies
- **Python packages** (requirements.txt):
  - Flask==2.3.3
  - Flask-WTF==1.1.1
  - WTForms==3.0.1
  - Flask-Limiter==3.5.0
  - Flask-Caching==2.1.0
  - kiteconnect==4.2.0
  - python-dotenv==1.0.0
  - redis==5.0.1
  - requests==2.31.0

- **Node.js packages** (package.json):
  - firebase-tools for deployment

## Application Flow
1. User visits homepage (index.html)
2. Fills out stock recommendation form
3. JavaScript sends AJAX request to /recommend
4. Flask processes request with AI integration
5. Returns personalized stock recommendations
6. Results displayed with copy/save options

## Deployment
- **Local Development**: Flask dev server on port 5003
- **Firebase Hosting**: Static files served from public/
- **Hybrid Setup**: Both Python backend and Firebase frontend

## API Integrations
- **Kite Connect**: Real-time stock data
- **Grok AI**: AI-powered recommendations
- **Rate Limiting**: 200 requests/day, 50/hour
- **Caching**: 1-hour cache for recommendations
