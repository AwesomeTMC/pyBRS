from midi_to_brs import *
import pyjkernel.jkrarchive as jkr
import pyjkernel

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
        output_file = input_files[0].removesuffix("_0.mid") + ".arc"
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
    arc = jkr.create_new_archive("brs")
    arc.create_file("brs/defaultremixseq.brs", brs.to_bytes())
    jkr.write_archive_file(arc, output_file, True, pyjkernel.JKRCompression.SZS)
    input("Close the window or press enter...")