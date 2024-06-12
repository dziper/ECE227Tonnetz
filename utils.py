import math
import mido
import py_midicsv as pm
import csv
import networkx as nx
import numpy as np
from tqdm import tqdm
import os

NOTE_LOOKUP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

MIDI_START_NOTE = 21
MIDI_START_OCTAVE = 0

DATA_ROOT = "data/clean_midi/"
OUTPUT_ROOT = "analysis/"

def num_to_note(note_num: int) -> str:
    norm_note = note_num - MIDI_START_NOTE + (57 - 48)  # A3 - C3
    curr_octave = math.floor(norm_note / len(NOTE_LOOKUP)) - MIDI_START_OCTAVE
    return f"{NOTE_LOOKUP[norm_note % len(NOTE_LOOKUP)]}{curr_octave}"


def read_csv_to_strings(file_path: str) -> list:
    lines = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Join each row's elements with commas to form a single string
            line = ','.join(row)
            lines.append(line)
    return lines


def midi_to_csv(midi_file_path: str, save_path: str):
    # Load the MIDI file and parse it into CSV format
    csv_string = pm.midi_to_csv(midi_file_path)

    # Write into csv file
    with open(save_path, "w") as f:
        f.writelines(csv_string)
        
        
def csv_to_midi(csv_file_path: str, save_path: str):
    # Parse the CSV output of the previous command back into a MIDI file
    csv_strings = read_csv_to_strings(csv_file_path)
    midi_object = pm.csv_to_midi(csv_strings)

    # Save the parsed MIDI file to disk
    with open(save_path, "wb") as output_file:
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)


GM_INSTRUMENT_NAMES = [
    "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano",
    "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet", "Celesta", "Glockenspiel",
    "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer", "Drawbar Organ",
    "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",
    "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)",
    "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics", "Acoustic Bass",
    "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1",
    "Synth Bass 2", "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp",
    "Timpani", "String Ensemble 1", "String Ensemble 2", "SynthStrings 1", "SynthStrings 2", "Choir Aahs", "Voice Oohs",
    "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section",
    "SynthBrass 1", "SynthBrass 2", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn",
    "Bassoon", "Clarinet", "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle",
    "Ocarina", "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiffer)", "Lead 5 (charang)",
    "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)", "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)",
    "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)", "FX 1 (rain)", "FX 2 (soundtrack)",
    "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
    "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bagpipe", "Fiddle", "Shanai", "Tinkle Bell", "Agogo",
    "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal", "Guitar Fret Noise",
    "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"
]

MIDI_CHANNEL_COUNT = 16
TRANSITION_COUNT_THRESH = 10


def type_0_track_to_notes(track: mido.MidiTrack):
    channels = [[] for _ in range(MIDI_CHANNEL_COUNT)]  # Max 16 midi channels
    instruments = [None] * MIDI_CHANNEL_COUNT
    last_note = [None] * MIDI_CHANNEL_COUNT
    transitions = [0] * MIDI_CHANNEL_COUNT
    for msg in track:
        if msg.type == "program_change":
            instruments[msg.channel] = GM_INSTRUMENT_NAMES[msg.program]
        if msg.type == "note_on" and msg.velocity != 0:
            channels[msg.channel].append(msg.note)
            if msg.note != last_note[msg.channel - 1]:
                last_note[msg.channel - 1] = msg.note
                transitions[msg.channel - 1] += 1

    for i, tr in enumerate(transitions):
        if tr < TRANSITION_COUNT_THRESH:
            channels[i] = []
    return channels, instruments


def track_to_notes(track: mido.MidiTrack):
    notes = []
    instrument = None
    last_note = None
    transitions = 0
    for msg in track:
        if msg.type == "note_on" and msg.velocity != 0:
            notes.append(msg.note)
            if msg.note != last_note:
                last_note = msg.note
                transitions += 1
        if msg.type == "program_change":
            instrument = GM_INSTRUMENT_NAMES[msg.program]

    if transitions < TRANSITION_COUNT_THRESH: return [], None
    return notes, instrument


def mido_to_notes_and_instr(midi: mido.MidiFile):
    channels = []
    instrs = []
    if midi.type == 2:
        return None, None
    if midi.type == 1:
        for track in midi.tracks:
            notes, instr = track_to_notes(track)
            if len(notes) > 0:
                channels.append(notes)
                instrs.append(instr)
    if midi.type == 0:
        channels, instrs = type_0_track_to_notes(midi.tracks[0])

    return channels, instrs



### Graph similarity ###
### Maybe we can see the two matrices as y_pred and y_true as in machine learning, and use sklearn to get the score?

# Compute the Jaccard similarity for edges
def jaccard_similarity_edge(G1, G2):
    edges_G1 = set(G1.edges())
    edges_G2 = set(G2.edges())
    intersection = edges_G1.intersection(edges_G2)
    union = edges_G1.union(edges_G2)
    return len(intersection) / len(union)

# Compute the cosine similarity between the Laplacian matrices of the graphs
def cos_similarity_laplacian(G1, G2):
    # Laplacian Matrix
    L1 = nx.laplacian_matrix(G1).todense()
    L2 = nx.laplacian_matrix(G2).todense()
    L1_flat = L1.flatten()
    L2_flat = L2.flatten()
    
    # Cosine similarity of Laplacian matrices
    return np.dot(L1_flat, L2_flat) / (np.linalg.norm(L1) * np.linalg.norm(L2))

# Compute the cosine similarity between the Adjacency matrices of the graphs
def cos_similarity_adj(G1, G2):
    # Adjacency matrices
    A1 = nx.adjacency_matrix(G1).todense()
    A2 = nx.adjacency_matrix(G2).todense()
    A1_flat = A1.flatten()
    A2_flat = A2.flatten()
    
    # Compute cosine similarity
    cosine_similarity = np.dot(A1_flat, A2_flat) / (np.linalg.norm(A1_flat) * np.linalg.norm(A2_flat))
    return cosine_similarity


DIST_LOOKUP = {
    (3, 4, 5): [0, 2, 2, 1, 1, 1, 2, 1, 1, 1, 2, 2]
}

def tonnetz_dist(from_note, to_note, intervals=(3, 4, 5)):
    if intervals in DIST_LOOKUP:
        diff = abs(to_note - from_note)
        octave_diff = diff // 12
        # Manhattan distance for 3,4,5
        return octave_diff * 3 + DIST_LOOKUP[intervals][diff % 12]
    else:
        raise ValueError(intervals)


def for_song_in_artist(artist, callback, skip_digits=True, tqdm_disable=False, report_errors=True):
    song_dir = os.path.join(DATA_ROOT, artist)

    for song_name in tqdm(sorted(os.listdir(song_dir)), disable=tqdm_disable):
        if skip_digits and any(char.isdigit() for char in song_name):
            # Skip repeated versions of the song
            continue
        try:
            callback(artist, song_name)
        except Exception as e:
            if report_errors:
                print(f"{song_name}: {e}")


def to_song_id(artist, name):
    return f"{artist}-{name}"


def to_pickle_path(song_id: str):
    if song_id.endswith(".pickle"):
        return os.path.join(OUTPUT_ROOT, "songPickles", f"{song_id}")
    return os.path.join(OUTPUT_ROOT, "songPickles", f"{song_id}.pickle")


def to_draw_path(song_id: str):
    if song_id.endswith(".png"):
        return os.path.join(OUTPUT_ROOT, "tonnetzImages", song_id)
    else:
        return os.path.join(OUTPUT_ROOT, "tonnetzImages", f"{song_id}-tonnetz.png")


def to_midi_path(song_id: str):
    hyphen = song_id.find("-")
    song_id = song_id[:hyphen] + "/" + song_id[hyphen + 1:]
    return os.path.join(DATA_ROOT, song_id + ".mid")
