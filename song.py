import csv
import utils
from utils import num_to_note
import mido
from tonnetz import TonnetzTrack
from typing import List, Optional, Dict, Tuple
import os
from matplotlib import pyplot as plt
import pickle

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

    tracks: List[TonnetzTrack] = []
    # midi_file: mido.MidiFile

    def __init__(self, path=None):
        if path is None:
            return
        if path.endswith(".mid"):
            self.load_song(path)
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

    def draw(self, output_file=None, save_file=True, show_image=False):
        xplots = 3
        yplots = 3

        if output_file is None:
            output_file = os.path.join(utils.OUTPUT_ROOT, "tonnetzImages", f"{self.to_song_id()}-tonnetz.png")

        fig, axes = plt.subplots(xplots, yplots, figsize=(20, 20))

        idx = 0
        for track in self.tracks:
            if idx >= xplots * yplots: break
            ax = axes[idx // xplots, idx % yplots]
            track.draw(edge_width_adjust=40, ax=ax)
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

