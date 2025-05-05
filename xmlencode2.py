import music21 as ml
from music21.clef import PitchClef

# Duration dictionary
note_time_dict = {
    "_quarter": [1, "quarter", 0],
    "_quarter.": [1.5, "quarter", 1],
    "_quarter..": [1.75, "quarter", 2],
    "_half": [2, "half", 0],
    "_half.": [3, "half", 1],
    "_half..": [3.5, "half", 2],
    "_whole": [4, "whole", 0],
    "_whole.": [6, "whole", 1],
    "_whole..": [7, "whole", 2],
    "_eighth": [0.5, "eighth", 0],
    "_eighth.": [0.75, "eighth", 1],
    "_eighth..": [0.875, "eighth", 2],
    "_16th": [0.25, "16th", 0],
    "_16th.": [0.375, "16th", 1],
    "_16th..": [0.4375, "16th", 2],
    "_32nd": [0.125, "32nd", 0],
    "_32nd.": [0.1875, "32nd", 1],
    "_32nd..": [0.21875, "32nd", 2],
}

# Clef dictionary: (sign, line)
clef_dict = {
    "clef-G2": ("G", 2),
    "clef-F4": ("F", 4),
    "clef-C1": ("C", 1),
    "clef-C3": ("C", 3),
    "clef-C4": ("C", 4),
}
key_sign_dict = {
    "keySignature-AbM": [-4,"major"],
    "keySignature-AM":  [3,"major"],
    "keySignature-BbM": [-2,"major"],
    "keySignature-BM":  [5, "major"],
    "keySignature-CM":  [0,"major"],
    "keySignature-C#M": [7,"major"],
    "keySignature-DbM": [-5,"major"],
    "keySignature-DM":  [2,"major"],
    "keySignature-EbM": [-3,"major"],
    "keySignature-EM":  [4,"major"],
    "keySignature-FM":  [-1,"major"],
    "keySignature-F#M": [6,"major"],
    "keySignature-GbM": [-6,"major"],
    "keySignature-GM":  [1,"major"]

}
# Time signatures
time_sign_dict = {
    "4/4": "4/4",
    "3/4": "3/4",
    "2/4": "2/4",
    "6/8": "6/8",
    "12/8": "12/8",
    "9/8": "9/8",
    "C/": "C",  # Common time
}

def create_musicxml(nested_notation):
    score = ml.stream.Score()
    part = ml.stream.Part()
    measure_number = 1
    first_measure = True

    for measure in nested_notation:
        current_measure = ml.stream.Measure(number=measure_number)

        for command in measure:
            # Handle clef (only in the first measure it appears)
            if command.startswith('clef-') and first_measure:
                clef_type = clef_dict.get(command)
                if clef_type:
                    clef = PitchClef()
                    clef.sign = clef_type[0]
                    clef.line = clef_type[1]
                    current_measure.append(clef)
            if command.startswith("keySignature-") and first_measure:
                key_type = key_sign_dict.get(command)
                if key_type:
                    sign_key = key_type[0]
                    key = ml.key.KeySignature(sign_key)
                    current_measure.append(key)

            # Handle time signature (only in the first measure it appears)
            elif command.startswith('timeSignature-') and first_measure:
                ts_value = command.split('-')[1]
                if ts_value in time_sign_dict:
                    current_measure.append(ml.meter.TimeSignature(time_sign_dict[ts_value]))

            # Handle notes
            elif command.startswith('note-'):
                base, duration_str = command[5:].split('_', 1)
                pitch = base  # Example: E3, F#3, Bb2
                n = ml.note.Note(pitch)
                dur_info = note_time_dict.get(f'_{duration_str}')
                if dur_info:
                    n.quarterLength = dur_info[0]
                current_measure.append(n)

            # Handle rests
            elif command.startswith('rest-'):
                _, duration_str = command.split('-', 1)
                dur_info = note_time_dict.get(f'_{duration_str}')
                if dur_info:
                    r = ml.note.Rest()
                    r.quarterLength = dur_info[0]
                    current_measure.append(r)

        part.append(current_measure)
        first_measure = False
        measure_number += 1

    score.append(part)
    return score.write('musicxml', fp='C:/Users/Edwin/Documents/blahblah.musicxml')


# Sample phrase input
phrase = [
    ['clef-F4', "keySignature-CM",'timeSignature-4/4', 'note-E3_quarter', 'note-E3_half', 'note-D3_quarter'],
    ['note-E3_half', 'note-D3_quarter', 'note-A2_quarter'],
    ['note-C3_half', 'note-B2_quarter', 'note-G3_quarter'],
    ['note-F3_half', 'note-F3_half'],
    ['clef-F4', 'timeSignature-C/', 'note-D3_half', 'note-E3_quarter', 'note-A2_quarter'],
    ['note-G3_quarter', 'note-A2_quarter', 'note-Bb2_quarter', 'note-F3_quarter'],
    ['note-G3_half', 'note-A2_quarter', 'note-D3_quarter'],
    ['note-G3_half', 'note-E3_half']
]

create_musicxml(phrase)
