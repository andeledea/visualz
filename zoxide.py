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
        self._load()

    def _load(self):
        """
        Load entries from the database file.
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
        score = entry["score"]
        last = entry["last_access"]
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
        """
        cutoff = self._now() - 90 * 86400
        self.entries = [
            e for e in self.entries
            if os.path.exists(e["path"]) or e["last_access"] > cutoff
        ]

    def _age(self):
        """
        Age entries if total score exceeds max_age.
        """
        total = sum(e["score"] for e in self.entries)
        if total > self.max_age:
            k = total / (self.max_age * 0.9)
            for e in self.entries:
                e["score"] = max(1, int(e["score"] / k))
            self.entries = [e for e in self.entries if e["score"] >= 1]

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
            if e["path"].lower() == path.lower():
                e["score"] += 1
                e["last_access"] = now
                self._save()
                return
        self.entries.append({"path": path, "score": 1, "last_access": now})
        self._save()

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
        
        path = entry["path"].lower()
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
        if last_query not in last_path:
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
        """
        self._prune()
        self._age()
        results = [
            (self._frecency(e), e)
            for e in self.entries if self._match(e, query)
        ]
        results.sort(reverse=True, key=lambda x: x[0])
        return [e for _, e in results]

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
            if e["path"].lower() == os.path.abspath(path).lower():
                e["score"] += 1
                e["last_access"] = self._now()
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
            print(f"{idx+1}. {entry['path']} (score: {score})")

        sel = input("Select a result number to increment score (or Enter to skip): ").strip()
        if sel.isdigit():
            sel_idx = int(sel) - 1
            if 0 <= sel_idx < len(results):
                db.select(results[sel_idx]['path'])
                new_score = db._frecency(results[sel_idx])
                print(f"Score for '{results[sel_idx]['path']}' incremented. New score: {new_score}")
            else:
                print("Invalid selection.")
        else:
            print("No selection made.")

