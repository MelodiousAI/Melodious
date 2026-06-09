import os

downloads_frontend_path = r"c:\Users\ahmad\Downloads\frontend"
exclude_dirs = {"node_modules", ".next", ".git"}
search_terms = ["onboarding", "infosec", "approval", "automated flow", "From request to onboarding"]

print("Starting search in Downloads/frontend with safe encoding...")
matches = []

if os.path.exists(downloads_frontend_path):
    for root, dirs, files in os.walk(downloads_frontend_path):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Skip if root contains excluded dirs
        if any(ex in root.split(os.sep) for ex in exclude_dirs):
            continue
            
        for file in files:
            if file.endswith(('.tsx', '.ts', '.js', '.jsx', '.html', '.css', '.md', '.json')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for term in search_terms:
                            if term.lower() in content.lower():
                                # Find line number and content
                                lines = content.splitlines()
                                for i, line in enumerate(lines):
                                    if term.lower() in line.lower():
                                        matches.append((file_path, i + 1, line.strip()[:200], term))
                except Exception as e:
                    pass
else:
    print("Downloads/frontend path does not exist.")

print(f"Search complete. Found {len(matches)} matches:")
with open("downloads_matches.txt", "w", encoding="utf-8") as out_f:
    out_f.write(f"Search complete. Found {len(matches)} matches:\n")
    for match in matches[:200]:  # Limit to first 200 matches
        out_f.write(f"File: {match[0]}\nLine {match[1]}: {match[2]} (Matched: {match[3]})\n\n")
print("Wrote matches to downloads_matches.txt")
