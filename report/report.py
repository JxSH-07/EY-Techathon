from functools import total_ordering
from supabase import create_client
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
from PIL import Image as PILImage

# ================== SUPABASE CONFIG ==================
SUPABASE_URL = "https://jlbtqzadztgowiggwumw.supabase.co"
SUPABASE_KEY = "sb_publishable_ZFhFQ5r_EnuFkgWJ6rNi0A_4efVVjXP"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== FETCH DATA ==================
def fetch_inventory():
    print("🔥 Attempting to fetch data from Supabase table: Data")
    try:
        # First, let's check if the table exists and is accessible
        print("🔍 Checking table access...")
        response = supabase.table("Data").select("*", count='exact').limit(1).execute()
        
        if hasattr(response, 'count'):
            print(f"✅ Table 'Data' exists with {response.count} total records")
        else:
            print("⚠️ Could not determine table size. The table might be empty or there might be permission issues.")
        
        # Now fetch only 2XY cable type data with cross-section < 5 sq.mm
        print("📡 Fetching 2XY cable data with cross-section < 1.5 sq.mm...")
        
        # First get all 2XY cables
        response = supabase.table('Data').select('*').eq('Cable Type', '2XY').execute()
        
        # Then filter in Python for cross-section < 5
        if hasattr(response, 'data'):
            filtered_data = [
                item for item in response.data 
                if item.get('Cross Section (sq.mm)') and float(item['Cross Section (sq.mm)']) < 1.5
            ]
            response.data = filtered_data
        
        if not response.data:
            print("⚠️ No data returned from the query. The table might be empty.")
        else:
            print(f"✅ Successfully retrieved {len(response.data)} records")
            
        # Print raw response for debugging
        print("\n🔍 Raw response from Supabase:")
        print(response)
        
        return response.data
        
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        print("Please check your Supabase credentials and table name.")
        return []

# ================== PDF GENERATION ==================
def generate_tender_pdf(data):
    pdf = canvas.Canvas("tender_report.pdf", pagesize=A4)
    width, height = A4
    
    # Add logo at the top center
    try:
        logo_path = os.path.join(os.path.dirname(__file__), '1.png')
        if os.path.exists(logo_path):
            # Open and resize the image using PIL
            img = PILImage.open(logo_path)
            img = img.resize((200, 80), PILImage.Resampling.LANCZOS)
            
            # Save the resized image temporarily
            temp_logo_path = os.path.join(os.path.dirname(__file__), 'temp_logo.png')
            img.save(temp_logo_path)
            
            # Draw the image on PDF
            pdf.drawImage(temp_logo_path, (width - 200)/2, height - 120, width=200, height=80)
            
            # Clean up the temporary file
            os.remove(temp_logo_path)
            
            y = height - 170  # Adjust y position for content below logo
        else:
            print("⚠️ Logo file not found. Continuing without logo.")
            y = height - 50
    except Exception as e:
        print(f"⚠️ Error loading logo: {str(e)}")
        y = height - 50

    # Company Header
    pdf.setFont("Helvetica-Bold", 16)
    company_name = "CONCEPTUAL CATALYSIS"
    company_name_width = pdf.stringWidth(company_name, "Helvetica-Bold", 16)
    pdf.drawString((width - company_name_width) / 2, y, company_name)
    y -= 25
    
    # Company Tagline
    pdf.setFont("Helvetica-Bold", 12)
    tagline = "Your Trusted Partner in Quality Wires & Cables"
    tagline_width = pdf.stringWidth(tagline, "Helvetica-Bold", 12)
    pdf.drawString((width - tagline_width) / 2, y, tagline)
    y -= 20
    
    # Company Description
    pdf.setFont("Helvetica", 10)
    description = [
        "Established with a vision to provide superior quality electrical solutions, we have been a leading",
        "manufacturer and supplier of high-performance wires and cables. With years of expertise in the industry,",
        "we specialize in delivering reliable and durable cabling solutions for residential, commercial, and",
        "industrial applications. Our commitment to quality, innovation, and customer satisfaction makes us the",
        "preferred choice for all your wiring needs."
    ]
    
    for line in description:
        if y < 100:  # Check if we need a new page
            pdf.showPage()
            y = height - 50
        pdf.drawString(50, y, line)
        y -= 15
    
    y -= 20  # Add extra space before title
    
    # Title
    pdf.setFont("Helvetica-Bold", 14)
    title = "Tender Proposal – 2XY Cable (<5 sq.mm) Specification Report"
    title_width = pdf.stringWidth(title, "Helvetica-Bold", 14)
    pdf.drawString((width - title_width) / 2, y, title)
    y -= 30
    
    # Add tender details section after the title
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "TENDER DETAILS")
    y -= 20

    # Tender information in a clean format
    tender_details = [
        ("Tender No.", "TDR/2024-25/001"),
        ("Tender Name", "Supply of 2XY Cables for Electrical Works"),
        ("Tender Opening Date", "25/12/2025"),
        ("Tender Closing Date", "15/01/2026"),
        ("Bid Validity", "90 days from the date of tender opening"),
        ("Earnest Money Deposit (EMD)", "Rs. 5,000/-"),
        ("Tender Document Fee", "Rs. 1,000/- (Non-refundable)"),
        ("Completion Period", "60 days from the date of work order"),
        ("Warranty", "24 months from the date of installation"),
        ("Payment Terms", "100% payment within 30 days of delivery and installation"),
        ("Total Qunatity Needed", "100")
    ]

    # Draw tender details
    pdf.setFont("Helvetica", 10)
    # Find the maximum label width for alignment
    pdf.setFont("Helvetica-Bold", 10)
    max_label_width = max(pdf.stringWidth(f"{label}:", "Helvetica-Bold", 10) for label, _ in tender_details)
    value_start = 60 + max_label_width  # 10px padding after the longest label
    
    for label, value in tender_details:
        if y < 100:  # Check if we need a new page
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)
        
        # Draw label in bold
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, f"{label}:")
        
        # Draw value with proper spacing
        pdf.setFont("Helvetica", 10)
        pdf.drawString(value_start, y, value)
        y -= 15

    y -= 15  # Add some space before the table
    
    # Filter data to show only the row with minimum price
    if data:
        # Find the item with minimum price (handle None or empty prices)
        valid_data = [item for item in data if item.get('Price (Rupees/m)') is not None]
        if valid_data:
            min_price_item = min(valid_data, key=lambda x: float(x['Price (Rupees/m)']))
            data = [min_price_item]
    
    # Table Header
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(30, y, "Category")
    pdf.drawString(100, y, "Cable Type")
    pdf.drawString(180, y, "Price (Rupees/m)")
    pdf.drawString(260, y, "Cross Sec (sq.mm)")
    pdf.drawString(360, y, "Conductor")
    pdf.drawString(450, y, "Standard")

    y -= 10
    pdf.line(30, y, 560, y)
    y -= 15

    # Table Rows
    pdf.setFont("Helvetica", 9)
    for item in data:
        price = item.get('Price (Rupees/m)', '')
        price_str = f"{price}" if price != '' else 'N/A'
        pdf.drawString(30, y, str(item.get("Product Category", '')))
        pdf.drawString(100, y, str(item.get("Cable Type", '')))
        pdf.drawString(180, y, price_str)
        pdf.drawString(260, y, str(item.get("Cross Section (sq.mm)", '')))
        pdf.drawString(360, y, str(item.get("Conductor Material", '')))
        pdf.drawString(450, y, str(item.get("Standard", '')))

        y -= 15

        # New page if space ends
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = height - 50
            
    # Add total price calculation
    total_quantity = 100
    y -= 30  # Add some space before the total
    pdf.setFont("Helvetica-Bold", 10)
    
    # Add total price calculation and breakdown
    y -= 5  # Add some space before the total
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "PRICE BREAKDOWN")
    y -= 15
    
    # Find minimum price from the data
    min_price = min(
        float(item.get('Price (Rupees/m)', float('inf'))) 
        for item in data 
        if item.get('Price (Rupees/m)')
    )
    
    # Price details
    subtotal = min_price * total_quantity
    gst = subtotal * 0.18  # 18% GST
    grand_total = subtotal + gst
    
    price_details = [
        ("Price per meter:", f"Rs. {int(min_price)}/m"),
        ("Total quantity:", "100 meters"),
        ("Subtotal:", f"Rs. {int(subtotal)}"),
        ("GST (18%):", f"Rs. {int(gst)}"),
        ("Grand Total:", f"Rs. {int(grand_total)}")
    ]
    
    # Draw price details
    pdf.setFont("Helvetica", 10)
    for label, value in price_details:
        if y < 100:  # Check if we need a new page
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)
        
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, label)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(180, y, value)
        y -= 15
    


    pdf.save()
    print("✅ Tender PDF Generated Successfully: tender_report.pdf")

def print_table_data(data):
    """Print all data from the Data table in a formatted way"""
    if not data:
        print("\n⚠️ No data found in the table.")
        return
        
    print("\n" + "="*120)
    print("DATABASE CONTENT - Data Table")
    print("="*120)
    
    # Print header
    print(f"{'Product Category':<25} | {'Cable Type':<15} | {'Price (Rupees/m)':<15} | {'Cross Section':<15} | {'Conductor':<15} | {'Standard'}")
    print("-" * 135)
    
    # Print each row
    for item in data:
        price = item.get('Price (Rupees/m)', '')
        price_str = f"₹{price}" if price != '' else 'N/A'
        print(f"{str(item.get('Product Category', '')):<25} | {str(item.get('Cable Type', '')):<15} | "
              f"{price_str:<15} | {str(item.get('Cross Section (sq.mm)', '')):<15} | "
              f"{str(item.get('Conductor Material', '')):<15} | {str(item.get('Standard', ''))}")

def insert_sample_data():
    """Insert sample data into the Data table"""
    print("\n🔄 Inserting sample data into the database...")
    
    sample_data = [
        {"Product Category": "BMS / Control Cable", "Cable Type": "BMS", "Voltage Grade": "300 V", "Conductor Material": "Copper", "Core Count": "2", "Cross Section (sq.mm)": "1", "Armouring": "Unarmoured", "Insulation Type": "PVC", "Standard": "BS 5308 / IEC 60227", "Price (Rupees/m)": "32", "Source": "Polycab BMS / Control Cables"},
        {"Product Category": "BMS / Control Cable", "Cable Type": "BMS", "Voltage Grade": "300 V", "Conductor Material": "Copper", "Core Count": "4", "Cross Section (sq.mm)": "1", "Armouring": "Unarmoured", "Insulation Type": "PVC", "Standard": "BS 5308 / IEC 60227", "Price (Rupees/m)": "50", "Source": "Polycab BMS / Control Cables"},
        # Add more sample data as needed (I've included just 2 for brevity)
    ]
    
    try:
        for item in sample_data:
            response = supabase.table("Data").insert(item).execute()
        print(f"✅ Successfully inserted {len(sample_data)} records into the Data table")
        return True
    except Exception as e:
        print(f"❌ Error inserting data: {str(e)}")
        return False

# ================== MAIN ==================
if __name__ == "__main__":
    import sys
    
    # Check if we should insert sample data
    if len(sys.argv) > 1 and sys.argv[1] == "--insert-sample":
        if insert_sample_data():
            print("\nSample data inserted. You can now run the script without arguments to view the data.")
    else:
        print("Fetching data from the database...")
        inventory_data = fetch_inventory()
        
        if not inventory_data:
            print("\nThe table is empty. To insert sample data, run: python report.py --insert-sample")
        else:
            print_table_data(inventory_data)
            
        generate_tender_pdf(inventory_data)
        print("\n✅ PDF generation complete: tender_report.pdf")
