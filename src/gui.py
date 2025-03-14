import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import pillow_heif
pillow_heif.register_heif_opener()  # Enable HEIF/HEIC support
from sorter import move_image, delete_image, undo_last_action
from utils import is_valid_folder
import threading
import rawpy

class ThemedTk(tk.Tk):
    """Custom Tkinter root window with modern theming"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure theme colors and styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use 'clam' theme as base
        
        # Color definitions
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.accent_color = "#1a73e8"
        self.hover_color = "#185abc"
        self.error_color = "#d32f2f"
        self.success_color = "#4caf50"
        
        # Apply styles to widgets
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TButton', 
                            background=self.accent_color, 
                            foreground=self.fg_color, 
                            borderwidth=0, 
                            font=('Arial', 10, 'bold'), 
                            padding=10)
        self.style.map('TButton', background=[('active', self.hover_color)])
        
        self.configure(bg=self.bg_color)

def load_raw_image(raw_path):
    """Reads RAW image files and converts them to Pillow format"""
    with rawpy.imread(raw_path) as raw:
        rgb = raw.postprocess()  # Convert RAW to RGB array
        return Image.fromarray(rgb)  # Convert array to Pillow Image

class SortifyV1:
    def __init__(self, root):
        """Initialize main application"""
        self.root = root
        self.root.title("SortifyV1")
        self.root.geometry("800x600")
        self.image_list = []
        self.current_index = 0
        self.categories = []
        self.folder_path = ""
        self.total_images = 0
        self.sorted_images = 0
        self.create_splash_screen()
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_splash_screen(self):
        """Show loading splash screen with progress bar"""
        self.clear_window()
        
        self.splash_frame = ttk.Frame(self.root, padding=20)
        self.splash_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        label = ttk.Label(self.splash_frame, text="SortifyV1 - Loading...", font=('Arial', 20, 'bold'))
        label.pack(pady=20)
        
        progress = ttk.Progressbar(self.splash_frame, mode="determinate", length=300)
        progress.pack(pady=10)
        
        def simulate_loading():
            """Simulate loading progress with thread"""
            for i in range(1, 101, 5):
                self.root.after(i * 20, lambda value=i: progress.configure(value=value))
            self.root.after(2000, self.create_main_menu)
        
        loading_thread = threading.Thread(target=simulate_loading)
        loading_thread.start()
    
    def create_main_menu(self):
        """Create main menu interface"""
        self.clear_window()
    
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(self.main_frame, text="SortifyV1", font=('Arial', 28, 'bold')).pack(pady=20)
        
        ttk.Button(self.main_frame, text="Select Folder", command=self.choose_folder, style='TButton').pack(pady=15, ipadx=20, ipady=10)
        
        self.github_credit()
    
    def choose_folder(self):
        """Handle folder selection and initialize categories"""
        folder = filedialog.askdirectory()
        if folder and is_valid_folder(folder):
            # Reset categories and get subfolders
            self.categories = []
            self.folder_path = folder
            subfolders = [f for f in os.listdir(folder) 
                          if os.path.isdir(os.path.join(folder, f))]

            # Use subfolders as default categories
            self.categories = subfolders
            self.create_category_menu()
        else:
            self.show_notification("Invalid folder or no images found!", "error")

    def create_category_menu(self):
        """Create category management interface"""
        self.clear_window()

        self.category_frame = ttk.Frame(self.root, padding=20)
        self.category_frame.place(relx=0.5, rely=0.5, anchor='center')

        ttk.Label(self.category_frame, text="Create Categories", font=('Arial', 24, 'bold')).pack(pady=10)

        input_frame = ttk.Frame(self.category_frame)
        input_frame.pack(pady=5)

        self.category_entry = ttk.Entry(input_frame, width=40)
        self.category_entry.pack(side="left", padx=5)

        ttk.Button(input_frame, text="+", command=self.add_category, style='TButton', width=3).pack(side="left")

        self.category_display = ttk.Frame(self.category_frame)
        self.category_display.pack(fill='x', pady=10)

        # Display existing categories
        for category in self.categories:
            category_button = ttk.Button(self.category_display, text=category, style='TButton')
            category_button.pack(side="left", padx=5, pady=5, ipadx=10, ipady=5)
            category_button.bind("<Button-1>", lambda e, cat=category: self.delete_category(cat))

        ttk.Button(self.category_frame, text="Start Sorting", command=self.start_sorting, style='TButton').pack(pady=10, ipadx=20, ipady=10)

        self.github_credit()

    def add_category(self):
        """Add new category from user input"""
        category = self.category_entry.get().strip()
        if category and category not in self.categories:
            self.categories.append(category)
            category_button = ttk.Button(self.category_display, text=category, style='TButton')
            category_button.pack(side="left", padx=5, pady=5, ipadx=10, ipady=5)
            category_button.bind("<Button-1>", lambda e, cat=category: self.delete_category(cat))

            # Create directory for new category
            os.makedirs(os.path.join(self.folder_path, category), exist_ok=True)
            self.category_entry.delete(0, 'end')

    def delete_category(self, category):
        """Remove existing category"""
        if category in self.categories:
            self.categories.remove(category)
            for widget in self.category_display.winfo_children():
                if widget.cget("text") == category:
                    widget.destroy()
            try:
                os.rmdir(os.path.join(self.folder_path, category))
            except OSError:
                self.show_notification(f"Cannot delete non-empty category: {category}", "error")
    
    def start_sorting(self):
        """Initialize image sorting process"""
        if not self.categories:
            self.show_notification("No categories created!", "error")
            return
        
        # Get supported image formats
        self.image_list = [f for f in os.listdir(self.folder_path) if f.lower().endswith((
            ".jpg", ".png", ".jpeg", ".heif", ".heic", ".cr2", ".nef", ".dng", ".arw", ".rw2", ".orf"
        ))]
        
        if not self.image_list:
            self.show_notification("No images found!", "error")
            return
        
        self.total_images = len(self.image_list)
        self.sorted_images = 0
        self.current_index = 0
        self.show_image()
    
    def show_image(self):
        """Display current image with controls"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Display progress counter
        ttk.Label(main_frame, text=f"Images: {self.sorted_images}/{self.total_images}", font=('Arial', 12)).pack(pady=5)
        
        if self.current_index < len(self.image_list):
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            file_extension = os.path.splitext(image_path)[1].lower()
            
            try:
                # Load image based on format
                if file_extension in ['.cr2', '.nef', '.dng', '.arw', '.rw2', '.orf']:
                    image = load_raw_image(image_path)
                elif file_extension in ['.heif', '.heic']:
                    image = Image.open(image_path)
                else:
                    image = Image.open(image_path)
                
                # Dynamic image resizing
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()
                max_width = int(window_width * 0.8)
                max_height = int(window_height * 0.8)
                image.thumbnail((max_width, max_height), Image.LANCZOS)
                
                self.current_image = ImageTk.PhotoImage(image)
                image_label = ttk.Label(main_frame, image=self.current_image)
                image_label.pack(expand=True)
            
            except Exception as e:
                self.show_notification(f"Failed to load image: {e}", "error")
                return

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # Category selection buttons
        for category in self.categories:
            ttk.Button(button_frame, text=category, 
                       command=lambda cat=category: self.move_image_to_category(cat), 
                       style='TButton').pack(side="left", padx=5, ipadx=10, ipady=5)

        # Control buttons
        button_row2 = ttk.Frame(main_frame)
        button_row2.pack(pady=5)

        ttk.Button(button_row2, text="Delete", command=self.delete_image, style='TButton').pack(side="left", padx=5, ipadx=10, ipady=5)
        ttk.Button(button_row2, text="Next", command=self.next_image, style='TButton').pack(side="left", padx=5, ipadx=10, ipady=5)
        ttk.Button(button_row2, text="Undo", command=self.undo_last_action, style='TButton').pack(side="left", padx=5, ipadx=10, ipady=5)
        ttk.Button(button_row2, text="Change Folder", command=self.change_folder_during_sorting, style='TButton').pack(side="left", padx=5, ipadx=10, ipady=5)

        self.github_credit()

    def change_folder_during_sorting(self):
        """Handle folder change during sorting process"""
        confirmation = messagebox.askyesno(
            "Change Folder", 
            "Are you sure you want to change the folder? \nUnsorted images in the current folder will be skipped."
        )

        if confirmation:
            self.categories = []
            folder = filedialog.askdirectory()

            if folder and is_valid_folder(folder):
                self.folder_path = folder
                subfolders = [f for f in os.listdir(folder) 
                              if os.path.isdir(os.path.join(folder, f))]
                self.categories = subfolders
                self.create_category_menu()
            else:
                self.show_notification("Invalid folder or no images found!", "error")
    
    def move_image_to_category(self, category):
        """Move image to selected category folder"""
        if self.current_index < len(self.image_list):
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            destination_folder = os.path.join(self.folder_path, category)
            
            # Save action details for undo
            current_image = {
                'original_path': image_path, 
                'destination_path': destination_folder, 
                'filename': self.image_list[self.current_index],
                'action': 'move'
            }
            
            move_image(image_path, destination_folder)
            del self.image_list[self.current_index]
            self.sorted_images += 1
            
            if self.current_index >= len(self.image_list):
                self.current_index = 0
            
            self.root.last_action = current_image
            self.show_image()
    
    def delete_image(self):
        """Delete current image permanently"""
        if self.current_index < len(self.image_list):
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            
            # Save action details for undo
            current_image = {
                'original_path': image_path, 
                'filename': self.image_list[self.current_index],
                'action': 'delete'
            }
            
            delete_image(image_path)
            del self.image_list[self.current_index]
            self.sorted_images += 1
            
            if self.current_index >= len(self.image_list):
                self.current_index = 0
            
            self.root.last_action = current_image
            self.show_image()
    
    def undo_last_action(self):
        """Undo the last performed action"""
        last_action = undo_last_action()

        if last_action:
            if last_action['type'] == 'move':
                self.image_list.insert(self.current_index, os.path.basename(last_action['original_path']))
                self.sorted_images -= 1
                self.show_image()
            elif last_action['type'] == 'delete':
                self.show_notification("Undo delete not fully supported yet", "error")
        else:
            self.show_notification("No action to undo", "info")
    
    def next_image(self):
        """Skip to next image in queue"""
        self.current_index += 1
        if self.current_index < len(self.image_list):
            self.show_image()
        else:
            self.show_notification("No more images to sort!", "info")
            self.create_main_menu()
    
    def show_notification(self, message, level="info"):
        """Show temporary status message"""
        colors = {"info": self.root.accent_color, "error": self.root.error_color}
        notification = ttk.Label(self.root, text=message, foreground=colors.get(level, "white"), font=("Arial", 12, "bold"))
        notification.pack(pady=5)
        self.root.after(3000, notification.destroy)
    
    def github_credit(self):
        """Display GitHub credit label"""
        credit_label = ttk.Label(self.root, text="GitHub: @arkaadiana", font=("Arial", 10), foreground="#ffffff")
        credit_label.place(relx=0.5, rely=1.0, anchor='s', y=-10)