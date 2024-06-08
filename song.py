import csv

import midiFile
import utils
from utils import num_to_note
import mido
from tonnetz import TonnetzTrack, TonnetzQuarterTrack
from typing import List, Optional, Dict, Tuple
import os
from matplotlib import pyplot as plt
import pickle
import pretty_midi
import numpy as np
import math
from tonnetz import MatrixType
from enum import Enum


class CompareMethod(Enum):
    LAP_COSINE_SIM = 1,
    EDGES_JACCARD_SIM = 2

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


# Collection of TonnetzTracks that represent all the tracks in a MIDI Song
class AnalyzedSong:
    name: str
    artist: str
    path: str
    tracks: List[TonnetzQuarterTrack]
    # midi_file: mido.MidiFile

    def __init__(self, path=None):
        if path is None:
            return

        self.name = os.path.splitext(os.path.basename(path))[0]
        self.artist = os.path.basename(os.path.dirname(path))
        self.tracks = []

        if path.endswith(".mid"):
            self.load_song(path)
        else:
            self.load_pickle(path)

    def load_song(self, path):
        if not os.path.exists(path):
            path = os.path.join(utils.DATA_ROOT, path)
        pm = pretty_midi.PrettyMIDI(path)
        pm.remove_invalid_notes()

        self.ticks_per_beat = pm.resolution
        self.beats_per_measure = pm.time_signature_changes[0].numerator
        self.ticks_per_measure = self.beats_per_measure * self.ticks_per_beat

        self.path = path

        for instrument in pm.instruments:
            if instrument.is_drum: continue
            intervals = np.array([(pm.time_to_tick(note.start), pm.time_to_tick(note.end)) for note in instrument.notes])
            notes = np.array([note.pitch for note in instrument.notes])
            notes = notes.reshape(-1, 1)
            note_interval = np.concatenate((notes, intervals), 1)

            ts = TonnetzQuarterTrack(instrument=utils.GM_INSTRUMENT_NAMES[instrument.program])
            if ts.analyze(note_interval, self.ticks_per_measure, self.beats_per_measure):
                self.tracks.append(ts)


    def draw(self, output_file=None, save_file=True, show_image=False, draw_quarters=True):
        xplots = 3
        yplots = 3

        if output_file is None:
            output_file = utils.to_draw_path(self.to_song_id())

        fig, axes = plt.subplots(xplots, yplots, figsize=(20, 20))

        idx = 0
        for track in self.tracks:
            if idx >= xplots * yplots: break
            ax = axes[idx // xplots, idx % yplots]
            track.draw(edge_width_adjust=40, ax=ax, draw_quarters=draw_quarters)
            ax.set_title(f"{track.instrument}")
            idx += 1

        for ax in axes.flatten():
            ax.set_axis_off()

        plt.subplots_adjust(wspace=0, hspace=0.1)
        fig.suptitle(f"{self.artist}-{self.name}", y=0.92)

        if save_file:
            plt.savefig(output_file)
        if show_image:
            plt.show()
        plt.close(fig)

    def to_song_id(self):
        return utils.to_song_id(self.artist, self.name)

    def save_pickle(self, output_path=None):
        if output_path is None:
            os.makedirs(os.path.join(utils.OUTPUT_ROOT, "songPickles"), exist_ok=True)
            output_path = utils.to_pickle_path(self.to_song_id())
        with open(output_path, 'wb') as handle:
            pickle.dump(self.__dict__, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_pickle(self, song_id):
        if not song_id.endswith(".pickle"):
            song_id = f"{song_id}.pickle"
        if not os.path.exists(song_id):
            song_id = utils.to_pickle_path(song_id)
        with open(song_id, 'rb') as handle:
            tmp = pickle.load(handle)
        self.__dict__.update(tmp)
        
        
    def edges_jaccard_sim_between_tracks(self, track1: TonnetzQuarterTrack, track2: TonnetzQuarterTrack):
        '''
        Return the summation of the similarity of the four quarter transitions in track1 and track2
        '''
        assert(len(track1.note_number_transitions) == len(track2.note_number_transitions)), \
            f"len of track1.transitions {len(track1.note_number_transitions)} != len of track2.transitions {len(track2.note_number_transitions)}"
            
        sim_score = 0
        for i in range(0, len(track1.note_number_transitions)):
            t1_qtrans = set(track1.note_number_transitions[i].keys())
            t2_qtrans = set(track2.note_number_transitions[i].keys())
            intersection = t1_qtrans.intersection(t2_qtrans)
            union = t1_qtrans.union(t2_qtrans)
            sim_score += len(intersection) / len(union)
        return sim_score


    # Compute the cosine similarity between the Laplacian matrices
    def laplacian_cos_similarity_between_tracks(self, track1: TonnetzQuarterTrack, track2: TonnetzQuarterTrack):
        '''
        Return the summation of the similarity of the four quarter transitions in track1 and track2
        '''
        assert(len(track1.note_number_transitions) == len(track2.note_number_transitions)), \
            f"len of track1.transitions {len(track1.note_number_transitions)} != len of track2.transitions {len(track2.note_number_transitions)}"
        
        sim_score = 0
        # Flatten the Laplacian Matrix
        L1 = track1.get_matrices(MatrixType.LAPLACIAN)
        L2 = track2.get_matrices(MatrixType.LAPLACIAN)
        
        for i in range(0, len(track1.note_number_transitions)):
            L1_flat = L1[i].flatten()
            L2_flat = L2[i].flatten()
            sim_score += np.dot(L1_flat, L2_flat) / (np.linalg.norm(L1) * np.linalg.norm(L2))
        return sim_score

    
    def first_N_tracks_sim_score(self, aSong: 'AnalyzedSong', compare_method: CompareMethod, N: int):
        '''
        Return the summation of the similarity of the first N tracks between self and aSong. Raise error when the num of tracks is less than N.
        '''
        assert(len(self.tracks) >= N), f"\'{self.artist} - {self.name}\' only has {len(self.tracks)} tracks, but require {N} tracks."
        assert(len(aSong.tracks) >= N), f"\'{aSong.artist} - {aSong.name}\' only has {len(aSong.tracks)} tracks, but require {N} tracks."
        score = 0
        for i in range(0, N):
            if compare_method == CompareMethod.LAP_COSINE_SIM:
                score += self.laplacian_cos_similarity_between_tracks(self.tracks[i], aSong.tracks[i])
            elif compare_method == CompareMethod.EDGES_JACCARD_SIM:
                score += self.edges_jaccard_sim_between_tracks(self.tracks[i], aSong.tracks[i])
        return score
            
        

def analyze_artist(artist, draw=False, skip_analyzed=True, tqdm_disable=True):
    print(f"ANALYZING {artist}")
    def callback(artist, song_name):
        if skip_analyzed and os.path.exists(utils.to_pickle_path(utils.to_song_id(artist, song_name[:-4]))):
            return
        anSong = AnalyzedSong(os.path.join(artist, song_name))
        anSong.draw(save_file=True, show_image=draw)
        anSong.save_pickle()

    res = utils.for_song_in_artist(artist, callback, tqdm_disable=tqdm_disable)
    print(f"COMPLETED {artist}")
