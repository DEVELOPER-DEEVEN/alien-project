import os
import re

# Mapping for CLI/Code files (Text replacement)
TEXT_MAP = {
    "[THOUGHT]": "[THOUGHT]",
    "[OBSERVATION]": "[OBSERVATION]",
    "[ACTION]": "[ACTION]",
    "[PLAN]": "[PLAN]",
    "[COMMENT]": "[COMMENT]",
    "[MSG]": "[MSG]",
    "[STATUS]": "[STATUS]",
    "[ORION]": "[ORION]",
    "[TASK]": "[TASK]",
    "[DEP]": "[DEP]",
    "[NEXT]": "[NEXT]",
    "[OK]": "[OK]",
    "[FAIL]": "[FAIL]",
    "[CONTINUE]": "[CONTINUE]",
    "[START]": "[START]",
    "[COMPLETE]": "[COMPLETE]",
    "[REASON]": "[REASON]",
    "[DATE]": "[DATE]",
    "[DOC]": "[DOC]",
    "[NEWS]": "[NEWS]",
    "[WEB]": "[WEB]",
    "[LANG]": "[LANG]",
    "[SCREENSHOT]": "[SCREENSHOT]",
    "[MAGIC]": "[MAGIC]",
    "[BRAIN]": "[BRAIN]",
    "[PAUSE]": "[PAUSE]",
    "[INFO]": "[INFO]",
    "[CONFIG]": "[CONFIG]",
    "[NEW]": "[NEW]",
    "[ALIEN]": "[ALIEN]",
    "[UFO]": "[UFO]",
}

# Regex for any other emojis (to be removed)
EMOJI_REGEX = re.compile(r"[\U0001F000-\U0001F9FF]|[\U00002600-\U000026FF]|[\U00002700-\U000027BF]")

def replace_emojis_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Apply specific mappings first
        for emoji, text in TEXT_MAP.items():
            content = content.replace(emoji, text)
            
        # Remove any remaining emojis using regex
        # Note: We replace with empty string to be safe, or we could leave them if they are obscure characters
        # But instructions said "REMOVE ALL".
        content = EMOJI_REGEX.sub("", content)
        
        if content != original_content:
            print(f"Updating {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    except Exception as e:
        print(f"Skipping {file_path}: {e}")

def main():
    root_dir = "."
    extensions = {'.py', '.md', '.txt', '.yaml', '.json', '.html', '.js', '.css'}
    
    for root, dirs, files in os.walk(root_dir):
        # Skip git and cache
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
            
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in extensions:
                file_path = os.path.join(root, file)
                replace_emojis_in_file(file_path)

if __name__ == "__main__":
    main()
