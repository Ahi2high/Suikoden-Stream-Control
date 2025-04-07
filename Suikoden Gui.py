import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import random

class SuikodenPartyDisplay:
    def __init__(self, master):
        self.master = master
        master.title("Suikoden I Party & 108 Stars")

        self.image_folder = "images"
        self.background_image_path = "background.jpeg"
        self.party_slots = 6
        self.party_members = [None] * self.party_slots
        self.all_characters = {
            "Gremio": "Gremio.png",
            "Cleo": "Cleo.png",
            "Pahn": "Pahn.png",
            "Viktor": "Viktor.png",
            "Luc": "Luc.png",
            "Tai Ho": "Tai Ho.png",
            "Tir McDohl": "Tir McDohl.png",
            "Mathiu Silverberg": "Mathiu.png",
            # Add all 108 characters here
                "Tir": "Tir.png",
        "Gremio": "Gremio.png",
        "Cleo": "Cleo.png",
        "Pahn": "Pahn.png",
        "Viktor": "Viktor.png",
        "Flik": "Flik.png",
        "Camille": "Camille.png",
        "Tai Ho": "Tai Ho.png",
        "Yam Koo": "Yam_Koo.png",
        "Ronnie Bell": "Ronnie Bell.png",
        "Kirkis": "Kirkis.png",
        "Valeria": "Valeria.png",
        "Griffith": "Griffith.png",
        "Warren": "Warren.png",
        "Kasumi": "Kasumi.png",
        "Krin": "Krin.png",
        "Futch": "Futch.png",
        "Humphrey": "Humphrey.png",
        "Milich Oppenheimer": "Milich.png",
        "Sonya Shulen": "Sonya.png",
        "Leon Silverberg": "Leon.png",
        "Mathiu Silverberg": "Mathiu.png",
        "Apple": "Apple.png",
        "Luc": "Luc.png",
        "Jeane": "Jeane.png",
        "Lepant": "Lepant.png",
        "Eileen": "Eileen.png",
        "Giovanni": "Giovanni.png",
        "Sheena": "Sheena.png",
        "Kimberly": "Kimberly.png",
        "Tesla": "Tesla.png",
        "Jabba": "Jabba.png",
        "Esmeralda": "Esmeralda.png",
        "Melodye": "Melodye.png",
        "Marco": "Marco.png",
        "Sergei": "Sergei.png",
        "Gaspar": "Gaspar.png",
        "Sansuke": "Sansuke.png",
        "Sarah": "Sarah.png",
        "Antonio": "Antonio.png",
        "Lester": "Lester.png",
        "Rock": "Rock.png",
        "Chapman": "Chapman.png",
        "Hugo": "Hugo.png",
        "Marie": "Marie.png",
        "Onil": "Onil.png",
        "Blackman": "Blackman.png",
        "Pezmerga": "Pezmerga.png",
        "Taggart": "Taggart.png",
        "Anji": "Anji.png",
        "Kanak": "Kanak.png",
        "Leonardo": "Leonardo.png",
        "Hix": "Hix.png",
        "Tengaar": "Tengaar.png",
        "Lorelai": "Lorelai.png",
        "Kreutz": "Kreutz.png",
        "Morgan": "Morgan.png",
        "Eikei": "Eikei.png",
        "Fukien": "Fukien.png",
        "Zen": "Zen.png",
        "Kage": "Kage.png",
        "Mina": "Mina.png",
        "Kasios": "Kasios.png",
        "Mose": "Mose.png",
        "Kamandol": "Kamandol.png",
        "Mace": "Mace.png",
        "Moose": "Moose.png",
        "Meese": "Meese.png",
        "Juppo": "Juppo.png",
        "Meg": "Meg.png",
        "Gen": "Gen.png",
        "Kai": "Kai.png",
        "Maas": "Maas.png",
        "Window": "Window.png",
        "Kwanda Rosman": "Kwandapng",
        "Kasim Hazil": "Kasim.png",
        "Crows": "Crows.png",
        "Chan": "Chan.png",
        "Quincy": "Quincy.png",
        "Hellion": "Hellion.png",
        "Maximillian": "Maximillian.png",
        "Sancho": "Sancho.png",
        "Viki": "Viki.png",
        "Georges": "Georges.png",
        "Gon": "Gon.png",
        "Kun To": "Kun To.png",
        "Lotte": "Lotte.png",
        "Zorak": "Zorak.png",
        "Ivanov": "Ivanov.png"
        }
        self.all_star_names = sorted(self.all_characters.keys())
        self.recruited_stars = {name: False for name in self.all_star_names}

        self.displayed_images = []
        self.name_labels = []
        self.star_widgets = {} # To store widgets for each star

        self._load_background()
        self._create_notebook()

    def _load_background(self):
        """Loads and sets the background image."""
        try:
            bg_image = Image.open(self.background_image_path)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self.master, image=self.bg_photo)
            bg_label.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            print(f"Error: Background image '{self.background_image_path}' not found.")
            pass

    def _create_notebook(self):
        """Creates the tabbed interface."""
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self._create_party_tab()
        self._create_stars_tab()

    def _create_party_tab(self):
        """Creates the tab for party selection."""
        party_tab = ttk.Frame(self.notebook)
        self.notebook.add(party_tab, text="Party")

        # --- Selection Frame ---
        selection_frame = ttk.LabelFrame(party_tab, text="Select Party Members")
        selection_frame.pack(pady=10, padx=10, fill="x")

        row_num = 0
        col_num = 0
        for i in range(len(self.all_characters)):
            name = self.all_star_names[i] # Use sorted list
            button = ttk.Button(selection_frame, text=name,
                                command=lambda n=name: self._open_selection_window(n))
            button.grid(row=row_num, column=col_num, padx=5, pady=5, sticky="ew")
            col_num += 1
            if col_num > 5:
                col_num = 0
                row_num += 1
        for i in range(6):
            selection_frame.grid_columnconfigure(i, weight=1)

        # --- Random Party Button ---
        random_button = ttk.Button(party_tab, text="Random Party", command=self._set_random_party)
        random_button.pack(pady=10)

        # --- Display Frame ---
        display_frame = ttk.LabelFrame(party_tab, text="Current Party")
        display_frame.pack(pady=10, padx=10, fill="x")

        for i in range(self.party_slots):
            image_label = ttk.Label(display_frame)
            image_label.grid(row=0, column=i, padx=10, pady=10)
            self.displayed_images.append(image_label)

            name_label = ttk.Label(display_frame, text="", anchor="center")
            name_label.grid(row=1, column=i, padx=10, pady=2, sticky="ew")
            self.name_labels.append(name_label)

            slot_button = ttk.Button(display_frame, text=f"Slot {i+1}",
                                     command=lambda slot=i: self._open_selection_window(None, slot))
            slot_button.grid(row=2, column=i, padx=10, pady=5, sticky="ew")
            display_frame.grid_columnconfigure(i, weight=1)

    def _create_stars_tab(self):
        """Creates the tab for the 108 Stars list."""
        stars_tab = ttk.Frame(self.notebook)
        self.notebook.add(stars_tab, text="108 Stars")

        columns = 10 # Adjust as needed for layout
        row_num = 0
        col_num = 0
        for name in self.all_star_names:
            image_path = os.path.join(self.image_folder, self.all_characters[name])
            try:
                img = Image.open(image_path)
                img = img.resize((100, 100)) # Smaller images for the list
                img_tk = ImageTk.PhotoImage(img)
                label = ttk.Label(stars_tab, image=img_tk)
                label.image = img_tk # Keep reference
                label.grid(row=row_num, column=col_num, padx=2, pady=2)
                label.bind("<Button-1>", lambda event, n=name: self._toggle_star_recruited(n, event.widget))
                self.star_widgets[name] = label
            except FileNotFoundError:
                error_label = ttk.Label(stars_tab, text="?")
                error_label.grid(row=row_num, column=col_num, padx=2, pady=2)
                error_label.bind("<Button-1>", lambda event, n=name: self._toggle_star_recruited(n, event.widget))
                self.star_widgets[name] = error_label # Still store it

            col_num += 1
            if col_num >= columns:
                col_num = 0
                row_num += 1

    def _toggle_star_recruited(self, star_name, widget):
        """Toggles the recruited status of a star and updates its appearance."""
        self.recruited_stars[star_name] = not self.recruited_stars[star_name]
        if self.recruited_stars[star_name]:
            widget.config(style="Recruited.TLabel") # Apply a style
        else:
            widget.config(style="") # Revert to default

    def _set_random_party(self):
        """Sets a random party from all available characters."""
        available_characters = list(self.all_characters.keys())
        if len(available_characters) <= self.party_slots:
            random_party = available_characters
        else:
            random_party = random.sample(available_characters, self.party_slots)

        for i in range(self.party_slots):
            if i < len(random_party):
                filename = self.all_characters[random_party[i]]
                self.party_members[i] = filename
            else:
                self.party_members[i] = None
        self._display_party()

    def _open_selection_window(self, selected_char=None, slot_index=None):
        """Opens a new window to select a party member."""
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Select Party Member")

        list_frame = ttk.Frame(selection_window)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.character_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=30)
        scrollbar.config(command=self.character_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.character_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for name in self.all_star_names: # Use sorted list
            self.character_list.insert(tk.END, name)

        select_button = ttk.Button(selection_window, text="Select",
                                   command=lambda: self._update_party_slot(self.character_list.get(tk.ACTIVE), slot_index, selection_window))
        select_button.pack(pady=5)

        if selected_char:
            try:
                index = self.all_star_names.index(selected_char) # Use sorted list
                self.character_list.select_set(index)
                self.character_list.activate(index)
            except ValueError:
                pass

    def _update_party_slot(self, character_name, slot_index, selection_window):
        """Updates the party slot with the selected character."""
        if character_name and slot_index is not None:
            filename = self.all_characters[character_name]
            self.party_members[slot_index] = filename
            self._display_party()
        selection_window.destroy()

    def _display_party(self):
        """Displays the current party members in the GUI."""
        for i, filename in enumerate(self.party_members):
            if filename:
                image_path = os.path.join(self.image_folder, filename)
                try:
                    img = Image.open(image_path)
                    img = img.resize((100, 100))
                    img_tk = ImageTk.PhotoImage(img)
                    self.displayed_images[i].config(image=img_tk)
                    self.displayed_images[i].image = img_tk
                    name = [name for name, file in self.all_characters.items() if file == filename][0]
                    self.name_labels[i].config(text=name)
                except FileNotFoundError:
                    self.displayed_images[i].config(image="")
                    self.name_labels[i].config(text=f"Image Not Found: {filename}")
            else:
                self.displayed_images[i].config(image="")
                self.name_labels[i].config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.configure("Recruited.TLabel", background="lightgreen") # Style for recruited stars
    app = SuikodenPartyDisplay(root)
    root.mainloop()