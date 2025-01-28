import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
# _xxxxx : [d,t,dot]
note_time_dict= {
            "_eighth":       [0.5,"eighth",0],
            "_eighth.":      [0.75,"eighth",1],
            "_eighth..":     [0.875,"eighth",2],
            "_half":         [2,"half",0],
            "_half.":        [3,"half",1],
            "_quarter":      [1,"quarter",0],
            "_quarter.":     [1.5,"quarter",2],
            "_quarter..":    [1.75,"quarter",0],
            "_sixteenth":    [0.25,"16th",0],
            "_sixteenth.":   [0.375,"16th",1],
            "_sixty_fourth": [0.0625,"64th",0],
            "_thirty_second":[0.125,"32nd",0],
            "_whole":        [4,"whole",0],
            "_whole.":       [6,"whole",1]
}
# note-nbd : [step,octave,alter]
note_pitch_dict= {
    "-A1_": ["A",1,0],
    "-A2_": ["A",2,0],
    "-A#2_":["A",2,1],
    "-Ab2_":["A",2,-1],
    "-A3_": ["A",3,0],
    "-A#3_":["A",3,1],
    "-Ab3_":["A",3,-1],
    "-A4_": ["A",4,0],
    "-A#4_":["A",4,1],
    "-Ab4_":["A",4,-1],
    "-A#5_":["A",5,1],
    "-Ab5_":["A",5,0],
    "-B1_": ["B",1,0],
    "-B2_": ["B",2,0],
    "-B#2_":["B",2,1],
    "-Bb2_":["B",2,-1],
    "-B3_": ["B",3,0],
    "-B#3_":["B",3,1],
    "-Bb3_":["B",3,-1],
    "-B4_": ["B",4,0],
    "-B#4_":["B",4,1],
    "-Bb4_":["B",4,-1],
    "-B#5_":["B",5,1],
    "-Bb5_":["B",5,0],
    "-C2_": ["C",2,0],
    "-C#2_":["C",2,1],
    "-Cb2_":["C",2,-1],
    "-C3_": ["C",3,0],
    "-C#3_":["C",3,1],
    "-Cb3_":["C",3,-1],
    "-C4_": ["C",4,0],
    "-C#4_":["C",4,1],
    "-Cb4_":["C",4,-1],
    "-C5_": ["C",5,0],
    "-C#5_":["C",5,1],
    "-Cb5_":["C",5,-1],
    "-C6_": ["C",6,0],
    "-C#6_":["C",6,1],
    "-Cb6_":["C",6,-1],
    "-D2_": ["D",2,0],
    "-D#2_":["D",2,1],
    "-Db2_":["D",2,-1],
    "-D3_": ["D",3,0],
    "-D#3_":["D",3,1],
    "-Db3_":["D",3,-1],
    "-D4_": ["D",4,0],
    "-D#4_":["D",4,1],
    "-Db4_":["D",4,-1],
    "-D5_": ["D",5,0],
    "-D#5_":["D",5,1],
    "-Db5_":["D",5,-1],
    "-D6_": ["D",6,0],
    "-D#6_":["D",6,1],
    "-Db6_":["D",6,-1],
    "-E2_": ["E",2,0],
    "-E#2_":["E",2,1],
    "-Eb2_":["E",2,-1],
    "-E3_": ["E",3,0],
    "-E#3_":["E",3,1],
    "-Eb3_":["E",3,-1],
    "-E4_": ["E",4,0],
    "-E#4_":["E",4,1],
    "-Eb4_":["E",4,-1],
    "-E5_": ["E",5,0],
    "-E#5_":["E",5,1],
    "-Eb5_":["E",5,-1],
    "-E6_": ["E",6,0],
    "-E#6_":["E",6,1],
    "-Eb6_":["E",6,-1],
    "-F2_": ["F",2,0],
    "-F#2_":["F",2,1],
    "-Fb2_":["F",2,-1],
    "-F3_": ["F",3,0],
    "-F#3_":["F",3,1],
    "-Fb3_":["F",3,-1],
    "-F4_": ["F",4,0],
    "-F#4_":["F",4,1],
    "-Fb4_":["F",4,-1],
    "-F5_": ["F",5,0],
    "-F#5_":["F",5,1],
    "-Fb5_":["F",5,-1],
    "-F6_": ["F",6,0],
    "-F#6_":["F",6,1],
    "-Fb6_":["F",6,-1],
    "-G2_":  ["G",2,0],
    "-G#2_":["G",2,1],
    "-Gb2_":["G",2,-1],
    "-G3_":  ["G",3,0],
    "-G#3_":["G",3,1],
    "-Gb3_":["G",3,-1],
    "-G4_": ["G",4,0],
    "-G#4_":["G",4,1],
    "-Gb4_":["G",4,-1],
    "-G5_": ["G",5,0],
    "-G#5_":["G",5,1],
    "-Gb5_":["G",5,-1],
    "-G6_": ["G",6,0],
    "-G#6_":["G",6,1],
    "-Gb6_":["G",6,-1]
}
# rest-nnn : [d,t,dot]
# duration is measured as a multiple of <duration> attribute
# remember to add "rest-eighth_fermata","rest-eighth._fermata","rest-half_fermata","rest-half._fermata","rest-quadruple_whole","rest-quarter_fermata","rest-quarter._fermata","rest-quarter.._fermata","rest-sixteenth_fermata","rest-whole_fermata"
rest_dict = {
            "rest-eighth":       [0.5,"eighth",0],
            "rest-eighth.":      [0.75,"eighth",1],
            "rest-eighth..":     [0.875,"eighth",2],
            "rest-half":         [2,"half",0],
            "rest-half.":        [3,"half",1],
            "rest-quarter":      [1,"quarter",0],
            "rest-quarter.":     [1.5,"quarter",2],
            "rest-quarter..":    [1.75,"quarter",0],
            "rest-sixteenth":    [0.25,"16th",0],
            "rest-sixteenth.":   [0.375,"16th",1],
            "rest-sixty_fourth": [0.0625,"64th",0],
            "rest-thirty_second":[0.125,"32nd",0],
            "rest-whole":        [4,"whole",0],
            "rest-whole.":       [6,"whole",1]
}


time_sign_dict = {
    "timeSignature-11/4": [11,4],
    "timeSignature-1/2":  [1,2],
    "timeSignature-12/16":[12,16],
    "timeSignature-12/4": [12,4],
    "timeSignature-12/8": [12,8],
    "timeSignature-1/4":  [1,3],
    "timeSignature-2/1":  [2,1],
    "timeSignature-2/2":  [2,2],
    "timeSignature-2/3":  [2,3],
    "timeSignature-2/4":  [2,4],
    "timeSignature-24/16":[24,16],
    "timeSignature-2/48": [2,48],
    "timeSignature-2/8":  [2,8],
    "timeSignature-3/1":  [3,1],
    "timeSignature-3/2":  [3,2],
    "timeSignature-3/4":  [3,4],
    "timeSignature-3/6":  [3,6],
    "timeSignature-3/8":  [3,8],
    "timeSignature-4/1":  [4,1],
    "timeSignature-4/2":  [4,2],
    "timeSignature-4/4":  [4,4],
    "timeSignature-4/8":  [4,8],
    "timeSignature-5/4":  [5,4],
    "timeSignature-5/8":  [5,8], 
    "timeSignature-6/16": [6,16],
    "timeSignature-6/2":  [6,2],
    "timeSignature-6/4":  [6,4],
    "timeSignature-6/8":  [6,8],
    "timeSignature-7/4":  [7,4],
    "timeSignature-8/12": [8,12],
    "timeSignature-8/16": [8,16],
    "timeSignature-8/2":  [8,2],
    "timeSignature-8/4":  [8,4],
    "timeSignature-8/8":  [8,8],
    "timeSignature-9/16": [9,16],
    "timeSignature-9/4":  [9,4],
    "timeSignature-9/8":  [9,8],
    "timeSignature-C":    [4,4],
    "timeSignature-C/":   [4,4],
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


clef_dict = {
    "clef-C1": ["C",1],
    "clef-C2": ["C",2],
    "clef-C3": ["C",3], 
    "clef-C4": ["C",4],
    "clef-C5": ["C",5],
    "clef-F3": ["F",3],
    "clef-F4": ["F",4],
    "clef-F5": ["F",5],
    "clef-G1": ["G",1],
    "clef-G2": ["G",2]

}

def create_musicxml(input_notation):
    score_partwise = ET.Element('score-partwise', version="3.1")
    
    # Add part-list section
    part_list = ET.SubElement(score_partwise, 'part-list')
    score_part = ET.SubElement(part_list, 'score-part', id="P1")
    ET.SubElement(score_part, 'part-name').text = "Music"
    
    part = ET.SubElement(score_partwise, 'part', id="P1")
    n = 1
    current_measure = ET.SubElement(part, 'measure', number=str(n))
    total_duration = 0  # Tracks total duration of the current measure
    
    divisions = 8  # Default divisions
    beats_per_measure = None  # To be set from the time signature

    # Add the initial <attributes> tag
    attributes = ET.SubElement(current_measure, "attributes")
    ET.SubElement(attributes, "divisions").text = str(divisions)

    for i, command in enumerate(input_notation):
        def extractor(pattern, string):
            match = re.search(pattern, string)
            return match.group(0) if match else None

        if command.startswith('clef-'):
            clef_type = clef_dict.get(command)
            if clef_type:
                clef_element = ET.SubElement(attributes, 'clef')
                ET.SubElement(clef_element, 'sign').text = clef_type[0]
                ET.SubElement(clef_element, 'line').text = str(clef_type[1])

        elif command.startswith('keySignature-'):
            key_signature = key_sign_dict.get(command)
            if key_signature:
                key_element = ET.SubElement(attributes, 'key')
                ET.SubElement(key_element, "fifths").text = str(key_signature[0])

        elif command.startswith('timeSignature-'):
            time_signature = time_sign_dict.get(command)
            if time_signature:
                beats_per_measure = time_signature[0]
                time_element = ET.SubElement(attributes, 'time')
                ET.SubElement(time_element, "beats").text = str(time_signature[0])
                ET.SubElement(time_element, "beat-type").text = str(time_signature[1])

        elif command.startswith('note-') or command.startswith('rest-'):
            pitch_match = extractor(r"(-.*?_)", command)
            time_match = extractor(r"(_.*)", command)

            if pitch_match:
                note_pitch = note_pitch_dict.get(pitch_match)
            else:
                note_pitch = None
            
            if time_match:
                note_time = note_time_dict.get(time_match) if command.startswith('note-') else rest_dict.get(time_match)
            else:
                note_time = None

            if note_time:
                note_duration = note_time[0] * divisions
                total_duration += note_duration

                # If the total duration exceeds the measure, create a new measure
                if beats_per_measure and total_duration > beats_per_measure * divisions:
                    total_duration = note_duration
                    n += 1
                    current_measure = ET.SubElement(part, 'measure', number=str(n))
                
                note = ET.SubElement(current_measure, 'note')

                if command.startswith('note-') and note_pitch:
                    pitch = ET.SubElement(note, 'pitch')
                    ET.SubElement(pitch, 'step').text = note_pitch[0]
                    ET.SubElement(pitch, 'octave').text = str(note_pitch[1])
                    if note_pitch[2] != 0:
                        ET.SubElement(pitch, "alter").text = str(note_pitch[2])
                elif command.startswith('rest-'):
                    ET.SubElement(note, 'rest')
                
                ET.SubElement(note, 'duration').text = str(note_duration)
                ET.SubElement(note, 'type').text = note_time[1]
                for _ in range(note_time[2]):
                    ET.SubElement(note, "dot")

        elif command == 'barline':
            n += 1
            current_measure = ET.SubElement(part, 'measure', number=str(n))
            total_duration = 0  # Reset duration for the new measure

    # Convert to a pretty-printed string
    rough_string = ET.tostring(score_partwise, encoding="unicode", method="xml")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    return pretty_xml



# Example input notation
# input_notation = ['clef-C1', 'keySignature-EbM', 'timeSignature-2/4', 'multirest-23', 'barline', 'rest-quarter', 'rest-eighth', 'note-Bb4_eighth', 'barline', 'note-Bb4_quarter.', 'note-G4_eighth', 'barline', 'note-Eb5_quarter.', 'note-D5_eighth', 'barline', 'note-C5_eighth', 'note-C5_eighth', 'rest-quarter']


# Output the result to a MusicXML file
# with open('output.txt', 'w') as f:
    #f.write(musicxml_output)

