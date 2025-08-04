import os
import time
import json
from datetime import datetime

class ZoxideDB:
    """
    Manages a zoxide-like database for directory access and search.

    Parameters
    ----------
    db_path : str, optional
        Path to the database file (default: "zoxide_db.json").
    max_age : int, optional
        Maximum total score before aging entries (default: 10000).
    """
    def __init__(self, db_path="zoxide_db.json", max_age=10000):
        """
        Initialize the ZoxideDB instance and load entries from file.

        Parameters
        ----------
        db_path : str
            Path to the database file.
        max_age : int
            Maximum total score before aging entries.
        """
        self.db_path = db_path
        self.max_age = max_age
        self.entries = []
        self.last_rule = True  # Last component rule
        self._load()

    def _load(self):
        """
        Load entries from the database file.
        Entries are in the format: [path, score, last_access].
        """
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
        else:
            self.entries = []

    def _save(self):
        """
        Save entries to the database file.
        """
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2)

    def _now(self):
        """
        Get the current time as a UNIX timestamp.

        Returns
        -------
        int
            Current UNIX timestamp.
        """
        return int(time.time())

    def _frecency(self, entry):
        """
        Calculate the frecency score for an entry.

        Parameters
        ----------
        entry : dict
            Entry containing 'score' and 'last_access'.

        Returns
        -------
        float
            Calculated frecency score.
        """
        score = entry[1]
        last = entry[2]
        now = self._now()
        delta = now - last
        if delta < 3600:         # within the last hour
            return score * 4
        elif delta < 86400:      # within the last day
            return score * 2
        elif delta < 604800:     # within the last week
            return score / 2
        else:
            return score / 4

    def _prune(self):
        """
        Remove entries that do not exist and are older than 90 days.
        UNUSED - This function is not called in the current implementation read the note below.
        
        Note
        ----
        It is important to not prune entries too aggressively, as this can lead to loss of useful data.
        For example if google drive is not mounted the prune function will remove all entries that are 
        not currently mounted and then the user will not be able to access them even when they mount the drive again.
        The deleted directories that are still present in the database will be removed by the _age function
        this is sub optimal but it is better than losing data.
        """
        cutoff = self._now() - 90 * 86400
        self.entries = [
            e for e in self.entries
            if os.path.exists(e[0]) or e[2] > cutoff
        ]

    def _age(self):
        """
        Age entries if total score exceeds max_age.
        """
        total = sum(e[1] for e in self.entries)
        if total > self.max_age:
            k = total / (self.max_age * 0.9)
            for e in self.entries:
                e[1] = max(1, int(e[1] / k))
            self.entries = [e for e in self.entries if e[1] >= 1]

    def add(self, path):
        """
        Add a directory path to the database or increment its score.

        Parameters
        ----------
        path : str
            Directory path to add or update.
        """
        path = os.path.abspath(path)
        now = self._now()
        for e in self.entries:
            if e[0].lower() == path.lower():
                e[1] += 1
                e[2] = now
                self._save()
                return
        self.entries.append([path, 1, now])  # [path, score, last_access]
        self._save()
        
    def populate_by_traversing(self, root, regex=None):
        """
        Populate the database by traversing a directory tree.

        Parameters
        ----------
        root : str
            Root directory to start traversing.
        """
        for dirpath, _, _ in os.walk(root):
            if regex:
                if not regex.search(dirpath):
                    continue
            self.add(dirpath)

    def _match(self, entry, query):
        """
        Check if an entry matches the query according to zoxide rules.

        Parameters
        ----------
        entry : dict
            Entry to check.
        query : str
            Query string.

        Returns
        -------
        bool
            True if entry matches, False otherwise.
        """
        # if query is empty, match everything
        if not query.strip():
            return True
        
        path = entry[0].lower()
        query = query.lower().strip()
        if not query:
            return True
        terms = query.split()
        idx = 0
        for term in terms:
            idx = path.find(term, idx)
            if idx == -1:
                return False
            idx += len(term)
        # Last component rule
        last_query = terms[-1].split("/")[-1]
        last_path = os.path.basename(path)
        if last_query not in last_path and self.last_rule:
            return False
        return True

    def search(self, query):
        """
        Search for entries matching the query, sorted by frecency.

        Parameters
        ----------
        query : str
            Query string.

        Returns
        -------
        list of dict
            Matching entries sorted by frecency.
            
        Notes
        -----
        This method only returns existing paths (so only paths that are currently mounted).
        If the path does not exist, it will not be included in the results.
        """
        # self._prune()  # Uncomment to enable pruning (IMPORTANT: read note in _prune)
        self._age()
        results = [
            (self._frecency(e), e)
            for e in self.entries if self._match(e, query)
        ]
        results.sort(reverse=True, key=lambda x: x[0])
        return [e for _, e in results if os.path.exists(e[0])]

    def select(self, path):
        """
        Increment the score and update last_access for a selected path.

        Parameters
        ----------
        path : str
            Path to select.

        Returns
        -------
        bool
            True if path was found and updated, False otherwise.
        """
        for e in self.entries:
            if e[0].lower() == os.path.abspath(path).lower():
                e[1] += 1
                e[2] = self._now()
                self._save()
                return True
        return False

if __name__ == "__main__":
    """
    Simple interactive test for ZoxideDB.
    """
    db = ZoxideDB("test_zoxide_db.json")

    while True:
        query = input("\nEnter search query (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break

        results = db.search(query)
        if not results:
            print("No matches found.")
            continue

        print("\nResults:")
        for idx, entry in enumerate(results):
            score = db._frecency(entry)
            print(f"{idx+1}. {entry[0]} (score: {score})")

        sel = input("Select a result number to increment score (or Enter to skip): ").strip()
        if sel.isdigit():
            sel_idx = int(sel) - 1
            if 0 <= sel_idx < len(results):
                db.select(results[sel_idx][0])
                new_score = db._frecency(results[sel_idx])
                print(f"Score for '{results[sel_idx][0]}' incremented. New score: {new_score}")
            else:
                print("Invalid selection.")
        else:
            print("No selection made.")

