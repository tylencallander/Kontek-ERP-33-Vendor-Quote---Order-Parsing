import json
import os
import pdfplumber
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

        # Chart Data

        # Chart Data
        #'item_no': '',
        #'quantity': '',
        #'backorder_qty': ''
        #'unit': '',
        #'tax': '',
        #'unit_price': '',
        #'amount_price': '',

        # Total Price

        'total_price': ''
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')
                
                for i, line in enumerate(lines):

                    # Header Data

                    if 'Order No' in line:
                        details['order_number'] = line.split(':')[-1].strip()
                    if 'Date' in line:
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
                    
                    # Chart Data

                    # Chart Data
                    #'item_no': '',
                    #'quantity': '',
                    #'backorder_qty': '',
                    #'unit': '',
                    #'tax': '',
                    #'unit_price': '',
                    #'amount_price': '',

                    # Total Price

                    if 'Total Amount' in line and not details['total_price']:
                        price_match = re.search(r'\d{1,3}(?:,\d{3})*\.\d{2}', line)
                        if price_match:
                            details['total_price'] = price_match.group(0)

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