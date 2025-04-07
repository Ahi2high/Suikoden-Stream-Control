import tkinter as tk
from tkinter import ttk
from party_tab import PartyTab
from stars_tab import StarsTab
from recruitment_tab import RecruitmentTab
import os
import json
from PIL import Image, ImageTk
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Suikoden I Stream Control")
        self.image_folder = "images"
        # Set up window size and properties
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # Load background image
        self.bg_image = Image.open("background.jpeg")
        self.bg_photo = None
        
        # Create canvas for background
        self.bg_canvas = tk.Canvas(self)
        self.bg_canvas.pack(fill="both", expand=True)
        
        # Add reference to background image to prevent garbage collection
        self.bg_canvas.image = None
        
        # Bind resize event
        self.bind("<Configure>", self._resize_background)
        
        # Load data
        self.all_characters = self._load_data("characters.json")
        self.recruitment_info = self._load_data("recruitment.json")
        
        # Set up ttk styles
        self._setup_styles()
        
        # Create notebook and tabs
        self._create_notebook()
        
        # Initial background resize
        # Initial background resize
        self._resize_background(None)

    def update_value(self):
        new_value = self.entry.get() if hasattr(self, 'entry') else ""
        print(f"Value updated: {new_value}")
        # If you need to make HTTP requests, import requests at the top
        # and uncomment the following line:
        # requests.get(f'http://127.0.0.1:5000/update/{new_value}')

    def _load_data(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {filename} not found. Please create this file.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {filename}. Check the file format.")
            return {}

    def _setup_styles(self):
        """Set up ttk styles for the application"""
        self.style = ttk.Style()
        
        # Set up a theme with dark colors
        bg_dark = "#000000"  # Black background
        bg_medium = "#000000"  # Black background
        accent_color = "#e94560"  # Red accent
        text_light = "#0050b8"  # Light text color
        button_bg = "#002421"  # Dark gray for buttons
        
        # Configure notebook style
        self.style.configure("TNotebook", 
                             background=bg_dark, 
                             borderwidth=0)
        self.style.configure("TNotebook.Tab", 
                             background="#333333",  # Dark gray for tabs 
                             foreground=text_light, 
                             padding=[10, 10], 
                             font=('Arial', 15, 'bold'))
        self.style.map("TNotebook.Tab", 
                       background=[("selected", accent_color), ("active", "#c23a54")],
                       foreground=[("selected", text_light), ("active", text_light)])
        
        # Configure frame styles with semi-transparent background
        self.style.configure("Suikoden.TFrame", 
                             background=bg_medium)
        
        # Configure button styles
        self.style.configure("Suikoden.TButton", 
                             foreground=text_light, 
                             background=button_bg,  # Dark gray for buttons
                             font=('Arial', 9, 'bold'))
        self.style.map("Suikoden.TButton", 
                       background=[("active", accent_color)],
                       foreground=[("active", text_light)],
                       relief=[("pressed", "sunken")])
        
        # Recruited button style
        self.style.configure("Recruited.TButton", 
                             foreground=text_light, 
                             background="#2a6041",  # Dark green 
                             font=('Arial', 9, 'bold'))
        self.style.map("Recruited.TButton", 
                       background=[("active", "#3a8157")],  # Lighter green
                       foreground=[("active", text_light)])
        
        # Label styles
        self.style.configure("Suikoden.TLabel", 
                            background=bg_medium,  # Black background
                            foreground=text_light,
                            font=('Arial', 10))
        
        # Labelframe styles
        self.style.configure("Suikoden.TLabelframe", 
                           background=bg_medium)
        self.style.configure("Suikoden.TLabelframe.Label", 
                           foreground=text_light,
                           background=bg_medium,
                           font=('Arial', 12, 'bold'))
        
        # Create a custom style for treeviews
        self.style.configure("Suikoden.Treeview", 
                           background="#111111",  # Slightly lighter black for treeview
                           foreground=text_light,
                           fieldbackground="#111111",
                           rowheight=25)
        self.style.map("Suikoden.Treeview",
                      background=[("selected", accent_color)],
                      foreground=[("selected", text_light)])

    def _resize_background(self, event):
        """Resize background image to fit window"""
        if event:
            width, height = event.width, event.height
        else:
            width, height = self.winfo_width(), self.winfo_height()
            
        if width > 1 and height > 1:  # Avoid invalid sizes
            # Resize image to fit window
            resized_img = self.bg_image.resize((width, height))
            self.bg_photo = ImageTk.PhotoImage(resized_img)
            
            # Update canvas with new image
            self.bg_canvas.delete("all")
            self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            self.bg_canvas.image = self.bg_photo

    def _create_notebook(self):
        """Create and configure the notebook and tabs"""
        # Create notebook with custom styling
        self.notebook = ttk.Notebook(self.bg_canvas, style="TNotebook")
        self.notebook.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        # Create tabs without bg_color parameter
        party_tab = PartyTab(self.notebook, self.image_folder, self.all_characters)
        self.notebook.add(party_tab, text="Party")

        stars_tab = StarsTab(self.notebook, self.image_folder, self.all_characters)
        self.notebook.add(stars_tab, text="108 Stars")

        recruitment_tab = RecruitmentTab(self.notebook, self.recruitment_info)
        self.notebook.add(recruitment_tab, text="Recruitment")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
