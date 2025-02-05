import xml.etree.ElementTree as ET

def parse_musicxml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    notation_data = []  # Nested list to store measures

    for part in root.findall("part"):
        for measure in part.findall("measure"):
            measure_data = []  # Store events for this measure

            # Check for attributes (clef, key, time, etc.)
            attributes = measure.find("attributes")
            if attributes is not None:
                # Clef
                clef = attributes.find("clef")
                if clef is not None:
                    sign = clef.find("sign").text
                    line = clef.find("line").text
                    measure_data.append(f"clef-{sign}{line}")

                # Key Signature
                key = attributes.find("key")
                if key is not None:
                    fifths = key.find("fifths").text
                    key_name = {  # Reverse mapping of fifths to key
                        "-4": "AbM", "-3": "EbM", "-2": "BbM", "-1": "FM",
                        "0": "CM", "1": "GM", "2": "DM", "3": "AM",
                        "4": "EM", "5": "BM", "6": "F#M", "7": "C#M"
                    }.get(fifths, "CM")
                    measure_data.append(f"keySignature-{key_name}")

                # Time Signature
                time = attributes.find("time")
                if time is not None:
                    beats = time.find("beats").text
                    beat_type = time.find("beat-type").text
                    measure_data.append(f"timeSignature-{beats}/{beat_type}")

                # Multirest
                measure_style = attributes.find("measure-style")
                if measure_style is not None:
                    multirest = measure_style.find("multiple-rest")
                    if multirest is not None:
                        measure_data.append(f"multirest-{multirest.text}")

            # Process notes & rests
            for note in measure.findall("note"):
                is_rest = note.find("rest") is not None

                # Duration & Type
                duration = int(note.find("duration").text)
                note_type = note.find("type").text
                dotted = len(note.findall("dot"))

                # Reverse lookup for duration
                duration_map = {
                    ("whole", 0): "_whole", ("whole", 1): "_whole.",
                    ("half", 0): "_half", ("half", 1): "_half.",
                    ("quarter", 0): "_quarter", ("quarter", 1): "_quarter.",
                    ("eighth", 0): "_eighth", ("eighth", 1): "_eighth.",
                    ("16th", 0): "_sixteenth", ("16th", 1): "_sixteenth."
                }
                duration_label = duration_map.get((note_type, dotted), f"_{note_type}")

                if is_rest:
                    measure_data.append(f"rest{duration_label}")
                else:
                    # Pitch information
                    pitch = note.find("pitch")
                    step = pitch.find("step").text
                    octave = pitch.find("octave").text
                    alter = pitch.find("alter")
                    alter_value = int(alter.text) if alter is not None else 0

                    # Reverse lookup for pitch alteration
                    alter_map = {0: "", 1: "#", -1: "b"}
                    pitch_name = f"{step}{alter_map[alter_value]}{octave}"

                    measure_data.append(f"note-{pitch_name}{duration_label}")

            notation_data.append(measure_data)

    return notation_data

# Example usage:
# notation = parse_musicxml("example.xml")
# print(notation)
