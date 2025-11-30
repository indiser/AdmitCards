"""
Admit Card Generator - Automated batch processing of admit cards from CSV data

TIME COMPLEXITY ANALYSIS:
- to_roman(num): O(1) - Fixed iterations for numbers 1-10
- load_coordinates(): O(1) - Reading fixed 8 fields from JSON
- save_coordinates(): O(1) - Writing fixed 8 fields to JSON
- find_coordinates(): O(1) - Interactive, not dependent on data size
- generate_admit_cards(): O(n * f * p) where:
  * n = number of students
  * f = number of fields (8, constant)
  * p = image processing time per field
  Overall: O(n) - Linear with number of students

SPACE COMPLEXITY ANALYSIS:
- coordinates: O(1) - Fixed 8 field coordinates
- text_sizes: O(1) - Fixed 8 field sizes
- data (DataFrame): O(n * f) - Stores all student records
- Image processing: O(w * h) - Template image dimensions (constant per card)
- Output files: O(n * w * h) - One image per student
  Overall: O(n) - Linear with number of students

OVERALL EFFICIENCY:
- Time: O(n) - Scales linearly with student count
- Space: O(n) - Scales linearly with output files
- Optimized for batch processing with minimal memory overhead
"""

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
from tqdm import tqdm

Imagefilename="C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/Blank.png"
DataFileName="C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/dummy_data.csv"
Output_path="C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/output"

FONT_PATH = "C:/Windows/Fonts/times.ttf"
FONT_SIZE = 35 


# Field names - moved to top for better organization
field_names = ['name', 'gender', 'semester', 'dob', 'course', 'APAAR', 'roll no.', 'reg no.']

# Validate and load data from CSV
def load_and_validate_data():
    """Load CSV and validate required columns exist."""
    try:
        data = pd.read_csv(DataFileName)
        missing_cols = [col for col in field_names if col not in data.columns]
        if missing_cols:
            print(f"ERROR: Missing columns in CSV: {missing_cols}")
            print(f"Required columns: {field_names}")
            return None
        print(f"✓ Loaded {len(data)} students from CSV")
        return data
    except FileNotFoundError:
        print(f"ERROR: CSV file not found: {DataFileName}")
        return None
    except Exception as e:
        print(f"ERROR loading CSV: {e}")
        return None

data = load_and_validate_data()
if data is None:
    print("Exiting due to data loading error")
    exit(1)


# Store coordinates here after finding them
coordinates = {
    'name': (0, 0),  # Replace with actual coordinates
    'gender': (0, 0),
    'semester': (0, 0),
    'dob': (0, 0),
    'course': (0, 0),
    'APAAR': (0, 0),
    'roll no.': (0, 0),
    'reg no.': (0, 0)
}

# Store text sizes (width, height) for covering placeholders
text_sizes = {
    'name': (400, 50),  # Adjust width/height to fully cover placeholder text
    'gender': (150, 50),
    'semester': (100, 50),
    'dob': (250, 50),
    'course': (400, 50),
    'APAAR': (300, 50),
    'roll no.': (250, 50),
    'reg no.': (250, 50)
}


# Coordinate capture state
current_field_index = [0]
captured_coords = {}

def to_roman(num):
    val = [10, 9, 5, 4, 1]
    syms = ['X', 'IX', 'V', 'IV', 'I']
    roman = ''
    i = 0
    num = int(num)
    while num > 0:
        for _ in range(num // val[i]):
            roman += syms[i]
            num -= val[i]
        i += 1
    return roman

def save_coordinates():
    """Save coordinates to JSON file."""
    config_file = "C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/coordinates.json"
    with open(config_file, 'w') as f:
        json.dump(captured_coords, f, indent=4)
    print(f"\nCoordinates saved to {config_file}")

def load_coordinates():
    """Load coordinates from JSON file if exists."""
    config_file = "C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/coordinates.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def on_click(event):
    """Callback function for mouse click events."""
    if event.inaxes and current_field_index[0] < len(field_names):
        field = field_names[current_field_index[0]]
        x, y = float(event.xdata), float(event.ydata)
        captured_coords[field] = [x, y]
        print(f"{field}: ({x:.2f}, {y:.2f})")
        current_field_index[0] += 1
        if current_field_index[0] >= len(field_names):
            print("\nAll coordinates captured!")
            save_coordinates()
            print("Close the window.")

def find_coordinates():
    """Display template and capture click coordinates with zoom/pan."""
    print("Click on placeholders in this order:")
    for i, field in enumerate(field_names, 1):
        print(f"{i}. {field}")
    print("\nControls:")
    print("- Use toolbar to zoom/pan")
    print("- Scroll wheel to zoom in/out")
    print("- Right-click drag to pan")
    print()
    
    img = mpimg.imread(Imagefilename)
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img)
    ax.set_title(f"Click on: {field_names[0]}")
    
    # Enable zoom and pan
    plt.tight_layout()
    
    def update_title(event):
        if current_field_index[0] < len(field_names):
            ax.set_title(f"Click on: {field_names[current_field_index[0]]}")
            fig.canvas.draw()
    
    fig.canvas.mpl_connect('button_press_event', lambda e: (on_click(e), update_title(e)))
    plt.show()


def validate_coordinates():
    """Check if coordinates are properly loaded."""
    if not coordinates or all(v == (0, 0) for v in coordinates.values()):
        print("ERROR: Coordinates not loaded or invalid!")
        print("Please run 'Load' mode first to capture coordinates.")
        return False
    print("✓ Coordinates loaded successfully")
    return True

def validate_template():
    """Check if template image exists."""
    if not os.path.exists(Imagefilename):
        print(f"ERROR: Template image not found: {Imagefilename}")
        return False
    print("✓ Template image found")
    return True


# Load saved coordinates if available
saved_coords = load_coordinates()
if saved_coords:
    coordinates = {k: tuple(v) for k, v in saved_coords.items()}
    print("Loaded saved coordinates from coordinates.json")



def generate_admit_cards():
    """Generate admit cards for all students in the CSV with validation and progress bar."""
    # Validation checks
    if not validate_template():
        return
    if not validate_coordinates():
        return
    
    # Create output directory
    if not os.path.exists(Output_path):
        os.makedirs(Output_path)
        print(f"✓ Created output directory: {Output_path}")
    
    # Load font once (optimization)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        print(f"✓ Loaded font: {FONT_PATH}")
    except:
        print("⚠ Font not found, using default")
        font = ImageFont.load_default()
    
    # Load template once (optimization - cache template)
    try:
        template_img = Image.open(Imagefilename)
        print(f"✓ Template loaded: {template_img.size[0]}x{template_img.size[1]}px")
    except Exception as e:
        print(f"ERROR: Failed to load template: {e}")
        return
    
    print(f"\nGenerating {len(data)} admit cards...")
    
    # Generate cards with progress bar
    failed_cards = []
    for index, row in tqdm(data.iterrows(), total=len(data), desc="Progress", unit="card"):
        try:
            # Use cached template (copy it)
            img = template_img.copy()
            draw = ImageDraw.Draw(img)
            
            # Replace each field
            for field in field_names:
                if field in coordinates:
                    x, y = coordinates[field]
                    w, h = text_sizes[field]
                    
                    # Write student data
                    value = to_roman(row[field]) if field == 'semester' else str(row[field])
                    draw.text((x, y), value, font=font, fill='black')
            
            # Sanitize filename (remove special characters)
            safe_filename = str(row['roll no.']).replace('/', '_').replace('\\', '_')
            output_file = os.path.join(Output_path, f"{safe_filename}.png")
            img.save(output_file)
            
        except Exception as e:
            failed_cards.append((row.get('name', 'Unknown'), str(e)))
    
    # Summary
    print(f"\n✓ Successfully generated {len(data) - len(failed_cards)}/{len(data)} admit cards")
    print(f"✓ Saved to: {Output_path}")
    
    if failed_cards:
        print(f"\n⚠ Failed to generate {len(failed_cards)} cards:")
        for name, error in failed_cards:
            print(f"  - {name}: {error}")




if __name__=="__main__":
    print("\n" + "="*50)
    print("    ADMIT CARD GENERATOR")
    print("="*50)
    print('\nType "Load" to capture coordinates')
    print('Type "Generate" to create admit cards\n')
    
    user_input = input("Enter your choice: ").strip().title()
    
    if user_input == "Load":
        if not validate_template():
            exit(1)
        find_coordinates()
    elif user_input == "Generate":
        if data is not None:
            generate_admit_cards()
        else:
            print("Cannot generate cards - data loading failed")
    else:
        print("Invalid input. Please type 'Load' or 'Generate'")
        exit(1)
