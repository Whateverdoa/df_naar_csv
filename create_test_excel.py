#!/usr/bin/env python3
"""
Create a test Excel file for testing the FastAPI endpoints
"""
import pandas as pd
from pathlib import Path

# Create test data
test_data = {
    'aantal': [100, 150, 200, 75, 300, 125, 180, 90, 250, 160],
    'Omschrijving': [
        'Product A - Red Label',
        'Product B - Blue Label', 
        'Product C - Green Label',
        'Product D - Yellow Label',
        'Product E - Purple Label',
        'Product F - Orange Label',
        'Product G - Pink Label',
        'Product H - Brown Label',
        'Product I - Black Label',
        'Product J - White Label'
    ],
    'sluitbarcode': [12345678, 12345679, 12345680, 12345681, 12345682, 
                     12345683, 12345684, 12345685, 12345686, 12345687],
    'Artnr': ['ART001', 'ART002', 'ART003', 'ART004', 'ART005',
              'ART006', 'ART007', 'ART008', 'ART009', 'ART010'],
    'beeld': ['product_a.pdf', 'product_b.pdf', 'product_c.pdf', 'product_d.pdf', 'product_e.pdf',
              'product_f.pdf', 'product_g.pdf', 'product_h.pdf', 'product_i.pdf', 'product_j.pdf']
}

# Create DataFrame
df = pd.DataFrame(test_data)

# Create test_files directory
test_dir = Path('test_files')
test_dir.mkdir(exist_ok=True)

# Save as Excel file
excel_path = test_dir / 'test_labels.xlsx'
df.to_excel(excel_path, index=False, engine='openpyxl')

# Save as CSV file
csv_path = test_dir / 'test_labels.csv'
df.to_csv(csv_path, index=False, sep=';')

print(f"✅ Created test files:")
print(f"   📊 Excel: {excel_path}")
print(f"   📄 CSV: {csv_path}")
print(f"   📈 Records: {len(df)}")
print(f"   🏷️  Total labels: {df['aantal'].sum()}")
print("\nTest data preview:")
print(df.head())
