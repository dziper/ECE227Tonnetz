from dataclasses import dataclass, field

import utils
from song import AnalyzedSong
from tonnetz import NoteTransitions
from typing import List, Optional, Dict, Tuple, Callable
import numpy as np
from tqdm import tqdm


@dataclass
class Comparison:
    # Represents results of a comparison
    songs: Tuple[str, str]
    scores: List[Dict[Tuple[int, int], float]]
    total_score: float = 0

    def __init__(self, song1: AnalyzedSong, song2: AnalyzedSong):
        self.songs = (song1.to_song_id(), song2.to_song_id())
        self.scores = [{} for _ in range(song1.beats_per_measure)]

    def add_score(self, qnote: int, tracks: Tuple[int, int], score: float):
        self.scores[qnote][tracks] = score
        self.total_score += score

    def get_best_matches(self, count=5):
        matches: List[Tuple[int, Tuple[int, int], float]] = []
        for q, scr in enumerate(self.scores):
            for tracks in scr:
                matches.append((q, tracks, scr[tracks]))
        matches.sort(key=lambda m: m[2], reverse=True)
        matches = matches[:count]
        return matches

    def __repr__(self):
        return f"{self.songs[0]} / {self.songs[1]} : Total {round(self.total_score, 3)}"

    def best_to_str(self, count=5):
        best = self.get_best_matches(count)
        r = ""
        for m in best:
            r += f"Q{m[0]} C{m[1][0]}/C{m[1][1]}: {round(m[2], 3)}\n"
        return r.strip()


def edge_list_tonnetz_distance(e1: NoteTransitions, e2: NoteTransitions, offset=0, weighted=True):
    similarity = 0
    for transition in e1:
        other_transition = (transition[0] + offset, transition[1] + offset)
        if other_transition in e2:
            # We have a shared edge
            weight_diff = abs(e1[transition] - e2[other_transition])
            max_weight = max(e1[transition], e2[transition])
            # Further edges in Tonnetz are given more weight
            ton_dist = utils.tonnetz_dist(transition[0], transition[1])
            if not weighted:
                ton_dist = 1

            similarity += ton_dist * (1-weight_diff) * max_weight
    return similarity


def simple_compare(song1: AnalyzedSong, song2: AnalyzedSong, max_channels=3, dist_weighted=True) -> Optional[Comparison]:
    if song1.beats_per_measure != song2.beats_per_measure: return None
    comp = Comparison(song1, song2)
    for c1, tr1 in enumerate(song1.tracks):
        if c1 == max_channels: break
        for c2, tr2 in enumerate(song2.tracks):
            if c2 == max_channels: break

            for q in range(len(tr1.note_number_transitions)):
                # q is qnote number
                eltd = edge_list_tonnetz_distance(tr1.note_number_transitions[q], tr2.note_number_transitions[q], weighted=dist_weighted)
                # print(f"{tr1.instrument}/{tr2.instrument} : Q{q} : {eltd}")
                comp.add_score(q, (c1, c2), eltd)
    return comp


def compute_similarity_matrix(song_ids: List[str], similarity_function: Callable[[AnalyzedSong, AnalyzedSong], Optional[Comparison]]):
    n = len(song_ids)
    similarity_matrix = np.zeros((n, n))
    comparisons = [[None] * n for _ in range(n)]
    for i in tqdm(range(n)):
        currSong = AnalyzedSong(song_ids[i])
        for j in range(i, n):
            comp = similarity_function(currSong, AnalyzedSong(song_ids[j]))
            if comp is None: continue
            comparisons[i][j] = comp
            similarity_matrix[i, j] = comp.total_score
            similarity_matrix[j, i] = comp.total_score
    return similarity_matrix, comparisons
