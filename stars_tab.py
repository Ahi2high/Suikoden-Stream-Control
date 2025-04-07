import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ScrollableFrame(ttk.Frame):
    """A scrollable frame using canvas and scrollbar"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set, bg="#121b2f")
        
        # Create a frame inside the canvas for content
        self.content_frame = ttk.Frame(self.canvas, style="Suikoden.TFrame")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Pack the widgets
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind events
        self.content_frame.bind("<Configure>", self._configure_content_frame)
        self.canvas.bind("<Configure>", self._configure_canvas)
        
        # Bind mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _configure_content_frame(self, event):
        # Update the canvas's scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _configure_canvas(self, event):
        # Resize the inner frame to fill the canvas
        self.canvas.itemconfigure(self.canvas_frame, width=event.width)
        
    def _on_mousewheel(self, event):
        # Scroll up/down using mousewheel
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
class StarsTab(ttk.Frame):
    def __init__(self, parent, image_folder, all_characters):
        super().__init__(parent, style="Suikoden.TFrame")
        self.image_folder = image_folder
        self.all_characters = all_characters
        self.all_star_names = sorted(self.all_characters.keys())
        self.recruited_stars = {name: False for name in self.all_star_names}
        self.star_widgets = {}
        
        # Create styles for better visibility
        self.style = ttk.Style()
        # Style for star frames with semi-transparent background
        self.style.configure("StarFrame.Suikoden.TFrame", background="#16213e")
        
        # Style for star name labels
        self.style.configure("StarName.Suikoden.TLabel", 
                             foreground="white",
                             background="#16213e",
                             font=("Arial", 10))
                             
        # Style for recruited stars
        self.style.configure("Recruited.Suikoden.TLabel", 
                             foreground="#4ade80",  # Light green for recruited
                             background="#16213e",
                             font=("Arial", 10, "bold"))
        
        self._create_widgets()

    def _create_widgets(self):
        # Create a scrollable frame
        self.scrollable = ScrollableFrame(self)
        self.scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a title label
        title_frame = ttk.Frame(self.scrollable.content_frame, style="Suikoden.TFrame")
        title_frame.grid(row=0, column=0, columnspan=6, sticky="ew", padx=10, pady=10)
        
        title_label = ttk.Label(title_frame, text="108 STARS OF DESTINY", 
                               style="Suikoden.TLabel",
                               background="#16213e",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=5)
        
        counter_label = ttk.Label(title_frame, 
                                text="Click on a character's name to mark as recruited",
                                style="Suikoden.TLabel",
                                background="#16213e")
        counter_label.pack(pady=5)
        
        # Create a content frame with grid layout
        columns = 10  # Number of columns in the grid
        row_num = 1  # Start at row 1 (row 0 is for the title)
        col_num = 0
        
        for name in self.all_star_names:
            # Create a frame with semi-transparent background for each star
            frame = ttk.Frame(self.scrollable.content_frame, style="StarFrame.Suikoden.TFrame")
            frame.grid(row=row_num, column=col_num, padx=8, pady=8, sticky="nsew")
            
            # Add internal frame padding
            inner_frame = ttk.Frame(frame, style="StarFrame.Suikoden.TFrame")
            inner_frame.pack(padx=5, pady=5, fill="both", expand=True)
            
            # Load and display character image
            image_path = os.path.join(self.image_folder, self.all_characters[name])
            try:
                img = Image.open(image_path)
                img = img.resize((80, 80))
                img_tk = ImageTk.PhotoImage(img)
                label = ttk.Label(inner_frame, image=img_tk, style="Suikoden.TLabel", background="#16213e")
                label.image = img_tk
                label.pack(pady=(0, 5))
            except FileNotFoundError:
                error_label = ttk.Label(inner_frame, text="?", style="Suikoden.TLabel", background="#16213e")
                error_label.pack(pady=(0, 5))

            # Create a name label with better visibility
            name_label = ttk.Label(inner_frame, text=name, 
                                  style="StarName.Suikoden.TLabel", 
                                  cursor="hand2",
                                  wraplength=120)  # Wrap long names
            name_label.pack(fill="x", pady=2)
            name_label.bind("<Button-1>", lambda event, n=name, l=name_label: self._toggle_star_recruited(n, l))
            self.star_widgets[name] = name_label

            # Configure the column/row layout
            col_num += 1
            if col_num >= columns:
                col_num = 0
                row_num += 1

    def _toggle_star_recruited(self, star_name, name_label):
        """Toggles the recruited status of a star and updates its appearance."""
        self.recruited_stars[star_name] = not self.recruited_stars[star_name]
        if self.recruited_stars[star_name]:
            name_label.config(style="Recruited.Suikoden.TLabel")
        else:
            name_label.config(style="StarName.Suikoden.TLabel")
    def get_recruited_stars(self):
        """Returns the dictionary of recruited stars."""
        return self.recruited_stars