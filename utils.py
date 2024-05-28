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
