import os
import sys
import shutil

def get_data_dir() -> str:
    """
    Returns the path to the persistent, writable data directory.
    - If in development, returns the 'data' directory in the workspace.
    - If running as a packaged app (frozen), tries to use a 'data' directory 
      next to the executable (portable mode). If that's read-only (e.g. Program Files),
      falls back to the user's Local AppData directory.
    """
    # 1. Dev Mode
    if not getattr(sys, 'frozen', False):
        dev_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.normpath(os.path.join(dev_dir, "data"))
        
    # 2. Frozen Mode (Compiled App)
    exe_dir = os.path.dirname(sys.executable)
    local_data_dir = os.path.join(exe_dir, "data")
    
    # Try to verify write permissions in the local data directory
    try:
        if not os.path.exists(local_data_dir):
            os.makedirs(local_data_dir, exist_ok=True)
        # Verify write capability by creating/deleting a temporary file
        test_file = os.path.join(local_data_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return os.path.normpath(local_data_dir)
    except (OSError, IOError):
        # We don't have write permissions in the exe folder. Fallback to AppData/Local.
        appdata = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
        fallback_dir = os.path.join(appdata, "APITestStudio", "data")
        os.makedirs(fallback_dir, exist_ok=True)
        return os.path.normpath(fallback_dir)

def get_data_file_path(filename: str) -> str:
    """
    Resolves the writable path for a specific file or folder.
    If the file/folder does not exist in the writable persistent directory,
    copies the default version from the read-only bundled assets (sys._MEIPASS).
    """
    persistent_dir = get_data_dir()
    persistent_path = os.path.join(persistent_dir, filename)
    
    # If the persistent path already exists, just return it
    if os.path.exists(persistent_path):
        return os.path.normpath(persistent_path)
        
    # If it's missing, try to restore from bundled resources if running frozen
    if getattr(sys, 'frozen', False):
        bundled_dir = getattr(sys, '_MEIPASS', '')
        bundled_path = os.path.normpath(os.path.join(bundled_dir, "data", filename))
        if os.path.exists(bundled_path):
            try:
                # Ensure the parent directory of the target path exists
                os.makedirs(os.path.dirname(persistent_path), exist_ok=True)
                if os.path.isdir(bundled_path):
                    shutil.copytree(bundled_path, persistent_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(bundled_path, persistent_path)
            except Exception as e:
                print(f"Error copying default asset {filename}: {e}")
                return bundled_path
                
    return os.path.normpath(persistent_path)
