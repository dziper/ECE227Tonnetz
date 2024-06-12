import song
import utils
import os
import random

THRESH = 2000

if __name__ == "__main__":
    while True:
        analyzedCount = len(os.listdir(os.path.join(utils.OUTPUT_ROOT, 'songPickles')))
        print(f"Analyzed {analyzedCount} so far.")
        if analyzedCount > THRESH:
            print("Done!")
            break

        song.analyze_artist(
            random.choice(
                 ["The Beatles", "ABBA", "AC DC", "Metallica", "Tori Amos", "Ace of Base", "a-ha", "Radiohead", "Nirvana", "Red Hot Chili Peppers", "Britney Spears", "Madonna", "Cake", "Fiona Apple"]
            )
        )

