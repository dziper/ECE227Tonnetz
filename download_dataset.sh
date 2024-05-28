#!/bin/bash
mkdir -p data
cd data
curl http://hog.ee.columbia.edu/craffel/lmd/clean_midi.tar.gz > clean_midi.tar.gz
tar -xf clean_midi.tar.gz
