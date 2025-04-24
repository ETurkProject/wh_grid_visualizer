import os
import csv
import glob

def combine_csv_files(input_folder, output_file):
    # Dictionary to track unique SKU-Location combinations
    # Format: {(sku, location): timestamp}
    unique_entries = {}
    
    # Get all CSV files in the input folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    print(f"Found {len(csv_files)} CSV files in {input_folder}")
    
    # Process each CSV file
    for file_path in csv_files:
        print(f"Processing: {os.path.basename(file_path)}")
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # Skip the header row
            
            # Continue if the file has the expected header structure
            if header and len(header) >= 3 and 'Timestamp' in header and 'SKU' in header and 'Location' in header:
                timestamp_idx = header.index('Timestamp')
                sku_idx = header.index('SKU')
                location_idx = header.index('Location')
                
                # Process each row
                for row in reader:
                    if len(row) >= 3:
                        timestamp = row[timestamp_idx]
                        sku = row[sku_idx]
                        location = row[location_idx]
                        
                        # Add entry if it's not a duplicate
                        entry_key = (sku, location)
                        if entry_key not in unique_entries:
                            unique_entries[entry_key] = timestamp
            else:
                print(f"Skipping {file_path} - Incorrect header structure")
    
    # Write the combined data to output file
    print(f"Writing {len(unique_entries)} unique entries to {output_file}")
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Timestamp', 'SKU', 'Location'])
        
        for (sku, location), timestamp in unique_entries.items():
            writer.writerow([timestamp, sku, location])
    
    print(f"Finished! Combined data saved to {output_file}")

if __name__ == "__main__":
    # Change these paths as needed
    input_folder = "scan0404"
    output_file = "combined_sku_locations.csv"
    
    combine_csv_files(input_folder, output_file) 