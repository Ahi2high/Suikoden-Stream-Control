import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import random

class PartyTab(ttk.Frame):
    def __init__(self, parent, image_folder, all_characters, bg_color=None):
        super().__init__(parent, style="Suikoden.TFrame")
        self.image_folder = image_folder
        self.all_characters = all_characters
        
        # Process characters to handle roles
        self.character_info = self._process_character_names()
        self.all_star_names = sorted(self.character_info.keys())
        
        self.party_slots = 6
        self.party_members = [None] * self.party_slots
        self.displayed_images = [None] * self.party_slots  # Initialize with None
        
        # Store selected character names to prevent duplicates
        self.selected_character_names = [None] * self.party_slots

        self._create_widgets()

    def _process_character_names(self):
        """Process character names to handle roles and duplicates"""
        character_info = {}
        
        for name, image in self.all_characters.items():
            # Handle characters with role information in parentheses
            display_name = name
            role = None
            
            if "(" in name and ")" in name:
                base_name = name.split("(")[0].strip()
                role = name.split("(")[1].replace(")", "").strip()
                
                # Check if this is a duplicate with role information
                if base_name in self.all_characters:
                    # Skip duplicates that have different roles but same base name and image
                    # We'll show the role in the selection window instead
                    if self.all_characters[base_name] == image:
                        continue
                
                display_name = base_name
                
            # Add to character info dictionary
            if display_name in character_info:
                # If name already exists but role is different, add role
                existing_role = character_info[display_name].get('role')
                if role and existing_role != role:
                    character_info[display_name]['roles'].append(role)
            else:
                character_info[display_name] = {
                    'image': image,
                    'role': role,
                    'roles': [role] if role else []
                }
                
        return character_info
    
    def _create_widgets(self):
        # Title frame
        title_frame = ttk.Frame(self, style="Suikoden.TFrame")
        title_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        # Add title label
        title_label = ttk.Label(
            title_frame, 
            text="SUIKODEN PARTY", 
            style="Suikoden.TLabel",
            background="black",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=5)
        
        # Add subtitle
        subtitle_label = ttk.Label(
            title_frame,
            text="Click on a slot to select a character",
            style="Suikoden.TLabel",
            background="black",
            font=('Arial', 10, 'italic')
        )
        subtitle_label.pack(pady=5)
        # --- Controls Frame ---
        controls_frame = ttk.Frame(self, style="Suikoden.TFrame")
        controls_frame.pack(pady=10, fill="x")
        
        # --- Random Party Button ---
        random_button = ttk.Button(controls_frame, text="Random Party", 
                                style="Suikoden.TButton", command=self._set_random_party)
        random_button.pack(side=tk.LEFT, padx=20)
        
        # --- Clear Party Button ---
        clear_button = ttk.Button(controls_frame, text="Clear Party", 
                               style="Suikoden.TButton", command=self._clear_party)
        clear_button.pack(side=tk.RIGHT, padx=20)
        
        # --- Party Display Frame ---
        display_frame = ttk.Frame(self, style="Suikoden.TFrame")
        display_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Create frame for party member slots with black background
        party_slots_frame = ttk.Frame(display_frame, style="Suikoden.TFrame")
        party_slots_frame.pack(fill="both", expand=True, pady=10)
        
        # Store slot frames and background images
        self.slot_frames = []
        self.slot_bg_labels = []
        
        for i in range(self.party_slots):
            # Create frame for each party slot with black background
            slot_frame = ttk.Frame(party_slots_frame, style="Suikoden.TFrame", cursor="hand2")
            # Position in a 2x3 grid layout
            row = i // 3
            col = i % 3
            slot_frame.grid(row=row, column=col, padx=15, pady=10)
            self.slot_frames.append(slot_frame)
            
            # Make the entire slot clickable
            slot_frame.bind("<Button-1>", lambda event, idx=i: self._open_selection_window(None, idx))
            
            # Load the rune background from file
            rune_bg_path = os.path.join(self.image_folder, "Rune", f"{i+1}.png")
            try:
                rune_bg = Image.open(rune_bg_path)
                rune_bg = rune_bg.resize((120, 150))
                rune_bg_tk = ImageTk.PhotoImage(rune_bg)
                
                # Create background label
                bg_label = ttk.Label(slot_frame, image=rune_bg_tk, style="Suikoden.TLabel")
                bg_label.image = rune_bg_tk
                bg_label.pack(pady=0)
                bg_label.bind("<Button-1>", lambda event, idx=i: self._open_selection_window(None, idx))
                self.slot_bg_labels.append(bg_label)
            except Exception as e:
                print(f"Error loading rune background {i+1}: {e}")
                # Fallback: create black background
                bg_label = ttk.Label(slot_frame, text=f"Slot {i+1}", 
                                    style="Suikoden.TLabel", 
                                    background="black",
                                    foreground="white",
                                    width=15, height=8)
                bg_label.pack(pady=0)
                bg_label.bind("<Button-1>", lambda event, idx=i: self._open_selection_window(None, idx))
                self.slot_bg_labels.append(bg_label)
            
            # Create placeholder for character image that will overlay on the background
            image_label = ttk.Label(slot_frame, background=None)
            image_label.place(relx=0.5, rely=0.5, anchor="center")
            image_label.bind("<Button-1>", lambda event, idx=i: self._open_selection_window(None, idx))
            self.displayed_images[i] = image_label
            
            # Add slot number label
            slot_label = ttk.Label(slot_frame, text=f"Slot {i+1}", 
                                 style="Suikoden.TLabel",
                                 background="black",
                                 foreground="white")
            slot_label.place(relx=0.5, rely=0.05, anchor="n")
            slot_label.bind("<Button-1>", lambda event, idx=i: self._open_selection_window(None, idx))
            
            # Add name label for character (initially empty)
            name_label = ttk.Label(slot_frame, text="", 
                                 style="Suikoden.TLabel",
                                 background="black",
                                 foreground="#e94560",   # Use accent color for names
                                 font=('Arial', 9, 'bold'))
            name_label.place(relx=0.5, rely=0.85, anchor="s")
            name_label.bind("<Button-1>", lambda event, idx=i: self._open_selection_window(None, idx))
            # Store reference to name label
            setattr(slot_frame, "name_label", name_label)
            
            # Configure grid weights for proper spacing in the 2x3 layout
            if i < 3:  # Only need to configure the 3 columns once
                party_slots_frame.grid_columnconfigure(i, weight=1)
            if i < 2:  # Only need to configure the 2 rows once
                party_slots_frame.grid_rowconfigure(i, weight=1)

    def _set_random_party(self):
        """Sets a random party of 6 from all available characters."""
        available_characters = list(self.character_info.keys())
        if len(available_characters) <= self.party_slots:
            random_party = available_characters
        else:
            random_party = random.sample(available_characters, self.party_slots)

        # Clear current selections
        self.selected_character_names = [None] * self.party_slots
        
        for i in range(self.party_slots):
            if i < len(random_party):
                character_name = random_party[i]
                filename = self.character_info[character_name]['image']
                self.party_members[i] = filename
                self.selected_character_names[i] = character_name
            else:
                self.party_members[i] = None
                self.selected_character_names[i] = None
        self._display_party()
        
    def _clear_party(self):
        """Clears all party member slots."""
        self.party_members = [None] * self.party_slots
        self.selected_character_names = [None] * self.party_slots
        self._display_party()
    def _open_selection_window(self, selected_char=None, slot_index=None):
        """Opens a new window to select a party member for a specific slot."""
        # Create a top-level window
        selection_window = tk.Toplevel(self)
        selection_window.title("Select Party Member")
        selection_window.geometry("500x600")
        selection_window.minsize(400, 500)
        
        # Create a frame with black background for the window
        bg_frame = ttk.Frame(selection_window, style="Suikoden.TFrame")
        bg_frame.pack(fill="both", expand=True)
        
        # Set the background color to black
        selection_window.configure(background="#000000")
        
        # Main content frame
        content_frame = ttk.Frame(bg_frame, style="Suikoden.TFrame")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title label
        slot_text = f"for Slot {slot_index + 1}" if slot_index is not None else ""
        title_label = ttk.Label(content_frame, text=f"Select Character {slot_text}", 
                               style="Suikoden.TLabel", font=('Arial', 14, 'bold'), background="black")
        title_label.pack(pady=(10, 15))
        
        # Frame for search functionality
        search_frame = ttk.Frame(content_frame, style="Suikoden.TFrame")
        search_frame.pack(fill="x", pady=(0, 10))
        
        # Search label
        search_label = ttk.Label(search_frame, text="Search:", style="Suikoden.TLabel", background="black")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Search entry
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill="x", expand=True)
        
        # Creating a custom style for the treeview
        # Creating a custom style for the treeview in selection window
        style = ttk.Style()
        style.configure("Suikoden.Treeview", 
                      background="#000000",  # Pure black background
                      rowheight=25,
                      fieldbackground="#111111")
        style.map("Suikoden.Treeview",
                background=[("selected", "#e94560")],  # Red accent for selected items
                foreground=[("selected", "white")])
        # Create frame for the treeview
        tree_frame = ttk.Frame(content_frame, style="Suikoden.TFrame")
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollbar for the listbox
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        
        # Create Treeview for character selection
        columns = ('character', 'role')
        character_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                     style="Suikoden.Treeview",
                                     yscrollcommand=scrollbar.set)
        
        # Configure the scrollbar
        scrollbar.configure(command=character_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure columns
        character_tree.column('character', width=200, anchor='w')
        character_tree.column('role', width=150, anchor='w')
        
        # Set column headings
        character_tree.heading('character', text='Character')
        character_tree.heading('role', text='Role')
        
        character_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Store IDs to reference characters
        character_ids = {}
        
        # Function to populate the character list
        def populate_character_list(search_text=""):
            character_tree.delete(*character_tree.get_children())
            character_ids.clear()
            
            # Get already selected characters
            already_selected = [name for name in self.selected_character_names if name is not None]
            
            for name in self.all_star_names:
                # Filter by search text if provided
                if search_text and search_text.lower() not in name.lower():
                    continue
                    
                # Get role information
                role_text = ""
                if self.character_info[name]['roles']:
                    role_text = ", ".join(role for role in self.character_info[name]['roles'] if role)
                
                # Show different status for already selected characters
                if name in already_selected:
                    item_id = character_tree.insert('', 'end', values=(name, f"{role_text} (Already Selected)"),
                                                  tags=('selected',))
                else:
                    item_id = character_tree.insert('', 'end', values=(name, role_text))
                
                character_ids[item_id] = name
            
        # Bind the search entry to the filter function
        def on_search_change(*args):
            populate_character_list(search_var.get())
            
        search_var.trace_add("write", on_search_change)
        
        # Configure tag for already selected items
        character_tree.tag_configure('selected', background="#333333", foreground="gray70")
        
        # Populate list initially
        populate_character_list()
        
        # Buttons frame
        buttons_frame = ttk.Frame(content_frame, style="Suikoden.TFrame")
        buttons_frame.pack(fill="x", pady=(0, 5))
        
        # Select button
        def on_select():
            selection = character_tree.selection()
            if selection:
                item_id = selection[0]
                character_name = character_ids[item_id]
                
                # Check if character is already selected in another slot
                if character_name in self.selected_character_names and slot_index is not None:
                    current_index = self.selected_character_names.index(character_name)
                    if current_index != slot_index:
                        # Ask if user wants to move the character
                        if tk.messagebox.askyesno("Character Already Selected", 
                                            f"{character_name} is already in slot {current_index + 1}. Move to slot {slot_index + 1}?"):
                            # Remove from current slot
                            self.selected_character_names[current_index] = None
                            self.party_members[current_index] = None
                            # Add to new slot
                            self._update_party_slot(character_name, slot_index, selection_window)
                    else:
                        # Already in this slot, just close
                        selection_window.destroy()
                else:
                    # Not yet selected, add to party
                    self._update_party_slot(character_name, slot_index, selection_window)
            else:
                tk.messagebox.showinfo("Selection Required", "Please select a character.")
        
        # Create a custom style for the selection window buttons
        style.configure("SelectionWindow.TButton",
                      background="#444444",
                      foreground="white",
                      font=('Arial', 10, 'bold'))
        style.map("SelectionWindow.TButton",
                background=[("active", "#e94560")],
                foreground=[("active", "white")])
        
        # Select button with improved visibility
        select_button = ttk.Button(buttons_frame, text="Select", style="SelectionWindow.TButton",
                                 command=on_select)
        select_button.pack(side=tk.LEFT, padx=10, pady=5, fill="x", expand=True)
        
        # Cancel button with improved visibility
        cancel_button = ttk.Button(buttons_frame, text="Cancel", style="SelectionWindow.TButton",
                                 command=selection_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=5, fill="x", expand=True)
        
        # Set initial selection if provided
        if selected_char:
            for item_id in character_ids:
                if character_ids[item_id] == selected_char:
                    character_tree.selection_set(item_id)
                    character_tree.see(item_id)
                    break
        
        # Make window modal
        selection_window.transient(self.winfo_toplevel())
        selection_window.grab_set()
        
        # Center the window
        selection_window.update_idletasks()
        width = selection_window.winfo_width()
        height = selection_window.winfo_height()
        x = (selection_window.winfo_screenwidth() // 2) - (width // 2)
        y = (selection_window.winfo_screenheight() // 2) - (height // 2)
        selection_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Focus on the window
        selection_window.focus_set()
    def _update_party_slot(self, character_name, slot_index, selection_window):
        """Updates the party slot with the selected character."""
        if character_name and slot_index is not None and 0 <= slot_index < self.party_slots:
            # Update the party member data
            filename = self.character_info[character_name]['image']
            self.party_members[slot_index] = filename
            self.selected_character_names[slot_index] = character_name
            
            # Update the display
            self._display_party()
            
        # Close the selection window
        selection_window.destroy()

    def _display_party(self):
        """Displays the current party members in the GUI."""
        for i in range(self.party_slots):
            filename = self.party_members[i]
            if filename:
                try:
                    # Construct the proper image path
                    image_path = os.path.join(self.image_folder, filename)
                    
                    # Open and resize image
                    img = Image.open(image_path)
                    img = img.resize((90, 90))  # Size for 2x3 grid layout
                    
                    # Create PhotoImage
                    img_tk = ImageTk.PhotoImage(img)
                    
                    # Display image
                    self.displayed_images[i].config(image=img_tk)
                    self.displayed_images[i].image = img_tk  # Keep reference to prevent garbage collection
                    
                    # Get character name
                    char_name = self.selected_character_names[i]
                    
                    # Update name label
                    if char_name and hasattr(self.slot_frames[i], "name_label"):
                        self.slot_frames[i].tooltip_text = char_name
                        self.slot_frames[i].name_label.config(text=char_name)
                except FileNotFoundError:
                    print(f"Image file not found: {filename}")
                    self.displayed_images[i].config(image="")
                    if hasattr(self.slot_frames[i], "name_label"):
                        self.slot_frames[i].name_label.config(text="Image not found")
                except Exception as e:
                    print(f"Error loading image for {filename}: {e}")
                    self.displayed_images[i].config(image="")
                    if hasattr(self.slot_frames[i], "name_label"):
                        self.slot_frames[i].name_label.config(text="Error")
            else:
                # Clear the image and name if no character is selected
                self.displayed_images[i].config(image="")
                if hasattr(self.slot_frames[i], "name_label"):
                    self.slot_frames[i].name_label.config(text="")
    def get_current_party_files(self):
        """Returns the list of current party member filenames."""
        return self.party_members