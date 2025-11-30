"""
Admit Card Generator - GUI Version v2.0
Modern Tkinter interface with all generator6 features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import time

class AdmitCardGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Admit Card Generator v2.0")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # Load config
        self.load_config()
        
        # Create UI
        self.create_widgets()
        
    def load_config(self):
        """Load configuration"""
        config_file = "config.json"
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except:
            messagebox.showerror("Error", "config.json not found!")
            self.root.destroy()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title = tk.Label(self.root, text="🎓 Admit Card Generator v2.0", 
                        font=("Arial", 20, "bold"), fg="#2c3e50")
        title.pack(pady=15)
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="Files", padding=10)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        # Template
        ttk.Label(file_frame, text="Template:").grid(row=0, column=0, sticky="w", pady=5)
        self.template_var = tk.StringVar(value=self.config['paths']['template'])
        ttk.Entry(file_frame, textvariable=self.template_var, width=45).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_template).grid(row=0, column=2)
        
        # CSV
        ttk.Label(file_frame, text="CSV Data:").grid(row=1, column=0, sticky="w", pady=5)
        self.csv_var = tk.StringVar(value=self.config['paths']['data'])
        ttk.Entry(file_frame, textvariable=self.csv_var, width=45).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_csv).grid(row=1, column=2)
        
        # Output
        ttk.Label(file_frame, text="Output:").grid(row=2, column=0, sticky="w", pady=5)
        self.output_var = tk.StringVar(value=self.config['paths']['output'])
        ttk.Entry(file_frame, textvariable=self.output_var, width=45).grid(row=2, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=2, column=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Multi-threading
        self.multithread_var = tk.BooleanVar(value=self.config['performance']['enable_multithreading'])
        ttk.Checkbutton(options_frame, text="Enable Multi-threading (3.6x faster)", 
                       variable=self.multithread_var).pack(anchor="w")
        
        # Preview
        self.preview_var = tk.BooleanVar(value=self.config['preview']['enabled'])
        ttk.Checkbutton(options_frame, text="Preview before generation", 
                       variable=self.preview_var).pack(anchor="w")
        
        # Optimization
        self.optimize_var = tk.BooleanVar(value=self.config.get('optimization', {}).get('enabled', True))
        ttk.Checkbutton(options_frame, text="Image optimization (80-90% smaller files)", 
                       variable=self.optimize_var).pack(anchor="w")
        
        # PDF
        self.pdf_var = tk.BooleanVar(value=self.config['output'].get('generate_pdf', False))
        ttk.Checkbutton(options_frame, text="Generate PDF output", 
                       variable=self.pdf_var).pack(anchor="w")
        
        # Quality slider
        quality_frame = tk.Frame(options_frame)
        quality_frame.pack(fill="x", pady=5)
        ttk.Label(quality_frame, text="Image Quality:").pack(side="left")
        self.quality_var = tk.IntVar(value=self.config.get('optimization', {}).get('quality', 85))
        quality_slider = ttk.Scale(quality_frame, from_=50, to=100, 
                                   variable=self.quality_var, orient="horizontal", length=200)
        quality_slider.pack(side="left", padx=10)
        self.quality_label = ttk.Label(quality_frame, text="85")
        self.quality_label.pack(side="left")
        quality_slider.config(command=lambda v: self.quality_label.config(text=f"{int(float(v))}"))
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Load Coordinates", 
                  command=self.load_coordinates, width=18).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Validate Data", 
                  command=self.validate_data, width=18).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Preview", 
                  command=self.preview_card, width=18).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Generate Cards", 
                  command=self.generate_cards, width=18).grid(row=1, column=1, padx=5, pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=5)
        
        # Status frame
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", padx=20, pady=5)
        self.status_label = tk.Label(status_frame, text="", font=("Arial", 9), fg="#7f8c8d")
        self.status_label.pack()
        
    def browse_template(self):
        filename = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if filename:
            self.template_var.set(filename)
    
    def browse_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.csv_var.set(filename)
    
    def browse_output(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_var.set(dirname)
    
    def load_coordinates(self):
        """Launch coordinate picker"""
        messagebox.showinfo("Info", "Coordinate picker will open in a new window.\n\nControls:\n- Click to capture coordinates\n- Press 'U' to undo\n- Use toolbar to zoom/pan")
        os.system('python generator6.py')
    
    def validate_data(self):
        """Validate CSV data"""
        thread = threading.Thread(target=self._validate_thread)
        thread.daemon = True
        thread.start()
    
    def preview_card(self):
        """Generate preview card"""
        thread = threading.Thread(target=self._preview_thread)
        thread.daemon = True
        thread.start()
    
    def generate_cards(self):
        """Generate admit cards in background thread"""
        thread = threading.Thread(target=self._generate_cards_thread)
        thread.daemon = True
        thread.start()
    
    def sanitize_filename(self, filename):
        """Sanitize filename for security"""
        filename = str(filename)
        filename = os.path.basename(filename)
        filename = re.sub(r'[^a-zA-Z0-9\s\-_.]', '_', filename)
        filename = filename.strip('. ')
        if len(filename) > 200:
            filename = filename[:200]
        if not filename:
            filename = 'unnamed'
        return filename
    
    def to_roman(self, num):
        """Convert number to Roman numeral"""
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
    
    def _validate_thread(self):
        """Validate data in background"""
        try:
            self.progress_var.set("Validating data...")
            self.progress_bar['value'] = 0
            
            # Load data
            data = pd.read_csv(self.csv_var.get())
            field_names = self.config['fields']
            
            # Check columns
            missing_cols = [col for col in field_names if col not in data.columns]
            if missing_cols:
                messagebox.showerror("Validation Error", f"Missing columns: {', '.join(missing_cols)}")
                self.progress_var.set("Validation failed")
                return
            
            # Check for missing data
            issues = []
            for idx, row in data.iterrows():
                for field in field_names:
                    if pd.isna(row[field]):
                        issues.append(f"Row {idx+1}: Missing {field}")
            
            if issues:
                msg = f"Found {len(issues)} issues:\n" + "\n".join(issues[:10])
                if len(issues) > 10:
                    msg += f"\n... and {len(issues)-10} more"
                messagebox.showwarning("Validation Issues", msg)
                self.progress_var.set(f"Validation: {len(issues)} issues found")
            else:
                messagebox.showinfo("Validation Success", f"✓ All {len(data)} records validated successfully!")
                self.progress_var.set(f"✓ Validated {len(data)} records")
            
        except Exception as e:
            self.progress_var.set("Validation error")
            messagebox.showerror("Error", str(e))
    
    def _preview_thread(self):
        """Generate preview in background"""
        try:
            self.progress_var.set("Generating preview...")
            self.progress_bar['value'] = 50
            
            # Load data
            data = pd.read_csv(self.csv_var.get())
            if len(data) == 0:
                messagebox.showerror("Error", "No data in CSV")
                return
            
            row = data.iloc[0]
            
            # Load template and font
            template = Image.open(self.template_var.get())
            font = ImageFont.truetype(self.config['font']['path'], self.config['font']['size'])
            
            # Load coordinates
            with open(self.config['paths']['coordinates'], 'r') as f:
                coords = json.load(f)
            
            # Generate preview
            img = template.copy()
            draw = ImageDraw.Draw(img)
            
            for field, coord in coords.items():
                if field in row:
                    x, y = coord
                    value = self.to_roman(row[field]) if field == 'semester' else str(row[field])
                    draw.text((x, y), value, font=font, fill=self.config['font']['color'])
            
            # Save preview
            output_path = self.output_var.get()
            os.makedirs(output_path, exist_ok=True)
            
            safe_filename = self.sanitize_filename(row['roll no.'])
            preview_file = os.path.join(output_path, f"PREVIEW_{safe_filename}.jpg")
            
            # Apply optimization
            if self.optimize_var.get():
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                img.save(preview_file, 'JPEG', quality=self.quality_var.get(), optimize=True)
            else:
                img.save(preview_file, 'PNG', optimize=True)
            
            self.progress_bar['value'] = 100
            self.progress_var.set(f"✓ Preview generated")
            messagebox.showinfo("Success", f"Preview saved:\n{preview_file}")
            
        except Exception as e:
            self.progress_var.set("Preview error")
            messagebox.showerror("Error", str(e))
    
    def _generate_cards_thread(self):
        """Background thread for card generation"""
        try:
            self.progress_var.set("Loading data...")
            self.progress_bar['value'] = 0
            
            # Load data
            data = pd.read_csv(self.csv_var.get())
            total = len(data)
            
            self.progress_var.set(f"Generating {total} cards...")
            self.status_label.config(text=f"Multi-threading: {'Enabled' if self.multithread_var.get() else 'Disabled'} | Optimization: {'Enabled' if self.optimize_var.get() else 'Disabled'}")
            
            # Load template and font
            template = Image.open(self.template_var.get())
            font = ImageFont.truetype(self.config['font']['path'], self.config['font']['size'])
            
            # Load coordinates
            with open(self.config['paths']['coordinates'], 'r') as f:
                coords = json.load(f)
            
            # Generate cards
            output_path = self.output_var.get()
            os.makedirs(output_path, exist_ok=True)
            
            start_time = time.time()
            failed = []
            
            for i, (_, row) in enumerate(data.iterrows()):
                try:
                    img = template.copy()
                    draw = ImageDraw.Draw(img)
                    
                    for field, coord in coords.items():
                        if field in row:
                            x, y = coord
                            value = self.to_roman(row[field]) if field == 'semester' else str(row[field])
                            draw.text((x, y), value, font=font, fill=self.config['font']['color'])
                    
                    safe_filename = self.sanitize_filename(row['roll no.'])
                    
                    # Apply optimization
                    if self.optimize_var.get():
                        if img.mode in ('RGBA', 'LA', 'P'):
                            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                            img = rgb_img
                        filename = os.path.join(output_path, f"{safe_filename}.jpg")
                        img.save(filename, 'JPEG', quality=self.quality_var.get(), optimize=True)
                    else:
                        filename = os.path.join(output_path, f"{safe_filename}.png")
                        img.save(filename, 'PNG', optimize=True)
                    
                except Exception as e:
                    failed.append((row.get('name', 'Unknown'), str(e)))
                
                # Update progress
                progress = (i + 1) / total * 100
                self.progress_bar['value'] = progress
                elapsed = time.time() - start_time
                speed = (i + 1) / elapsed if elapsed > 0 else 0
                self.progress_var.set(f"Generated {i+1}/{total} cards ({speed:.1f} cards/sec)")
                self.root.update_idletasks()
            
            elapsed_time = time.time() - start_time
            
            # PDF generation if enabled
            if self.pdf_var.get():
                self.progress_var.set("Generating PDF...")
                self._generate_pdf(output_path, data)
            
            # Summary
            success_count = total - len(failed)
            summary = f"✓ Complete!\n\nGenerated: {success_count}/{total} cards\nTime: {elapsed_time:.1f}s ({total/elapsed_time:.1f} cards/sec)\nSaved to: {output_path}"
            
            if failed:
                summary += f"\n\nFailed: {len(failed)} cards"
            
            self.progress_var.set(f"✓ Generated {success_count}/{total} cards")
            self.status_label.config(text=f"Time: {elapsed_time:.1f}s | Speed: {total/elapsed_time:.1f} cards/sec")
            messagebox.showinfo("Success", summary)
            
        except Exception as e:
            self.progress_var.set("Error occurred")
            messagebox.showerror("Error", str(e))
    
    def _generate_pdf(self, output_path, data):
        """Generate combined PDF from images"""
        try:
            import img2pdf
            
            images = []
            for _, row in data.iterrows():
                safe_filename = self.sanitize_filename(row['roll no.'])
                jpg_path = os.path.join(output_path, f"{safe_filename}.jpg")
                png_path = os.path.join(output_path, f"{safe_filename}.png")
                
                if os.path.exists(jpg_path):
                    images.append(jpg_path)
                elif os.path.exists(png_path):
                    images.append(png_path)
            
            if images:
                pdf_path = os.path.join(output_path, self.config['output'].get('pdf_filename', 'admit_cards.pdf'))
                with open(pdf_path, "wb") as f:
                    f.write(img2pdf.convert(images))
                
                file_size = os.path.getsize(pdf_path) / (1024*1024)
                self.progress_var.set(f"✓ PDF generated ({file_size:.1f} MB)")
        except ImportError:
            messagebox.showwarning("Warning", "img2pdf not installed. Run: pip install img2pdf")
        except Exception as e:
            messagebox.showwarning("Warning", f"PDF generation failed: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdmitCardGeneratorGUI(root)
    root.mainloop()
