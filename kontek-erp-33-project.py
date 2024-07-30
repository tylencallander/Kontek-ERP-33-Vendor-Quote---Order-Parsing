import json
import os
import pdfplumber
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_file_details(file_path):
    details = {
        'filename': os.path.basename(file_path),
        'file_location': file_path,
        'order_number': '',
        'order_date': '',
        'ship_date': '',
        'ship_to': '',
        'bill_to': ''
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                if 'Order No' in line:
                    details['order_number'] = line.split(':')[-1].strip()
                if 'Date' in line:
                    details['order_date'] = line.split(':')[-1].strip()
                if 'Ship Date:' in line:
                    extracted_date = line.split(':')[-1].strip()
                    details['ship_date'] = extracted_date if extracted_date else "N/A"
                if 'Ship To:' in line:
                    details['ship_to'] = ' '.join(lines[i+2:i+3]).strip()  # Assuming address spans the next two lines
                if 'Purchased From:' in line:
                    details['bill_to'] = ' '.join(lines[i+1:i+2]).strip()  # Assuming address spans the next two lines


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
