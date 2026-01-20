#!/usr/bin/env python3
"""
Script to download all external images from markdown files and update links to local images.
"""
import os
import re
import urllib.request
import urllib.parse
from pathlib import Path

# Configuration
DOCS_DIR = Path(__file__).parent
IMAGES_DIR = DOCS_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Pattern to find image URLs
IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\((https?://[^\)]+\.(png|jpg|jpeg|gif|svg|webp))\)', re.IGNORECASE)

def sanitize_filename(url):
    """Convert URL to a safe filename."""
    # Extract filename from URL
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path)
    
    # If no filename, create one from URL
    if not filename or '.' not in filename:
        # Use last part of path or domain
        path_parts = [p for p in parsed.path.split('/') if p]
        if path_parts:
            filename = path_parts[-1]
        else:
            filename = parsed.netloc.replace('.', '_')
        
        # Add extension if missing
        if '.' not in filename:
            # Try to get extension from URL
            ext_match = re.search(r'\.(png|jpg|jpeg|gif|svg|webp)', url, re.IGNORECASE)
            if ext_match:
                filename += '.' + ext_match.group(1).lower()
            else:
                filename += '.png'  # Default
    
    # Sanitize filename
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename

def download_image(url, local_path):
    """Download image from URL to local path."""
    try:
        print(f"Downloading: {url}")
        urllib.request.urlretrieve(url, local_path)
        print(f"  ✓ Saved to: {local_path}")
        return True
    except Exception as e:
        print(f"  ✗ Error downloading {url}: {e}")
        return False

def process_markdown_file(md_file):
    """Process a markdown file to find and download images."""
    print(f"\nProcessing: {md_file.name}")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all image URLs
    matches = list(IMAGE_PATTERN.finditer(content))
    if not matches:
        print("  No images found")
        return content
    
    print(f"  Found {len(matches)} image(s)")
    
    # Download each image and update content
    new_content = content
    for match in reversed(matches):  # Reverse to maintain positions
        alt_text = match.group(1)
        url = match.group(2)
        ext = match.group(3)
        
        # Generate local filename
        local_filename = sanitize_filename(url)
        local_path = IMAGES_DIR / local_filename
        
        # Download if not exists
        if not local_path.exists():
            if not download_image(url, local_path):
                continue
        else:
            print(f"  ⊙ Already exists: {local_filename}")
        
        # Update markdown link
        relative_path = f"images/{local_filename}"
        old_link = match.group(0)
        new_link = f"![{alt_text}]({relative_path})"
        new_content = new_content[:match.start()] + new_link + new_content[match.end():]
        print(f"  ✓ Updated link: {alt_text[:30]}...")
    
    return new_content

def main():
    """Main function."""
    print("=" * 60)
    print("Image Downloader for docs_vi/")
    print("=" * 60)
    
    # Find all markdown files
    md_files = list(DOCS_DIR.glob("*.md"))
    print(f"\nFound {len(md_files)} markdown file(s)")
    
    # Process each file
    for md_file in md_files:
        try:
            new_content = process_markdown_file(md_file)
            
            # Write updated content
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✓ Updated: {md_file.name}")
        except Exception as e:
            print(f"  ✗ Error processing {md_file.name}: {e}")
    
    print("\n" + "=" * 60)
    print("Done!")
    print(f"Images saved to: {IMAGES_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
