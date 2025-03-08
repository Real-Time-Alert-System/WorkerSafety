import ultralytics
import warnings
import os
import re
import glob
import random
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from PIL import Image
import cv2
from ultralytics import YOLO

# Disable warnings
warnings.filterwarnings("ignore")

# Print ultralytics version
print(ultralytics.__version__)

# Configuration class
class CFG:
    DEBUG = False
    FRACTION = 0.05 if DEBUG else 1.0
    SEED = 88

    # classes
    CLASSES = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask',
               'NO-Safety Vest', 'Person', 'Safety Cone',
               'Safety Vest', 'machinery', 'vehicle']
    NUM_CLASSES_TO_TRAIN = len(CLASSES)

    # training
    EPOCHS = 3 if DEBUG else 50  # 100
    BATCH_SIZE = 4

    BASE_MODEL = 'yolov8s'  # yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    BASE_MODEL_WEIGHTS = f'{BASE_MODEL}.pt'
    EXP_NAME = f'ppe_css_{EPOCHS}_epochs'

    OPTIMIZER = 'auto'  # SGD, Adam, Adamax, AdamW, NAdam, RAdam, RMSProp, auto
    LR = 1e-3
    LR_FACTOR = 0.01
    WEIGHT_DECAY = 5e-4
    DROPOUT = 0.0
    PATIENCE = 20
    PROFILE = False
    LABEL_SMOOTHING = 0.0

    # paths
    CUSTOM_DATASET_DIR = 'css-data/'
    OUTPUT_DIR = './'


def setup_dataset_yaml():
    """Create YAML file for the dataset configuration"""
    dict_file = {
        'train': os.path.join(CFG.CUSTOM_DATASET_DIR, 'train'),
        'val': os.path.join(CFG.CUSTOM_DATASET_DIR, 'valid'),
        'test': os.path.join(CFG.CUSTOM_DATASET_DIR, 'test'),
        'nc': CFG.NUM_CLASSES_TO_TRAIN,
        'names': CFG.CLASSES
    }

    with open(os.path.join(CFG.OUTPUT_DIR, 'data.yaml'), 'w+') as file:
        yaml.dump(dict_file, file)


def read_yaml_file(file_path):
    """Read a YAML file and return its contents"""
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print("Error reading YAML:", e)
            return None


def print_yaml_data(data):
    """Print YAML data with proper formatting"""
    formatted_yaml = yaml.dump(data, default_style=False)
    print(formatted_yaml)


def display_image(image, print_info=True, hide_axis=False):
    """Display an image with optional information"""
    if isinstance(image, str):  # Check if it's a file path
        img = Image.open(image)
        plt.imshow(img)
    elif isinstance(image, np.ndarray):  # Check if it's a NumPy array
        image = image[..., ::-1]  # BGR to RGB
        img = Image.fromarray(image)
        plt.imshow(img)
    else:
        raise ValueError("Unsupported image format")

    if print_info:
        print('Type: ', type(img), '\n')
        print('Shape: ', np.array(img).shape, '\n')

    if hide_axis:
        plt.axis('off')

    plt.show()


def plot_random_images_from_folder(folder_path, num_images=20, seed=CFG.SEED):
    """Plot random images from a folder"""
    random.seed(seed)

    # Get a list of image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png', '.jpeg', '.gif'))]

    # Ensure that we have at least num_images files to choose from
    if len(image_files) < num_images:
        raise ValueError("Not enough images in the folder")

    # Randomly select num_images image files
    selected_files = random.sample(image_files, num_images)

    # Create a subplot grid
    num_cols = 5
    num_rows = (num_images + num_cols - 1) // num_cols
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 8))

    for i, file_name in enumerate(selected_files):
        # Open and display the image using PIL
        img = Image.open(os.path.join(folder_path, file_name))

        if num_rows == 1:
            ax = axes[i % num_cols]
        else:
            ax = axes[i // num_cols, i % num_cols]

        ax.imshow(img)
        ax.axis('off')
        # ax.set_title(file_name)

    # Remove empty subplots
    for i in range(num_images, num_rows * num_cols):
        if num_rows == 1:
            fig.delaxes(axes[i % num_cols])
        else:
            fig.delaxes(axes[i // num_cols, i % num_cols])

    plt.tight_layout()
    plt.show()


def get_image_properties(image_path):
    """Get properties of an image file"""
    # Read the image file
    img = cv2.imread(image_path)

    # Check if the image file is read successfully
    if img is None:
        raise ValueError("Could not read image file")

    # Get image properties
    properties = {
        "width": img.shape[1],
        "height": img.shape[0],
        "channels": img.shape[2] if len(img.shape) == 3 else 1,
        "dtype": img.dtype,
    }

    return properties


def analyze_dataset():
    """Analyze dataset stats and class distribution"""
    class_idx = {str(i): CFG.CLASSES[i] for i in range(CFG.NUM_CLASSES_TO_TRAIN)}

    class_stat = {}
    data_len = {}
    class_info = []

    for mode in ['train', 'valid', 'test']:
        class_count = {CFG.CLASSES[i]: 0 for i in range(CFG.NUM_CLASSES_TO_TRAIN)}

        path = os.path.join(CFG.CUSTOM_DATASET_DIR, mode, 'labels')

        for file in os.listdir(path):
            with open(os.path.join(path, file)) as f:
                lines = f.readlines()

                for cls in set([line[0] for line in lines]):
                    class_count[class_idx[cls]] += 1

        data_len[mode] = len(os.listdir(path))
        class_stat[mode] = class_count

        class_info.append({'Mode': mode, **class_count, 'Data_Volume': data_len[mode]})

    dataset_stats_df = pd.DataFrame(class_info)
    return dataset_stats_df


def plot_class_distribution(dataset_stats_df):
    """Plot class distribution across train, valid, and test sets"""
    # Create subplots with 1 row and 3 columns
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Plot vertical bar plots for each mode in subplots
    for i, mode in enumerate(['train', 'valid', 'test']):
        sns.barplot(
            data=dataset_stats_df[dataset_stats_df['Mode'] == mode].drop(columns='Mode'),
            orient='v',
            ax=axes[i],
            palette='Set2'
        )

        axes[i].set_title(f'{mode.capitalize()} Class Statistics')
        axes[i].set_xlabel('Classes')
        axes[i].set_ylabel('Count')
        axes[i].tick_params(axis='x', rotation=90)

        # Add annotations on top of each bar
        for p in axes[i].patches:
            axes[i].annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', fontsize=8, color='black', xytext=(0, 5),
                            textcoords='offset points')

    plt.tight_layout()
    plt.show()


def check_image_sizes():
    """Check image sizes across train, valid, and test sets"""
    for mode in ['train', 'valid', 'test']:
        print(f'\nImage sizes in {mode} set:')

        img_size = 0
        for file in glob.glob(os.path.join(CFG.CUSTOM_DATASET_DIR, mode, 'images', '*')):
            image = Image.open(file)

            if image.size != img_size:
                print(f'{image.size}')
                img_size = image.size
                print('\n')


def test_base_model(example_image_path):
    """Test the base model on an example image"""
    model = YOLO(CFG.BASE_MODEL_WEIGHTS)
    img_properties = get_image_properties(example_image_path)
    
    results = model.predict(
        source=example_image_path,
        device='cpu',
        imgsz=(img_properties['height'], img_properties['width']),
        save=True,
        save_txt=True,
        save_conf=True,
        exist_ok=True,
    )

    # Check predictions with base model
    example_image_inference_output = example_image_path.split('/')[-1]
    print(f"Base model inference saved at: runs/detect/predict/{example_image_inference_output}")
    
    return img_properties


def train_model(img_properties):
    """Train the YOLOv8 model on the dataset"""
    print('Model: ', CFG.BASE_MODEL_WEIGHTS)
    print('Epochs: ', CFG.EPOCHS)
    print('Batch: ', CFG.BATCH_SIZE)
    
    model = YOLO(CFG.BASE_MODEL_WEIGHTS)

    # Train
    model.train(
        data=os.path.join(CFG.OUTPUT_DIR, 'data.yaml'),
        task='detect',
        imgsz=(img_properties['height'], img_properties['width']),
        epochs=CFG.EPOCHS,
        batch=CFG.BATCH_SIZE,
        optimizer=CFG.OPTIMIZER,
        lr0=CFG.LR,
        lrf=CFG.LR_FACTOR,
        weight_decay=CFG.WEIGHT_DECAY,
        dropout=CFG.DROPOUT,
        fraction=CFG.FRACTION,
        patience=CFG.PATIENCE,
        profile=CFG.PROFILE,
        label_smoothing=CFG.LABEL_SMOOTHING,
        name=f'{CFG.BASE_MODEL}_{CFG.EXP_NAME}',
        seed=CFG.SEED,
        val=True,
        amp=True,
        exist_ok=True,
        resume=False,
        device='cpu',  # Change to '0' or appropriate GPU number if available
        verbose=False,
    )


def main():
    """Main function to run the training pipeline"""
    # Setup dataset YAML
    setup_dataset_yaml()
    
    # Display YAML data
    file_path = os.path.join(CFG.OUTPUT_DIR, 'data.yaml')
    yaml_data = read_yaml_file(file_path)
    if yaml_data:
        print_yaml_data(yaml_data)
    
    # Set example image path - adjust this to your local path
    example_image_path = os.path.join(CFG.CUSTOM_DATASET_DIR, 'train/images', os.listdir(os.path.join(CFG.CUSTOM_DATASET_DIR, 'train/images'))[0])
    print(f"Using example image: {example_image_path}")
    
    # Display example image
    try:
        display_image(example_image_path, print_info=True, hide_axis=False)
    except Exception as e:
        print(f"Error displaying image: {e}")
    
    # Display random training images
    try:
        folder_path = os.path.join(CFG.CUSTOM_DATASET_DIR, 'train/images/')
        plot_random_images_from_folder(folder_path, num_images=20, seed=CFG.SEED)
    except Exception as e:
        print(f"Error plotting random images: {e}")
    
    # Analyze dataset
    try:
        dataset_stats_df = analyze_dataset()
        print("Dataset Statistics:")
        print(dataset_stats_df)
        
        # Plot class distribution
        plot_class_distribution(dataset_stats_df)
    except Exception as e:
        print(f"Error analyzing dataset: {e}")
    
    # Check image sizes
    try:
        check_image_sizes()
    except Exception as e:
        print(f"Error checking image sizes: {e}")
    
    # Test base model
    try:
        img_properties ={"height": 416, "width": 416}
    except Exception as e:
        print(f"Error testing base model: {e}")
        # Fallback to a default image size if needed
        img_properties = {"height": 416, "width": 416}
    
    # Train model
    try:
        train_model(img_properties)
    except Exception as e:
        print(f"Error during model training: {e}")


if __name__ == "__main__":
    main()
