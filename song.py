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


# Collection of TonnetzTracks that represent all of the tracks in a MIDI Song
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
            self.load_songV2(path)
        else:
            self.load_pickle(path)

    def load_song(self, path):
        if not os.path.exists(path):
            path = os.path.join(utils.DATA_ROOT, path)
        midi_file = mido.MidiFile(path, clip=True)
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.artist = os.path.basename(os.path.dirname(path))

        channels, instruments = utils.mido_to_notes_and_instr(midi_file)

        for channel, instr in zip(channels, instruments):
            if len(channel) == 0: continue
            ts = TonnetzTrack(instrument=instr)
            ts.analyze(channel)
            self.tracks.append(ts)

    def load_songV2(self, path):
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
            ts.analyze(note_interval, self.ticks_per_measure, self.beats_per_measure)
            self.tracks.append(ts)


    def draw(self, output_file=None, save_file=True, show_image=False, draw_quarters=True):
        xplots = 3
        yplots = 3

        if output_file is None:
            output_file = os.path.join(utils.OUTPUT_ROOT, "tonnetzImages", f"{self.to_song_id()}-tonnetz.png")

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
        return f"{self.artist}-{self.name}"

    def save_pickle(self, output_path=None):
        if output_path is None:
            os.makedirs(os.path.join(utils.OUTPUT_ROOT, "songPickles"), exist_ok=True)
            output_path = os.path.join(utils.OUTPUT_ROOT, "songPickles", f"{self.to_song_id()}.pickle")
        with open(output_path, 'wb') as handle:
            pickle.dump(self.__dict__, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_pickle(self, song_id):
        song_id = f"{song_id}.pickle"
        if not os.path.exists(song_id):
            song_id = os.path.join(utils.OUTPUT_ROOT, "songPickles", song_id)
        with open(song_id, 'rb') as handle:
            tmp = pickle.load(handle)
        self.__dict__.update(tmp)

