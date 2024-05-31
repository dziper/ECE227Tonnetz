import mido

class MidiFile:
    def __init__(self, midi_file: str):
        self.midi_file = mido.MidiFile(midi_file, clip=True)
        self.time_signatures = self._get_time_signatures()
        self.tempos = self._get_tempos()
        self.measures = self._get_measures()
    
    def _get_time_signatures(self) -> list:
        time_signatures = []
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.type == 'time_signature':
                    time_signatures.append(msg)
        
        return time_signatures
    
    def _get_tempos(self) -> list:
        tempos = []
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempos.append(msg)
        
        return tempos
    
    
    # Function to get the length of a measure in seconds
    def _measure_length_in_seconds(self, numerator, tempo):
    
        # Calculate beats per minute (BPM)
        bpm = 60000000 / tempo
        
        # Calculate beats per measure
        beats_per_measure = numerator
        
        # Calculate duration of one beat in seconds
        beat_duration_seconds = 60 / bpm
        
        # Calculate length of one measure in seconds
        measure_length_seconds = beats_per_measure * beat_duration_seconds
        
        return measure_length_seconds
    
    
    def ticks_per_measure(self, ticks_per_beat, numerator, denominator):
        beats_per_measure = numerator
        beat_length = 4 / denominator  # 4 is the default whole note length in MIDI
        return ticks_per_beat * beats_per_measure * beat_length
    
    
    def get_measures(self):
        ticks_per_beat = self.midi_file.ticks_per_beat
        current_ticks_per_measure = self.ticks_per_measure(ticks_per_beat, 4, 4)  # Default to 4/4 time signature
        current_tick = 0
        measures = []
        current_measure = []
        
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.is_meta:
                    if msg.type == 'time_signature':
                        numerator = msg.numerator
                        denominator = msg.denominator
                        current_ticks_per_measure = self.ticks_per_measure(ticks_per_beat, numerator, denominator)
                    elif msg.type == 'set_tempo':
                        tempo = msg.tempo
                        # Tempo changes could be handled here if needed, but are usually not necessary for measure splitting
                else:
                    current_measure.append(msg)
                
                current_tick += msg.time
                
                if current_tick >= current_ticks_per_measure:
                    measures.append(current_measure)
                    current_measure = []
                    current_tick -= current_ticks_per_measure  # Carry over the extra ticks to the next measure
            
            if current_measure:
                measures.append(current_measure)
        
        return measures