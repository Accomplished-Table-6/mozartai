import mozart_predict as mp
import xmlencoder as xl
import tempfile
import image_dissector as imd
import os


image_path = "Data/Example/Capture.PNG"
Temp_path = "Data/Temp"
model_path = "Models/semantic_model.meta"
voc_file_path = "Data/vocabulary_semantic.txt"
measure_list = []
file_list = imd.split_sheet_music_per_measure(image_path, Temp_path, multi_measure_rests=[], margin_x=5, margin_y=20)
for i in range(len(file_list)):
  result = mp.decode_music_score(file_list[i], model_path, voc_file_path)
  sanitized_result = [ele for ele in result if ele != 'barline']
  measure_list.append(sanitized_result)
print(measure_list)
print(xl.create_musicxml(measure_list))
