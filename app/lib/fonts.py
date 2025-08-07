import os
from PyQt5.QtGui import QFontDatabase

# Go up from lib/ to app/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT_FOLDER = os.path.join(BASE_DIR, "assets", "fonts", "Inter", "static")

def load_inter_fonts():
    font_db = QFontDatabase()
    loaded_families = set()

    for file in os.listdir(FONT_FOLDER):
        if file.endswith(".ttf"):
            path = os.path.join(FONT_FOLDER, file)
            font_id = font_db.addApplicationFont(path)
            if font_id != -1:
                family = font_db.applicationFontFamilies(font_id)[0]
                loaded_families.add(family)
            else:
                print(f"Failed to load font: {file}")
    
    return loaded_families
