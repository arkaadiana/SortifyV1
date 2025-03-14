# Import custom GUI components from the gui module
from gui import ThemedTk, SortifyV1

if __name__ == "__main__":
    """Main entry point for the application"""
    
    # Create the themed root window
    root = ThemedTk()
    
    # Initialize the main application with the root window
    app = SortifyV1(root)
    
    # Start the Tkinter event loop
    root.mainloop()