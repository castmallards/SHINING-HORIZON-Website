# SHINING HORIZON - ADMIN WORKFLOW EXAMPLES

## Real-World Usage Scenarios

This guide shows you exactly how to use the admin dashboard for common tasks with real examples from your business.

---

## Scenario 1: Adding Siemens PLC Products

### Background
You've received a new shipment of Siemens PLCs and need to add them to your website.

### Step-by-Step Process

#### Step 1: Check if Brand Exists
1. Go to **Brands** page
2. Look for "Siemens" in the list
3. If not found, click **"Add Brand"**

**Add Brand Form:**
```
Name: Siemens
Logo: [Upload Siemens logo image]
Display Order: 1
Status: Active ✓
```

#### Step 2: Check if Category Exists
1. Go to **Categories** page
2. Look for "Industrial Automation"
3. If not found, click **"Add Category"**

**Add Category Form:**
```
Name: Industrial Automation
Type: Detailed
Description: Complete range of industrial automation and control systems
Hero Title: Industrial Automation Solutions
Hero Description: Leading brands of PLCs, drives, HMIs, and control systems for industrial applications
Display Order: 1
Show on Home: ✓
Status: Active ✓
```

#### Step 3: Add Subcategory
1. Go to **Subcategories** page
2. Click **"Add Subcategory"**

**Add Subcategory Form:**
```
Category: Industrial Automation
Name: PLC Controllers
Description: Programmable Logic Controllers from leading brands including Siemens, ABB, and Mitsubishi
Display Order: 1
Status: Active ✓
```

#### Step 4: Add Products
1. Go to **Products** page
2. Click **"Add Product"**

**Product 1: Siemens S7-1200**
```
Category: Industrial Automation
Subcategory: PLC Controllers
Brand: Siemens
Name: Siemens S7-1200 CPU 1214C
Part Number: 6ES7214-1AG40-0XB0
Short Description: Compact PLC for small to medium automation applications
Description: SIMATIC S7-1200 CPU 1214C, compact CPU, DC/DC/DC, 
onboard I/O: 14 DI 24V DC; 10 DO 24V DC; 2 AI 0-10V DC, 
power supply: DC 20.4-28.8V DC, program/data memory 100 KB
Image: [Upload product image]
Display Order: 1
Status: Active ✓
```

**Product 2: Siemens S7-1500**
```
Category: Industrial Automation
Subcategory: PLC Controllers
Brand: Siemens
Name: Siemens S7-1500 CPU 1511-1 PN
Part Number: 6ES7511-1AK02-0AB0
Short Description: High-performance PLC for advanced automation
Description: SIMATIC S7-1500 CPU1511-1PN central processing unit 
with PROFINET interface, 300 KB work memory, requires SIMATIC 
memory card
Image: [Upload product image]
Display Order: 2
Status: Active ✓
```

#### Step 5: Generate Pages
1. Click **"Generate Pages"** in sidebar
2. Click **"Generate All Pages"** button
3. Wait for success message

#### Step 6: Verify on Website
1. Open new tab: `http://46.62.254.185:3004/`
2. Click "Industrial Automation" category
3. Find "PLC Controllers" subcategory
4. See your Siemens products listed

✅ **Complete!** Your Siemens PLCs are now on the website.

---

## Scenario 2: Adding Complete Pneumatic Products Line

### Background
You want to add your entire pneumatic products catalog including cylinders, valves, and fittings from Festo and SMC brands.

### Quick Method: CSV Import

#### Step 1: Prepare Brands CSV

**File: brands.csv**
```csv
name,display_order
Festo,1
SMC,2
```

#### Step 2: Prepare Category CSV

**File: categories.csv**
```csv
name,type,description,hero_title,hero_description,display_order
Pneumatic Products,detailed,Pneumatic components and systems,Pneumatic Solutions,Complete range of pneumatic cylinders valves and accessories,3
```

#### Step 3: Prepare Subcategories CSV

**File: subcategories.csv**
```csv
category_name,name,description,display_order
Pneumatic Products,Cylinders,Pneumatic cylinders and actuators from Festo and SMC,1
Pneumatic Products,Valves,Solenoid and manual pneumatic valves,2
Pneumatic Products,Air Treatment,Filters regulators and lubricators FRL units,3
Pneumatic Products,Fittings,Pneumatic connectors and push-in fittings,4
```

#### Step 4: Prepare Products CSV

**File: products.csv**
```csv
category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order
Pneumatic Products,Cylinders,Festo,Festo Compact Cylinder ADVU,ADVU-32-50-P-A,Compact pneumatic cylinder,Festo ADVU series compact pneumatic cylinder bore 32mm stroke 50mm with position sensing,1
Pneumatic Products,Cylinders,Festo,Festo Standard Cylinder DSBC,DSBC-32-100-PPVA-N3,ISO standard cylinder,Festo DSBC ISO standard pneumatic cylinder with adjustable cushioning bore 32mm stroke 100mm,2
Pneumatic Products,Cylinders,SMC,SMC Compact Cylinder CQ2,CQ2B32-50DZ,Compact air cylinder,SMC CQ2 series compact cylinder with auto switch bore 32mm stroke 50mm,3
Pneumatic Products,Valves,Festo,Festo Solenoid Valve MFH,MFH-5-1/4,5/2 way solenoid valve,Festo MFH series solenoid operated directional control valve 5/2 way 1/4 inch,1
Pneumatic Products,Valves,SMC,SMC Solenoid Valve SY,SY5120-5LZD,5 port solenoid valve,SMC SY series 5 port solenoid valve with manifold base,2
Pneumatic Products,Air Treatment,Festo,Festo FRL Unit MS6,MS6-LFR-1/2-D7-ERV,Filter regulator lubricator,Festo MS6 series FRL combination unit 1/2 inch with pressure gauge,1
Pneumatic Products,Fittings,Festo,Festo Push-in Fitting QS,QS-6,Push-in straight fitting,Festo QS series push-in fitting for 6mm tube,1
Pneumatic Products,Fittings,SMC,SMC Push-in Fitting KQ2,KQ2H06-01S,Push-in elbow fitting,SMC KQ2 series push-in elbow fitting 6mm to 1/8 inch,2
```

#### Step 5: Import Files

1. Go to **Import Data** page
2. Import in order:
   - Upload `brands.csv` → Click "Import Brands"
   - Upload `categories.csv` → Click "Import Categories"  
   - Upload `subcategories.csv` → Click "Import Subcategories"
   - Upload `products.csv` → Click "Import Products"

3. Check results:
   - Brands: Created 2
   - Categories: Created 1
   - Subcategories: Created 4
   - Products: Created 8

#### Step 6: Generate and Verify

1. Click **"Generate Pages"**
2. Visit website
3. Check "Pneumatic Products" category
4. Verify all subcategories and products appear

✅ **Complete!** Entire pneumatic line added in minutes.

---

## Scenario 3: Adding Electrical Products with Multiple Brands

### Background
You stock electrical products from multiple brands: Schneider, ABB, and Siemens.

### Products to Add

**Circuit Breakers:**
- Schneider iC60N (various ratings)
- ABB S200 series
- Siemens 5SY series

**Cables & Wires:**
- Generic brand cables

### Method: Manual Entry with Filters

#### Step 1: Add Brands (if needed)
```
Schneider - Display Order: 1
ABB - Display Order: 2
Siemens - Display Order: 3
Generic - Display Order: 4
```

#### Step 2: Add Category
```
Name: Electrical Products
Type: Detailed
Description: Electrical components and distribution systems
Hero Title: Electrical Solutions
Hero Description: Quality electrical products from leading manufacturers
Display Order: 2
```

#### Step 3: Add Subcategories
```
1. Circuit Breakers - MCBs, MCCBs, and protection devices
2. Cables & Wires - Power and control cables
3. Switchgear - Distribution panels and switches
4. Transformers - Power and control transformers
```

#### Step 4: Add Circuit Breaker Products

**Schneider iC60N 10A:**
```
Category: Electrical Products
Subcategory: Circuit Breakers
Brand: Schneider
Name: Schneider iC60N 2P 10A
Part Number: A9F44210
Short Description: 2-pole miniature circuit breaker 10A C-curve
Description: Schneider iC60N 2P 10A C curve miniature circuit breaker, 
6kA breaking capacity, DIN rail mounting, IEC 60898-1 compliant
Display Order: 1
```

**Schneider iC60N 16A:**
```
Category: Electrical Products
Subcategory: Circuit Breakers
Brand: Schneider
Name: Schneider iC60N 2P 16A
Part Number: A9F44216
Short Description: 2-pole miniature circuit breaker 16A C-curve
Description: Schneider iC60N 2P 16A C curve miniature circuit breaker, 
6kA breaking capacity, DIN rail mounting
Display Order: 2
```

**ABB S200 Series:**
```
Category: Electrical Products
Subcategory: Circuit Breakers
Brand: ABB
Name: ABB S200 MCB 2P 20A
Part Number: S202-C20
Short Description: 2-pole MCB 20A C-characteristic
Description: ABB S200 series miniature circuit breaker, 2-pole, 
20A rated current, C-characteristic, 6kA breaking capacity
Display Order: 3
```

#### Step 5: Add Cable Products

**Power Cable:**
```
Category: Electrical Products
Subcategory: Cables & Wires
Brand: Generic
Name: NYM Cable 3x2.5mm²
Part Number: NYM-3X2.5
Short Description: PVC insulated power cable
Description: NYM cable 3 core 2.5mm² copper conductor, 
PVC insulated and sheathed, suitable for fixed installations
Display Order: 1
```

#### Step 6: Generate and Check

1. Generate pages
2. Visit "Electrical Products" category
3. See all products organized by subcategory
4. Filter by brand to see specific manufacturer products

✅ **Complete!** Electrical products catalog ready.

---

## Scenario 4: Updating Product Information

### Background
You need to update prices, descriptions, or part numbers for existing products.

### Example: Update Siemens PLC Description

#### Step 1: Find Product
1. Go to **Products** page
2. Use filters:
   - Category: Industrial Automation
   - Subcategory: PLC Controllers
   - Brand: Siemens
3. Find "Siemens S7-1200 CPU 1214C"
4. Click **Edit** button

#### Step 2: Update Information
```
Update Description to:
SIMATIC S7-1200 CPU 1214C, compact CPU, DC/DC/DC
Onboard I/O: 14 DI 24V DC; 10 DO 24V DC; 2 AI 0-10V DC
Power supply: DC 20.4-28.8V DC
Program/data memory: 100 KB
Integrated PROFINET interface
Supports up to 3 communication modules
Ideal for small to medium automation tasks
```

#### Step 3: Save and Regenerate
1. Click **"Save"**
2. Go to **Generate Pages**
3. Click **"Generate All Pages"**
4. Check website for updated information

✅ **Complete!** Product information updated.

---

## Scenario 5: Managing Product Images

### Background
You have high-quality product photos and want to add them to your products.

### Best Practices for Images

#### Image Requirements
- **Format**: JPG, PNG, or WEBP
- **Size**: Under 5MB
- **Resolution**: 800x800 pixels minimum
- **Background**: White or transparent preferred
- **Quality**: Clear, well-lit product photos

#### Adding Images to Products

**Method 1: During Product Creation**
1. When adding new product
2. Click "Choose File" in Image field
3. Select product image
4. Image uploads automatically
5. Save product

**Method 2: Updating Existing Product**
1. Go to Products page
2. Click Edit on product
3. Click "Choose File" in Image field
4. Select new image
5. Save product
6. Regenerate pages

#### Organizing Images

**Recommended Folder Structure:**
```
Your Computer/
└── Product Images/
    ├── PLCs/
    │   ├── siemens-s7-1200.jpg
    │   ├── siemens-s7-1500.jpg
    │   └── abb-ac500.jpg
    ├── VFDs/
    │   ├── abb-acs580.jpg
    │   └── siemens-g120.jpg
    └── Sensors/
        ├── keyence-lv-n11.jpg
        └── sick-wl4.jpg
```

✅ **Complete!** Professional product images added.

---

## Scenario 6: Bulk Update Using CSV

### Background
You need to update display order for 50 products or add new products in bulk.

### Process

#### Step 1: Export Current Data (Manual)
1. Go to each product
2. Note down: name, part number, category, etc.
3. Create CSV with current data

#### Step 2: Modify CSV
```csv
category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order
Industrial Automation,PLC Controllers,Siemens,Siemens S7-1200,6ES7214-1AG40-0XB0,Compact PLC,Full description,1
Industrial Automation,PLC Controllers,Siemens,Siemens S7-1500,6ES7511-1AK02-0AB0,High-performance PLC,Full description,2
Industrial Automation,VFDs,ABB,ABB ACS580,ACS580-01-038A-4,General purpose drive,Full description,1
```

#### Step 3: Import Updated CSV
1. Go to **Import Data**
2. Upload modified CSV
3. System will:
   - Update existing products (matching by name/part number)
   - Create new products
   - Skip duplicates

#### Step 4: Verify Updates
1. Check Products page
2. Verify display order changed
3. Check new products added
4. Regenerate pages

✅ **Complete!** Bulk updates applied.

---

## Scenario 7: Seasonal Product Management

### Background
You want to temporarily hide products that are out of stock or seasonal.

### Deactivating Products

#### Step 1: Find Product
1. Go to **Products** page
2. Find product to deactivate
3. Click **Edit**

#### Step 2: Change Status
```
Status: Inactive ✗
```

#### Step 3: Save and Regenerate
1. Click **"Save"**
2. Generate pages
3. Product won't appear on website

### Reactivating Products

#### When Stock Returns:
1. Edit product
2. Change Status to Active ✓
3. Save and regenerate
4. Product reappears on website

✅ **Complete!** Seasonal products managed.

---

## Scenario 8: Creating Product Families

### Background
You have product families like "Siemens S7-1200 Series" with multiple models.

### Organization Strategy

#### Use Display Order for Grouping

**S7-1200 Series (Display Order 1-10):**
```
1. Siemens S7-1200 CPU 1211C (Display Order: 1)
2. Siemens S7-1200 CPU 1212C (Display Order: 2)
3. Siemens S7-1200 CPU 1214C (Display Order: 3)
4. Siemens S7-1200 CPU 1215C (Display Order: 4)
```

**S7-1500 Series (Display Order 11-20):**
```
11. Siemens S7-1500 CPU 1511 (Display Order: 11)
12. Siemens S7-1500 CPU 1513 (Display Order: 12)
13. Siemens S7-1500 CPU 1515 (Display Order: 13)
```

#### Naming Convention
```
Format: [Brand] [Series] [Model] [Specification]

Examples:
- Siemens S7-1200 CPU 1214C DC/DC/DC
- ABB ACS580 Drive 18.5kW 400V
- Festo DSBC Cylinder 32mm Bore 100mm Stroke
```

✅ **Complete!** Product families organized.

---

## Common Tasks Quick Reference

### Daily Tasks
| Task | Steps | Time |
|------|-------|------|
| Add single product | Products → Add → Fill form → Save | 2 min |
| Update product info | Products → Edit → Modify → Save | 1 min |
| Upload image | Edit product → Choose file → Save | 1 min |
| Generate pages | Generate Pages → Generate All | 30 sec |

### Weekly Tasks
| Task | Steps | Time |
|------|-------|------|
| Add new brand | Brands → Add → Fill → Save | 1 min |
| Add subcategory | Subcategories → Add → Fill → Save | 1 min |
| Bulk import 50 products | Prepare CSV → Import → Generate | 10 min |

### Monthly Tasks
| Task | Steps | Time |
|------|-------|------|
| Review all products | Products → Check each → Update | 30 min |
| Update images | Edit products → Upload new images | 20 min |
| Add new category | Categories → Add → Configure | 5 min |

---

## Tips for Efficiency

### 1. Use CSV Import for Bulk Operations
- Faster than manual entry
- Less prone to errors
- Easy to update multiple products

### 2. Organize Before Adding
- Plan category structure first
- Add all brands before products
- Use consistent naming

### 3. Use Display Order Strategically
- Group related products
- Put popular items first
- Use gaps (10, 20, 30) for future additions

### 4. Keep Images Ready
- Prepare images before adding products
- Use consistent image sizes
- Name files clearly

### 5. Generate Pages Regularly
- After adding products
- After updating information
- Before showing website to customers

---

## Troubleshooting Common Issues

### Issue: Product Not Showing on Website
**Solution:**
1. Check product status is "Active"
2. Check category/subcategory are active
3. Regenerate pages
4. Clear browser cache (Ctrl+F5)

### Issue: Image Not Uploading
**Solution:**
1. Check file size (under 5MB)
2. Check file format (JPG, PNG, WEBP)
3. Try different image
4. Check internet connection

### Issue: CSV Import Fails
**Solution:**
1. Check CSV format (UTF-8)
2. Verify column names match exactly
3. Check for special characters
4. Import in correct order

### Issue: Duplicate Products
**Solution:**
1. Check part numbers are unique
2. Use CSV import (handles duplicates)
3. Manually delete duplicates
4. Regenerate pages

---

## Best Practices Summary

✅ **DO:**
- Add brands before products
- Use clear, descriptive names
- Include part numbers
- Upload high-quality images
- Use consistent naming
- Generate pages after changes
- Keep CSV templates
- Regular backups

❌ **DON'T:**
- Skip display order
- Use special characters in names
- Upload huge images (>5MB)
- Forget to regenerate pages
- Delete categories with products
- Import without checking format

---

**Need More Help?**
- See User Guide for detailed instructions
- Check Technical Documentation for advanced topics
- Contact support: info@shininghorizon.com

---

**Document Version**: 1.0  
**Last Updated**: February 2026
