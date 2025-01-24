import numpy as np
import cv2

def convert_inputs_to_ctc_format(target_text):
    SPACE_TOKEN = "-"
    SPACE_INDEX = 4
    FIRST_INDEX = 0

    original = " ".join(target_text.strip().lower().split(" ").replace(".","").replace("?","").replace(",","").replace("'","").replace("!","").replace("-",""))
    print(original)
    targets = original.replace(" ","  ")
    targets = targets.split(" ")

    # Adding blank label