import os
import re

# Regex for decorative unicode characters commonly mistaken as "clean"
# This range covers most emoji and Dingbats.
DECORATIVE_REGEX = re.compile(r"[\U0001F000-\U0001F9FF]|[\U00002600-\U000026FF]|[\U00002700-\U000027BF]|[\U0001F300-\U0001FAFF]")

def clean_readme(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Replace specific recurring patterns
        content = content.replace("📑", "") 
        content = content.replace("🧠", "")
        content = content.replace("🛡️", "")
        content = content.replace("📚", "")
        
        # Aggressive Regex Removal for any other decorative noise
        content = DECORATIVE_REGEX.sub("", content)
        
        if content != original_content:
            print(f"Cleaning Emojis from: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    root_dir = "."
    
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
            
        for file in files:
            # STRICTLY ONLY READMEs
            if file.upper().endswith("README.md") or file.endswith("_test.md") or file.endswith("_CONFIG.md"):
                file_path = os.path.join(root, file)
                clean_readme(file_path)

if __name__ == "__main__":
    main()
