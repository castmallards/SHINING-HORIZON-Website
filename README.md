# Shining Horizon Trading - Industrial Products Catalog

> Complete web application for managing and displaying industrial products catalog with admin dashboard, bulk import, and automatic page generation.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Support](#support)

---

## 🎯 Overview

Shining Horizon Trading is a full-stack web application designed for industrial product catalog management. The system provides:

- **Public Website**: Modern, responsive website for showcasing products
- **Admin Dashboard**: Comprehensive management interface
- **REST API**: Backend services for all operations
- **Page Generator**: Automatic HTML page generation from database
- **CSV Import**: Bulk data import functionality

### Key Capabilities

✅ Manage thousands of products across multiple categories  
✅ Organize by categories, subcategories, and brands  
✅ Bulk import via CSV files  
✅ Automatic static page generation  
✅ Image upload and management  
✅ User authentication and authorization  
✅ Mobile-responsive design  

---

## ✨ Features

### For Administrators

- **Product Management**: Add, edit, delete products with rich details
- **Category Organization**: Hierarchical category and subcategory structure
- **Brand Management**: Manage manufacturer brands with logos
- **Bulk Import**: Import hundreds of products via CSV
- **Image Upload**: Upload and manage product images
- **User Management**: Multiple admin users with role-based access
- **Page Generation**: One-click generation of all website pages
- **Search & Filter**: Find products quickly with advanced filters

### For Customers

- **Easy Navigation**: Browse products by category and brand
- **Product Search**: Find products quickly
- **Detailed Information**: Complete product specifications and images
- **Quote Request**: Multi-step quote request form
- **Mobile Friendly**: Responsive design for all devices
- **Fast Loading**: Optimized static pages

---

## 🛠 Technology Stack

### Backend
- **Python 3.13+**: Core programming language
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Jinja2**: Template engine
- **JWT**: Secure authentication
- **Bcrypt**: Password hashing

### Frontend
- **HTML5**: Modern markup
- **CSS3 & Tailwind CSS**: Styling framework
- **JavaScript ES6+**: Interactivity
- **AOS**: Scroll animations
- **Inter Font**: Typography

### Development Tools
- **Git**: Version control
- **Python venv**: Virtual environment
- **Python HTTP Server**: Development server

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- Git
- Web browser (Chrome, Firefox, or Edge)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/moeezshafi/SHINING-HORIZON-Website.git
cd SHINING-HORIZON-Website
```

2. **Setup Backend**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python init_db.py
```

3. **Start Backend Server**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

4. **Start Frontend Server** (new terminal)
```bash
# From project root
python -m http.server 3000
```

5. **Access the Application**
- Public Website: http://localhost:3000
- Admin Dashboard: http://localhost:3000/admin/login.html
- API Docs: http://localhost:8000/docs

### Default Login
- Username: `admin@shininghorizon.com`
- Password: `admin@123`

---

## 📚 Documentation

Comprehensive documentation is available in the following files:

| Document | Description | Pages |
|----------|-------------|-------|
| **DOCUMENTATION_INDEX.md** | Guide to all documentation | 5 |
| **PROJECT_SUMMARY.md** | Executive overview | 25 |
| **SHINING_HORIZON_USER_GUIDE.md** | Complete user guide | 60 |
| **TECHNICAL_DOCUMENTATION.md** | Technical details | 50 |
| **QUICK_START_GUIDE.md** | 5-minute setup | 5 |
| **ADMIN_WORKFLOW_EXAMPLES.md** | Real-world examples | 40 |
| **SYSTEM_CREDENTIALS.md** | Access credentials ⚠️ | 10 |

**Total Documentation**: 190+ pages, 47,000+ words

### Quick Links
- [User Guide](SHINING_HORIZON_USER_GUIDE.md) - Learn how to use the system
- [Technical Docs](TECHNICAL_DOCUMENTATION.md) - Installation and deployment
- [Quick Start](QUICK_START_GUIDE.md) - Get started in 5 minutes
- [Workflow Examples](ADMIN_WORKFLOW_EXAMPLES.md) - Step-by-step tutorials

---

## 📁 Project Structure

```
SHINING-HORIZON-Website/
├── admin/                      # Admin dashboard
│   ├── assets/                 # CSS, JS, images
│   ├── index.html              # Dashboard home
│   ├── login.html              # Login page
│   ├── products.html           # Product management
│   ├── categories.html         # Category management
│   ├── brands.html             # Brand management
│   ├── import.html             # CSV import
│   └── users.html              # User management
│
├── backend/                    # Backend application
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── models/             # Database models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── routers/            # API routes
│   │   ├── services/           # Business logic
│   │   └── templates/          # Jinja2 templates
│   ├── uploads/                # Uploaded images
│   ├── requirements.txt        # Python dependencies
│   ├── init_db.py              # Database initialization
│   └── shining_horizon.db      # SQLite database
│
├── components/                 # Shared components
│   ├── header.js               # Navigation header
│   ├── footer.js               # Footer
│   └── shared-styles.css       # Common styles
│
├── public/                     # Static assets
│   ├── logo/                   # Company logos
│   ├── categories/             # Category images
│   ├── products/               # Product images
│   └── brands/                 # Brand logos
│
├── catalog_data/               # CSV import files
│   ├── brands.csv
│   ├── categories.csv
│   ├── subcategories.csv
│   └── products.csv
│
├── index.html                  # Homepage
├── products.html               # All products page
├── brands.html                 # All brands page
├── categories.html             # All categories page
├── quote.html                  # Quote request form
├── category-*.html             # Generated category pages
├── product-*.html              # Generated product pages
│
└── Documentation/              # Complete documentation
    ├── DOCUMENTATION_INDEX.md
    ├── PROJECT_SUMMARY.md
    ├── SHINING_HORIZON_USER_GUIDE.md
    ├── TECHNICAL_DOCUMENTATION.md
    ├── QUICK_START_GUIDE.md
    ├── ADMIN_WORKFLOW_EXAMPLES.md
    └── SYSTEM_CREDENTIALS.md
```

---

## 💼 Usage

### Adding Products

#### Method 1: Manual Entry
1. Login to admin dashboard
2. Navigate to Products → Add Product
3. Fill in product details
4. Upload product image
5. Save and generate pages

#### Method 2: CSV Import
1. Prepare CSV files (brands, categories, subcategories, products)
2. Go to Import Data section
3. Upload files in order
4. Generate pages

**CSV Format Example:**
```csv
category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order
Industrial Automation,PLC Controllers,Siemens,Siemens S7-1200,6ES7214-1AG40-0XB0,Compact PLC,Full description here,1
```

### Managing Categories

```
Category Structure:
└── Industrial Automation (Category)
    ├── PLC Controllers (Subcategory)
    │   ├── Siemens S7-1200 (Product)
    │   └── ABB AC500 (Product)
    ├── VFDs (Subcategory)
    │   └── ABB ACS580 (Product)
    └── HMI Panels (Subcategory)
```

### Generating Pages

After adding or updating products:
1. Click "Generate Pages" in sidebar
2. Click "Generate All Pages"
3. Wait for completion
4. Visit public website to see changes

---

## 🔌 API Reference

### Base URL
```
Production: http://46.62.254.185:8000
Development: http://localhost:8000
```

### Authentication

**Login:**
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin@shininghorizon.com",
  "password": "admin@123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/categories` | List all categories |
| POST | `/categories` | Create category |
| GET | `/products` | List all products |
| POST | `/products` | Create product |
| GET | `/brands` | List all brands |
| POST | `/import/brands` | Import brands CSV |
| POST | `/import/products` | Import products CSV |
| POST | `/generate/all` | Generate all pages |

**Full API Documentation**: http://46.62.254.185:8000/docs

---

## 🚢 Deployment

### Production Deployment

The system is currently deployed at:
- **Server IP**: 46.62.254.185
- **Frontend Port**: 3004
- **Backend Port**: 8000

### Deployment Options

1. **Traditional Server** (Current)
   - Linux server with Nginx
   - Supervisor for process management
   - See [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) for details

2. **Docker**
   - Containerized deployment
   - Easy scaling
   - Consistent environment

3. **Cloud Hosting**
   - AWS, DigitalOcean, Linode
   - Managed services
   - Auto-scaling

See [Deployment Guide](TECHNICAL_DOCUMENTATION.md#deployment) for detailed instructions.

---

## 🔒 Security

### Features
- JWT token authentication
- Bcrypt password hashing
- Role-based access control
- Input validation
- SQL injection protection
- CORS configuration
- File upload validation

### Best Practices
- Change default credentials immediately
- Use HTTPS in production
- Regular security updates
- Monitor access logs
- Regular backups
- Strong password policy

---

## 🧪 Testing

### Manual Testing
1. Test login functionality
2. Add sample products
3. Test CSV import
4. Generate pages
5. Verify public website
6. Test quote form

### API Testing
Use the interactive API documentation:
```
http://46.62.254.185:8000/docs
```

---

## 🔧 Maintenance

### Regular Tasks

**Daily:**
- Monitor server logs
- Check disk space
- Verify backups

**Weekly:**
- Review user activity
- Update product information
- Check for errors

**Monthly:**
- Update dependencies
- Security audit
- Performance optimization
- Database cleanup

### Backup

**Database Backup:**
```bash
cp backend/shining_horizon.db backups/db_$(date +%Y%m%d).db
```

**Full Backup:**
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz \
  --exclude='backend/venv' \
  --exclude='backend/__pycache__' \
  .
```

---

## 📊 Database Schema

### Tables

- **users**: Admin user accounts
- **categories**: Main product categories
- **subcategories**: Product types within categories
- **brands**: Manufacturer brands
- **products**: Individual products

### Relationships

```
categories (1) ──→ (N) subcategories
categories (1) ──→ (N) products
subcategories (1) ──→ (N) products
brands (1) ──→ (N) products
```

---

## 🎨 Customization

### Branding
- Update logo in `public/logo/`
- Modify colors in CSS files
- Update company information in footer

### Content
- Edit homepage content in `index.html`
- Customize category descriptions
- Update contact information

### Features
- Add new product fields
- Implement additional filters
- Create custom reports
- Add email notifications

---

## 🐛 Troubleshooting

### Common Issues

**Can't Login:**
- Check credentials: `admin@shininghorizon.com` / `admin@123`
- Verify backend is running
- Clear browser cache

**CSV Import Fails:**
- Check CSV format (UTF-8)
- Verify column names
- Import in correct order

**Images Not Showing:**
- Check file format (JPG, PNG, WEBP)
- Verify file size (< 5MB)
- Clear browser cache

**Pages Not Updating:**
- Click "Generate Pages" again
- Clear browser cache (Ctrl+F5)
- Check products are active

See [Troubleshooting Guide](SHINING_HORIZON_USER_GUIDE.md#troubleshooting) for more solutions.

---

## 📞 Support

### Contact Information
- **Email**: info@shininghorizon.com
- **WhatsApp**: +966 53 659 8520
- **GitHub**: https://github.com/moeezshafi/SHINING-HORIZON-Website

### Documentation
- [User Guide](SHINING_HORIZON_USER_GUIDE.md)
- [Technical Documentation](TECHNICAL_DOCUMENTATION.md)
- [Quick Start Guide](QUICK_START_GUIDE.md)
- [Workflow Examples](ADMIN_WORKFLOW_EXAMPLES.md)

### Resources
- API Documentation: http://46.62.254.185:8000/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Tailwind CSS: https://tailwindcss.com/docs

---

## 📝 License

Proprietary - Shining Horizon Trading  
All rights reserved.

This software is the property of Shining Horizon Trading and is protected by copyright law. Unauthorized copying, distribution, or modification is prohibited.

---

## 👥 Credits

**Developed for**: Shining Horizon Trading  
**Version**: 1.0.0  
**Release Date**: February 2026  
**Status**: Production Ready ✅

---

## 🗺 Roadmap

### Future Enhancements
- [ ] Customer accounts and login
- [ ] Online ordering system
- [ ] Inventory management
- [ ] Price management
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Email notifications
- [ ] Product comparison
- [ ] Wishlist functionality
- [ ] Mobile app

---

## 📈 Statistics

- **Total Documentation**: 190+ pages
- **Code Files**: 100+
- **Database Tables**: 5
- **API Endpoints**: 30+
- **Supported Products**: Unlimited
- **Categories**: Unlimited
- **Brands**: Unlimited

---

## 🎓 Getting Help

### For Users
1. Read the [User Guide](SHINING_HORIZON_USER_GUIDE.md)
2. Check [Workflow Examples](ADMIN_WORKFLOW_EXAMPLES.md)
3. Try [Quick Start Guide](QUICK_START_GUIDE.md)
4. Contact support

### For Developers
1. Read [Technical Documentation](TECHNICAL_DOCUMENTATION.md)
2. Check API docs at `/docs`
3. Review code comments
4. Contact development team

---

## ✅ System Requirements

### Server Requirements
- **OS**: Windows, Linux, or macOS
- **Python**: 3.13+
- **RAM**: 2GB minimum
- **Disk**: 1GB minimum (more for images)
- **Network**: Internet connection

### Client Requirements
- **Browser**: Chrome, Firefox, Safari, or Edge
- **Device**: Desktop, tablet, or mobile
- **Internet**: Required for access

---

## 🔄 Version History

### Version 1.0.0 (February 2026)
- ✅ Initial release
- ✅ Complete admin dashboard
- ✅ Public website
- ✅ CSV import functionality
- ✅ Page generation
- ✅ User authentication
- ✅ Comprehensive documentation

---

## 🙏 Acknowledgments

Built with modern technologies:
- FastAPI - Modern Python web framework
- Tailwind CSS - Utility-first CSS framework
- SQLAlchemy - Python SQL toolkit
- Jinja2 - Template engine

---

## 📧 Contact

**Shining Horizon Trading**  
Email: info@shininghorizon.com  
WhatsApp: +966 53 659 8520  
Website: http://46.62.254.185:3004/

---

**Made with ❤️ for Shining Horizon Trading**

---

*Last Updated: February 2026*
