# SHINING HORIZON TRADING - TECHNICAL DOCUMENTATION

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Installation Guide](#installation-guide)
5. [Database Schema](#database-schema)
6. [API Documentation](#api-documentation)
7. [Frontend Structure](#frontend-structure)
8. [Deployment](#deployment)
9. [Security](#security)
10. [Maintenance](#maintenance)

---

## System Overview

### Project Description
Shining Horizon Trading is a full-stack web application for managing and displaying an industrial products catalog. The system consists of:
- **Admin Dashboard**: For managing products, categories, brands
- **Public Website**: Static HTML pages for customers
- **REST API**: Backend services for data management
- **Page Generator**: Automatic HTML page generation from database

### Key Features
- Product catalog management (CRUD operations)
- Category and subcategory organization
- Brand management with logos
- Bulk CSV import functionality
- Static page generation
- Image upload and management
- User authentication and authorization
- Responsive design for mobile and desktop

---

## Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.13+ | Programming language |
| **FastAPI** | Latest | Web framework |
| **SQLAlchemy** | Latest | ORM (Object-Relational Mapping) |
| **SQLite** | 3.x | Database |
| **Uvicorn** | Latest | ASGI server |
| **Pydantic** | Latest | Data validation |
| **Jinja2** | Latest | Template engine |
| **Python-Jose** | Latest | JWT authentication |
| **Passlib** | Latest | Password hashing |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | - | Markup |
| **CSS3** | - | Styling |
| **JavaScript** | ES6+ | Interactivity |
| **Tailwind CSS** | 3.x | CSS framework |
| **AOS** | 2.x | Scroll animations |
| **Inter Font** | - | Typography |

### Development Tools
- **Git**: Version control
- **VS Code**: Code editor
- **Python venv**: Virtual environment
- **Python HTTP Server**: Development server

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER                        │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Public Website  │         │  Admin Dashboard │     │
│  │  (Static HTML)   │         │  (SPA)           │     │
│  └────────┬─────────┘         └────────┬─────────┘     │
└───────────┼──────────────────────────────┼──────────────┘
            │                              │
            │ HTTP                         │ HTTP/REST API
            │                              │
┌───────────┼──────────────────────────────┼──────────────┐
│           ▼                              ▼               │
│  ┌─────────────────┐         ┌──────────────────┐      │
│  │  Static Files   │         │   FastAPI App    │      │
│  │  (Port 3000)    │         │   (Port 8000)    │      │
│  └─────────────────┘         └────────┬─────────┘      │
│                                        │                 │
│                              ┌─────────┴─────────┐      │
│                              │                   │      │
│                         ┌────▼─────┐      ┌─────▼────┐ │
│                         │ SQLite   │      │ Uploads  │ │
│                         │ Database │      │ Folder   │ │
│                         └──────────┘      └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Application Layers

#### 1. Presentation Layer
- **Public Website**: Static HTML pages generated from database
- **Admin Dashboard**: Single-page application for management

#### 2. API Layer (FastAPI)
- **Routers**: Handle HTTP requests
- **Services**: Business logic
- **Schemas**: Data validation
- **Models**: Database entities

#### 3. Data Layer
- **SQLite Database**: Persistent storage
- **File System**: Image uploads

---

## Installation Guide

### Prerequisites
- Python 3.13 or higher
- Git
- Web browser (Chrome, Firefox, or Edge)

### Step 1: Clone Repository
```bash
git clone https://github.com/moeezshafi/SHINING-HORIZON-Website.git
cd SHINING-HORIZON-Website
```

### Step 2: Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Initialize Database
```bash
python init_db.py
```

This creates:
- SQLite database (`shining_horizon.db`)
- Database tables
- Default admin user (username: `admin`, password: `admin123`)

### Step 3: Start Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

### Step 4: Start Frontend Server

Open a new terminal in the project root:

```bash
python -m http.server 3000
```

Frontend will be available at: `http://localhost:3000`

### Step 5: Access the Application

- **Public Website**: http://46.62.254.185:3004/
- **Admin Dashboard**: http://46.62.254.185:3004/admin/login.html
- **API Documentation**: http://46.62.254.185:8000/docs

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│   users     │
├─────────────┤
│ id          │ PK
│ username    │
│ email       │
│ password    │
│ role        │
│ is_active   │
│ created_at  │
└─────────────┘

┌─────────────────┐
│   categories    │
├─────────────────┤
│ id              │ PK
│ name            │
│ slug            │
│ type            │ (simple/detailed)
│ description     │
│ hero_title      │
│ hero_description│
│ image           │
│ display_order   │
│ is_active       │
│ show_on_home    │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────┐
│  subcategories      │
├─────────────────────┤
│ id                  │ PK
│ category_id         │ FK → categories.id
│ name                │
│ slug                │
│ description         │
│ image               │
│ display_order       │
│ is_active           │
│ created_at          │
│ updated_at          │
└────────┬────────────┘
         │
         │ 1:N
         │
┌────────▼────────┐         ┌─────────────┐
│    products     │ N:1     │   brands    │
├─────────────────┤─────────┤─────────────┤
│ id              │ PK      │ id          │ PK
│ category_id     │ FK      │ name        │
│ subcategory_id  │ FK      │ slug        │
│ brand_id        │ FK ────▶│ logo        │
│ name            │         │ display_order│
│ slug            │         │ is_active   │
│ part_number     │         │ created_at  │
│ short_description│        │ updated_at  │
│ description     │         └─────────────┘
│ image           │
│ display_order   │
│ is_active       │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### Table Descriptions

#### users
Stores admin user accounts.
- **role**: 'admin' or 'super_admin'
- **password**: Bcrypt hashed

#### categories
Main product categories (e.g., Industrial Automation).
- **type**: 'simple' (basic page) or 'detailed' (full hero section)
- **slug**: URL-friendly identifier
- **show_on_home**: Display on homepage

#### subcategories
Product types within categories (e.g., PLC Controllers).
- **category_id**: Parent category reference

#### brands
Manufacturer brands (e.g., Siemens, ABB).
- **logo**: Path to brand logo image

#### products
Individual products with specifications.
- **category_id**: Required
- **subcategory_id**: Optional
- **brand_id**: Optional
- **part_number**: Manufacturer part number

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication

All API endpoints (except login) require JWT authentication.

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin@shininghorizon.com",
  "password": "admin@123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin@shininghorizon.com",
    "email": "admin@shininghorizon.com",
    "role": "super_admin"
  }
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer {token}

Response:
{
  "id": 1,
  "username": "admin@shininghorizon.com",
  "email": "admin@shininghorizon.com",
  "role": "super_admin"
}
```

### Categories API

#### List Categories
```http
GET /categories?include_inactive=false
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "name": "Industrial Automation",
    "slug": "industrial-automation",
    "type": "detailed",
    "description": "...",
    "product_count": 25,
    "subcategory_count": 5
  }
]
```

#### Create Category
```http
POST /categories
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Industrial Automation",
  "type": "detailed",
  "description": "Automation products",
  "hero_title": "Industrial Automation",
  "hero_description": "Complete automation solutions",
  "display_order": 1,
  "show_on_home": true
}
```

#### Update Category
```http
PUT /categories/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Delete Category
```http
DELETE /categories/{id}
Authorization: Bearer {token}

Response:
{
  "message": "Category deleted successfully"
}
```

### Products API

#### List Products
```http
GET /products?category_id=1&subcategory_id=2&brand_id=3&skip=0&limit=100
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "name": "Siemens S7-1200",
    "slug": "siemens-s7-1200",
    "part_number": "6ES7214-1AG40-0XB0",
    "category": {
      "id": 1,
      "name": "Industrial Automation"
    },
    "subcategory": {
      "id": 1,
      "name": "PLC Controllers"
    },
    "brand": {
      "id": 1,
      "name": "Siemens"
    }
  }
]
```

#### Create Product
```http
POST /products
Authorization: Bearer {token}
Content-Type: application/json

{
  "category_id": 1,
  "subcategory_id": 1,
  "brand_id": 1,
  "name": "Siemens S7-1200",
  "part_number": "6ES7214-1AG40-0XB0",
  "short_description": "Compact PLC",
  "description": "Full description...",
  "display_order": 1
}
```

### Import API

#### Import Brands
```http
POST /import/brands
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: brands.csv

Response:
{
  "created": 10,
  "updated": 5,
  "skipped": 2,
  "errors": []
}
```

#### Import Categories
```http
POST /import/categories
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: categories.csv
```

#### Import Subcategories
```http
POST /import/subcategories
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: subcategories.csv
```

#### Import Products
```http
POST /import/products
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: products.csv
```

### Upload API

#### Upload Image
```http
POST /upload/image/{folder}
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: image.jpg
folder: products | categories | brands | subcategories

Response:
{
  "filename": "abc123.jpg",
  "url": "/uploads/products/abc123.jpg"
}
```

### Generator API

#### Generate All Pages
```http
POST /generate/all
Authorization: Bearer {token}

Response:
{
  "message": "Generated 45 pages successfully",
  "categories": 10,
  "products": 35
}
```

#### Generate Category Page
```http
POST /generate/category/{id}
Authorization: Bearer {token}

Response:
{
  "message": "Category page generated",
  "filename": "category-industrial-automation.html"
}
```

---

## Frontend Structure

### Directory Layout

```
project-root/
├── index.html                    # Homepage
├── brands.html                   # All brands page
├── categories.html               # All categories page
├── products.html                 # All products page
├── quote.html                    # Quote request form
├── category-*.html               # Generated category pages
├── product-*.html                # Generated product pages
├── brand-*.html                  # Generated brand pages
│
├── components/                   # Shared components
│   ├── header.js                 # Navigation header
│   ├── footer.js                 # Footer
│   └── shared-styles.css         # Common styles
│
├── public/                       # Static assets
│   ├── logo/                     # Company logos
│   ├── categories/               # Category images
│   ├── products/                 # Product images
│   ├── brands/                   # Brand logos
│   └── hero/                     # Hero section images
│
├── admin/                        # Admin dashboard
│   ├── index.html                # Dashboard home
│   ├── login.html                # Login page
│   ├── categories.html           # Category management
│   ├── subcategories.html        # Subcategory management
│   ├── products.html             # Product management
│   ├── brands.html               # Brand management
│   ├── import.html               # CSV import
│   ├── users.html                # User management
│   └── assets/                   # Admin assets
│       ├── css/
│       │   └── style.css         # Admin styles
│       └── js/
│           ├── api.js            # API client
│           ├── auth.js           # Authentication
│           └── utils.js          # Utilities
│
├── backend/                      # Backend application
│   ├── app/
│   │   ├── main.py               # FastAPI app
│   │   ├── config.py             # Configuration
│   │   ├── database.py           # Database connection
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── routers/              # API routes
│   │   ├── services/             # Business logic
│   │   └── templates/            # Jinja2 templates
│   ├── uploads/                  # Uploaded files
│   ├── requirements.txt          # Python dependencies
│   ├── init_db.py                # Database initialization
│   └── shining_horizon.db        # SQLite database
│
└── catalog_data/                 # CSV import files
    ├── brands.csv
    ├── categories.csv
    ├── subcategories.csv
    └── products.csv
```

### Component Architecture

#### Header Component (components/header.js)
```javascript
// Dynamically loaded navigation
// Features:
// - Responsive mobile menu
// - Active page highlighting
// - Dropdown menus
// - Search functionality
```

#### Footer Component (components/footer.js)
```javascript
// Dynamically loaded footer
// Features:
// - Company information
// - Quick links
// - Contact details
// - Social media links
```

### Page Generation

Pages are generated using Jinja2 templates:

1. **Template Files** (`backend/app/templates/`)
   - `category_detailed.html`: Full category pages
   - `category_simple.html`: Basic category pages
   - `product_listing.html`: Product detail pages

2. **Generation Process**:
   - Admin clicks "Generate Pages"
   - Backend fetches data from database
   - Jinja2 renders templates with data
   - HTML files saved to project root
   - Static pages ready for deployment

---

## Deployment

### Production Deployment Options

#### Option 1: Traditional Web Server

**Requirements:**
- Linux server (Ubuntu 20.04+ recommended)
- Nginx web server
- Python 3.13+
- Supervisor (process manager)

**Steps:**

1. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3.13 python3-pip nginx supervisor
```

2. **Clone Repository**
```bash
cd /var/www
git clone https://github.com/moeezshafi/SHINING-HORIZON-Website.git
cd SHINING-HORIZON-Website
```

3. **Setup Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
```

4. **Configure Supervisor**
Create `/etc/supervisor/conf.d/shining-horizon.conf`:
```ini
[program:shining-horizon-api]
command=/var/www/SHINING-HORIZON-Website/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/var/www/SHINING-HORIZON-Website/backend
user=www-data
autostart=true
autorestart=true
```

5. **Configure Nginx**
Create `/etc/nginx/sites-available/shining-horizon`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend
    location / {
        root /var/www/SHINING-HORIZON-Website;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Uploads
    location /uploads {
        alias /var/www/SHINING-HORIZON-Website/backend/uploads;
    }
}
```

6. **Enable and Start**
```bash
sudo ln -s /etc/nginx/sites-available/shining-horizon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start shining-horizon-api
```

#### Option 2: Docker Deployment

**Dockerfile (Backend)**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/shining_horizon.db:/app/shining_horizon.db
    environment:
      - DATABASE_URL=sqlite:///./shining_horizon.db
  
  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
```

---

## Security

### Authentication
- **JWT Tokens**: Secure token-based authentication
- **Password Hashing**: Bcrypt with salt
- **Token Expiration**: 24-hour token lifetime

### Best Practices
1. **Change Default Credentials**: Immediately after installation
2. **Use HTTPS**: In production (SSL/TLS certificates)
3. **CORS Configuration**: Restrict allowed origins
4. **Input Validation**: All inputs validated with Pydantic
5. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
6. **File Upload Validation**: Only allowed image formats
7. **Rate Limiting**: Implement in production

### Production Security Checklist
- [ ] Change default admin password
- [ ] Configure CORS with specific origins
- [ ] Enable HTTPS
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Update dependencies regularly
- [ ] Monitor logs for suspicious activity
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets

---

## Maintenance

### Regular Tasks

#### Daily
- Monitor server logs
- Check disk space
- Verify backups

#### Weekly
- Review user activity
- Check for errors in logs
- Update product information

#### Monthly
- Update dependencies
- Security audit
- Performance optimization
- Database cleanup

### Backup Strategy

#### Database Backup
```bash
# Backup SQLite database
cp backend/shining_horizon.db backups/shining_horizon_$(date +%Y%m%d).db

# Automated daily backup (crontab)
0 2 * * * cp /var/www/SHINING-HORIZON-Website/backend/shining_horizon.db /backups/db_$(date +\%Y\%m\%d).db
```

#### File Backup
```bash
# Backup uploads folder
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz backend/uploads/

# Full backup
tar -czf backups/full_backup_$(date +%Y%m%d).tar.gz \
  --exclude='backend/venv' \
  --exclude='backend/__pycache__' \
  .
```

### Monitoring

#### Log Files
- **Backend Logs**: Check uvicorn output
- **Nginx Logs**: `/var/log/nginx/access.log` and `error.log`
- **Application Logs**: Implement logging in FastAPI

#### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

### Troubleshooting

#### Backend Not Starting
```bash
# Check Python version
python --version

# Check dependencies
pip list

# Check database
ls -la backend/shining_horizon.db

# Check logs
tail -f /var/log/supervisor/shining-horizon-api.log
```

#### Database Issues
```bash
# Reinitialize database
cd backend
python init_db.py

# Check database integrity
sqlite3 shining_horizon.db "PRAGMA integrity_check;"
```

---

## Performance Optimization

### Frontend Optimization
1. **Image Optimization**
   - Compress images before upload
   - Use WebP format
   - Implement lazy loading

2. **Caching**
   - Browser caching headers
   - CDN for static assets

3. **Minification**
   - Minify CSS and JavaScript
   - Combine files where possible

### Backend Optimization
1. **Database Indexing**
   - Index frequently queried columns
   - Optimize query performance

2. **Caching**
   - Redis for session storage
   - Cache frequently accessed data

3. **Connection Pooling**
   - Configure SQLAlchemy pool size
   - Optimize database connections

---

## Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub
```

### Testing
```bash
# Run backend tests
cd backend
pytest

# Check code style
flake8 app/

# Type checking
mypy app/
```

---

## API Rate Limits

In production, implement rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/products")
@limiter.limit("100/minute")
async def get_products():
    pass
```

---

## Environment Variables

Create `.env` file in backend directory:

```env
# Application
APP_NAME=Shining Horizon Admin API
DEBUG=False

# Database
DATABASE_URL=sqlite:///./shining_horizon.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Upload
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=5242880

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Conclusion

This technical documentation provides a comprehensive overview of the Shining Horizon Trading system. For additional support or questions, refer to the user guide or contact the development team.

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Maintained By**: Development Team
