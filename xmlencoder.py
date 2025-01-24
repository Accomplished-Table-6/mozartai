import xml.etree.ElementTree as ET

def create_musicxml(input_notation):
    # Create the rooot element
    score_partwise = ET.Element("score-partwise",version="3.1")

    # Initialize the part
    part = ET.SubElement(score_partwise,"part",id="P1")

    # Initialize variables for the current measures and their content
    

