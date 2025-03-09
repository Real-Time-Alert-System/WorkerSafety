import yaml
import os
from sklearn.model_selection import train_test_split

def split_dataset(yaml_path='data.yaml', split=0.5):
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    
    # Get all training images
    train_dir = data['train']
    images = [f for f in os.listdir(train_dir) if f.endswith(('.jpg', '.png'))]
    
    # Split images
    train1, train2 = train_test_split(images, test_size=split, random_state=42)
    
    # Create subset directories
    os.makedirs('css-data/train1', exist_ok=True)
    os.makedirs('css-data/train2', exist_ok=True)
    
    # Copy files (you'll need to implement this)
    copy_files(train1, 'css-data/train1')
    copy_files(train2, 'css-data/train2')
    
    # Create YAML files
    for i, (subset, path) in enumerate([(train1, 'subset1.yaml'), (train2, 'subset2.yaml')]):
        data['train'] = f'css-data/train{i+1}'
        with open(path, 'w') as f:
            yaml.dump(data, f)

def copy_files(file_list, target_dir):
    """Helper function to copy images and labels"""
    import shutil
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(target_dir.replace('images', 'labels'), exist_ok=True)
    
    for f in file_list:
        # Copy image
        shutil.copy(f, os.path.join(target_dir, f))
        # Copy label
        label_file = f.replace('images', 'labels').replace('.jpg', '.txt').replace('.png', '.txt')
        shutil.copy(label_file, os.path.join(target_dir.replace('images', 'labels'), label_file))
