# SHINING HORIZON - QUICK START GUIDE

## 🚀 Getting Started in 5 Minutes

### Step 1: Start the Servers (2 minutes)

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
python -m http.server 3000
```

### Step 2: Login to Admin (1 minute)

1. Open browser: `http://46.62.254.185:3004/admin/login.html`
2. Login:
   - Username: `admin@shininghorizon.com`
   - Password: `admin@123`

### Step 3: Add Your First Product (2 minutes)

1. **Add Brand**: Brands → Add Brand → Enter "Siemens" → Save
2. **Add Category**: Categories → Add Category → Enter "Industrial Automation" → Save
3. **Add Subcategory**: Subcategories → Add → Select category → Enter "PLC Controllers" → Save
4. **Add Product**: Products → Add Product → Fill form → Save

### Step 4: Generate Website

1. Click "Generate Pages" in sidebar
2. Click "Generate All Pages" button
3. Visit: `http://46.62.254.185:3004/`

✅ **Done!** Your website is live with your first product.

---

## 📋 CSV Import Quick Reference

### Import Order (IMPORTANT!)
1. Brands first
2. Categories second
3. Subcategories third
4. Products last

### CSV Templates

**brands.csv**
```csv
name,display_order
Siemens,1
ABB,2
```

**categories.csv**
```csv
name,type,description,hero_title,hero_description,display_order
Industrial Automation,detailed,Automation products,Industrial Solutions,Complete automation range,1
```

**subcategories.csv**
```csv
category_name,name,description,display_order
Industrial Automation,PLC Controllers,Programmable Logic Controllers,1
```

**products.csv**
```csv
category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order
Industrial Automation,PLC Controllers,Siemens,Siemens S7-1200,6ES7214-1AG40-0XB0,Compact PLC,Full description here,1
```

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Public Website | http://46.62.254.185:3004/ |
| Admin Login | http://46.62.254.185:3004/admin/login.html |
| Admin Dashboard | http://46.62.254.185:3004/admin/index.html |
| API Docs | http://46.62.254.185:8000/docs |
| API Health | http://46.62.254.185:8000/health |

---

## 🆘 Common Issues

### "Failed to fetch"
- ✅ Check backend is running on port 8000
- ✅ Refresh the page
- ✅ Check you're logged in

### CSV Import Fails
- ✅ Check file format (UTF-8 CSV)
- ✅ Verify column names match exactly
- ✅ Import in correct order

### Images Not Showing
- ✅ Use JPG, PNG, or WEBP
- ✅ Keep under 5MB
- ✅ Clear browser cache (Ctrl+F5)

### Can't Login
- ✅ Username: `admin@shininghorizon.com`
- ✅ Password: `admin@123`
- ✅ Check backend is running

---

## 📞 Support

- **Email**: info@shininghorizon.com
- **WhatsApp**: +966 53 659 8520

---

## 🎯 Next Steps

1. ✅ Change default admin password
2. ✅ Add your company logo
3. ✅ Import your product catalog
4. ✅ Generate website pages
5. ✅ Customize colors and branding
6. ✅ Deploy to production server

---

**Need detailed instructions?** See the full User Guide (SHINING_HORIZON_USER_GUIDE.md)

**Technical details?** See Technical Documentation (TECHNICAL_DOCUMENTATION.md)
