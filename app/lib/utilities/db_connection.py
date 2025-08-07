import os

def get_db_path():
    """
    Return the absolute path to the LADOC.db file located at the TP-MP root.
    Walks up directories from current file location until it finds LADOC.db.
    """
    current_path = os.path.abspath(os.path.dirname(__file__))

    while True:
        possible_db_path = os.path.join(current_path, "LADOC.db")
        if os.path.exists(possible_db_path):
            return possible_db_path
        parent = os.path.dirname(current_path)
        if parent == current_path:
            raise FileNotFoundError("LADOC.db not found in any parent directory.")
        current_path = parent
