import json
import os
import fitz  
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_project_data(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Failed to load data from {filepath}: {e}")
        return {}

def parse_file_details(file_path):
    try:
        doc = fitz.open(file_path)
        text = doc[0].get_text("text")
    except Exception as e:
        logging.error(f"Failed to open or read {file_path}: {e}")
        return {}

    details = {
        'filename': os.path.basename(file_path),
        'file_location': file_path,
        'order_number': '',
        'date': '',
        'ship_to': '',
        'bill_to': '',
        'items': [],
        'currency': '',
        'tax_rate': '',
        'kontek_hst_number': '',
        'terms': ''
    }

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if 'Order No.:' in line:
            details['order_number'] = line.split(':')[-1].strip()
        elif 'Date:' in line:
            details['date'] = line.split(':')[-1].strip()
        elif line.startswith('Ship To:'):
            details['ship_to'] = line[8:].strip()
        elif line.startswith('Bill To:'):
            details['bill_to'] = line[8:].strip()
        elif line.startswith('XEL-'):  
            parts = line.split()
            if len(parts) >= 5:
                item = {
                    'part_number': parts[0],
                    'quantity': parts[1],
                    'description': ' '.join(parts[2:-2]),
                    'price': parts[-2],
                    'total': parts[-1]
                }
                details['items'].append(item)
        elif 'HST Number:' in line:
            details['kontek_hst_number'] = line.split(':')[-1].strip()
        elif 'Terms:' in line:
            details['terms'] = line.split(':')[-1].strip()
        elif 'Currency:' in line:
            details['currency'] = line.split(':')[-1].strip()
        elif 'Tax Rate:' in line:
            details['tax_rate'] = line.split(':')[-1].strip()

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
    print("Scanning directory...")
    order_data = scan_directory(directory_path)
    print("Saving JSON...")
    save_json(order_data)
    print("Process completed.")

if __name__ == '__main__':
    main()

