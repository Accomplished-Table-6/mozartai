import cv2
import numpy as np
import os

def split_sheet_music_per_measure(image_path, output_dir, multi_measure_rests=None, margin_x=5, margin_y=20):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the original image (color) and a grayscale version for processing
    original_image = cv2.imread(image_path)  # Load original image in color (to preserve quality)
    gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Load grayscale image for processing

    if original_image is None or gray_image is None:
        print("Error: Could not load image.")
        return []

    # Binarize the grayscale image
    _, binary = cv2.threshold(gray_image, 135, 255, cv2.THRESH_BINARY_INV)

    # Detect horizontal lines (staff lines)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    detected_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Find contours of staff lines
    contours, _ = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    staff_lines = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])  # Sort by y-coordinate
    print(f"Detected {len(staff_lines)} staff lines in {image_path}")

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

    # Initialize measure count and file list
    measure_count = 0
    all_filenames = []  # List to store all generated filenames

    # Crop each staff into individual measures
    for i, staff in enumerate(staff_groups):
        # Compute staff bounding box with margins
        x_min = max(min([x for x, y, w, h in staff]) - margin_x, 0)
        x_max = min(max([x + w for x, y, w, h in staff]) + margin_x, gray_image.shape[1])
        y_min = max(min([y for x, y, w, h in staff]) - margin_y, 0)
        y_max = min(max([y + h for x, y, w, h in staff]) + margin_y, gray_image.shape[0])

        # Crop the staff from the grayscale image (for measure detection)
        staff_image = binary[y_min:y_max, x_min:x_max]

        # Detect vertical lines (measure boundaries)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        detected_columns = cv2.morphologyEx(staff_image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

        # Find contours for measure splitting
        column_contours, _ = cv2.findContours(detected_columns, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        column_boundaries = sorted([cv2.boundingRect(c)[0] for c in column_contours])

        # Ensure we include the first boundary (left edge)
        if len(column_boundaries) == 0:
            print(f"Warning: No measure boundaries detected in staff {i + 1}.")
            continue

        column_boundaries.insert(0, 0)  # Add leftmost boundary
        print(f"Staff {i + 1}: Detected {len(column_boundaries) - 1} measure boundaries (including the first).")

        # Split staff into individual measures
        for j in range(len(column_boundaries) - 1):
            measure_x_min = max(column_boundaries[j] - margin_x, 0)
            measure_x_max = min(column_boundaries[j + 1] + margin_x, staff_image.shape[1])

            # Apply cropping on the **original** image instead of the binarized one
            measure_image = original_image[y_min:y_max, x_min + measure_x_min:x_min + measure_x_max]

            if measure_image.size == 0:
                print(f"Warning: Measure image for measure {measure_count + 1} is empty.")
                continue

            # Check for multi-measure rests
            duration = 1  # Default duration if not a multi-measure rest
            measure_number = measure_count + 1
            if multi_measure_rests:
                for rest in multi_measure_rests:
                    if rest[0] == measure_number:
                        duration = rest[1]
                        break

            # Save the cropped measure from the original image
            output_path = os.path.join(output_dir, f"measure_{measure_number}.png")
            cv2.imwrite(output_path, measure_image)
            all_filenames.append(output_path)  # Store the filename
            measure_count += duration  # Increment measure count by duration

    print(f"Saved {measure_count} measures to '{output_dir}'.")
    return all_filenames  # Return the list of filenames

# Example usage
image_path = "Data/Example/Capture.PNG"
output_dir = "Data/Temp"
# Define multi-measure rests as nested list: [measure_number, duration]
multi_measure_rests = []  # Example: measure 1 is 2 measures long, measure 4 is 3 measures long

file_list = split_sheet_music_per_measure(image_path, output_dir, multi_measure_rests, margin_x=5, margin_y=20)
print("Generated files:", file_list)
