import cv2
import numpy as np
import os
from glob import glob
import pytesseract  # Tesseract OCR for number detection


def detect_multi_measure_rest(measure_image):
    """
    Detects if the given measure contains a multi-measure rest.
    This is done by looking for a thick horizontal bar and extracting numbers above it.

    Returns:
        rest_count (int): The number of measures in the multi-measure rest (1 if no multi-measure rest is found).
    """
    # Binarize the image to enhance detection
    _, binary = cv2.threshold(measure_image, 128, 255, cv2.THRESH_BINARY_INV)

    # Detect thick horizontal bars
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 2))
    thick_bars = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

    # Find contours of thick bars
    contours, _ = cv2.findContours(thick_bars, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 1  # No thick bar found, assume it's a single measure

    # Assume the multi-measure rest bar is the widest horizontal element
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Extract the region above the thick bar to look for the number
    number_region = measure_image[max(0, y - 50):y, x:x + w]

    # Use OCR (Tesseract) to extract the number above the thick bar
    config = "--psm 7"  # OCR mode for detecting a single word/number
    detected_text = pytesseract.image_to_string(number_region, config=config, lang="eng")

    try:
        rest_count = int(detected_text.strip())
        return rest_count
    except ValueError:
        return 1  # If OCR fails, assume it's a single measure


def split_sheet_music_from_folder(input_folder, output_folder):
    file_list = []
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all image file paths from the input folder
    image_files = sorted(glob(os.path.join(input_folder, "*.png")) + 
                         glob(os.path.join(input_folder, "*.jpg")) + 
                         glob(os.path.join(input_folder, "*.jpeg")))
    
    if not image_files:
        print("Error: No images found in the input folder.")
        return

    measure_count = 1  # Start the measure numbering at 1

    for image_file in image_files:
        print(f"Processing {image_file}...")

        # Load the image
        image = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"Error: Could not load image {image_file}. Skipping...")
            continue

        # Binarize the image
        _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

        # Detect horizontal lines (staff lines)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        detected_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        # Find contours of staff lines
        contours, _ = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        staff_lines = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])  # Sort by y-coordinate

        # Group staff lines into sets (1 set = 1 staff)
        staff_groups = []
        group = []
        prev_y = None
        for contour in staff_lines:
            x, y, w, h = cv2.boundingRect(contour)
            if prev_y is None or abs(y - prev_y) < 20:  # Group nearby lines
                group.append((x, y, w, h))
            else:
                staff_groups.append(group)
                group = [(x, y, w, h)]
            prev_y = y
        if group:
            staff_groups.append(group)

        # Crop each staff into individual measures
        for staff in staff_groups:
            x_min = min([x for x, y, w, h in staff])
            x_max = max([x + w for x, y, w, h in staff])
            y_min = min([y for x, y, w, h in staff])
            y_max = max([y + h for x, y, w, h in staff])

            # Crop the staff
            staff_image = binary[y_min:y_max, x_min:x_max]

            # Detect vertical lines (measure boundaries)
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            detected_columns = cv2.morphologyEx(staff_image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

            # Find contours for measure splitting
            column_contours, _ = cv2.findContours(detected_columns, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            column_boundaries = sorted([cv2.boundingRect(c)[0] for c in column_contours])

            # Split staff into individual measures
            for j in range(len(column_boundaries) - 1):
                measure_x_min = column_boundaries[j]
                measure_x_max = column_boundaries[j + 1]

                # Crop the measure
                measure_image = staff_image[:, measure_x_min:measure_x_max]

                # Detect multi-measure rest and get the measure count
                rest_count = detect_multi_measure_rest(measure_image)

                # Save the measure or skip numbering for multi-measure rests
                if rest_count == 1:
                    file_list.append(f"measure_{measure_count.png}")
                    output_path = os.path.join(output_folder, f"measure_{measure_count}.png")
                    cv2.imwrite(output_path, measure_image)
                    measure_count += 1
                else:
                    # Skip measure numbers for multi-measure rest
                    file_list.append(f"measure_{measure_count.png}")
                    measure_count += rest_count

    print(f"Saved measures to '{output_folder}'. Last measure number: {measure_count - 1}.")
    return file_list


# Example usage
input_folder = "sheet_music_pages"  # Folder containing the input sheet music images
output_folder = "output_measures"   # Folder to save the measures
split_sheet_music_from_folder(input_folder, output_folder)
