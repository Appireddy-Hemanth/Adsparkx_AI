import os
import sys
import subprocess

# Ensure project root is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# If running directly, execute the streamlit application
if __name__ == "__main__":
    streamlit_app_path = os.path.join(project_root, "ui", "streamlit_app.py")
    subprocess.run(["streamlit", "run", streamlit_app_path])
