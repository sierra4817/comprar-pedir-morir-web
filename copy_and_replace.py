import os
import shutil
import re

src_dir = r"c:\Users\as\Desktop\Comprar. Pedir prestado. Morir,AS"
dest_dir = r"c:\Users\as\Downloads\Organizado\08_Proyectos_Web\capitalinvisible-web"

def main():
    # 1. Clear dest_dir/audio directory
    dest_audio_dir = os.path.join(dest_dir, "audio")
    if os.path.exists(dest_audio_dir):
        print(f"Clearing destination audio folder: {dest_audio_dir}")
        shutil.rmtree(dest_audio_dir)
    os.makedirs(dest_audio_dir, exist_ok=True)

    # 2. Copy files and folders
    for item in os.listdir(src_dir):
        # Skip this script
        if item == "copy_and_replace.py":
            continue
            
        src_item = os.path.join(src_dir, item)
        dest_item = os.path.join(dest_dir, item)
        
        # Skip git directory
        if item == ".git" or item == ".gitignore":
            continue
            
        if os.path.isdir(src_item):
            print(f"Copying folder {item} to destination...")
            if os.path.exists(dest_item):
                shutil.rmtree(dest_item)
            shutil.copytree(src_item, dest_item)
        else:
            print(f"Copying file {item} to destination...")
            shutil.copy2(src_item, dest_item)

    # 3. Perform string replacements in the destination files
    files_to_modify = [
        "index.html",
        "app.html",
        "aviso-legal.html",
        "politica-privacidad.html",
        "politica-cookies.html"
    ]
    
    for filename in files_to_modify:
        file_path = os.path.join(dest_dir, filename)
        if os.path.exists(file_path):
            print(f"Updating URLs in {filename}...")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace GitHub Pages URLs with custom domain
            content = content.replace("https://sierra4817.github.io/comprar-pedir-morir-web/", "https://capitalinvisible.online/")
            content = content.replace("https://sierra4817.github.io/comprar-pedir-morir-web", "https://capitalinvisible.online/")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
    print("Copy and replacement complete!")

if __name__ == "__main__":
    main()
