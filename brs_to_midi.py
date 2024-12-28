from pybrs import *
import pretty_midi
from brs_util import *
import sys
from galaxyinstruments import GalaxyInstruments, make_icode

def add_instrument(midi : pretty_midi.PrettyMIDI, bank_no, prog_no, galaxy_instruments: GalaxyInstruments):
    for inst in midi.instruments:
        inst : pretty_midi.Instrument
        if inst.program == prog_no:
            return inst
    
    inst = pretty_midi.Instrument(prog_no, False, str(galaxy_instruments.find_inst_by_bank_prog(bank_no, prog_no)))
    inst.control_changes.append(pretty_midi.ControlChange(0, bank_no, 0)) # bank no change
    midi.instruments.append(inst)
    return inst

def brs_sequence_to_midi(brs_sequence, tempo, galaxy_instruments) -> pretty_midi.PrettyMIDI:
    if tempo <= 0:
        raise ZeroDivisionError("Tempo must be positive.")
    note_rate = 60 / tempo
    file = pretty_midi.PrettyMIDI()
    for brs_track in brs_sequence.tracks:
        brs_track : BRSTrack
        bank_no = brs_track.bank_no.get_val()
        prog_no = brs_track.program_no.get_val()
        instrument = add_instrument(file, bank_no, prog_no, galaxy_instruments)
        j = 0
        for brs_note in brs_track.notes:
            brs_note : BRSNote
            current_time = j * note_rate
            brs_note_key = brs_note.key.get_val()
            brs_note_time = brs_note.length.get_val()
            brs_note_delay = brs_note.delay.get_val()
            if brs_note_delay > 0:
                current_time += brs_note_delay / 48 * note_rate
            if brs_note_key > -1:
                instrument.notes.append(pretty_midi.Note(brs_note.velocity.get_val(), brs_note_key, current_time, current_time + brs_note_time / 48 * note_rate))
            j += 1
    return file

def main():
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
        print("You must pass the .brs as an argument.")
        return
    filename = sys.argv[1]
    if not filename.endswith(".brs"):
        print("Input file must be a .brs")
        return
    output_path = filename.removesuffix(".brs")

    if len(sys.argv) == 3:
        output_path = sys.argv[2]

    brs = BRS(filename)
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