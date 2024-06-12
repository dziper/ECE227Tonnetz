import pretty_midi
from typing import List
import utils
import os
from song import AnalyzedSong
from comparison import simple_compare


def filter_tracks(song: AnalyzedSong, tracks: List[int]):
    original = pretty_midi.PrettyMIDI(utils.to_midi_path(song.to_song_id()))
    tempo = original.get_tempo_changes()[1][0]
    midi = pretty_midi.PrettyMIDI()
    for t in tracks:
        midi.instruments.append(
            original.instruments[song.instrument_indices[t]]
        )

    return midi, tempo


def transfer_tempo(midi, original_tempo, new_tempo):
    tempo_ratio = original_tempo / new_tempo

    # Scale the timing of each note
    for instrument in midi.instruments:
        for note in instrument.notes:
            note.start *= tempo_ratio
            note.end *= tempo_ratio


def transform_songs(from_song, to_song, instrument_match_thresh=0.7):
    compared = simple_compare(from_song, to_song)
    best_instr = compared.get_best_instrument_matches(thresh=instrument_match_thresh)

    midi1, tempo1 = filter_tracks(from_song, [m[0][0] for m in best_instr])
    midi1.write(os.path.join(utils.OUTPUT_ROOT, "transformed", f"{from_song.to_song_id()}<-{to_song.to_song_id()}" + ".mid"))

    for match in best_instr:
        print(f"S1: {from_song.tracks[match[0][0]].instrument} S2: {to_song.tracks[match[0][1]].instrument}, Score {match}")

    midi2, tempo2 = filter_tracks(to_song, [m[0][1] for m in best_instr])
    # Transform!
    for i, instr in enumerate(midi2.instruments):
        instr.program = midi1.instruments[i].program

    transfer_tempo(midi2, tempo2, tempo1)

    midi2.write(os.path.join(utils.OUTPUT_ROOT, "transformed", f"{to_song.to_song_id()}->{from_song.to_song_id()}" + ".mid"))
    return midi1, midi2
