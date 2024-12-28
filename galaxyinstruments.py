import csv

def make_icode(bank_no, program_no):
    return f"#{bank_no:02x}{program_no:02x}"

class GalaxyInstrument:
    def __init__(self, bank_no, program_no, name):
        self.bank_no = bank_no
        self.program_no = program_no
        self.name = name
    def get_icode(self):
        return make_icode(self.bank_no, self.program_no)
    def __str__(self):
        return self.get_icode() + " " + self.name

class GalaxyInstruments:
    def __init__(self, game="smg2"):
        self.data = []
        with open(game + "insts.csv", "r") as f:
            reader = csv.reader(f)
            for lines in reader:
                self.data.append(GalaxyInstrument(int(lines[0], 16), int(lines[1], 16), lines[2]))
    def find_inst_by_bank_prog(self, bank, prog) -> GalaxyInstrument:
        for inst in self.data:
            if inst.bank_no == bank and inst.program_no == prog:
                return inst
        return GalaxyInstrument(bank, prog, "")
    def find_inst_by_name(self, name: str) -> GalaxyInstrument:
        if name.startswith("#"):
            bank = int(name[1:3], 16)
            prog = int(name[3:5], 16)
            return self.find_inst_by_bank_prog(bank, prog)
        for inst in self.data:
            if inst.name.lower() == name.lower():
                return inst
        return None
    