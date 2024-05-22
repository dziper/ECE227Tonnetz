from typing import List, Tuple, Optional, Dict
import networkx as nx
import math
from math import cos, sin, pi

NOTE_LOOKUP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class Tonnetz:
    def __init__(self, intervals: Tuple[int] = (3, 4, 5), x: int = 10, y: int = 20, start_note=0, start_octave=3):
        self.G = nx.triangular_lattice_graph(x, y)
        pos = nx.get_node_attributes(self.G, "pos")
        self.pos = rotate_positions(pos, 30)
        self._compute_notes(intervals, start_note, start_octave)

    def draw(self):
        nx.draw(self.G, self.pos)
        nx.draw_networkx_labels(self.G, self.pos, self.notes)

    def _compute_notes(self, intervals, start_note, start_octave):
        self.notes = {name: "A" for name in self.G.nodes()}
        curr = start_note
        current_row = 0
        last_start = start_note
        for coord in self.notes.keys():
            y_coord = coord[1]
            if y_coord > current_row:
                current_row = y_coord
                curr = last_start
                if current_row % 2 == 1: curr += intervals[1]
                else: curr += len(NOTE_LOOKUP) - intervals[2]
                last_start = curr

            curr_octave = start_octave + math.floor(curr / len(NOTE_LOOKUP))
            new_note = f"{NOTE_LOOKUP[curr % len(NOTE_LOOKUP)]}{curr_octave}"
            self.notes[coord] = new_note
            curr -= intervals[0]  # Horizontal


def rotate_positions(pos, degrees):
    rad = -degrees * pi / 180
    return {coord: (
        p[0] * cos(rad) - p[1] * sin(rad),
        p[1] * cos(rad) + p[0] * sin(rad)
    ) for coord, p in pos.items()}
