import os

def is_valid_folder(folder_path):
    """
    Check if the selected folder contains supported image files.
    
    Parameters:
    folder_path (str): Path to the folder to validate
    
    Returns:
    bool: True if folder contains valid image files, False otherwise
    """
    # Check if path is a valid directory
    if not os.path.isdir(folder_path):
        return False
    
    # Supported image extensions grouped by type
    image_extensions = [
        # Common image formats
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        # HEIF/HEIC formats
        '.heif', '.heic',
        # RAW camera formats
        '.dng', '.cr2', '.nef', '.arw', '.rw2', '.orf'
    ]
    
    # Check for at least one valid image file in the folder
    image_files = [f for f in os.listdir(folder_path) 
                   if os.path.isfile(os.path.join(folder_path, f)) 
                   and os.path.splitext(f)[1].lower() in image_extensions]
    
    # Return True if any valid images found
    return len(image_files) > 0