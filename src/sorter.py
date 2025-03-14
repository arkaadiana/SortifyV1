import os
import shutil

class ActionTracker:
    """Class to track and manage file operations history"""
    def __init__(self):
        self.action_history = []  # Stores all tracked actions
    
    def record_move(self, original_path, destination_path, category):
        """
        Record a file move operation
        Args:
            original_path: Source file path
            destination_path: Destination file path
            category: Target category/folder name
        Returns:
            Recorded action dictionary
        """
        action = {
            'type': 'move',
            'original_path': original_path,
            'destination_path': destination_path,
            'category': category
        }
        self.action_history.append(action)
        return action
    
    def record_delete(self, original_path):
        """
        Record a file deletion operation
        Args:
            original_path: Path of deleted file
        Returns:
            Recorded action dictionary
        """
        action = {
            'type': 'delete',
            'original_path': original_path
        }
        self.action_history.append(action)
        return action
    
    def undo_last_action(self):
        """
        Reverse the last recorded action
        Returns:
            The undone action dictionary or None if unsuccessful
        """
        if not self.action_history:
            return None
        
        last_action = self.action_history.pop()
        
        try:
            if last_action['type'] == 'move':
                # Ensure original directory exists
                os.makedirs(os.path.dirname(last_action['original_path']), exist_ok=True)
                
                # Move file back to original location
                shutil.move(last_action['destination_path'], last_action['original_path'])
                print(f"Undo move: {last_action['destination_path']} -> {last_action['original_path']}")
                return last_action
            
            elif last_action['type'] == 'delete':
                # Note: Actual undelete implementation would require a backup system
                print(f"Delete undo not fully implemented for {last_action['original_path']}")
                return None
        
        except Exception as e:
            print(f"Undo error: {e}")
            return None

# Global instance for tracking file operations
action_tracker = ActionTracker()

def move_image(image_path, destination_folder):
    """
    Move image to target folder with conflict resolution
    Args:
        image_path: Source file path
        destination_folder: Target directory path
    Returns:
        New file path if successful, None otherwise
    """
    try:
        os.makedirs(destination_folder, exist_ok=True)
        filename = os.path.basename(image_path)
        destination_path = os.path.join(destination_folder, filename)
        
        # Handle filename conflicts by appending counter
        if os.path.exists(destination_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(destination_path):
                filename = f"{base}_{counter}{ext}"
                destination_path = os.path.join(destination_folder, filename)
                counter += 1
        
        shutil.move(image_path, destination_path)
        
        # Record the move operation
        action_tracker.record_move(image_path, destination_path, os.path.basename(destination_folder))
        
        print(f"Moved {filename} to {destination_folder}")
        return destination_path
    
    except Exception as e:
        print(f"Error moving image: {e}")
        return None

def delete_image(image_path):
    """
    Permanently delete an image file
    Args:
        image_path: Path of file to delete
    """
    try:
        # Record deletion before executing
        action_tracker.record_delete(image_path)
        
        os.remove(image_path)
        print(f"Deleted {image_path}")
    except Exception as e:
        print(f"Error deleting image: {e}")

def undo_last_action():
    """
    Public interface for undoing last file operation
    Returns:
        Result of the undo operation
    """
    return action_tracker.undo_last_action()