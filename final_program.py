import mozart_predict as mp
import xmlencoder as xl
import tempfile
import image_dissector as imd


image_path = "Data/Example/Example2.png"
Temp_path = tempfile.TemporaryDirectory(dir ="Data/temp")
model_path = "Models/semantic_model.meta"
voc_file_path = "Data/vocabulary_semantic.txt"
measure_list = []
file_list = imd.split_sheet_music_from_folder(image_path,Temp_path)

for i in range(len(file_list)):
  measure_path = f"Data/temp/{file_list[i]}"
  measure_section = mp.decode_music_score(measure_path,model_path,voc_file_path)
  measure_list.append(measure_section)
print(xl.create_musicxml(measure_list))
os.removedir(Temp_path)
