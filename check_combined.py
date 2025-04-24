import csv

def analyze_combined_csv(file_path):
    # Count rows and check for unique SKU-Location pairs
    row_count = 0
    unique_pairs = set()
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip header row
        
        for row in reader:
            row_count += 1
            if len(row) >= 3:
                sku = row[1]
                location = row[2]
                unique_pairs.add((sku, location))
    
    print(f"Total rows in file (excluding header): {row_count}")
    print(f"Unique SKU-Location pairs: {len(unique_pairs)}")
    
    # Check if every pair is unique
    is_all_unique = row_count == len(unique_pairs)
    print(f"All SKU-Location pairs are unique: {is_all_unique}")

if __name__ == "__main__":
    file_path = "combined_sku_locations.csv"
    analyze_combined_csv(file_path) 