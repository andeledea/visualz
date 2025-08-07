import re
import os
import configparser as cp

from zoxide import ZoxideDB

config = cp.ConfigParser()
config.read("config.ini")

class Populator:
    """
    Class to populate the Zoxide database by traversing a directory tree.
    """

    @staticmethod
    def populate_by_traversing(db: ZoxideDB, root, regex_keep=None, regex_discard=None):
        """
        Populate the database by traversing a directory tree.

        Parameters
        ----------
        root : str
            Root directory to start traversing.
        """
        for dirpath, _, _ in os.walk(root):
            if regex_keep:
                if not re.search(regex_keep, dirpath):
                    continue
            if regex_discard:
                if re.search(regex_discard, dirpath):
                    continue
            db.add(dirpath)
            
    @staticmethod
    def populate_by_gemini(db: ZoxideDB, root):
        """
        Populate the database using the Gemini API.

        Parameters
        ----------
        db : ZoxideDB
            The database to populate.
        query : str
            The search query to use with the Gemini API.
        """
        from google import genai
        from google.genai import types

        # export the API key as an environment variable
        os.environ["GEMINI_API_KEY"] = config.get("POPULATOR", "gemini_api_key")
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Explain how AI works in a few words",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
            ),
        )
        print(response.text)
        # for dirpath, _, _ in os.walk(root):
            
            

if __name__ == "__main__":
    import configparser as cp
    
    config = cp.ConfigParser()
    config.read("config.ini")
    db = ZoxideDB(config, "zoxide_test_db.json")
    # Populator.populate_by_traversing(db, "/path/to/start", regex_keep=r"keep_pattern", regex_discard=r"discard_pattern")
    
    Populator.populate_by_gemini(db, "")