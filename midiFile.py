import mido

class MidiFile:
    def __init__(self, midi_file: str):
        self.midi_file = mido.MidiFile(midi_file, clip=True)
        self.time_signatures = self._get_time_signatures()
        self.tempos = self._get_tempos()
        self.measures = self._get_measures()
        self.current_ticks_per_measure
    
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
    
    
    def _ticks_per_measure(self, ticks_per_beat, numerator, denominator):
        beats_per_measure = numerator
        beat_length = 4 / denominator  # 4 is the default whole note length in MIDI
        return ticks_per_beat * beats_per_measure * beat_length
    
    
    def _get_measures(self):
        ticks_per_beat = self.midi_file.ticks_per_beat
        self.current_ticks_per_measure = self._ticks_per_measure(ticks_per_beat, 4, 4)  # Default to 4/4 time signature
        current_tick = 0
        measures = []
        current_measure = []
        
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.is_meta:
                    if msg.type == 'time_signature':
                        numerator = msg.numerator
                        denominator = msg.denominator
                        self.current_ticks_per_measure = self._ticks_per_measure(ticks_per_beat, numerator, denominator)
                    elif msg.type == 'set_tempo':
                        tempo = msg.tempo
                        # Tempo changes could be handled here if needed, but are usually not necessary for measure splitting
                elif msg.type != 'note_on' and msg.type != 'note_off': continue
                else:
                    current_measure.append(msg)
                
                current_tick += msg.time
                
                if current_tick >= self.current_ticks_per_measure:
                    measures.append(current_measure)
                    current_measure = []
                    current_tick -= self.current_ticks_per_measure  # Carry over the extra ticks to the next measure
            
            if current_measure:
                measures.append(current_measure)
        
        return measures