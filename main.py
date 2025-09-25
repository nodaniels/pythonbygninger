"""
iPhone-style Building Navigation App
Main GUI application with mobile-like interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageDraw
import os
import sys

# Add the prototype directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import BuildingManager
from building_config import ConfigurationManager, BuildingConfig, FontSizeRange, RoomPattern

class BuildingNavigationApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        
        # Initialize building manager and configuration manager
        buildings_path = os.path.join(os.path.dirname(__file__), "bygninger")
        self.building_manager = BuildingManager(buildings_path)
        self.config_manager = ConfigurationManager(buildings_path)
        
        # GUI variables
        self.current_floor_image = None
        self.current_result = None
        self.scale_factor = 1.0
        self.current_screen = "building_selection"  # "building_selection", "room_search", or "config"
        self.config_window = None
        
        # Create GUI
        self.create_gui()
        
        # Load available buildings
        self.load_available_buildings()
    
    def setup_window(self):
        """Configure main window in iPhone-like format"""
        self.root.title("Building Navigation")
        self.root.geometry("375x812")  # iPhone 13 Pro dimensions
        self.root.configure(bg='#f8f9fa')
        self.root.resizable(False, False)
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Configure modern iOS-like styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure('Search.TButton',
                       background='#007AFF',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('SF Pro Display', 16, 'bold'))
        
        style.map('Search.TButton',
                 background=[('active', '#0056CC')])
    
    def create_gui(self):
        """Create the main GUI interface"""
        # Header
        self.header_frame = tk.Frame(self.root, bg='#f8f9fa', height=100)
        self.header_frame.pack(fill=tk.X, padx=20, pady=(40, 20))
        self.header_frame.pack_propagate(False)
        
        self.title_label = tk.Label(self.header_frame, 
                              text="Building Navigation",
                              font=('SF Pro Display', 24, 'bold'),
                              bg='#f8f9fa',
                              fg='#1c1c1e')
        self.title_label.pack(expand=True)
        
        self.subtitle_label = tk.Label(self.header_frame,
                                 text="Vælg bygning",
                                 font=('SF Pro Display', 16),
                                 bg='#f8f9fa', 
                                 fg='#8e8e93')
        self.subtitle_label.pack()
        
        # Main content frame (will switch between building selection and room search)
        self.main_frame = tk.Frame(self.root, bg='#f8f9fa')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Building selection frame
        self.building_frame = tk.Frame(self.main_frame, bg='#f8f9fa')
        
        # Search frame (initially hidden)
        self.search_frame = tk.Frame(self.main_frame, bg='#f8f9fa')
        
        self.create_building_selection()
        self.create_search_interface()
        
        # Result info frame
        self.info_frame = tk.Frame(self.root, bg='#f8f9fa')
        self.info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.info_label = tk.Label(self.info_frame,
                                  text="",
                                  font=('SF Pro Display', 14),
                                  bg='#f8f9fa',
                                  fg='#8e8e93',
                                  wraplength=300,
                                  justify=tk.CENTER)
        self.info_label.pack()
        
        # Image display frame
        self.image_frame = tk.Frame(self.root, bg='white', relief=tk.FLAT, bd=1)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 40))
        
        self.image_label = tk.Label(self.image_frame, bg='white')
        self.image_label.pack(expand=True)
        
        # Loading label (initially hidden)
        self.loading_label = tk.Label(self.root,
                                     text="Loading...",
                                     font=('SF Pro Display', 16),
                                     bg='#f8f9fa',
                                     fg='#8e8e93')
    
    def create_building_selection(self):
        """Create building selection interface"""
        building_label = tk.Label(self.building_frame,
                                 text="Vælg bygning",
                                 font=('SF Pro Display', 18, 'bold'),
                                 bg='#f8f9fa',
                                 fg='#1c1c1e')
        building_label.pack(anchor=tk.W, pady=(20, 20))
        
        # Building buttons container
        self.buildings_container = tk.Frame(self.building_frame, bg='#f8f9fa')
        self.buildings_container.pack(fill=tk.X, pady=10)
    
    def create_search_interface(self):
        """Create room search interface"""
        # Back button
        back_btn = ttk.Button(self.search_frame,
                             text="← Tilbage til bygninger",
                             command=self.show_building_selection)
        back_btn.pack(anchor=tk.W, pady=(0, 20))
        
        search_label = tk.Label(self.search_frame,
                               text="Søg efter lokale",
                               font=('SF Pro Display', 18, 'bold'),
                               bg='#f8f9fa',
                               fg='#1c1c1e')
        search_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Search input with iOS style
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.search_frame,
                               textvariable=self.search_var,
                               font=('SF Pro Display', 16),
                               bg='white',
                               fg='#1c1c1e',
                               relief=tk.FLAT,
                               bd=0,
                               highlightthickness=1,
                               highlightcolor='#007AFF',
                               highlightbackground='#d1d1d6')
        search_entry.pack(fill=tk.X, pady=(0, 15), ipady=12)
        search_entry.bind('<Return>', lambda e: self.search_room())
        
        # Search button
        search_btn = ttk.Button(self.search_frame,
                               text="Søg",
                               style='Search.TButton',
                               command=self.search_room)
        search_btn.pack(fill=tk.X, ipady=8)
    
    def load_available_buildings(self):
        """Load list of available buildings"""
        self.loading_label.pack(pady=20)
        self.root.update()
        
        try:
            buildings = self.building_manager.get_available_buildings()
            if buildings:
                self.show_building_selection()
                self.populate_building_buttons(buildings)
            else:
                self.info_label.config(text="No buildings found in bygninger folder")
        except Exception as e:
            self.info_label.config(text=f"Error loading buildings: {str(e)}")
        finally:
            self.loading_label.pack_forget()
    
    def populate_building_buttons(self, buildings):
        """Create buttons for each available building"""
        # Clear existing buttons
        for widget in self.buildings_container.winfo_children():
            widget.destroy()
            
        for building in buildings:
            # Container for building button and config button
            building_container = tk.Frame(self.buildings_container, bg='#f8f9fa')
            building_container.pack(fill=tk.X, pady=5)
            
            # Main building button
            btn = ttk.Button(building_container,
                            text=building.title(),
                            style='Search.TButton',
                            command=lambda b=building: self.select_building(b))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
            
            # Configuration button
            config_btn = ttk.Button(building_container,
                                   text="⚙️",
                                   width=3,
                                   command=lambda b=building: self.open_config_window(b))
            config_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def select_building(self, building_name):
        """Select and load a specific building"""
        self.loading_label.config(text=f"Loading {building_name}...")
        self.loading_label.pack(pady=20)
        self.root.update()
        
        try:
            success = self.building_manager.load_building_floors(building_name)
            if success:
                self.subtitle_label.config(text=building_name.title())
                self.show_search_interface()
                self.info_label.config(text="Ready to search! Enter a room number above.")
            else:
                self.info_label.config(text=f"Error loading {building_name}. Check PDF files.")
        except Exception as e:
            self.info_label.config(text=f"Error: {str(e)}")
        finally:
            self.loading_label.pack_forget()
    
    def show_building_selection(self):
        """Show building selection screen"""
        self.current_screen = "building_selection"
        self.search_frame.pack_forget()
        self.building_frame.pack(fill=tk.BOTH, expand=True)
        self.subtitle_label.config(text="Vælg bygning")
        
    def show_search_interface(self):
        """Show room search screen"""
        self.current_screen = "room_search"
        self.building_frame.pack_forget()
        self.search_frame.pack(fill=tk.BOTH, expand=True)
    
    def search_room(self):
        """Search for a room and display results"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a room number")
            return
        
        # Show loading
        self.info_label.config(text="Searching...")
        self.root.update()
        
        try:
            # Search for room
            result = self.building_manager.search_room(query)
            
            if not result:
                self.info_label.config(text=f'Room "{query}" not found')
                self.image_label.config(image='')
                self.current_floor_image = None
                return
            
            # Get room and floor info
            room = result['room']
            floor_name = result['floor']
            parser = result['parser']
            
            # Find nearest entrance
            nearest_entrance = self.building_manager.get_nearest_entrance(room['x'], room['y'])
            
            # Update info
            entrance_text = ""
            if nearest_entrance:
                entrance_text = " • Orange prik viser nærmeste indgang"
            
            self.info_label.config(text=f'Found "{room["id"]}" on {floor_name}{entrance_text}')
            
            # Render PDF with markers
            self.render_pdf_with_markers(parser, room, nearest_entrance)
            
            self.current_result = result
            
        except Exception as e:
            self.info_label.config(text=f"Error searching: {str(e)}")
            print(f"Search error: {e}")
    
    def render_pdf_with_markers(self, parser, room, entrance=None):
        """Render PDF page with room and entrance markers"""
        try:
            print(f"Rendering PDF with room at ({room['x']:.3f}, {room['y']:.3f})")
            if entrance:
                print(f"  and entrance at ({entrance['x']:.3f}, {entrance['y']:.3f})")
                
            # Render PDF as image with safe scaling
            pdf_image = parser.render_pdf_as_image(scale=1.5)
            if not pdf_image:
                self.info_label.config(text="Error rendering PDF")
                print("Failed to render PDF as image")
                return
            
            # Get image dimensions
            img_width, img_height = pdf_image.size
            
            # Calculate scale to fit in display area (maintaining aspect ratio)
            display_width = 335  # iPhone width minus padding
            display_height = 400  # Available height for image
            
            scale_x = display_width / img_width
            scale_y = display_height / img_height
            self.scale_factor = min(scale_x, scale_y)
            
            # Resize image
            new_width = int(img_width * self.scale_factor)
            new_height = int(img_height * self.scale_factor)
            pdf_image = pdf_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create drawing context
            draw = ImageDraw.Draw(pdf_image)
            
            # Draw room marker (green circle)
            room_x = room['x'] * new_width
            room_y = room['y'] * new_height
            marker_size = 8
            
            draw.ellipse([room_x - marker_size, room_y - marker_size,
                         room_x + marker_size, room_y + marker_size],
                        fill='#4CAF50', outline='#2E7D32', width=2)
            
            # Draw entrance marker (orange circle)
            if entrance:
                entrance_x = entrance['x'] * new_width
                entrance_y = entrance['y'] * new_height
                
                draw.ellipse([entrance_x - marker_size, entrance_y - marker_size,
                             entrance_x + marker_size, entrance_y + marker_size],
                            fill='#FF9800', outline='#F57C00', width=2)
            
            # Convert to PhotoImage for tkinter
            self.current_floor_image = ImageTk.PhotoImage(pdf_image)
            self.image_label.config(image=self.current_floor_image)
            
        except Exception as e:
            self.info_label.config(text=f"Error rendering image: {str(e)}")
            print(f"Render error: {e}")
    
    def open_config_window(self, building_name):
        """Open configuration window for a building"""
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.destroy()
        
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title(f"Konfiguration - {building_name}")
        self.config_window.geometry("600x700")
        self.config_window.configure(bg='#f8f9fa')
        
        # Load current config
        config = self.config_manager.load_config(building_name)
        
        # Create configuration interface
        self.create_config_interface(self.config_window, config)
    
    def create_config_interface(self, parent, config):
        """Create configuration interface"""
        # Main scroll frame
        canvas = tk.Canvas(parent, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header = tk.Label(scrollable_frame, text=f"Konfiguration for {config.building_name}",
                         font=('SF Pro Display', 18, 'bold'), bg='#f8f9fa', fg='#1c1c1e')
        header.pack(pady=20)
        
        # Font Size Ranges
        font_frame = ttk.LabelFrame(scrollable_frame, text="Font Størrelser", padding=10)
        font_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.font_ranges = []
        for i, font_range in enumerate(config.font_size_ranges):
            range_frame = tk.Frame(font_frame, bg='white')
            range_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(range_frame, text=f"Range {i+1}:", bg='white').pack(side=tk.LEFT)
            
            min_var = tk.DoubleVar(value=font_range.min_size)
            max_var = tk.DoubleVar(value=font_range.max_size)
            
            tk.Label(range_frame, text="Min:", bg='white').pack(side=tk.LEFT, padx=(10, 0))
            tk.Entry(range_frame, textvariable=min_var, width=8).pack(side=tk.LEFT, padx=5)
            
            tk.Label(range_frame, text="Max:", bg='white').pack(side=tk.LEFT, padx=(10, 0))
            tk.Entry(range_frame, textvariable=max_var, width=8).pack(side=tk.LEFT, padx=5)
            
            self.font_ranges.append((min_var, max_var))
        
        # Add font range button
        ttk.Button(font_frame, text="Tilføj Font Range", 
                  command=lambda: self.add_font_range(font_frame)).pack(pady=5)
        
        # Room Patterns
        patterns_frame = ttk.LabelFrame(scrollable_frame, text="Lokale Mønstre", padding=10)
        patterns_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.pattern_vars = []
        for pattern in config.room_patterns:
            pattern_frame = tk.Frame(patterns_frame, bg='white', relief=tk.RIDGE, bd=1)
            pattern_frame.pack(fill=tk.X, pady=2, padx=5)
            
            enabled_var = tk.BooleanVar(value=pattern.enabled)
            pattern_var = tk.StringVar(value=pattern.pattern)
            desc_var = tk.StringVar(value=pattern.description)
            
            tk.Checkbutton(pattern_frame, variable=enabled_var, bg='white').pack(side=tk.LEFT, padx=5)
            tk.Entry(pattern_frame, textvariable=pattern_var, width=25).pack(side=tk.LEFT, padx=5)
            tk.Entry(pattern_frame, textvariable=desc_var, width=20).pack(side=tk.LEFT, padx=5)
            
            self.pattern_vars.append((enabled_var, pattern_var, desc_var))
        
        # Entrance Keywords
        entrance_frame = ttk.LabelFrame(scrollable_frame, text="Indgangs Nøgleord", padding=10)
        entrance_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.entrance_var = tk.StringVar(value=", ".join(config.entrance_keywords))
        tk.Entry(entrance_frame, textvariable=self.entrance_var, width=50).pack(fill=tk.X)
        tk.Label(entrance_frame, text="Adskil med kommaer", font=('Arial', 10), 
                fg='#666').pack(anchor=tk.W)
        
        # Other Settings
        other_frame = ttk.LabelFrame(scrollable_frame, text="Andre Indstillinger", padding=10)
        other_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.min_length_var = tk.IntVar(value=config.min_text_length)
        self.max_length_var = tk.IntVar(value=config.max_text_length)
        self.case_sensitive_var = tk.BooleanVar(value=config.case_sensitive)
        
        tk.Label(other_frame, text="Min tekstlængde:").grid(row=0, column=0, sticky=tk.W, pady=2)
        tk.Entry(other_frame, textvariable=self.min_length_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        tk.Label(other_frame, text="Max tekstlængde:").grid(row=1, column=0, sticky=tk.W, pady=2)
        tk.Entry(other_frame, textvariable=self.max_length_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        tk.Checkbutton(other_frame, text="Store/små bogstaver vigtigt", 
                      variable=self.case_sensitive_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = tk.Frame(scrollable_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Button(button_frame, text="Gem Konfiguration", 
                  command=lambda: self.save_config(config.building_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Nulstil til Standard", 
                  command=lambda: self.reset_config(config.building_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Konfiguration", 
                  command=lambda: self.test_config(config.building_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Debug Tekst", 
                  command=lambda: self.debug_pdf_text(config.building_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Luk", 
                  command=self.config_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store config reference
        self.current_config = config
    
    def add_font_range(self, parent):
        """Add new font range"""
        range_frame = tk.Frame(parent, bg='white')
        range_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(range_frame, text=f"Range {len(self.font_ranges)+1}:", bg='white').pack(side=tk.LEFT)
        
        min_var = tk.DoubleVar(value=1.0)
        max_var = tk.DoubleVar(value=10.0)
        
        tk.Label(range_frame, text="Min:", bg='white').pack(side=tk.LEFT, padx=(10, 0))
        tk.Entry(range_frame, textvariable=min_var, width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Label(range_frame, text="Max:", bg='white').pack(side=tk.LEFT, padx=(10, 0))
        tk.Entry(range_frame, textvariable=max_var, width=8).pack(side=tk.LEFT, padx=5)
        
        self.font_ranges.append((min_var, max_var))
    
    def save_config(self, building_name):
        """Save current configuration"""
        try:
            # Build font ranges
            font_ranges = []
            for min_var, max_var in self.font_ranges:
                if min_var.get() < max_var.get():
                    font_ranges.append(FontSizeRange(min_var.get(), max_var.get()))
            
            # Build room patterns
            room_patterns = []
            for enabled_var, pattern_var, desc_var in self.pattern_vars:
                if pattern_var.get().strip():
                    room_patterns.append(RoomPattern(
                        pattern_var.get().strip(),
                        desc_var.get().strip(),
                        enabled_var.get()
                    ))
            
            # Build entrance keywords
            entrance_keywords = [kw.strip() for kw in self.entrance_var.get().split(',') if kw.strip()]
            
            # Create new config
            new_config = BuildingConfig(
                building_name=building_name,
                font_size_ranges=font_ranges,
                room_patterns=room_patterns,
                entrance_keywords=entrance_keywords,
                exclude_patterns=self.current_config.exclude_patterns,  # Keep existing exclude patterns
                min_text_length=self.min_length_var.get(),
                max_text_length=self.max_length_var.get(),
                case_sensitive=self.case_sensitive_var.get()
            )
            
            # Save config
            self.config_manager.save_config(new_config)
            
            # If this building is currently loaded, ask if user wants to reload it
            if (self.building_manager.current_building == building_name and
                messagebox.askyesno("Genindlæs bygning", 
                                  f"Vil du genindlæse {building_name} med den nye konfiguration?")):
                self.building_manager.load_building_floors(building_name)
                self.info_label.config(text=f"Bygning {building_name} genindlæst med ny konfiguration")
            
            messagebox.showinfo("Succes", f"Konfiguration gemt for {building_name}")
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke gemme konfiguration: {str(e)}")
    
    def reset_config(self, building_name):
        """Reset to default configuration"""
        if messagebox.askyesno("Bekræft", "Nulstil til standard konfiguration?"):
            default_config = self.config_manager.create_default_config(building_name)
            self.config_manager.save_config(default_config)
            self.config_window.destroy()
            self.open_config_window(building_name)
    
    def test_config(self, building_name):
        """Test current configuration by scanning building PDFs"""
        try:
            # Save current config first
            self.save_config(building_name)
            
            # Create a test window
            test_window = tk.Toplevel(self.config_window)
            test_window.title(f"Test Resultater - {building_name}")
            test_window.geometry("600x500")
            test_window.configure(bg='#f8f9fa')
            
            # Text area for results
            text_area = scrolledtext.ScrolledText(test_window, wrap=tk.WORD, 
                                                 font=('Courier New', 10),
                                                 bg='white', fg='black')
            text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Show loading message
            text_area.insert(tk.END, f"Tester konfiguration for {building_name}...\n\n")
            test_window.update()
            
            # Test the configuration
            building_path = os.path.join(self.building_manager.buildings_base_path, building_name)
            if os.path.exists(building_path):
                # Load config and test on PDFs
                config = self.config_manager.load_config(building_name)
                pdf_files = [f for f in os.listdir(building_path) if f.endswith('.pdf')]
                
                total_rooms = 0
                total_entrances = 0
                
                for pdf_file in pdf_files:
                    pdf_path = os.path.join(building_path, pdf_file)
                    floor_name = os.path.splitext(pdf_file)[0]
                    
                    text_area.insert(tk.END, f"Tester {floor_name}:\n")
                    text_area.update()
                    
                    # Create parser with config
                    from pdf_parser import PDFParser
                    parser = PDFParser(pdf_path, config)
                    
                    if parser.load_pdf():
                        rooms, entrances = parser.extract_text_with_coordinates()
                        
                        text_area.insert(tk.END, f"  Fundet {len(rooms)} lokaler\n")
                        text_area.insert(tk.END, f"  Fundet {len(entrances)} indgange\n")
                        
                        # Show some example rooms
                        if rooms:
                            text_area.insert(tk.END, "  Eksempler på fundne lokaler:\n")
                            for i, room in enumerate(rooms[:5]):  # Show first 5
                                text_area.insert(tk.END, f"    - {room['id']} (font: {room['font_size']:.1f})\n")
                            if len(rooms) > 5:
                                text_area.insert(tk.END, f"    ... og {len(rooms)-5} mere\n")
                        
                        total_rooms += len(rooms)
                        total_entrances += len(entrances)
                        
                        text_area.insert(tk.END, "\n")
                        text_area.update()
                    else:
                        text_area.insert(tk.END, f"  Fejl ved indlæsning af PDF\n\n")
                    
                    parser.close()
                
                text_area.insert(tk.END, f"\nSamlet resultat:\n")
                text_area.insert(tk.END, f"  Total lokaler: {total_rooms}\n")
                text_area.insert(tk.END, f"  Total indgange: {total_entrances}\n\n")
                text_area.insert(tk.END, "Test fuldført! Du kan nu justere konfigurationen efter behov.")
                
            else:
                text_area.insert(tk.END, f"Fejl: Kan ikke finde bygning {building_name}")
                
        except Exception as e:
            messagebox.showerror("Test Fejl", f"Kunne ikke teste konfiguration: {str(e)}")
    
    def debug_pdf_text(self, building_name):
        """Advanced debug window with search functionality to analyze PDF text and font sizes"""
        if not self.building_manager.current_building or self.building_manager.current_building != building_name:
            messagebox.showwarning("Advarsel", "Indlæs bygningen først")
            return
        
        # Create debug window
        debug_window = tk.Toplevel(self.root)
        debug_window.title(f"Debug Tekst - {building_name}")
        debug_window.geometry("900x700")
        debug_window.configure(bg='#f8f9fa')
        
        # Search frame
        search_frame = tk.Frame(debug_window, bg='#f8f9fa')
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="🔍 Søg efter tekst:", bg='#f8f9fa', font=('Arial', 12)).pack(side=tk.LEFT)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=('Arial', 12), width=30)
        search_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        # Search results frame
        results_frame = tk.Frame(debug_window, bg='#f8f9fa')
        results_frame.pack(fill=tk.X, padx=20, pady=5)
        
        search_results_label = tk.Label(results_frame, text="", bg='#f8f9fa', font=('Arial', 10, 'italic'))
        search_results_label.pack(side=tk.LEFT)
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(debug_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
            
        
        # Store all text entries for searching
        all_text_entries = []
        
        def collect_all_text():
            """Collect all text from all floors for searching"""
            import fitz
            
            # Import OCR check function
            from pdf_parser import check_ocr_availability
            
            all_entries = []
            
            for floor_name, parser in self.building_manager.floors.items():
                if not parser.doc:
                    continue
                    
                try:
                    page = parser.doc[0]
                    page_rect = page.rect
                    text_dict = page.get_text("dict")
                    
                    # Calculate scale factor
                    reference_size = 595 * 842
                    actual_size = page_rect.width * page_rect.height
                    size_scale_factor = (actual_size / reference_size) ** 0.5
                    
                    has_normal_text = False
                    
                    # Get normal text
                    for block in text_dict.get("blocks", []):
                        if "lines" not in block:
                            continue
                            
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if not text:
                                    continue
                                    
                                has_normal_text = True
                                font_size = span["size"]
                                bbox = span["bbox"]
                                normalized_font_size = font_size / size_scale_factor
                                
                                # Calculate position
                                center_x = (bbox[0] + bbox[2]) / 2
                                center_y = (bbox[1] + bbox[3]) / 2
                                norm_x = center_x / page_rect.width
                                norm_y = center_y / page_rect.height
                                
                                all_entries.append({
                                    'text': text,
                                    'floor': floor_name,
                                    'font_size': font_size,
                                    'normalized_font_size': normalized_font_size,
                                    'position': f"({norm_x:.3f}, {norm_y:.3f})",
                                    'bbox': bbox,
                                    'source': 'PDF',
                                    'confidence': 1.0
                                })
                    
                    # If no normal text found, try OCR
                    if not has_normal_text and check_ocr_availability():
                        try:
                            import easyocr
                            import cv2
                            import numpy as np
                            
                            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                            
                            # Try OCR at scale 2.0
                            mat = fitz.Matrix(2.0, 2.0)
                            pix = page.get_pixmap(matrix=mat)
                            img_data = pix.tobytes("png")
                            img_array = np.frombuffer(img_data, dtype=np.uint8)
                            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                            
                            if img is not None:
                                results = reader.readtext(img)
                                
                                for (bbox, text, confidence) in results:
                                    if confidence < 0.1:  # Very low threshold for debug
                                        continue
                                        
                                    text_clean = text.strip()
                                    if not text_clean:
                                        continue
                                    
                                    # Calculate position
                                    bbox_array = np.array(bbox)
                                    center_x = np.mean(bbox_array[:, 0]) / (page_rect.width * 2.0)
                                    center_y = np.mean(bbox_array[:, 1]) / (page_rect.height * 2.0)
                                    
                                    # Estimate font size
                                    bbox_height = np.max(bbox_array[:, 1]) - np.min(bbox_array[:, 1])
                                    font_size = bbox_height / 2.0
                                    
                                    all_entries.append({
                                        'text': text_clean,
                                        'floor': floor_name,
                                        'font_size': font_size,
                                        'normalized_font_size': font_size,
                                        'position': f"({center_x:.3f}, {center_y:.3f})",
                                        'bbox': bbox,
                                        'source': 'OCR',
                                        'confidence': confidence
                                    })
                        except Exception as ocr_error:
                            print(f"OCR failed for {floor_name}: {ocr_error}")
                            
                except Exception as e:
                    print(f"Error collecting text from {floor_name}: {e}")
                    
            return all_entries
        
        def update_display(entries_to_show=None):
            """Update the text display"""
            text_widget.delete(1.0, tk.END)
            
            if entries_to_show is None:
                entries_to_show = all_text_entries
            
            if not entries_to_show:
                text_widget.insert(tk.END, "Ingen tekst fundet i PDF'erne.\n\n")
                try:
                    from pdf_parser import check_ocr_availability
                    if not check_ocr_availability():
                        text_widget.insert(tk.END, "💡 Tip: Installer EasyOCR for at læse billedbaserede PDF'er:\n")
                        text_widget.insert(tk.END, "pip install easyocr opencv-python\n")
                except:
                    pass
                return
            
            # Group by floor
            floors = {}
            for entry in entries_to_show:
                floor = entry['floor']
                if floor not in floors:
                    floors[floor] = []
                floors[floor].append(entry)
            
            # Display by floor
            for floor_name, entries in floors.items():
                text_widget.insert(tk.END, f"\n{'='*60}\n")
                text_widget.insert(tk.END, f"📄 {floor_name.upper()}\n")
                text_widget.insert(tk.END, f"{'='*60}\n\n")
                
                # Sort entries by font size (descending)
                entries.sort(key=lambda x: x['font_size'], reverse=True)
                
                for entry in entries:
                    # Color code based on source
                    if entry['source'] == 'OCR':
                        prefix = "🤖 [OCR]"
                    else:
                        prefix = "📝 [PDF]"
                    
                    confidence_str = f" (conf: {entry['confidence']:.2f})" if entry['confidence'] < 1.0 else ""
                    
                    text_widget.insert(tk.END, f"{prefix} '{entry['text']}'{confidence_str}\n")
                    text_widget.insert(tk.END, f"    📏 Font størrelse: {entry['font_size']:.2f}\n")
                    text_widget.insert(tk.END, f"    📐 Normaliseret: {entry['normalized_font_size']:.2f}\n")
                    text_widget.insert(tk.END, f"    📍 Position: {entry['position']}\n")
                    text_widget.insert(tk.END, f"    🏠 Etage: {entry['floor']}\n\n")
        
        def search_text():
            """Search for specific text"""
            query = search_var.get().strip().lower()
            
            if not query:
                # Show all entries if no search query
                update_display()
                search_results_label.config(text="Viser alle tekstforekomster")
                return
            
            # Filter entries that contain the search query
            matching_entries = []
            for entry in all_text_entries:
                if query in entry['text'].lower():
                    matching_entries.append(entry)
            
            update_display(matching_entries)
            
            if matching_entries:
                search_results_label.config(text=f"Fundet {len(matching_entries)} match(es) for '{query}'")
                
                # Show font size statistics for matches
                if len(matching_entries) > 0:
                    font_sizes = [entry['font_size'] for entry in matching_entries]
                    min_font = min(font_sizes)
                    max_font = max(font_sizes)
                    avg_font = sum(font_sizes) / len(font_sizes)
                    
                    stats_text = f"\n📊 STATISTIK FOR '{query}':\n"
                    stats_text += f"{'='*40}\n"
                    stats_text += f"Antal forekomster: {len(matching_entries)}\n"
                    stats_text += f"Font størrelse range: {min_font:.2f} - {max_font:.2f}\n"
                    stats_text += f"Gennemsnitlig font størrelse: {avg_font:.2f}\n"
                    stats_text += f"Foreslået range: {min_font-0.2:.2f} - {max_font+0.2:.2f}\n"
                    stats_text += f"{'='*40}\n\n"
                    
                    text_widget.insert(1.0, stats_text)
            else:
                search_results_label.config(text=f"Ingen matches fundet for '{query}'")
        
        # Bind search to Enter key and real-time search
        def on_search_change(*args):
            search_text()
        
        search_var.trace('w', on_search_change)
        search_entry.bind('<Return>', lambda e: search_text())
        
        # Add search button
        search_button = tk.Button(search_frame, text="🔍 Søg", command=search_text, 
                                 bg='#007AFF', fg='white', font=('Arial', 10))
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Add clear button
        def clear_search():
            search_var.set("")
            search_text()
        
        clear_button = tk.Button(search_frame, text="❌ Ryd", command=clear_search,
                               bg='#FF3B30', fg='white', font=('Arial', 10))
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Add export button
        def export_results():
            """Export current results to text file"""
            try:
                import datetime
                current_content = text_widget.get(1.0, tk.END)
                filename = f"debug_{building_name}_{search_var.get() or 'all'}.txt".replace(" ", "_")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Debug rapport for {building_name}\n")
                    f.write(f"Søgeterm: '{search_var.get() or 'alle'}'\n")
                    f.write(f"Genereret: {datetime.datetime.now()}\n")
                    f.write("="*80 + "\n\n")
                    f.write(current_content)
                
                messagebox.showinfo("Eksporteret", f"Rapport gemt som {filename}")
            except Exception as e:
                messagebox.showerror("Fejl", f"Kunne ikke eksportere: {e}")
        
        export_button = tk.Button(search_frame, text="💾 Eksporter", command=export_results,
                                bg='#34C759', fg='white', font=('Arial', 10))
        export_button.pack(side=tk.RIGHT, padx=5)
        
        # Load and display all text
        try:
            text_widget.insert(tk.END, "📋 Indlæser al tekst fra PDF'erne...\n")
            text_widget.update()
            
            all_text_entries = collect_all_text()
            update_display()
            
            search_results_label.config(text=f"Fundet {len(all_text_entries)} tekstforekomster i alt")
            
            # Focus on search entry
            search_entry.focus()
            
        except Exception as e:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"❌ Fejl ved indlæsning af tekst: {e}\n")
            messagebox.showerror("Fejl", f"Kunne ikke indlæse tekst: {e}")
    
    def on_closing(self):
        """Clean up when closing app"""
        try:
            self.building_manager.close_all()
            if self.config_window and self.config_window.winfo_exists():
                self.config_window.destroy()
        except:
            pass
        self.root.destroy()


def main():
    """Main application entry point"""
    root = tk.Tk()
    
    try:
        app = BuildingNavigationApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except ImportError as e:
        error_msg = f"Required Python packages are missing:\n{str(e)}\n\n"
        error_msg += "Please install requirements:\n"
        error_msg += "pip install PyMuPDF Pillow\n\n"
        error_msg += "For OCR support (image-based PDFs):\n"
        error_msg += "pip install pytesseract opencv-python numpy"
        
        messagebox.showerror("Missing Dependencies", error_msg)
    except Exception as e:
        messagebox.showerror("Application Error", f"An error occurred:\n{str(e)}")


if __name__ == "__main__":
    main()
