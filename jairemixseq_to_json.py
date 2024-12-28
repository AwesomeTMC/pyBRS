import pyjkernel
import sys
from pybrs import *

def main():
    if len(sys.argv) < 1:
        print("You must pass the .arc as an argument.")
        return
    filename = sys.argv[1]
    if not filename.endswith(".arc"):
        print("Input file must be a .arc")
        return
    output_path = filename.removesuffix(".arc") + ".json"
    if len(sys.argv) == 3:
        output_path = sys.argv[2]
    file = None
    try:
        arc = pyjkernel.from_archive_file(filename)
        file = arc.get_file("brs/defaultremixseq.brs")
    except Exception as e:
        print("Failed to load archive. Full error:")
        print(str(e))
        return
    if file:
        brs = BRS()
        brs.from_bytes(file.data)
        # class -> json
        with open(output_path, "w", encoding="ascii") as f:
            json.dump(brs.write_json(), f, indent=4)
            f.flush()

if __name__ == '__main__':
    main()