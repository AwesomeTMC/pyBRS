import sys
from pybrs import *
from galaxyinstruments import GalaxyInstruments
from brs_to_midi import brs_sequence_to_midi
import pyjkernel.jkrarchive as jkr

def main():
    # parse args
    if "-m" in sys.argv:
        manual_tempo_input = True
        sys.argv.remove("-m")
    else:
        manual_tempo_input = False
    if "-smg" in sys.argv:
        game = "smg"
        sys.argv.remove("-smg")
    else:
        game = "smg2"
    if len(sys.argv) < 1:
        print("You must pass the .arc as an argument.")
        return
    filename = sys.argv[1]
    if not filename.endswith(".arc"):
        print("Input file must be a .arc")
        return
    output_path = filename.removesuffix(".arc")

    if len(sys.argv) == 3:
        output_path = sys.argv[2]

    # get brs data from arc
    arc = jkr.from_archive_file(filename)
    file = arc.get_file("brs/defaultremixseq.brs")
    brs = BRS()
    brs.from_bytes(file.data)
    insts = GalaxyInstruments(game)
    i = 0
    for brs_sequence in brs.sequences:
        if manual_tempo_input:
            tempo = int(input("Enter the tempo for MIDI " + str(i) + ": "))
        else:
            tempo = 120
        brs_sequence_to_midi(brs_sequence, tempo, insts).write(output_path.removesuffix(".mid") + "_" + str(i) + ".mid")
        i += 1
if __name__ == "__main__":
    main()