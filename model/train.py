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
    CHECKPOINT_DIR = 'runs/train/ppe_detection/weights'  # Added checkpoint path


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


def get_last_checkpoint():
    """Find the latest checkpoint file"""
    if os.path.exists(CFG.CHECKPOINT_DIR):
        checkpoints = [f for f in os.listdir(CFG.CHECKPOINT_DIR) if f.endswith('.pt')]
        if checkpoints:
            return os.path.join(CFG.CHECKPOINT_DIR, 'last.pt')
    return None

def read_yaml_file(file_path):
    """Read a YAML file and return its contents"""
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Error reading YAML file {file_path}: {e}")
            return None

def train_model(img_properties, resume=False):
    """Train the YOLOv8 model on the dataset with checkpointing"""
    print('Model: ', CFG.BASE_MODEL_WEIGHTS)
    print('Epochs: ', CFG.EPOCHS)
    print('Batch: ', CFG.BATCH_SIZE)
    
    # Load last checkpoint if available and resuming
    checkpoint = get_last_checkpoint() if resume else CFG.BASE_MODEL_WEIGHTS
    model = YOLO(checkpoint)

    # Training parameters with checkpoint saving
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
        resume=resume,  # Modified to support resuming
        device='cpu',  # Change to '0' or appropriate GPU number if available
        verbose=False,
        save_period=1,  # Save checkpoint every 5 epochs
        project='ppe_detection',  # Organized project name
        single_cls=False  # Ensure multiclass training
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
    
    # Set example image path
    example_image_path = os.path.join(CFG.CUSTOM_DATASET_DIR, 'train/images', 
                                    os.listdir(os.path.join(CFG.CUSTOM_DATASET_DIR, 'train/images'))[0])
    print(f"Using example image: {example_image_path}")
    
    # Display example image
    try:
        display_image(example_image_path, print_info=True, hide_axis=False)
    except Exception as e:
        print(f"Error displaying image: {e}")
    
    # Get image properties
    try:
        img_properties = get_image_properties(example_image_path)
    except Exception as e:
        print(f"Error getting image properties: {e}")
        img_properties = {"height": 416, "width": 416}  # Fallback
    
    # Check for existing checkpoints
    last_checkpoint = get_last_checkpoint()
    resume_training = False
    
    if last_checkpoint:
        print(f"Found existing checkpoint: {last_checkpoint}")
        resume_training = input("Resume training from checkpoint? (y/n): ").lower() == 'y'
    
    # Train model
    try:
        train_model(img_properties, resume=resume_training)
    except Exception as e:
        print(f"Error during model training: {e}")
        if last_checkpoint:
            print(f"Last checkpoint available at: {last_checkpoint}")


if __name__ == "__main__":
    main()
