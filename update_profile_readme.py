# Author: Daniel Calbick
# Date: 2023-09-19

import os
import base64
from datetime import datetime

def update_readme(readme_path, logos_dir):
    # Save original README content
    with open(readme_path, 'r') as f:
        original_content = f.read()

    try:
        with open(readme_path, 'r+') as f:
            readme_content = f.read()

            # Define the pattern for finding placeholders
            pattern = "logo=data:image/svg%2bxml;base64,"

            # Find all placeholders
            placeholders = []
            start = 0
            while True:
                start = readme_content.find(pattern, start)
                if start == -1: break
                end = readme_content.find('.svg', start)
                if end == -1: break
                placeholders.append(readme_content[start+len(pattern):end])
                start = end

            for placeholder in placeholders:
                with open(f"{logos_dir}/{placeholder}.svg", "rb") as svg_file:
                    b64_svg = base64.b64encode(svg_file.read()).decode('utf-8')
                    readme_content = readme_content.replace(f"{pattern}{placeholder}.svg", f"{pattern}{b64_svg}")

            current_date = datetime.now().strftime('%Y-%m-%d')
            readme_content = readme_content.replace('<strong><em>Last Updated:</em> year-month-day', f'<strong><em>Last Updated:</em> {current_date}')

            # Rewrite the readme with base64 SVGs
            f.seek(0)
            f.truncate()
            f.write(readme_content)

        # Push changes to README to branch=profile-assets
        os.system("zsh update_readme.sh")


    finally:
        # Revert README to original state
        with open(readme_path, 'w') as f:
            f.write(original_content)

if __name__ == "__main__":
    readme_path = "README.md"
    logos_dir = "./logos"
    update_readme(readme_path, logos_dir)
