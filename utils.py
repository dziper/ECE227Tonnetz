import math
import py_midicsv as pm
import csv

NOTE_LOOKUP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

MIDI_START_NOTE = 21
MIDI_START_OCTAVE = 0

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
