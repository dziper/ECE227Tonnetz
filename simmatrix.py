import comparison
import sys
import os
import utils
import pickle

def main():
    songs = sorted(os.listdir(os.path.join(utils.OUTPUT_ROOT, "songPickles")))
    total = len(os.listdir(os.path.join(utils.OUTPUT_ROOT, "songPickles")))
    print(total)

    from_idx = int(sys.argv[1])
    to_idx = int(sys.argv[2])

    sim_mat = comparison.compute_sim_portion(songs, comparison.simple_compare, from_idx, to_idx)
    with open(os.path.join(utils.OUTPUT_ROOT, f"sim_matrix-{from_idx}-{to_idx}.pickle"), "wb") as handle:
        pickle.dump(sim_mat, handle, pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    main()
