from typing import List, Tuple, Optional, Dict
import networkx as nx
import math
from math import cos, sin, pi

NOTE_LOOKUP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class Tonnetz:
    def __init__(self, intervals: Tuple[int, int, int] = (3, 4, 5), x: int = 10, y: int = 20,
                 start_note=0, start_octave=3):
        self.G = nx.triangular_lattice_graph(x, y)
        pos = nx.get_node_attributes(self.G, "pos")
        self.pos = rotate_positions(pos, 30)
        self._compute_notes(intervals, start_note, start_octave)

    def draw(self):
        nx.draw(self.G, self.pos)
        nx.draw_networkx_labels(self.G, self.pos, self.notes)

    def _compute_notes(self, intervals, start_note, start_octave):
        self.notes: Dict[Tuple[int, int], str] = {}  # Maps note coord to note name
        self.note_map: Dict[int, List[Tuple[int, int]]] = {}  # Maps note number to list of positions in Graph

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

            self.notes[coord] = num_to_note(curr, start_octave)
            if curr not in self.note_map:
                self.note_map[curr] = []
            self.note_map[curr].append(coord)
            curr -= intervals[0]  # Horizontal


def rotate_positions(pos, degrees):
    rad = -degrees * pi / 180
    return {coord: (
        p[0] * cos(rad) - p[1] * sin(rad),
        p[1] * cos(rad) + p[0] * sin(rad)
    ) for coord, p in pos.items()}


def num_to_note(note_num: int, start_octave=0) -> str:
    curr_octave = start_octave + math.floor(note_num / len(NOTE_LOOKUP))
    return f"{NOTE_LOOKUP[note_num % len(NOTE_LOOKUP)]}{curr_octave}"

