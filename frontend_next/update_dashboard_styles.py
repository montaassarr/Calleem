import os
import re

DASHBOARD_DIR = "/home/montassar/Desktop/ai_receptionist/frontend_next/app/dashboard"

def update_file_content(content):
    # 1. Replace glass container classes
    # glass-strong, glass-panel, glass -> bg-white border border-slate-200 shadow-sm
    content = re.sub(r'className="(.*?)glass(?:-strong|-panel)?(.*?)"', r'className="\1bg-white border border-slate-200 shadow-sm\2"', content)
    
    # 2. Update table headers and rows
    # bg-white/5 -> bg-slate-50
    content = content.replace("bg-white/5", "bg-slate-50")
    
    # 3. Update borders
    # border-white/10 or border-white/20 -> border-slate-200
    content = re.sub(r'border-white/\d+', 'border-slate-200', content)
    
    # 4. Update specific text colors if needed
    # text-white/50 -> text-muted-foreground (usually mostly fine, but let's check for specific white text that might disappear on white bg)
    # If we find explicit text-white, we might want to change it to text-slate-900 or text-foreground, UNLESS it's on a primary button/card.
    # Safe bet: Remove text-white/xx on non-primary elements if possible. But this is risky with regex.
    # Let's focus on the containers first.
    
    # 5. Fix potential double borders or shadows from replacement
    content = content.replace("border border-slate-200 shadow-sm border ", "border border-slate-200 shadow-sm ")
    
    # 6. Target Helper for Card components that lack explicit background
    # This is a bit complex with regex, but we can look for <Card className="..."> that DOESN'T contain bg-
    # A simpler safe approach for a script: Replace <Card className=" with <Card className="bg-white border-slate-200 shadow-sm 
    # But check if it already has bg-white to avoid duplication?
    # Actually, we can just replace 'className="' with 'className="bg-white border-slate-200 shadow-sm ' inside <Card ...> tags? 
    # That's hard to parse with regex.
    # Let's try to match the specific patterns seen in voice-agent pages
    
    # Pattern A: <Card className="...">
    # We want to insert bg-white if not present.
    def replace_card_class(match):
        prefix = match.group(1) # <Card 
        attrs = match.group(2) # ... className="
        classes = match.group(3) # ...
        suffix = match.group(4) # " ... >
        
        if "bg-" not in classes and "glass" not in classes:
             return f'{prefix}{attrs}bg-white border-slate-200 shadow-sm {classes}{suffix}'
        return match.group(0)

    # Regex for Card with className
    # <Card ... className="..." ... >
    # This is tricky across multiple lines.
    # Let's do a simpler replacements for common patterns found in the files we read.
    
    # Replace generic <Card> with <Card className="bg-white border-slate-200 shadow-sm">
    content = re.sub(r'<Card\s*>', r'<Card className="bg-white border-slate-200 shadow-sm">', content)
    
    # Replace <Card className="... without bg- ...">
    # We will just prepend bg-white border-slate-200 shadow-sm to className if it starts with hover: or generic utils
    content = re.sub(r'(<Card[^>]*className=")(?!bg-|glass)([^"]*")', r'\1bg-white border-slate-200 shadow-sm \2', content)

    # 7. Update bg-muted colors
    # bg-muted -> bg-slate-100
    content = content.replace("bg-muted", "bg-slate-100")
    
    return content

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tsx") or file.endswith(".jsx"):
                file_path = os.path.join(root, file)
                
                # Skip layout.tsx as we already handled it manually
                if file == "layout.tsx" and root == DASHBOARD_DIR:
                    continue
                    
                with open(file_path, 'r') as f:
                    content = f.read()
                
                new_content = update_file_content(content)
                
                if new_content != content:
                    print(f"Updating {file_path}")
                    with open(file_path, 'w') as f:
                        f.write(new_content)

if __name__ == "__main__":
    process_directory(DASHBOARD_DIR)
