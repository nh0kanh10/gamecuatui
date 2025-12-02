#!/usr/bin/env python3
"""
Download recommended models for benchmarking
Automatically downloads quantized GGUF models for testing
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import urllib.request
import json

# Model configurations to test
MODELS = [
    {
        "name": "Phi-3-mini-4k (3.8B) - Q4_K_M",
        "size": "2.4GB",
        "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
        "filename": "phi-3-mini-4k-q4.gguf",
        "priority": 1,
        "notes": "Khuyến nghị - nhỏ, nhanh, quality tốt"
    },
    {
        "name": "Llama-3.2-3B - Q4_K_M",
        "size": "1.9GB",
        "url": "https://huggingface.co/lmstudio-community/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "filename": "llama-3.2-3b-q4.gguf",
        "priority": 2,
        "notes": "Mới nhất, context 128K"
    },
    {
        "name": "Mistral-7B-v0.2 - Q4_K_M",
        "size": "4.4GB",
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "filename": "mistral-7b-q4.gguf",
        "priority": 3,
        "notes": "Balanced - so sánh với 3B models"
    }
]


def download_file(url: str, dest: Path, model_name: str):
    """Download file with progress bar"""
    print(f"\n📥 Downloading: {model_name}")
    print(f"   URL: {url}")
    print(f"   Destination: {dest}")
    
    def reporthook(count, block_size, total_size):
        if total_size > 0:
            percent = min(int(count * block_size * 100 / total_size), 100)
            mb_downloaded = count * block_size / 1024 / 1024
            mb_total = total_size / 1024 / 1024
            sys.stdout.write(f"\r   Progress: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
            sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, dest, reporthook)
        print(f"\n   ✅ Downloaded successfully")
        return True
    except Exception as e:
        print(f"\n   ❌ Download failed: {e}")
        return False


def check_disk_space(required_gb: float) -> bool:
    """Check if enough disk space available"""
    try:
        import shutil
        stat = shutil.disk_usage(".")
        free_gb = stat.free / (1024**3)
        
        if free_gb < required_gb:
            print(f"⚠️  Warning: Only {free_gb:.1f}GB free, need {required_gb:.1f}GB")
            return False
        return True
    except:
        return True  # If can't check, proceed anyway


def main():
    print(f"""
{'='*70}
🎯 Model Downloader for LLM Benchmarking
{'='*70}

This script will download recommended models for testing on HP ZBook G7.
Models are stored in: d:/GameBuild/models/

""")
    
    # Create models directory
    models_dir = Path("d:/GameBuild/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate total size
    total_size_gb = sum(float(m['size'].replace('GB', '')) for m in MODELS)
    
    if not check_disk_space(total_size_gb + 1):  # +1GB buffer
        print("❌ Not enough disk space")
        sys.exit(1)
    
    print(f"Total size: ~{total_size_gb:.1f}GB\n")
    
    # Ask user which models to download
    print("Available models:")
    for i, model in enumerate(MODELS, 1):
        print(f"\n{i}. {model['name']}")
        print(f"   Size: {model['size']}")
        print(f"   Notes: {model['notes']}")
    
    print(f"\n{'='*70}")
    choice = input("\nDownload options:\n  1) All models (recommended)\n  2) Priority 1 only (fastest)\n  3) Custom selection\n  0) Exit\n\nYour choice: ").strip()
    
    if choice == '0':
        print("Cancelled.")
        sys.exit(0)
    
    # Determine which models to download
    to_download = []
    
    if choice == '1':
        to_download = MODELS
    elif choice == '2':
        to_download = [m for m in MODELS if m['priority'] == 1]
    elif choice == '3':
        indices = input("Enter model numbers (comma-separated, e.g. 1,2): ").strip()
        try:
            selected = [int(i.strip()) - 1 for i in indices.split(',')]
            to_download = [MODELS[i] for i in selected if 0 <= i < len(MODELS)]
        except:
            print("❌ Invalid selection")
            sys.exit(1)
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    if not to_download:
        print("❌ No models selected")
        sys.exit(1)
    
    # Download each model
    print(f"\n{'='*70}")
    print(f"Downloading {len(to_download)} model(s)...\n")
    
    downloaded = []
    failed = []
    
    for model in to_download:
        dest = models_dir / model['filename']
        
        # Skip if already exists
        if dest.exists():
            print(f"\n✅ Already exists: {model['name']}")
            print(f"   Skipping download...")
            downloaded.append(model)
            continue
        
        # Download
        success = download_file(model['url'], dest, model['name'])
        
        if success:
            downloaded.append(model)
        else:
            failed.append(model)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 DOWNLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Downloaded: {len(downloaded)}")
    print(f"❌ Failed: {len(failed)}")
    
    if downloaded:
        print(f"\n✅ Successfully downloaded models:")
        for m in downloaded:
            print(f"   - {models_dir / m['filename']}")
    
    if failed:
        print(f"\n❌ Failed downloads:")
        for m in failed:
            print(f"   - {m['name']}")
            print(f"     Try manual download: {m['url']}")
    
    # Next steps
    if downloaded:
        print(f"\n{'='*70}")
        print(f"🎯 NEXT STEPS")
        print(f"{'='*70}")
        print(f"\n1. Install dependencies:")
        print(f"   pip install llama-cpp-python psutil GPUtil tabulate colorama")
        print(f"\n2. Run benchmark:")
        
        first_model = downloaded[0]
        model_path = models_dir / first_model['filename']
        
        print(f"\n   # CPU-only test:")
        print(f'   python benchmarks/benchmark_inference.py --model "{model_path}" --n_gpu_layers 0 --test_name "{first_model["filename"]}_CPU"')
        
        print(f"\n   # Hybrid GPU test (8 layers):")
        print(f'   python benchmarks/benchmark_inference.py --model "{model_path}" --n_gpu_layers 8 --test_name "{first_model["filename"]}_8GPU"')
        
        print(f"\n3. Compare results in: benchmarks/results/\n")


if __name__ == "__main__":
    main()
