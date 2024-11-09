import os
import json
import shutil

def read_json_files(folder_path):
    """Reads all JSON files from a given folder and returns their filenames."""
    print("Reading JSON files from folder...")
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    print(f"Found {len(json_files)} JSON files.")
    return json_files

def identify_categories(folder_path, json_files):
    """Identifies unique categories from the JSON files."""
    print("Identifying categories from JSON files...")
    categories = set()
    for json_file in json_files:
        with open(os.path.join(folder_path, json_file), 'r', encoding='utf-8') as file:
            content = json.load(file)
            for shape in content.get('shapes', []):
                categories.add(shape['label'])
    print(f"Identified categories: {categories}")
    return list(categories)

def extract_and_write_data_per_file(folder_path, json_files, categories, output_folder):
    """Extracts data from each JSON file and writes to separate YOLO format .txt files per image."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    category_mapping = {label: i for i, label in enumerate(categories)}

    for image_id, json_file in enumerate(json_files):
        print(f"Processing file: {json_file} ({image_id + 1}/{len(json_files)})")
        with open(os.path.join(folder_path, json_file), 'r', encoding='utf-8') as f:
            content = json.load(f)
            image_name = os.path.basename(content['imagePath'])
            image_height = content['imageHeight']
            image_width = content['imageWidth']

            txt_annotations = []
            for shape in content.get('shapes', []):
                label = shape['label']
                points = shape['points']
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                x_min = min(x_coords)
                y_min = min(y_coords)
                x_max = max(x_coords)
                y_max = max(y_coords)
                bbox_width = x_max - x_min
                bbox_height = y_max - y_min

                # Convert to YOLO format (normalized center x, center y, width, height)
                x_center = (x_min + bbox_width / 2) / image_width
                y_center = (y_min + bbox_height / 2) / image_height
                norm_width = bbox_width / image_width
                norm_height = bbox_height / image_height

                class_id = category_mapping[label]
                txt_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}")

            output_txt_path = os.path.join(output_folder, image_name.replace('.jpg', '.txt').replace('.png', '.txt'))
            with open(output_txt_path, 'w', encoding='utf-8') as output_txt:
                output_txt.write("\n".join(txt_annotations))
            print(f"Written YOLO TXT: {output_txt_path}")

            # Copy the image file to the output folder
            image_path = os.path.join(folder_path, image_name)
            if os.path.exists(image_path):
                shutil.copy(image_path, os.path.join(output_folder, image_name))
                print(f"Copied image: {image_name} to {output_folder}")
            else:
                print(f"Warning: Image file {image_name} not found.")

            # Copy the JSON file to the output folder
            shutil.copy(os.path.join(folder_path, json_file), os.path.join(output_folder, json_file))
            print(f"Copied JSON: {json_file} to {output_folder}")

def verify_conversion(output_folder):
    """Verifies the correctness of the conversion by checking if the output .txt files exist."""
    print("Verifying YOLO TXT files...")
    valid = True
    for file_name in os.listdir(output_folder):
        if file_name.endswith('.txt'):
            try:
                with open(os.path.join(output_folder, file_name), 'r', encoding='utf-8') as file:
                    content = file.readlines()
                if content:
                    print(f"Verification passed: {file_name} contains annotations.")
                else:
                    print(f"Verification warning: {file_name} is empty.")
            except Exception as e:
                print(f"Verification failed: {file_name} could not be read. Error: {e}")
                valid = False
    return valid

def main(folder_path, output_folder):
    print("Starting conversion process...")
    json_files = read_json_files(folder_path)
    categories = identify_categories(folder_path, json_files)
    extract_and_write_data_per_file(folder_path, json_files, categories, output_folder)

    if verify_conversion(output_folder):
        print("Conversion completed successfully.")
    else:
        print("Conversion completed with errors.")

 
main('augmented', 'output_final')
