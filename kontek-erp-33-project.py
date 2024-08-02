import json
import os
import pdfplumber
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_table_data(lines):
    items = []
    item_pattern = re.compile(r'^X\w+')  # Regex pattern to find items starting with 'X' and followed by any word character

    for line in lines:
        if item_pattern.match(line):
            parts = line.split()
            if len(parts) >= 4:  # Adjust this as needed based on the expected number of columns
                item_no = parts[0]
                quantity = parts[1]  # Assuming 'Ordered' quantity is the second column
                unit_price = parts[-2]  # Assuming 'Unit Price' is the second last column
                amount_price = parts[-1]  # Assuming 'Amount' is the last column
                items.append({
                    item_no: {
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'amount_price': amount_price
                    }
                })
    return items

def parse_file_details(file_path):
    details = {
        
        # Header Data

        'filename': os.path.basename(file_path),
        'file_location': file_path,
        'order_number': '',
        'order_date': '',
        'ship_date': '',
        'ship_to': {'location': '', 'address': ''},
        'bill_to': {'location': '', 'address': ''},

        # Table Data

        'items': [],

        # Footer Data

        'ktk_hst_num': '',
        'hst_rate': '',
        'subtotal': '',
        'hst': '',
        'total_price': ''
      
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')
                details['items'] = parse_table_data(lines)  # Parse table data and update items


                for i, line in enumerate(lines):

                    # Header Data

                    if 'Order No' in line:
                        details['order_number'] = line.split(':')[-1].strip()
                    if 'Date' in line and 'Ship Date' not in line:
                        details['order_date'] = line.split(':')[-1].strip()
                    if 'Ship Date:' in line:
                        extracted_date = line.split(':')[-1].strip()
                        details['ship_date'] = extracted_date if extracted_date else "N/A"
                    if 'Ship To:' in line:
                        details['ship_to']['location'] = ' '.join(lines[i+2:i+3]).strip()
                        details['ship_to']['address'] = ' '.join(lines[i+4:i+5] + lines[i+6:i+7] + lines[i+7:i+9])
                    if 'Purchased From:' in line:
                        details['bill_to']['location'] = ' '.join(lines[i+1:i+2]).strip()
                        details['bill_to']['address'] = ' '.join(lines[i+3:i+4] + lines[i+5:i+6])
                    
                    # Table Data

                    # Footer Data

                    if 'Total Amount' in line and not details['total_price']:
                        price_match = re.search(r'\d{1,3}(?:,\d{3})*\.\d{2}', line)
                        if price_match:
                            details['total_price'] = price_match.group(0)
                    if 'H - HST' in line:
                        hst_rate = line.replace('H - HST', '').strip()
                        if hst_rate:
                            details['hst_rate'] = hst_rate
                    if 'HST:' in line:
                        details['ktk_hst_num'] = line.split(':')[-1].strip()
                    if 'HST' in line and 'HST:' not in line:
                        details['hst'] = line.split(':')[-1].strip().replace('HST ', '')
                    if 'Subtotal:' in line:
                        details['subtotal'] = line.split(':')[-1].strip()
                    
                
                if details['total_price']: 
                    break

    except Exception as e:
        logging.error(f"Failed to open or parse {file_path}: {e}")

    return details

def scan_directory(directory_path):
    results = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            results[filename] = parse_file_details(file_path)
    return results

def save_json(data, filename='order.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    directory_path = "P:/KONTEK/ENGINEERING/ELECTRICAL/Application Development/ERP/33. Vendor Quote and Order Parsing Kontek"
    logging.info("Scanning directory...")
    order_data = scan_directory(directory_path)
    logging.info("Saving JSON...")
    save_json(order_data)
    logging.info("Process completed.")

if __name__ == '__main__':
    main()