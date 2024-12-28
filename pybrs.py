import struct
import json
import brs_util

def unpack_s32(buffer, offset):
    return struct.unpack_from(">i", buffer, offset)[0]
def pack_s32(val):
    return struct.pack(">i", val)
def unpack_u32(buffer, offset):
    return struct.unpack_from(">I", buffer, offset)[0]
def pack_u32(val):
    return struct.pack(">I", val)
def unpack_u8(buffer, offset):
    return struct.unpack_from("B", buffer, offset)[0]
def pack_u8(val):
    return struct.pack("B", val)

class TypedChunk():
    # Initialize Typed Chunk
    def __init__(self, name, default_val = None):
        self.name = name
        self.val = default_val
        self.size = 0
        
    def from_bytes(self, buffer, offset: int = 0):
        raise NotImplementedError("Not implemented from base class")
    # Add data to json object
    def to_json(self, obj: dict):
        obj[self.name] = self.val
    def to_bytes(self) -> bytes:
        raise NotImplementedError("Not implemented from base class")
    def from_json(self, entry):
        raise NotImplementedError("Not implemented from base class")
    def get_val(self): 
        return self.val
    def get_size(self):
        return self.size
    def set_val(self, new_val):
        self.val = new_val

class U32Chunk(TypedChunk):
    def __init__(self, name, default_val=0):
        super().__init__(name, default_val)
        self.size = 4
    def from_bytes(self, buffer, offset: int = 0):
        self.val = unpack_u32(buffer, offset)
        return self.val
    def to_bytes(self) -> bytes:
        return pack_u32(self.val)
    def from_json(self, entry):
        self.val = entry[self.name]
    def set_val(self, new_val):
        if (self.val > 4294967295):
            self.val = 4294967295
        elif (self.val < 0):
            self.val = 0
        else:
            self.val = new_val
class S32Chunk(TypedChunk):
    def __init__(self, name, default_val=0):
        super().__init__(name, default_val)
        self.size = 4
    def from_bytes(self, buffer, offset: int = 0):
        self.val = unpack_s32(buffer, offset)
        return self.val
    def to_bytes(self) -> bytes:
        return pack_s32(self.val)
    def from_json(self, entry):
        self.val = entry[self.name]
    def set_val(self, new_val):
        if (self.val > 2147483647):
            self.val = 2147483647
        elif (self.val < -2147483648):
            self.val = -2147483648
        else:
            self.val = new_val

class U8Chunk(TypedChunk):
    def __init__(self, name, default_val=0):
        super().__init__(name, default_val)
        self.size = 1
    def from_bytes(self, buffer, offset: int = 0):
        self.val = unpack_u8(buffer, offset)
    def to_bytes(self) -> bytes:
        return pack_u8(self.val)
    def from_json(self, entry):
        self.val = entry[self.name]
    def set_val(self, new_val):
        if (self.val > 255):
            self.val = 255
        elif (self.val < 0):
            self.val = 0
        else:
            self.val = new_val

class BRSNote:
    """A note, with the key to play, the velocity of it, the length to play it for, and the delay 
    after the corresponding rainbow note is collected. Time related variables are in frames (60 frames = 1 second).
    If the key to play is -1, no note will be played on its track when the rainbow note is collected."""
    def __init__(self):
        """Initializes the key (-1), velocity (0), length (0), and delay (0)."""
        self.key = S32Chunk("Key", -1)
        self.velocity = U32Chunk("Velocity")
        self.length = U32Chunk("Length")
        self.delay = U32Chunk("Delay")
    def from_bytes(self, data, offset):
        self.key.from_bytes(data, offset)
        self.velocity.from_bytes(data, offset + 0x4)
        self.length.from_bytes(data, offset + 0x8)
        self.delay.from_bytes(data, offset + 0xC)
    def to_json(self):
        obj = {}
        self.key.to_json(obj)
        self.velocity.to_json(obj)
        self.length.to_json(obj)
        self.delay.to_json(obj)
        return obj
    def from_json(self, entry):
        self.key.from_json(entry)
        self.velocity.from_json(entry)
        self.length.from_json(entry)
        self.delay.from_json(entry)
    def to_bytes(self) -> bytes:
        data = bytearray()
        data += self.key.to_bytes()
        data += self.velocity.to_bytes()
        data += self.length.to_bytes()
        data += self.delay.to_bytes()
        return data

class BRSTrack:
    """A track with notes and the track's instrument."""
    def __init__(self):
        self.bank_no = U8Chunk("BankNo")
        self.program_no = U8Chunk("ProgramNo")
        self.notes = []
    def from_bytes(self, data, offset, note_count):
        """Reads in the BRSTrack bytes, with note_count representing the number of notes in the track."""
        offset += 2
        self.bank_no.from_bytes(data, offset)
        offset += 1
        self.program_no.from_bytes(data, offset)
        offset += 1
        self.notes = []
        for i in range(note_count):
            note = BRSNote()
            note.from_bytes(data, offset)
            self.notes.append(note)
            offset += 0x10
    def to_json(self):
        obj = {}
        self.bank_no.to_json(obj)
        self.program_no.to_json(obj)
        notes_json = []
        for x in self.notes:
            notes_json.append(x.to_json())
        obj["Notes"] = notes_json
        return obj
    def from_json(self, entry):
        self.bank_no.from_json(entry)
        self.program_no.from_json(entry)
        self.notes = []
        for x in entry["Notes"]:
            note = BRSNote()
            note.from_json(x)
            self.notes.append(note)
    def to_bytes(self):
        data = bytearray()
        data += pack_u8(0)
        data += pack_u8(0)
        data += self.bank_no.to_bytes()
        data += self.program_no.to_bytes()
        for x in self.notes:
            data += x.to_bytes()
        return data
    def insert_note(self, index : int, note):
        # to insert it at 2, len(brs_notes) must be at least 3.
        while len(self.notes) <= index:
            self.notes.append(BRSNote())
        if self.notes[index].key.get_val() == -1:
            self.notes[index] = note
            return True
        else:
            return False

class BRSSequence:
    """
    A container of tracks. Each BRSSequence is one Rainbow Notes song.
    The NoteCount dictates the length of the unused note array and how many
    notes are in each track.
    """
    def __init__(self):
        """Initializes this BRSSequence with a note count of 0 and an empty unused note array and track array."""
        self.noteCount = U32Chunk("NoteCount")
        self.unused_note_array = []
        self.tracks = []
    def from_bytes(self, data, offset=0):
        track_count = unpack_u32(data, offset)
        offset += 4
        note_count = self.noteCount.from_bytes(data, offset)
        offset += 4
        self.unused_note_array = []
        for i in range(note_count):
            self.unused_note_array.append(unpack_u32(data, offset))
            offset += 4
        self.tracks = []
        for i in range(track_count):
            track = BRSTrack()
            track.from_bytes(data, offset, note_count)
            self.tracks.append(track)
            offset += note_count * 0x10 + 4

    def to_json(self):
        obj = {}
        self.noteCount.to_json(obj)
        obj["UnusedNoteArray"] = self.unused_note_array
        tracks_json = []
        for x in self.tracks:
            tracks_json.append(x.to_json())
        obj["Tracks"] = tracks_json
        return obj
    def from_json(self, entry):
        self.noteCount.from_json(entry)
        self.unused_note_array = entry["UnusedNoteArray"]
        self.tracks = []
        for x in entry["Tracks"]:
            track = BRSTrack()
            track.from_json(x)
            self.tracks.append(track)
    def to_bytes(self) -> bytes:
        data = bytearray()
        data += pack_u32(len(self.tracks))
        data += self.noteCount.to_bytes()
        for x in self.unused_note_array:
            data += pack_s32(x)
        for x in self.tracks:
            data += x.to_bytes()
        return data
    
    def auto_fill(self):
        """
        Uses the track with the most amount of notes as a 
        basis for the number of notes in the song.
        Sets the note count, the unused note array, and fills in
        each track that does not have enough notes with notes that
        don't play anything.
        Since all tracks must have the same note count, this is recommended.
        Returns whether or not it was successful.
        """
        # Cannot calculate note count if there are no tracks
        if len(self.tracks) == 0:
            return False
        
        # Find track with most notes, set max_count accordingly
        max_count = 0
        for track in self.tracks:
            track : BRSTrack
            count = len(track.notes)
            if count > max_count:
                max_count = count
        
        # Set noteCount to the new count
        self.noteCount.set_val(max_count)

        brs_util.fill_until_length(self.unused_note_array, 48, max_count)
        
        # fill tracks with empty notes
        for track in self.tracks:
            brs_util.fill_until_length(track.notes, BRSNote(), max_count)
        return True
    
    def add_note(self, bank_no: int, program_no: int, index : int, brs_note : BRSNote):
        # see if a track already exists with space
        i = 0
        for track in self.tracks:
            track : BRSTrack
            # make sure the track has the bank_no and program_no we're looking for
            if track.bank_no.get_val() != bank_no or track.program_no.get_val() != program_no:
                if len(track.notes) > index and track.notes[index].key.get_val() != -1:
                    i += 1
                continue
            # if there's no space, keep trying with another track.
            if not track.insert_note(index, brs_note):
                i += 1
                continue
            if i > 15:
                print("WARN: Notes may be cut off. Subdividing may fix this.")
            # successfully added using insert_note
            return
        
        # track does not exist. time to make a new one
        new_track = BRSTrack()
        new_track.bank_no.set_val(bank_no)
        new_track.program_no.set_val(program_no)
        new_track.insert_note(index, brs_note)
        self.tracks.append(new_track)
        

class BRS:
    """A full BRS file. Contains several BRSSequences within."""

    def __init__(self, file_path=None):
        self.sequences = []
        if file_path:
            self.from_file(file_path)

    def from_bytes(self, data):
        # set up sequence offsets
        offset = 0
        sequence_offsets = []
        sequence_num = unpack_u32(data, offset)
        offset += 4
        for i in range(sequence_num):
            sequence_offsets.append(unpack_u32(data, offset))
            offset += 4
        sequence_offsets.append(len(data))

        self.sequences = []
        # read each sequence
        for i in range(sequence_num):
            brs_sequence = BRSSequence()
            brs_sequence.from_bytes(data[sequence_offsets[i]:sequence_offsets[i + 1]])
            self.sequences.append(brs_sequence)

    def read_json(self, json):
        self.sequences = []
        for entry in json:
            sequence = BRSSequence()
            sequence.from_json(entry)
            self.sequences.append(sequence)

    def to_bytes(self) -> bytes:
        data = bytearray()
        # set up sequence offsets
        data += pack_u32(len(self.sequences)) # _0 - sequence count
        sequence_offset = len(self.sequences) * 4 + 4
        packed_sequences = []
        for x in self.sequences:
            data += pack_u32(sequence_offset)
            seq_data = x.to_bytes()
            packed_sequences.append(seq_data)
            sequence_offset += len(seq_data)
        for x in packed_sequences:
            data += x
        return data
    def write_json(self):
        obj = []
        for sequence in self.sequences:
            obj.append(sequence.to_json())
        return obj
    def from_file(self, file_path):
        data = None
        with open(file_path, "rb") as f:
            data = f.read()
        self.from_bytes(data)
