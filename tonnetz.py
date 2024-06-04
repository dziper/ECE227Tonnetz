from typing import List, Tuple, Optional, Dict, Set
import mido
import networkx as nx
import math
from math import cos, sin, pi
import utils
from utils import NOTE_LOOKUP, num_to_note
import os
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

from overrides import overrides

Coord = Tuple[int, int]
DEFAULT_START = 57  # A3

TONNETZ_INTERVALS = (
    (1,1,10), (1,2,9), (1,3,8), (1,4,7), (1,5,6), (2,2,8),
    (2,3,7), (2,4,6), (2,5,5), (3,4,5), (3,3,6), (4,4,4)
)

class Tonnetz:
    def __init__(self, intervals: Tuple[int, int, int] = (3, 4, 5), x: int = 12, y: int = 24,
                 start_note=DEFAULT_START):
        self.G = nx.triangular_lattice_graph(x, y)
        pos = nx.get_node_attributes(self.G, "pos")
        self.pos = rotate_positions(pos, 30)
        self._compute_notes(intervals, start_note)

    def draw(self, draw_edges=True, ax=None):
        if draw_edges:
            nx.draw(self.G, self.pos, node_size=150, ax=ax)
        else:
            nx.draw_networkx_nodes(self.G, self.pos, node_size=150, ax=ax)
        nx.draw_networkx_labels(self.G, self.pos, self.notes, font_size=6, ax=ax)

    def _compute_notes(self, intervals, start_note):
        self.notes: Dict[Coord, str] = {name: "A" for name in self.G.nodes()}  # Maps note coord to note name
        self.note_map: Dict[int, List[Coord]] = {}  # Maps note number to list of positions in Graph

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

            self.notes[coord] = num_to_note(curr)
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


def dist(fromCoord, toCoord, pos):
    return math.sqrt((pos[fromCoord][0] - pos[toCoord][0])**2 + (pos[fromCoord][1] - pos[toCoord][1])**2)


DIST_THRESH = 4
WIDTH_ADJUST = 10
MAX_EDGE_WIDTH = 4
MIN_TRANSITIONS = 4


def _compute_transitions(prev_notes, curr_notes):
    transitions = []
    for p in prev_notes:
        for c in curr_notes:
            if p == c: continue
            transitions.append((p, c))
    return transitions


class TonnetzTrack(Tonnetz):
    instrument: str

    def __init__(self, instrument=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transitions: Dict[Tuple[Coord, Coord], float] = {}
        self.instrument = instrument

    def analyze(self, note_sequence: List[int]):
        self.transitions = {}
        prev = None
        for note in note_sequence:
            if prev is None or note not in self.note_map or prev not in self.note_map:
                prev = note
                continue
            self._add_transition(prev, note, 1/len(note_sequence))
            prev = note

    def _add_transition(self, prev, note, weight):
        if note not in self.note_map: return
        if prev not in self.note_map: return

        for prevCoord in self.note_map[prev]:
            closest = None
            closest_dist = None
            for currCoord in self.note_map[note]:
                d = dist(prevCoord, currCoord, self.pos)
                if closest is None or d < closest_dist:
                    closest = currCoord
                    closest_dist = d
            if closest_dist < DIST_THRESH:
                transition = (prevCoord, closest)
                if transition not in self.transitions:
                    self.transitions[transition] = 0
                self.transitions[transition] += weight

    def analyzeV2(self, intervals: np.ndarray):
        # intervals: [note, start, stop]

        prev_notes = []
        curr_notes = []
        curr_start = 0

        for i in range(intervals.shape[0]):
            if intervals[i,1] != curr_start:
                trans = _compute_transitions(prev_notes, curr_notes)
                for t in trans:
                    self._add_transition(t[0], t[1], (1/len(trans)) / intervals.shape[0])
                prev_notes = curr_notes
                curr_notes = []

            curr_start = intervals[i, 1]
            curr_notes.append(intervals[i, 0])


    @overrides
    def draw(self, draw_edges=False, edge_width_adjust=WIDTH_ADJUST, ax=None):
        Tonnetz.draw(self, draw_edges=draw_edges, ax=ax)
        weights = [v * edge_width_adjust for v in self.transitions.values()]
        nx.draw_networkx_edges(self.G, self.pos, edgelist=list(self.transitions.keys()),
                               width=weights, edge_color='r', ax=ax)


NoteTransitions = Dict[Tuple[int, int], float]

class MatrixType(Enum):
    ADJACENCY = 1
    DEGREE = 2
    LAPLACIAN = 3
    
class CentralityType(Enum):
    DEGREE = 1
    BETWEENESS = 2
    CLOSENESS = 3
    EIGENVECTOR = 4
    

class TonnetzQuarterTrack(Tonnetz):
    instrument: str
    
    def __init__(self, instrument=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transitions: List[Dict[Tuple[Coord, Coord], float]] = []
        self.note_number_transitions: List[NoteTransitions] = []
        self.instrument = instrument

    def _add_transition(self, prev, note, weight, qnote):
        if qnote >= len(self.transitions): raise ValueError(f"Quarter {qnote}")
        if note not in self.note_map: return
        if prev not in self.note_map: return

        if (prev, note) not in self.note_number_transitions[qnote]:
            self.note_number_transitions[qnote][(prev, note)] = 0
        self.note_number_transitions[qnote][(prev, note)] += weight

        for prevCoord in self.note_map[prev]:
            closest = None
            closest_dist = None
            for currCoord in self.note_map[note]:
                d = dist(prevCoord, currCoord, self.pos)
                if closest is None or d < closest_dist:
                    closest = currCoord
                    closest_dist = d
            if closest_dist < DIST_THRESH:
                transition = (prevCoord, closest)
                if transition not in self.transitions[qnote]:
                    self.transitions[qnote][transition] = 0
                self.transitions[qnote][transition] += weight

    def analyze(self, intervals: np.ndarray, ticks_per_measure, beats_per_measure=4):
        # intervals: [note, start, stop]
        self.transitions = [{} for _ in range(beats_per_measure)]
        self.note_number_transitions = [{} for _ in range(beats_per_measure)]

        prev_notes = []
        curr_notes = []
        curr_start = 0

        for i in range(intervals.shape[0]):
            if intervals[i,1] != curr_start:
                trans = _compute_transitions(prev_notes, curr_notes)
                for t in trans:
                    qnote = (curr_start // ticks_per_measure) % beats_per_measure
                    self._add_transition(t[0], t[1], (1/len(trans)) / intervals.shape[0], qnote)
                prev_notes = curr_notes
                curr_notes = []

            curr_start = intervals[i, 1]
            curr_notes.append(intervals[i, 0])
        
        return not (all(len(qt) < MIN_TRANSITIONS for qt in self.transitions))


    @overrides
    def draw(self, draw_edges=False, edge_width_adjust=WIDTH_ADJUST, ax=None, draw_quarters=True):
        Tonnetz.draw(self, draw_edges=draw_edges, ax=ax)
        if not draw_quarters:
            # Combine all transitions
            total_trans = {}
            for qtrans in self.transitions:
                for trans in qtrans:
                    if trans not in total_trans:
                        total_trans[trans] = qtrans[trans]
                    else:
                        total_trans[trans] += qtrans[trans]
            weights = [min(MAX_EDGE_WIDTH, v * edge_width_adjust) for v in total_trans.values()]
            nx.draw_networkx_edges(self.G, self.pos, edgelist=list(total_trans.keys()),
                                   width=weights, edge_color='r', ax=ax)
            return

        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        for qnote in range(len(self.transitions) - 1, -1, -1):
            weights = [min(MAX_EDGE_WIDTH, v * edge_width_adjust * 4) for v in self.transitions[qnote].values()]
            nx.draw_networkx_edges(self.G, self.pos, edgelist=list(self.transitions[qnote].keys()),
                                   width=weights, edge_color=colors[qnote], ax=ax)


    def get_matrices(self, matrix_type: MatrixType) -> list:
        '''
        Return the matrix of each quarter transition in self.transitions
        '''
        matirces = []
        for trans in self.transitions:
            tempG = nx.Graph()
            tempG.add_nodes_from(self.G.nodes)
            tempG.add_weighted_edges_from([(n0, n1, w) for (n0, n1), w in trans.items()])
            if matrix_type == MatrixType.ADJACENCY:
                matirces.append(nx.adjacency_matrix(tempG).todense())
            elif matrix_type == MatrixType.DEGREE:
                matirces.append(np.diag([d for n, d in tempG.degree()]))
            elif matrix_type == MatrixType.LAPLACIAN:
                matirces.append(nx.laplacian_matrix(tempG).todense())    
        return matirces
    
    
    def get_centralities(self, centrality_type: CentralityType) -> list:
        '''
        Return the centrality of each quarter transition in self.transitions
        '''
        centralities = []
        for trans in self.transitions:
            tempG = nx.Graph()
            tempG.add_nodes_from(self.G.nodes)
            tempG.add_weighted_edges_from([(n0, n1, w) for (n0, n1), w in trans.items()])
            if centrality_type == CentralityType.DEGREE:
                centralities.append(nx.degree_centrality(tempG))
            elif centrality_type == CentralityType.CLOSENESS:
                centralities.append(nx.closeness_centrality(tempG))
            elif centrality_type == CentralityType.BETWEENESS:
                centralities.append(nx.betweenness_centrality(tempG))
            elif centrality_type == CentralityType.EIGENVECTOR:
                centralities.append(nx.eigenvector_centrality(tempG))
        return centralities    
