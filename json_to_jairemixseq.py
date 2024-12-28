import pyjkernel
import sys
from pybrs import *

def main():
    if len(sys.argv) < 1:
        print("You must pass the .json as an argument.")
        return
    filename = sys.argv[1]
    if not filename.endswith(".json"):
        print("Input file must be a .json.")
        return
    output_path = filename.removesuffix(".json") + ".arc"
    if len(sys.argv) == 3:
        output_path = sys.argv[2]
    new_brs = BRS()
    with open(filename, "r", encoding="ascii") as f:
        entry = json.load(f)
    new_brs.read_json(entry)

    arc = pyjkernel.create_new_archive("brs")
    arc.create_file("brs/defaultremixseq.brs", new_brs.to_bytes())
    pyjkernel.write_archive_file(arc, output_path, True, pyjkernel.JKRCompression.SZS)

if __name__ == '__main__':
    main()