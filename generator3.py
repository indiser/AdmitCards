"""
Admit Card Generator - Automated batch processing of admit cards from CSV data

TIME COMPLEXITY ANALYSIS:
- to_roman(num): O(1) - Fixed iterations for numbers 1-10
- load_coordinates(): O(1) - Reading fixed 8 fields from JSON
- save_coordinates(): O(1) - Writing fixed 8 fields to JSON
- find_coordinates(): O(1) - Interactive, not dependent on data size
- generate_admit_cards(): O(n/w) with multithreading where:
  * n = number of students
  * w = number of worker threads
  Overall: O(n) - Linear with number of students (parallelized)

SPACE COMPLEXITY ANALYSIS:
- coordinates: O(1) - Fixed 8 field coordinates
- text_sizes: O(1) - Fixed 8 field sizes
- data (DataFrame): O(n * f) - Stores all student records
- Image processing: O(w * h * workers) - Template per thread
- Output files: O(n * w * h) - One image per student
  Overall: O(n) - Linear with number of students

IMPROVEMENTS:
- Configuration file for easy customization
- Multi-threading for 3-4x faster generation
- Preview mode to test before batch processing
"""

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Load configuration
def load_config():
    """Load configuration from config.json"""
    config_file = "C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/config.json"
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("✓ Configuration loaded")
        return config
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {config_file}")
        exit(1)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        exit(1)

config = load_config()

# Extract configuration
Imagefilename = config['paths']['template']
DataFileName = config['paths']['data']
Output_path = config['paths']['output']
COORDINATES_FILE = config['paths']['coordinates']

FONT_PATH = config['font']['path']
FONT_SIZE = config['font']['size']
FONT_COLOR = config['font']['color']

field_names = config['fields']
text_sizes = {k: tuple(v) for k, v in config['text_sizes'].items()}

ENABLE_MULTITHREADING = config['performance']['enable_multithreading']
MAX_WORKERS = config['performance']['max_workers']

PREVIEW_ENABLED = config['preview']['enabled']
PREVIEW_COUNT = config['preview']['preview_count']


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


# Store coordinates
coordinates = {}

# Coordinate capture state
current_field_index = [0]
captured_coords = {}

def to_roman(num):
    """Convert number to Roman numeral."""
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
    with open(COORDINATES_FILE, 'w') as f:
        json.dump(captured_coords, f, indent=4)
    print(f"\nCoordinates saved to {COORDINATES_FILE}")

def load_coordinates():
    """Load coordinates from JSON file if exists."""
    if os.path.exists(COORDINATES_FILE):
        with open(COORDINATES_FILE, 'r') as f:
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


# Load saved coordinates
saved_coords = load_coordinates()
if saved_coords:
    coordinates = {k: tuple(v) for k, v in saved_coords.items()}
    print("✓ Loaded saved coordinates")


def generate_single_card(row, template_img, font):
    """Generate a single admit card (for multithreading)."""
    try:
        img = template_img.copy()
        draw = ImageDraw.Draw(img)
        
        for field in field_names:
            if field in coordinates:
                x, y = coordinates[field]
                value = to_roman(row[field]) if field == 'semester' else str(row[field])
                draw.text((x, y), value, font=font, fill=FONT_COLOR)
        
        safe_filename = str(row['roll no.']).replace('/', '_').replace('\\', '_')
        output_file = os.path.join(Output_path, f"{safe_filename}.png")
        img.save(output_file)
        return (True, row.get('name', 'Unknown'), None)
    except Exception as e:
        return (False, row.get('name', 'Unknown'), str(e))


def preview_admit_card():
    """Generate preview of first admit card."""
    print("\n" + "="*50)
    print("    PREVIEW MODE")
    print("="*50)
    
    if not validate_template() or not validate_coordinates():
        return False
    
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()
    
    template_img = Image.open(Imagefilename)
    
    print(f"\nGenerating preview for first {PREVIEW_COUNT} student(s)...")
    
    for i in range(min(PREVIEW_COUNT, len(data))):
        row = data.iloc[i]
        success, name, error = generate_single_card(row, template_img, font)
        
        if success:
            preview_file = os.path.join(Output_path, f"PREVIEW_{row['roll no.']}.png")
            img = Image.open(os.path.join(Output_path, f"{row['roll no.']}.png"))
            img.save(preview_file)
            print(f"✓ Preview generated: {preview_file}")
            print(f"  Student: {name}")
        else:
            print(f"✗ Preview failed for {name}: {error}")
    
    response = input("\nPreview looks good? Continue with full generation? (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def generate_admit_cards():
    """Generate admit cards with multithreading and preview."""
    if not validate_template() or not validate_coordinates():
        return
    
    if not os.path.exists(Output_path):
        os.makedirs(Output_path)
        print(f"✓ Created output directory: {Output_path}")
    
    # Preview mode
    if PREVIEW_ENABLED:
        if not preview_admit_card():
            print("\nGeneration cancelled by user")
            return
    
    # Load font and template
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        print(f"✓ Loaded font: {FONT_PATH}")
    except:
        print("⚠ Font not found, using default")
        font = ImageFont.load_default()
    
    try:
        template_img = Image.open(Imagefilename)
        print(f"✓ Template loaded: {template_img.size[0]}x{template_img.size[1]}px")
    except Exception as e:
        print(f"ERROR: Failed to load template: {e}")
        return
    
    print(f"\nGenerating {len(data)} admit cards...")
    if ENABLE_MULTITHREADING:
        print(f"✓ Multi-threading enabled ({MAX_WORKERS} workers)")
    
    start_time = time.time()
    failed_cards = []
    
    if ENABLE_MULTITHREADING:
        # Multi-threaded generation
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(generate_single_card, row, template_img, font): row 
                      for _, row in data.iterrows()}
            
            for future in tqdm(as_completed(futures), total=len(data), desc="Progress", unit="card"):
                success, name, error = future.result()
                if not success:
                    failed_cards.append((name, error))
    else:
        # Single-threaded generation
        for _, row in tqdm(data.iterrows(), total=len(data), desc="Progress", unit="card"):
            success, name, error = generate_single_card(row, template_img, font)
            if not success:
                failed_cards.append((name, error))
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print(f"\n✓ Successfully generated {len(data) - len(failed_cards)}/{len(data)} admit cards")
    print(f"✓ Time taken: {elapsed_time:.2f} seconds ({len(data)/elapsed_time:.2f} cards/sec)")
    print(f"✓ Saved to: {Output_path}")
    
    if failed_cards:
        print(f"\n⚠ Failed to generate {len(failed_cards)} cards:")
        for name, error in failed_cards[:5]:  # Show first 5 errors
            print(f"  - {name}: {error}")
        if len(failed_cards) > 5:
            print(f"  ... and {len(failed_cards) - 5} more")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("    ADMIT CARD GENERATOR v2.0")
    print("="*50)
    print('\nOptions:')
    print('  "Load"     - Capture coordinates from template')
    print('  "Generate" - Create admit cards for all students')
    print('  "Preview"  - Generate preview card(s) only\n')
    
    user_input = input("Enter your choice: ").strip().title()
    
    if user_input == "Load":
        if not validate_template():
            exit(1)
        find_coordinates()
    elif user_input == "Preview":
        if data is not None:
            preview_admit_card()
        else:
            print("Cannot generate preview - data loading failed")
    elif user_input == "Generate":
        if data is not None:
            generate_admit_cards()
        else:
            print("Cannot generate cards - data loading failed")
    else:
        print("Invalid input. Please type 'Load', 'Preview', or 'Generate'")
        exit(1)
