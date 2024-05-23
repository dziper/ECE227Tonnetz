import csv
from utils import num_to_note

# One note at a time
class SimpleSong:
    def __init__(self, csv_path):
        self.data = {"track": [],
                     "time": [],
                     "channel": []}
        self.notes = []
        with open(csv_path, newline='') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[2].strip() == "Note_on_c":  # Use strip() to remove leading/trailing whitespace
                    self.data["track"].append(row[0].strip())
                    self.data["time"].append(row[1].strip())
                    self.data["channel"].append(row[3].strip())
                    self.notes.append(int(row[4].strip()))

    def __repr__(self):
        return repr([num_to_note(n) for n in self.notes])