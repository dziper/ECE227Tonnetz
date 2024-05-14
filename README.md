# ECE227Tonnetz
Research project for ECE 227

### Get MIDI files for lots of songs

### Parse note/chord data from MIDI files
- Need to decide what data to get (just notes, chords, instrumentation)

### Encode each MIDI file into a graph
- Want to encode something meaningful about the song into the graph, to be able to compare different songs
- Transition probabilities between notes on circle of fifths
- Representing time series of music?
	- Represent each measure as one little graph? 
		- This gives us `n` graphs (assuming song is `n` measures)
	- Look at the first quarter note of each measure, and encode their relationships with surrounding notes in a graph 
		- This gives us `4` graphs for the entire song (maybe easier to compare with other songs)


### Graph Analysis
- Using Tonnetz Graph?
	- XY distance of notes as layed out on Tonnetz can give a (informative?) distance metric between two notes
	- Encodes circle of thirds, fourths, and fifths distance


### Quantify Distance between two Songs/Graphs


### Cluster Similar Songs/Graphs


