#!/usr/bin/env python3
"""
Setup script for Vosk model download and configuration
"""

import os
import requests
import tarfile
import zipfile
from pathlib import Path

def download_file(url, filename):
    """Download a file with progress indicator"""
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\rProgress: {progress:.1f}%", end='', flush=True)
    
    print(f"\n{filename} downloaded successfully!")

def extract_model(archive_path, extract_to="vosk-model"):
    """Extract the downloaded model archive"""
    print(f"Extracting {archive_path}...")
    
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall('.')
    elif archive_path.endswith('.tar.gz'):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall('.')
    
    # Find the extracted directory and rename it
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith('vosk-model'):
            if item != extract_to:
                os.rename(item, extract_to)
            break
    
    print(f"Model extracted to {extract_to}/")

def setup_vosk_model():
    """Download and setup a small Vosk model for wake word detection"""
    
    # Small English model (~50MB) - good for wake word detection
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_filename = "vosk-model-small-en-us-0.15.zip"
    
    print("Vosk Model Setup for Wake Word Detection")
    print("=" * 50)
    
    # Check if model already exists
    if os.path.exists("vosk-model"):
        print("✅ Vosk model already exists at 'vosk-model/'")
        return
    
    try:
        # Download the model
        download_file(model_url, model_filename)
        
        # Extract the model
        extract_model(model_filename)
        
        # Clean up the archive
        os.remove(model_filename)
        
        print("✅ Vosk model setup complete!")
        print("📁 Model location: ./vosk-model/")
        print("🎉 You can now run the voice assistant!")
        
    except Exception as e:
        print(f"❌ Error setting up Vosk model: {e}")
        print("Please check your internet connection and try again.")

def install_dependencies():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    os.system("pip install -r requirements.txt")
    print("✅ Dependencies installed!")

if __name__ == "__main__":
    print("Voice Assistant Setup")
    print("=" * 30)
    
    # Install dependencies
    install_dependencies()
    
    # Setup Vosk model
    setup_vosk_model()
    
    print("\n🚀 Setup complete! You can now run:")
    print("   python voice_assistant_test.py")
    print("\nOr test wake word detection alone:")
    print("   python wake_word_detector.py") 