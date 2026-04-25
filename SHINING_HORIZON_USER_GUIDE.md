# SHINING HORIZON TRADING - USER GUIDE

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Admin Dashboard Overview](#admin-dashboard-overview)
4. [Managing Your Catalog](#managing-your-catalog)
5. [Step-by-Step Tutorials](#step-by-step-tutorials)
6. [Generating Website Pages](#generating-website-pages)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

Welcome to the Shining Horizon Trading website management system. This guide will help you manage your industrial products catalog, including categories, subcategories, brands, and products.

### What Can You Do?
- Add and manage product categories (Industrial Automation, Electrical Products, etc.)
- Organize products into subcategories (PLC Controllers, VFDs, Sensors, etc.)
- Manage brands (Siemens, ABB, Schneider, etc.)
- Add detailed product information with images
- Import bulk data using CSV files
- Generate website pages automatically

---

## Getting Started

### Accessing the Admin Dashboard

1. **Open your web browser** (Chrome, Firefox, or Edge recommended)
2. **Navigate to**: `http://46.62.254.185:3004/admin/login.html`
3. **Login with your credentials**:
   - Username: `admin@shininghorizon.com`
   - Password: `admin@123`
   - ⚠️ **Important**: Change these credentials after first login!

### Dashboard Layout

After logging in, you'll see:
- **Left Sidebar**: Navigation menu with all management sections
- **Main Area**: Content and data tables
- **Top Bar**: Your profile and logout button

---

## Admin Dashboard Overview

### Navigation Menu Sections

#### CATALOG SECTION
- **Dashboard**: Overview and statistics
- **Categories**: Main product categories (e.g., Industrial Automation)
- **Subcategories**: Product types within categories (e.g., PLC Controllers)
- **Products**: Individual products with specifications
- **Brands**: Manufacturer brands (e.g., Siemens, ABB)
- **Import Data**: Bulk import from CSV files

#### SYSTEM SECTION
- **Users**: Manage admin users
- **Generate Pages**: Create website pages from your data
- **Logout**: Sign out of the system

---

## Managing Your Catalog

### Understanding the Hierarchy

Your catalog follows this structure:

```
Category (e.g., Industrial Automation)
  └── Subcategory (e.g., PLC Controllers)
        └── Product (e.g., Siemens S7-1200)
              └── Brand (e.g., Siemens)
```

### 1. BRANDS

Brands are manufacturers of your products.

**Adding a Brand:**
1. Click **"Brands"** in the sidebar
2. Click **"Add Brand"** button
3. Fill in the form:
   - **Name**: Brand name (e.g., "Siemens")
   - **Logo**: Upload brand logo image (optional)
   - **Display Order**: Number for sorting (lower numbers appear first)
   - **Status**: Active/Inactive
4. Click **"Save"**

**Example Brands:**
- Siemens
- ABB
- Schneider Electric
- Mitsubishi
- Delta
- Festo
- SMC

---

### 2. CATEGORIES

Categories are the main product groups on your website.

**Adding a Category:**
1. Click **"Categories"** in the sidebar
2. Click **"Add Category"** button
3. Fill in the form:
   - **Name**: Category name (e.g., "Industrial Automation")
   - **Type**: 
     - **Simple**: Basic category page
     - **Detailed**: Full page with hero section
   - **Description**: Brief description
   - **Hero Title**: Main heading for detailed pages
   - **Hero Description**: Subtitle for detailed pages
   - **Display Order**: Sorting number
   - **Show on Home**: Display on homepage
   - **Status**: Active/Inactive
4. Click **"Save"**

**Example Categories:**
- Industrial Automation
- Electrical Products
- Pneumatic Products
- Tools
- Lifting Equipment
- HVAC & Spare Parts

---

### 3. SUBCATEGORIES

Subcategories organize products within a category.

**Adding a Subcategory:**
1. Click **"Subcategories"** in the sidebar
2. Click **"Add Subcategory"** button
3. Fill in the form:
   - **Category**: Select parent category
   - **Name**: Subcategory name (e.g., "PLC Controllers")
   - **Description**: Brief description
   - **Display Order**: Sorting number
   - **Status**: Active/Inactive
4. Click **"Save"**

**Example: Industrial Automation Subcategories**
- PLC Controllers
- VFDs (Variable Frequency Drives)
- HMI Panels
- Sensors
- Motor Starters

**Example: Electrical Products Subcategories**
- Circuit Breakers
- Cables & Wires
- Switchgear
- Transformers

---

### 4. PRODUCTS

Products are the individual items you sell.

**Adding a Product:**
1. Click **"Products"** in the sidebar
2. Click **"Add Product"** button
3. Fill in the form:
   - **Category**: Select main category
   - **Subcategory**: Select subcategory (if applicable)
   - **Brand**: Select manufacturer brand
   - **Name**: Product name (e.g., "Siemens S7-1200 PLC")
   - **Part Number**: Manufacturer part number (e.g., "6ES7214-1AG40-0XB0")
   - **Short Description**: Brief one-line description
   - **Description**: Detailed product information
   - **Image**: Upload product image
   - **Display Order**: Sorting number
   - **Status**: Active/Inactive
4. Click **"Save"**

**Product Example:**
```
Name: Siemens S7-1200 CPU 1214C
Part Number: 6ES7214-1AG40-0XB0
Category: Industrial Automation
Subcategory: PLC Controllers
Brand: Siemens
Short Description: Compact PLC for small automation applications
Description: SIMATIC S7-1200 CPU 1214C, compact CPU, 
DC/DC/DC, onboard I/O: 14 DI 24V DC; 10 DO 24V DC; 
2 AI 0-10V DC, power supply: DC 20.4-28.8V DC, 
program/data memory 100 KB
```

---

## Step-by-Step Tutorials

### Tutorial 1: Adding PLC Automation Products

Let's add a complete PLC automation product line.

#### Step 1: Add the Brand
1. Go to **Brands** → Click **"Add Brand"**
2. Enter:
   - Name: `Siemens`
   - Display Order: `1`
3. Click **"Save"**

#### Step 2: Add the Category
1. Go to **Categories** → Click **"Add Category"**
2. Enter:
   - Name: `Industrial Automation`
   - Type: `Detailed`
   - Description: `Industrial automation and control systems`
   - Hero Title: `Industrial Automation Solutions`
   - Hero Description: `Complete range of PLCs, drives, and control systems`
   - Display Order: `1`
   - Show on Home: ✓ (checked)
3. Click **"Save"**

#### Step 3: Add Subcategories
1. Go to **Subcategories** → Click **"Add Subcategory"**
2. Add PLC Controllers:
   - Category: `Industrial Automation`
   - Name: `PLC Controllers`
   - Description: `Programmable Logic Controllers from leading brands`
   - Display Order: `1`
3. Click **"Save"**
4. Repeat for other subcategories:
   - VFDs (Display Order: 2)
   - HMI Panels (Display Order: 3)
   - Sensors (Display Order: 4)

#### Step 4: Add Products
1. Go to **Products** → Click **"Add Product"**
2. Add Siemens PLC:
   - Category: `Industrial Automation`
   - Subcategory: `PLC Controllers`
   - Brand: `Siemens`
   - Name: `Siemens S7-1200 CPU 1214C`
   - Part Number: `6ES7214-1AG40-0XB0`
   - Short Description: `Compact PLC for automation applications`
   - Description: `SIMATIC S7-1200 CPU 1214C, compact CPU, DC/DC/DC, onboard I/O: 14 DI 24V DC; 10 DO 24V DC; 2 AI 0-10V DC`
   - Upload product image
   - Display Order: `1`
3. Click **"Save"**

✅ **Done!** You've added a complete product with category, subcategory, and brand.

---

### Tutorial 2: Bulk Import Using CSV Files

For adding many products at once, use the CSV import feature.

#### Step 1: Prepare Your CSV Files

Create CSV files in this order:

**1. brands.csv**
```csv
name,display_order
Siemens,1
ABB,2
Schneider,3
```

**2. categories.csv**
```csv
name,type,description,hero_title,hero_description,display_order
Industrial Automation,detailed,Automation and control systems,Industrial Automation Solutions,Complete range of automation products,1
Electrical Products,detailed,Electrical components and systems,Electrical Solutions,Quality electrical products,2
```

**3. subcategories.csv**
```csv
category_name,name,description,display_order
Industrial Automation,PLC Controllers,Programmable Logic Controllers,1
Industrial Automation,VFDs,Variable Frequency Drives,2
Electrical Products,Circuit Breakers,Protection devices,1
```

**4. products.csv**
```csv
category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order
Industrial Automation,PLC Controllers,Siemens,Siemens S7-1200,6ES7214-1AG40-0XB0,Compact PLC,SIMATIC S7-1200 CPU 1214C with onboard I/O,1
Industrial Automation,VFDs,ABB,ABB ACS580,ACS580-01-038A-4,General purpose drive,ABB ACS580 18.5kW 380-480V 3-phase,1
```

#### Step 2: Import the Files

1. Go to **Import Data** in the sidebar
2. Import in this order:
   - **First**: Upload `brands.csv` → Click "Import Brands"
   - **Second**: Upload `categories.csv` → Click "Import Categories"
   - **Third**: Upload `subcategories.csv` → Click "Import Subcategories"
   - **Fourth**: Upload `products.csv` → Click "Import Products"

3. Check the results:
   - Green message = Success
   - Red message = Error (check your CSV format)

#### Step 3: Verify the Import

1. Go to each section (Brands, Categories, etc.)
2. Verify all data was imported correctly
3. Edit any items if needed

---

## Generating Website Pages

After adding your products, generate the public website pages.

### How to Generate Pages

1. Click **"Generate Pages"** in the sidebar
2. Click **"Generate All Pages"** button
3. Wait for the process to complete (may take a few seconds)
4. You'll see a success message when done

### What Gets Generated?

The system creates:
- Category pages (e.g., `category-industrial-automation.html`)
- Product detail pages (e.g., `product-plc-controllers.html`)
- Brand pages (e.g., `brand-siemens.html`)

### Viewing Your Website

1. Open a new browser tab
2. Go to: `http://localhost:3000`
3. Browse your categories and products

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Failed to fetch" error
**Solution**: 
- Make sure the backend server is running
- Check that you're logged in
- Refresh the page and try again

#### Issue: CSV import fails
**Solution**:
- Check CSV file format (must be UTF-8 encoded)
- Verify column names match exactly
- Ensure no special characters in data
- Import in correct order (Brands → Categories → Subcategories → Products)

#### Issue: Images not showing
**Solution**:
- Use JPG, PNG, or WEBP formats
- Keep file size under 5MB
- Use clear, high-quality images

#### Issue: Can't login
**Solution**:
- Verify username: `admin@shininghorizon.com`
- Verify password: `admin@123`
- Clear browser cache
- Check that backend server is running

#### Issue: Generated pages not updating
**Solution**:
- Click "Generate Pages" again
- Clear browser cache (Ctrl+F5)
- Check that products are marked as "Active"

---

## Best Practices

### Product Organization
1. **Use clear naming**: "Siemens S7-1200 PLC" not just "PLC"
2. **Include part numbers**: Helps customers find exact products
3. **Write detailed descriptions**: Include specifications and features
4. **Use high-quality images**: Clear product photos build trust

### Category Structure
1. **Keep it simple**: 5-10 main categories maximum
2. **Logical grouping**: Group related products together
3. **Consistent naming**: Use industry-standard terms

### Data Management
1. **Regular backups**: Export your data regularly
2. **Test before bulk import**: Try with a few items first
3. **Keep CSV templates**: Save working CSV files as templates

---

## Quick Reference

### CSV File Formats

**Brands CSV:**
```
name,display_order
```

**Categories CSV:**
```
name,type,description,hero_title,hero_description,display_order
```

**Subcategories CSV:**
```
category_name,name,description,display_order
```

**Products CSV:**
```
category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order
```

### Important URLs

- **Public Website**: `http://46.62.254.185:3004/`
- **Admin Login**: `http://46.62.254.185:3004/admin/login.html`
- **Admin Dashboard**: `http://46.62.254.185:3004/admin/index.html`
- **API Documentation**: `http://46.62.254.185:8000/docs`

---

## Support

For technical support or questions:
- Email: info@shininghorizon.com
- WhatsApp: +966 53 659 8520

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Company**: Shining Horizon Trading
