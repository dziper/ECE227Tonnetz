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
    
    
    def _get_measures(self) -> list:
        if self.time_signatures:
            time_signature = self.time_signatures[0]
            numerator = time_signature.numerator
            # denominator = time_signature.denominator
        else:
            numerator = 4  # default to 4/4 time
            # denominator = 4

        if self.tempos:
            tempo = self.tempos[0].tempo
        else:
            tempo = 500000  # default to 120 BPM

        ticks_per_beat = self.midi_file.ticks_per_beat
        measure_length_sec = self._measure_length_in_seconds(numerator, tempo)
        quarter_length_sec = round(measure_length_sec / 4, 6)
        
        current_sec = 0
        current_measure = []
        measures = []

        # Iterate through the MIDI file to find all measures
        for msg in self.midi_file:
            # Check for tempo change
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            
            # Check for time signature change
            elif msg.type == 'time_signature':
                numerator = msg.numerator
                measure_length_sec = self._measure_length_in_seconds(numerator, tempo)
                quarter_length_sec = measure_length_sec / 4
            
            if (msg.type != 'note_on' and msg.type != 'note_off'): continue
            
            
            # If we reach the end of a measure, save the measure and reset
            if round(current_sec + msg.time, 6) >= quarter_length_sec:
                measures.append(current_measure)
                # print("append!!!")
                current_measure = []
                current_sec -= quarter_length_sec
                continue
            
            # Update the current tick count
            current_sec += msg.time
            
            # Add the message to the current measure
            current_measure.append(msg)

        # If there are remaining messages, add them as the last measure
        if current_measure:
            measures.append(current_measure)
        
        return measures