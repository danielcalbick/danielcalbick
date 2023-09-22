# Author: Daniel Calbick
# Date: 2023-09-21

import argparse
from bs4 import BeautifulSoup

def html_to_txt(html_file, output_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    plain_text = soup.get_text()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(plain_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HTML to plain text.")
    parser.add_argument("html_file", help="The HTML file to convert.")
    parser.add_argument("output_file", help="The output TXT file.")
    args = parser.parse_args()

    html_to_txt(args.html_file, args.output_file)
