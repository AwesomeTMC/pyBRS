import sys
from pybrs import *

def main():
    if len(sys.argv) < 1:
        print("You must pass the .brs as an argument.")
        return
    filename = sys.argv[1]
    if not filename.endswith(".brs"):
        print("Input file must be a .brs")
        return
    output_path = filename.removesuffix(".brs") + ".json"
    if len(sys.argv) == 3:
        output_path = sys.argv[2]
    data = None
    with open(filename, "rb") as f:
        data = f.read()
    if data:
        brs = BRS()
        brs.from_bytes(data)
        # class -> json
        with open(output_path, "w", encoding="ascii") as f:
            json.dump(brs.write_json(), f, indent=4)
            f.flush()

if __name__ == '__main__':
    main()