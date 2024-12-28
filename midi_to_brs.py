from pybrs import *
import pretty_midi
import sys
from brs_util import *
from galaxyinstruments import GalaxyInstruments, GalaxyInstrument

AUTO_TEMPO = -1

def auto_tempo(midi_file : pretty_midi.PrettyMIDI):
    tempo_changes = list(set(midi_file.get_tempo_changes()[1]))
    if len(tempo_changes) == 0:
        raise Exception("No tempo found!")
    tempo = tempo_changes[0]
    # check if there are more than one tempos in the song
    if len(tempo_changes) > 1:
        print("Auto selected tempo:", tempo)
    return tempo

def midi_to_brs(file_name, galaxy_insts, tempo=AUTO_TEMPO) -> BRS:
    midi_file = pretty_midi.PrettyMIDI(file_name)
    if tempo == AUTO_TEMPO:
        tempo = auto_tempo(midi_file)
    return pretty_midi_to_brs(midi_file, galaxy_insts, tempo)


def pretty_midi_to_brs(midi_file : pretty_midi.PrettyMIDI, galaxy_insts : GalaxyInstruments, tempo=120) -> BRS:
    brs_file = BRS()
    if tempo == 0:
        raise ZeroDivisionError("Tempo cannot be 0.")
    note_rate = 60 / tempo
    brs_sequence = BRSSequence()
    brs_file.sequences.append(brs_sequence)
    for instrument in midi_file.instruments:
        instrument : pretty_midi.Instrument
        for note in instrument.notes:
            note : pretty_midi.Note
            note_start = round(note.start, 4)
            note_num_kinda = round(note_start / note_rate, 4)
            j = int(note_num_kinda)
            remainder = round(note_start % note_rate, 4)
            if remainder == note_rate:
                remainder = 0
            delay = round(remainder * 48 / note_rate)
            brs_note = BRSNote()
            brs_note.key.set_val(note.pitch)
            length = int(round(note.duration * 48 / note_rate))
            brs_note.length.set_val(length)
            brs_note.delay.set_val(int(delay))
            brs_note.velocity.set_val(note.velocity)
            inst = galaxy_insts.find_inst_by_name(instrument.name)
            if not inst:
                inst = GalaxyInstrument(0,0,instrument.name)
                print("WARN: No instrument found for", instrument.name)
            brs_sequence.add_note(inst.bank_no, inst.program_no, j, brs_note)
        
    brs_sequence.auto_fill()
    return brs_file


def input_float(prompt, default_val):
    while True:
        try:
            inp = input(prompt)
            if inp:
                return float(inp)
            else:
                print("Using default value: ", default_val)
                return default_val
        except:
            print("Value is not a number. Please try again.")
    
if __name__ == '__main__':
    if "-m" in sys.argv:
        manual_tempo_input = True
        sys.argv.remove("-m")
    else:
        manual_tempo_input = False
    if "-ms" in sys.argv:
        manual_subdivide_input = True
        sys.argv.remove("-ms")
    else:
        manual_subdivide_input = False
    if "-smg" in sys.argv:
        game = "smg"
        sys.argv.remove("-smg")
    else:
        game = "smg2"
    if "-ps" in sys.argv:
        player_speed_index = sys.argv.index("-ps") + 1
        player_speed = sys.argv[player_speed_index]
        sys.argv.remove("-ps")
        sys.argv.remove(player_speed)
        player_speed = int(player_speed)
    else:
        player_speed = 13
    if sys.argv[1] == "-o":
        output_file = sys.argv[2]
        input_files = sys.argv[3::]
    else:
        input_files = sys.argv[1::]
        output_file = input_files[0].removesuffix(".mid") + ".brs"
    insts = GalaxyInstruments(game)
    brs = BRS()
    for file in input_files:
        print(file)
        tempo = auto_tempo(pretty_midi.PrettyMIDI(file))
        if manual_tempo_input:
            tempo = input_float("Enter tempo for " + file + " (default " + str(tempo) + "): ", tempo)
        if manual_subdivide_input:
            subdivide_amt = input_float("Enter subdivide amount for " + file + " (default 1): ", 1.0)
        else:
            subdivide_amt = 1
        new_sequence = midi_to_brs(file, insts, tempo * subdivide_amt).sequences[0]
        new_sequence : BRSSequence
        brs.sequences.append(new_sequence)
        spb = 60 / tempo
        print("Tempo:", tempo)
        print("Note count:", new_sequence.noteCount.get_val())
        print("Player Speed:", player_speed)
        song_duration = (new_sequence.noteCount.get_val()) * spb / subdivide_amt
        distance = song_duration * (player_speed * 60)
        print("Estimated distance to retain BPM:", distance)
    with open(output_file, "wb") as f:
        f.write(brs.to_bytes())
        f.flush()
    input("Close the window or press enter...")