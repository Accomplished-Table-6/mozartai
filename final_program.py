import mozart_predict as mp
import xmlencoder as xl


image_path = "Data/Example/Example2.png"
model_path = "Models/semantic_model.meta"
voc_file_path = "Data/vocabulary_semantic.txt"

result = mp.decode_music_score(image_path,model_path,voc_file_path)
print(result)
print(xl.create_musicxml(result))
