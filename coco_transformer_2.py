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
    """Extracts data from each JSON file and writes to separate COCO format JSON files per image."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    category_mapping = {label: i + 1 for i, label in enumerate(categories)}
    annotation_id = 1

    for image_id, json_file in enumerate(json_files):
        print(f"Processing file: {json_file} ({image_id + 1}/{len(json_files)})")
        with open(os.path.join(folder_path, json_file), 'r', encoding='utf-8') as f:
            content = json.load(f)
            image_info = {
                "id": image_id + 1,
                "file_name": content['imagePath'],
                "height": content['imageHeight'],
                "width": content['imageWidth']
            }

            annotations = []
            for shape in content.get('shapes', []):
                label = shape['label']
                points = shape['points']
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                x_min = min(x_coords)
                y_min = min(y_coords)
                width = max(x_coords) - x_min
                height = max(y_coords) - y_min
                bbox = [x_min, y_min, width, height]

                annotation = {
                    "id": annotation_id,
                    "image_id": image_id + 1,
                    "category_id": category_mapping[label],
                    "bbox": bbox,
                    "area": width * height,
                    "segmentation": [points],
                    "iscrowd": 0
                }
                annotations.append(annotation)
                annotation_id += 1

            coco_data = {
                "images": [image_info],
                "annotations": annotations,
                "categories": [{"id": i + 1, "name": cat} for i, cat in enumerate(categories)]
            }

            output_file_path = os.path.join(output_folder, image_info['file_name'].replace('.jpg', '.json').replace('.png', '.json'))
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                json.dump(coco_data, output_file, indent=4)
            print(f"Written COCO JSON: {output_file_path}")

            # Copy the image file to the output folder
            image_path = os.path.join(folder_path, content['imagePath'])
            if os.path.exists(image_path):
                shutil.copy(image_path, os.path.join(output_folder, content['imagePath']))
                print(f"Copied image: {content['imagePath']} to {output_folder}")
            else:
                print(f"Warning: Image file {content['imagePath']} not found.")

def verify_conversion(output_folder):
    """Verifies the correctness of the conversion by checking if the output files can be parsed."""
    print("Verifying COCO JSON files...")
    valid = True
    for file_name in os.listdir(output_folder):
        if file_name.endswith('.json'):
            try:
                with open(os.path.join(output_folder, file_name), 'r', encoding='utf-8') as file:
                    content = json.load(file)
                print(f"Verification passed: {file_name} is valid.")
            except json.JSONDecodeError:
                print(f"Verification failed: {file_name} is invalid.")
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
