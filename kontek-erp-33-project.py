import json
import os
import fitz  # PyMuPDF
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
        text = doc[0].get_text()
    except Exception as e:
        logging.error(f"Failed to open or read {file_path}: {e}")
        return {}

    details = {
        'filename': os.path.basename(file_path),
        'order_number': '',
        'date': '',
        'items': [],
        'subtotal': 0,
        'tax': 0,
        'total_amount': 0
    }

    lines = text.split('\n')
    for line in lines:
        try:
            if 'Order No.:' in line:
                details['order_number'] = line.split(':')[-1].strip()
            elif 'Date:' in line:
                details['date'] = line.split(':')[-1].strip()
            elif line.startswith('XEL-'):
                parts = line.split()
                if len(parts) > 4:
                    item = {
                        'item_no': parts[0],
                        'quantity_ordered': parts[1],
                        'description': ' '.join(parts[4:-2]),
                        'unit_price': parts[-2],
                        'amount': parts[-1]
                    }
                    details['items'].append(item)
        except IndexError as e:
            logging.warning(f"Skipping line due to IndexError: {line} | Error: {e}")

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
    directory_path = "P:/KONTEK/ENGINEERING/ELECTRICAL/Application Development/ERP/33. Vendor Quote and Order Parsing Kontek"  # Adjust path as needed
    print("Scanning directory...")
    order_data = scan_directory(directory_path)
    print("Saving JSON...")
    save_json(order_data)
    print("Process completed.")

if __name__ == '__main__':
    main()

