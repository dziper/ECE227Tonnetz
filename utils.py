import math

NOTE_LOOKUP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

MIDI_START_NOTE = 21
MIDI_START_OCTAVE = 0

def num_to_note(note_num: int) -> str:
    norm_note = note_num - MIDI_START_NOTE + (57 - 48)  # A3 - C3
    curr_octave = math.floor(norm_note / len(NOTE_LOOKUP)) - MIDI_START_OCTAVE
    return f"{NOTE_LOOKUP[norm_note % len(NOTE_LOOKUP)]}{curr_octave}"

