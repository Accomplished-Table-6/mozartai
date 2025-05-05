import mozart_predict as mp
import xmlencode2 as xl
import imd_staf as imd
import nested_list as nl

song_nam = "blahblah"
image_path = "Data/Example/Capture_1.PNG"
Temp_path = "Data/Temp/"
model_path = "Models/semantic_model.meta"
voc_file_path = "Data/vocabulary_semantic.txt"
file_list = imd.split_sheet_music_into_phrases(image_path, Temp_path, margin_x=5, margin_y=20)
phrase_list =[]
for phrases in file_list:
  result = mp.decode_music_score(phrases, model_path, voc_file_path)
  prase_list = [x for x in result]
  phrase_list.extend(prase_list)

def group_measures(notes):
    measures = []
    current_measure = []

    for item in notes:
        if item == "barline":
            measures.append(current_measure)
            current_measure = []
        else:
            current_measure.append(item)

    if current_measure:  # Add the last measure if not empty
        measures.append(current_measure)

    return measures
finale = group_measures(phrase_list)
print(finale)
xl.create_musicxml(finale)
