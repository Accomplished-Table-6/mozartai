import cv2
import numpy as np
import os

def split_sheet_music_per_measure(image_path, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load image.")
        return

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
    measure_count = 1  # Start the measure numbering at 1
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

            # Save the measure
            output_path = os.path.join(output_dir, f"measure_{measure_count}.png")
            cv2.imwrite(output_path, measure_image)
            measure_count += 1

    print(f"Saved {measure_count - 1} measures to '{output_dir}'.")

# Example usage
image_path = "sheet_music.png"  # Path to the input sheet music image
output_dir = "output_measures"  # Directory to save the measures
split_sheet_music_per_measure(image_path, output_dir)
