import tkinter as tk
from tkinter import messagebox, PhotoImage
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import simpledialog
import os
import subprocess
import platform

global DIRECTORY_PATH
global INITIAL_DIRECTORY_PATH, IconsDirectory

INITIAL_DIRECTORY_PATH = os.getcwd()
DIRECTORY_PATH = INITIAL_DIRECTORY_PATH

IconsDirectory = r'C:/Users/hacke/OneDrive/Desktop/Ramaiah Staff Server/Client/resources'
    
class UserInterfaceFrontend:

    class Card(tk.Frame):
        global INITIAL_DIRECTORY_PATH, DIRECTORY_PATH
        def __init__(self, parent, icon, name, file_type, master, **kwargs):
            super().__init__(parent, **kwargs)
            self.master = master  # Reference to the parent FileExplorer instance
            self.icon_path = os.path.join(IconsDirectory, icon)
            self.name = name
            self.file_type = file_type
            self.load_icon()
            self.create_widgets()
            try:
                self.config(cursor="hand", bg='white', highlightthickness=0)
            except tk.TclError:
                self.config(cursor="arrow", bg='white', highlightthickness=0)
            self.click_num = 0
            self.click_timer = None

        def load_icon(self):
            if not os.path.exists(self.icon_path):
                raise ValueError("The icon file does not exist")
            img = Image.open(self.icon_path)
            img = img.resize((50, 50), Image.LANCZOS)
            self.icon_img = ImageTk.PhotoImage(img)

        def create_widgets(self):
            self.icon_label = tk.Label(self, image=self.icon_img, bg='white')
            self.icon_label.image = self.icon_img
            self.icon_label.pack(pady=(0, 2))
            self.name_label = tk.Label(self, text=self.name, wraplength=60, bg='white', fg='black')
            self.name_label.pack(pady=0)
            self.icon_label.bind("<Button-1>", self.on_click)
            self.name_label.bind("<Button-1>", self.on_click)

            # Save the item ID when creating the card
            self.item_id = self.master.canvas.create_window(0, 0, window=self, anchor='nw')

        
        def rearrange(self, x, y):
            self.master.canvas.coords(self.item_id, x, y)

        def on_click(self, event):
            self.click_num += 1
            if not self.click_timer:
                self.click_timer = self.after(200, self.check_clicks)



        def check_clicks(self):
            global DIRECTORY_PATH
            if self.click_num == 1:
                self.select()
                print(f"Single clicked: {self.name}")
            elif self.click_num == 2:
                try:
                    if self.file_type == 'folder':
                        new_directory = os.path.join(DIRECTORY_PATH, self.name)
                        if os.path.exists(new_directory) and os.path.isdir(new_directory):
                            DIRECTORY_PATH = new_directory
                            self.master.update_files(os.listdir(DIRECTORY_PATH))
                            self.master.rearrange_cards(None)  # Update the card layout
                            self.master.create_back_button()  # Show the back button again
                            print(f"Change directory to: {DIRECTORY_PATH}")
                        else:
                            print(f"Folder does not exist: {new_directory}")
                    else:
                        file_path = os.path.join(DIRECTORY_PATH, self.name)
                        try:
                            if platform.system() == "Windows":
                                # On Windows, use the 'start' command to open files with spaces
                                subprocess.run(["start", "", file_path], shell=True)
                            else:
                                # On macOS and Linux, use 'open' to open the file
                                subprocess.run(["open", file_path])
                            print(f"Open file: {self.name}")
                        except Exception as e:
                            print(f"Error opening file {self.name}: {e}")
                except PermissionError:
                    messagebox.showerror('File Handling Error', 'Error: This is an administor directory, You do not have permission!')

            self.click_num = 0
            self.click_timer = None

        def populate_cards(self):
            # Delete existing cards
            for card in self.canvas.winfo_children():
                card.destroy()

            self.cards = []  # Reset the cards list

            for name, file_type in self.files:  
                if file_type == "folder":
                    icon = os.path.join(IconsDirectory, "folder.png")
                else:
                    icon = os.path.join(IconsDirectory, {
                        ".pdf": "pdf.png",
                        ".ppt": "ppt.png",
                        ".pptx": "ppt.png",
                        ".doc": "doc.png",
                        ".docx": "doc.png",
                        ".xls": "xls.png",
                        ".xlsx": "xls.png",
                        ".zip": "zip.png"
                    }.get(os.path.splitext(name)[1], "document.png"))

                card = UserInterfaceFrontend.Card(self.canvas, icon, name, file_type, master=self)  # Pass 'master=self' here
                card.bind("<Button-1>", lambda event, card=card: self.on_card_click(card, event))
                self.cards.append(card)

            self.rearrange_cards(None)
            self.update_idletasks()


        def select(self):
            for card in self.master.winfo_children():
                if isinstance(card, UserInterfaceFrontend.Card):
                    card.deselect()
            self.config(highlightbackground='blue', highlightthickness=2)
            self.master.master.selected_card = self.name  # Save the selected card's name

        def deselect(self):
            self.config(highlightthickness=0)


    class FileExplorer(tk.Frame):
        HEADER_SIZE = 10
        def __init__(self, parent, controller, *args, **kwargs):
            super().__init__(*args, **kwargs)
            tk.Frame.__init__(self, parent, bg='white')
            self.controller = controller
            self.config(bg='white')
            self.selected_card = None  # This will store the name of the selected card

            self.create_navbar(controller)

            self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg='white')
            self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

            # Create a vertical scrollbar
            self.scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
            self.scrollbar.pack(side="right", fill="y", expand=False)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            self.files = []  # Initialize an empty file list
            self.cards = []  # Initialize an empty list for cards

            self.refresh_files()
            self.bind('<Configure>', self.rearrange_cards)

        def on_card_click(self, card, event):
            card.on_click(event)

        def populate_files(self):
            try:
                self.files = [(f, "folder") for f in os.listdir(DIRECTORY_PATH) if os.path.isdir(os.path.join(DIRECTORY_PATH, f))]
                self.files.extend([(f, "file") for f in os.listdir(DIRECTORY_PATH) if os.path.isfile(os.path.join(DIRECTORY_PATH, f))])
            except OSError as e:
                messagebox.showerror("Error", f"Error reading directory: {e}")


        def create_navbar(self, controller):
            navbar_frame = tk.Frame(self, bg="light gray")
            navbar_frame.pack(fill=tk.X)

            self.left_frame = tk.Frame(navbar_frame, bg="light gray")
            self.left_frame.pack(side=tk.LEFT)

            middle_frame = tk.Frame(navbar_frame, bg="light gray")
            middle_frame.pack(side=tk.LEFT, expand=True)

            right_frame = tk.Frame(navbar_frame, bg="light gray")
            right_frame.pack(side=tk.RIGHT)

            create_folder_img = ImageTk.PhotoImage(Image.open(os.path.join(IconsDirectory, 'add-folder.png')).resize((20, 20), Image.LANCZOS))
            create_folder_button = tk.Button(self.left_frame, image=create_folder_img, command=self.create_folder, relief="flat", bg="light gray")
            create_folder_button.image = create_folder_img
            create_folder_button.pack(side=tk.LEFT, padx=5, pady=5)

            rename_img = ImageTk.PhotoImage(Image.open(os.path.join(IconsDirectory, 'rename.png')).resize((20, 20), Image.LANCZOS))
            rename_button = tk.Button(self.left_frame, image=rename_img, command=self.rename_file, relief="flat", bg="light gray")
            rename_button.image = rename_img
            rename_button.pack(side=tk.LEFT, padx=5, pady=5)

            delete_img = ImageTk.PhotoImage(Image.open(os.path.join(IconsDirectory, 'delete.png')).resize((20, 20), Image.LANCZOS))
            delete_button = tk.Button(self.left_frame, image=delete_img, command=self.delete_file, relief="flat", bg="light gray")
            delete_button.image = delete_img
            delete_button.pack(side=tk.LEFT, padx=5, pady=5)

            # Entry widget for changing the directory
            path_entry = tk.Entry(middle_frame, width=40)
            path_entry.pack(side=tk.LEFT, padx=5, pady=5)

            # Button to change directory based on the entry value
            change_dir_button = tk.Button(middle_frame, text="Change Directory", command=lambda: self.change_directory(path_entry.get()))
            change_dir_button.pack(side=tk.LEFT, padx=5, pady=5)

        def change_directory(self, new_path):
            global DIRECTORY_PATH
            if os.path.exists(new_path) and os.path.isdir(new_path):
                DIRECTORY_PATH = new_path
                self.refresh_files()
                self.rearrange_cards(None)  # Update the card layout
                self.create_back_button()  # Show the back button again
                print(f"Change directory to: {DIRECTORY_PATH}")
            else:
                messagebox.showerror("Invalid Path", f"The specified path is not valid: {new_path}")

            

        def create_back_button(self):
            global INITIAL_DIRECTORY_PATH
            if DIRECTORY_PATH is None or INITIAL_DIRECTORY_PATH is None:
                # One or both of the paths are not set yet, so do not create a back button.
                if hasattr(self, 'back_button'):
                    # If a back button already exists, hide it.
                    self.back_button.pack_forget()
            else:
                # Both paths are set, so you can compare them.
                if os.path.samefile(DIRECTORY_PATH, INITIAL_DIRECTORY_PATH):
                    # We are in the initial directory. Do not create a back button.
                    if hasattr(self, 'back_button'):
                        # If a back button already exists, hide it.
                        self.back_button.pack_forget()
                else:
                    # We are not in the initial directory. Create a back button if it doesn't exist.
                    if hasattr(self, 'back_button'): 
                        if self.back_button.winfo_exists(): 
                            self.back_button.pack(side=tk.LEFT, padx=5, pady=5)
                        else:
                            self.create_new_back_button()
                    else:
                        self.create_new_back_button()



        def create_new_back_button(self):
            back_img = ImageTk.PhotoImage(Image.open(os.path.join(IconsDirectory, 'back.png')).resize((20, 20), Image.LANCZOS))
            self.back_button = tk.Button(self.left_frame, image=back_img, command=self.navigate_back, relief="flat", bg="light gray")
            self.back_button.image = back_img
            self.back_button.pack(side=tk.LEFT, padx=5, pady=5)


        def create_folder(self):
            folder_name = simpledialog.askstring("Create A New Folder", "Please enter the name of the folder", parent=self)
            if folder_name is not None:  # User didn't press Cancel.
                folder_path = os.path.join(DIRECTORY_PATH, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                self.refresh_files()

        def delete_file(self):
            if self.selected_card is None:
                return

            confirm = messagebox.askyesno("Delete File", f"Are you sure you want to delete {self.selected_card}?")
            if confirm:
                file_path = os.path.join(DIRECTORY_PATH, self.selected_card)
                os.remove(file_path)
                self.refresh_files()


        def rename_file(self):
            if self.selected_card is None:
                return

            new_name = simpledialog.askstring("Rename File", "Please enter the new name of the file", parent=self)
            if new_name is not None:  # User didn't press Cancel.
                old_path = os.path.join(DIRECTORY_PATH, self.selected_card)
                new_path = os.path.join(DIRECTORY_PATH, new_name)
                os.rename(old_path, new_path)
                self.refresh_files()


        def navigate_back(self):
            global DIRECTORY_PATH
            DIRECTORY_PATH = os.path.dirname(DIRECTORY_PATH)
            self.refresh_files()
            if os.path.samefile(DIRECTORY_PATH, INITIAL_DIRECTORY_PATH):
                # We are in the initial directory, hide the back button.
                self.back_button.pack_forget()
            else:
                # We are not in the initial directory, show the back button.
                self.create_back_button()



        def refresh_files(self):
            self.populate_files()
            files_and_folders = self.files
            files_and_folders.sort(key=lambda x: (x[0] == 'folder', x[1].lower()))
            self.files = files_and_folders
            self.populate_cards()
            self.rearrange_cards(None)

            if not self.files or (self.files[0][0] != "folder" or self.files[0][1] != ".."):
                self.create_back_button()
            else:
                if DIRECTORY_PATH != INITIAL_DIRECTORY_PATH:
                    self.create_back_button()
                else:
                    if hasattr(self, 'back_button'):
                        self.back_button.pack_forget()



        def populate_cards(self):
            # Delete existing cards
            for card in self.canvas.winfo_children():
                card.destroy()

            self.cards = []  # Reset the cards list

            for name, file_type in self.files:
                if file_type == "folder":
                    icon = os.path.join(IconsDirectory, "folder.png")
                else:
                    icon = os.path.join(IconsDirectory, {
                        ".pdf": "pdf.png",
                        ".ppt": "ppt.png",
                        ".pptx": "ppt.png",
                        ".doc": "doc.png",
                        ".docx": "doc.png",
                        ".xls": "xls.png",
                        ".xlsx": "xls.png",
                        ".zip": "zip.png"
                    }.get(os.path.splitext(name)[1], "document.png"))

                card = UserInterfaceFrontend.Card(self.canvas, icon, name, file_type, master=self)  # Pass 'master=self' here
                card.bind("<Button-1>", lambda event, card=card: self.on_card_click(card, event))
                self.cards.append(card)

        def update_files(self, files):
            self.files = files
            self.refresh_files()

                        
        def rearrange_cards(self, event):
            card_width = 100
            cards_per_row = max(1, self.winfo_width() // card_width)
            canvas_height = len(self.cards) // cards_per_row * card_width
            self.canvas.config(scrollregion=(0, 0, self.winfo_width(), canvas_height))

            for idx, card in enumerate(self.cards):
                x = (idx % cards_per_row) * card_width
                y = (idx // cards_per_row) * card_width
                card.rearrange(x, y)

            self.update_idletasks()

        def deselect_all(self, event=None):
            for card in self.canvas.winfo_children():
                if isinstance(card, UserInterfaceFrontend.Card):
                    card.deselect()
            self.selected_card = None  # Set selected_card to None when all cards are deselected


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Set window size and position
        window_width = 600
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # Initializing frames to an empty dictionary
        self.frames = {}

        # iterating through a tuple consisting of
        # the different page layouts
        for F in (UserInterfaceFrontend.FileExplorer,):  # Note the comma after FileExplorer
            frame = F(container, self)
            self.frames[F] = frame
            frame.pack(fill="both", expand=True)

        self.show_frame(UserInterfaceFrontend.FileExplorer)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# Driver Code
app = MainApplication()
app.title("File Explorer")
app.mainloop()
