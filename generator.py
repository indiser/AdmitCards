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
import csv
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json

Imagefilename="C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/Blank.png"
DataFileName="C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/dummy_data.csv"
Output_path="C:/Users/ranab/OneDrive/Desktop/Admit Card Generator/output"

FONT_PATH = "C:/Windows/Fonts/times.ttf"
FONT_SIZE = 35 


# get the data from csv
data=pd.read_csv(DataFileName)


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


# get the quardinate of all the placeholders
field_names = ['name', 'gender', 'semester', 'dob', 'course', 'APAAR', 'roll no.', 'reg no.']
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


# change the template and genrate
def replace_text_in_image(
        input_path,
        output_path,
        old_text_position,
        old_text_size,
        new_text,
        background_color,
        font_path=None,
        font_size=None,
        text_color=(0,0,0)):
    try:
        img=Image.open(Imagefilename)
        print("Success")
    except IOError:
        print("Failed")

    draw=ImageDraw.Draw(img)
    x,y=old_text_position
    w,h=old_text_size
    draw.rectangle([x,y,x+w,y+h],fill=background_color)


    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception as e:
        print(f"Error loading font: {e}")
        font = ImageFont.load_default()

    
    draw.text((x, y), new_text, font=font, fill=text_color)

    try:
        img.save(output_path)
        print(f"Image saved successfully at '{output_path}'")
    except Exception as e:
        print(f"Error saving image: {e}")


# Load saved coordinates if available
saved_coords = load_coordinates()
if saved_coords:
    coordinates = {k: tuple(v) for k, v in saved_coords.items()}
    print("Loaded saved coordinates from coordinates.json")



# Generate admit cards for all students
def generate_admit_cards():
    """Generate admit cards for all students in the CSV."""
    if not os.path.exists(Output_path):
        os.makedirs(Output_path)
    
    # Load font
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        print("Font not found, using default")
        font = ImageFont.load_default()
    
    for index, row in data.iterrows():
        img = Image.open(Imagefilename).copy()
        draw = ImageDraw.Draw(img)
        
        # Replace each field
        for field in field_names:
            if field in coordinates:
                x, y = coordinates[field]
                w, h = text_sizes[field]
                
                # Write student data
                value = to_roman(row[field]) if field == 'semester' else str(row[field])
                draw.text((x, y), value, font=font, fill='black')
        
        # Save admit card
        output_file = os.path.join(Output_path, f"{row['roll no.']}.png")
        img.save(output_file)
        print(f"Generated: {output_file}")
    
    print(f"\nAll {len(data)} admit cards generated successfully!")




if __name__=="__main__":
    print('Type "Load" to load quardanates or "Generate" to generate Admit cards')
    user_input=input("Enter the name of the student: ").title()
    if user_input=="Load":
        find_coordinates()
    elif user_input=="Generate":
        generate_admit_cards()
    else:
        print("Please Provide a valid input")
