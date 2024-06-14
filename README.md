# ECE 227 Tonnetz Project
Daniel Ziper: dziper@ucsd.edu, Ying-Jieh Xia: yix050@ucsd.edu

### Contents
This repo contains many Jupyter Notebooks with our experimentation and research process for this project, as well as a few python utilities written for visualization and analysis

Here are the most interesting/important files in this repo
- `finalAnalysis.ipynb`: Code to generate and visualize final results for our research paper
  - Uses preanalyzed songs and precomputed similarity matrix
  - Contains similarity matrix visualization, clustering attempts, song transformation, and artist influence.
- `simpleAnalysis.ipynb`: `finalAnalysis` but run with less data.
- Experimentation
  - `SongAnalysis.ipynb`/`Tonnetz.ipynb` experimentation with analysis and generating Tonnetz graphs
  - `networkx.ipynb` experimentation with network metrics
- Python File utilities
  - `song.py`: contains `AnalyzedSong` class, which generates Tonnetz graphs from a midi file
  - `tonnetz.py`: used to draw and generate Tonnetz graphs from sequence of notes
  - `comparison.py`: Compares songs and computes similarity matrix
  - `transform.py`: Song transformation

### Setup

1. Download the [Clean Midi dataset](https://colinraffel.com/projects/lmd/) to `data/clean_midi` (or use `download_dataset.sh`)
2. `pip install pretty_midi networkx mido` 

### Resources

- We used [APPlayMIDI](https://github.com/benwiggy/APPlayMIDI) to easily play MIDI files on MacOS