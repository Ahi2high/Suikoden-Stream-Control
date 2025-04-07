import tkinter as tk
from tkinter import ttk, Toplevel
import os
from PIL import Image, ImageTk

class RecruitmentTab(ttk.Frame):
    def __init__(self, parent, recruitment_info, image_folder="Images"):
        super().__init__(parent, style="Suikoden.TFrame")
        self.recruitment_info = recruitment_info
        self.image_folder = image_folder
        self.character_images = {}  # Store image references to prevent garbage collection
        self.char_name_positions = {}  # Store positions of character names in text widget
        self._create_widgets()

    def _create_widgets(self):
        # Define colors to match the Suikoden style
        bg_dark = "#000000"    # Black background (was darker blue)
        bg_medium = "#000000"  # Black background (was medium blue)
        text_light = "#f1f1f1" # Match the light text color from main.py
        accent_color = "#e94560" # Red accent color from main.py
        
        # Create a main frame with padding
        main_frame = ttk.Frame(self, style="Suikoden.TFrame")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create a title frame
        title_frame = ttk.Frame(main_frame, style="Suikoden.TFrame")
        title_frame.pack(fill="x", pady=(0, 10))
        
        # Add a title label
        title_label = ttk.Label(
            title_frame, 
            text="RECRUITMENT INFORMATION", 
            style="Suikoden.TLabel",
            background=bg_medium,
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=5)
        
        # Add subtitle
        subtitle_label = ttk.Label(
            title_frame,
            text="How to recruit the 108 Stars of Destiny",
            style="Suikoden.TLabel",
            background=bg_medium,
            font=('Arial', 10, 'italic')
        )
        subtitle_label.pack(pady=5)
        
        # Create a hint label
        hint_label = ttk.Label(
            title_frame,
            text="Click on a character name to view their image",
            style="Suikoden.TLabel",
            background=bg_medium,
            font=('Arial', 8, 'italic'),
            foreground="#999999"
        )
        hint_label.pack(pady=(0, 5))
        
        # Create a frame for the text area and scrollbar
        text_frame = ttk.Frame(main_frame, style="Suikoden.TFrame")
        text_frame.pack(fill="both", expand=True)
        
        # Create a styled scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        
        # Create the text area with improved styling
        self.text_area = tk.Text(
            text_frame, 
            yscrollcommand=scrollbar.set, 
            wrap="word", 
            background=bg_medium,
            foreground=text_light,
            font=('Arial', 10),
            padx=15,
            pady=15,
            borderwidth=0,
            highlightthickness=0,
            insertbackground=text_light,  # Cursor color
            cursor="hand2"  # Use hand cursor to indicate clickable text
        )
        
        # Configure the scrollbar
        scrollbar.config(command=self.text_area.yview)
        
        # Pack the widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Configure text tags for different styling
        self.text_area.tag_configure("header", font=('Arial', 12, 'bold'), foreground="#ffffff")
        self.text_area.tag_configure("char_name", font=('Arial', 10, 'bold'), foreground=accent_color)
        self.text_area.tag_configure("method", font=('Arial', 10), foreground=text_light)
        self.text_area.tag_configure("category", font=('Arial', 11, 'bold'), foreground="#4ade80")
        
        # Add binding for clicking on character names
        self.text_area.tag_bind("char_name", "<Button-1>", self._on_character_click)
        
        # Fill the text area with character information
        self._populate_text_area()
        
        # Disable editing of the text
        self.text_area.config(state="disabled")
    
    def _populate_text_area(self):
        # Sort characters by name
        sorted_chars = sorted(self.recruitment_info.items())
        
        # Group the characters by initial letter for better organization
        current_letter = None
        
        for name, info in sorted_chars:
            # Check if we need to add a new letter category
            first_letter = name[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                self.text_area.insert(tk.END, f"\n{current_letter}\n", "category")
                self.text_area.insert(tk.END, "─" * 30 + "\n", "category")
            
            # Store the start position of the character name
            start_pos = self.text_area.index("end-1c")
            
            # Add the character name in bold with accent color
            self.text_area.insert(tk.END, f"{name}: ", "char_name")
            
            # Store the end position of the character name
            end_pos = self.text_area.index("end-1c")
            
            # Store the character name positions for click handling
            self.char_name_positions[name] = (start_pos, end_pos, info)
            
            # Add the recruitment method with proper styling
            self.text_area.insert(tk.END, f"{info['recruitment']}\n\n", "method")
    
    def _on_character_click(self, event):
        # Find which character was clicked
        clicked_pos = self.text_area.index(f"@{event.x},{event.y}")
        
        for name, (start_pos, end_pos, info) in self.char_name_positions.items():
            # Check if the clicked position is within this character's name range
            if self.text_area.compare(start_pos, "<=", clicked_pos) and self.text_area.compare(clicked_pos, "<=", end_pos):
                self._show_character_image(name, info)
                break
    
    def _show_character_image(self, name, info):
        # Create a popup window to display the character image
        popup = Toplevel(self)
        popup.title(name)
        popup.geometry("300x350")
        popup.resizable(False, False)
        # Configure the popup window style
        popup.configure(background="#000000")
        
        # Attempt to load and display character image
        try:
            image_path = os.path.join(self.image_folder, info["image"])
            image = Image.open(image_path)
            
            # Resize the image to fit in the popup window
            image = image.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Store reference to prevent garbage collection
            popup.photo = photo
            
            # Create image display
            image_label = ttk.Label(popup, image=photo, background="#000000")
            image_label.pack(pady=20)
            
            # Add character name label
            name_label = ttk.Label(
                popup, 
                text=name,
                foreground="#e94560",
                background="#000000",
                font=('Arial', 14, 'bold')
            )
            name_label.pack(pady=(0, 10))
            
            # Add recruitment info
            info_label = ttk.Label(
                popup, 
                text=info["recruitment"],
                font=('Arial', 10),
                foreground="#f1f1f1",
                background="#000000",
                wraplength=250,
                justify=tk.CENTER
            )
            info_label.pack(pady=10, padx=20)
            
            # Add a close button
            close_button = ttk.Button(
                popup,
                text="Close",
                command=popup.destroy
            )
            close_button.pack(pady=(0, 15))
            
            # Center the popup window on the screen
            popup.update_idletasks()
            width = popup.winfo_width()
            height = popup.winfo_height()
            x = (popup.winfo_screenwidth() // 2) - (width // 2)
            y = (popup.winfo_screenheight() // 2) - (height // 2)
            popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
        except Exception as e:
            # If image loading fails, show an error message
            error_label = ttk.Label(
                popup,
                text=f"Error loading image: {e}",
                font=('Arial', 10),
                foreground="#ff6b6b",
                background="#000000",
                wraplength=250,
                justify=tk.CENTER
            )
            error_label.pack(pady=20)
            
            # Still show character name and recruitment info
            name_label = ttk.Label(
                popup, 
                text=name,
                font=('Arial', 14, 'bold'), 
                foreground="#e94560",
                background="#000000"
            )
            name_label.pack(pady=(0, 10))
            
            info_label = ttk.Label(
                popup, 
                text=info["recruitment"],
                font=('Arial', 10),
                foreground="#f1f1f1",
                background="#000000",
                wraplength=250,
                justify=tk.CENTER
            )
            info_label.pack(pady=10, padx=20)
            
            # Add a close button
            close_button = ttk.Button(
                popup,
                text="Close",
                command=popup.destroy
            )
            close_button.pack(pady=(0, 15))
