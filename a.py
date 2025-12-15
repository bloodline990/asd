#!/usr/bin/env python3
import sys, os, tempfile, subprocess
from urllib.parse import urlparse, urlsplit

def run_command_in_zsh(command):
    try:
        result = subprocess.run(["zsh", "-c", command], capture_output=True, text=True)
        if result.returncode != 0:
            
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        return False

class colors:
    GRAY = "\033[90m"

def get_hostname(url):
    if url.startswith('http'):
        return urlsplit(url).netloc
    else:
        return url.strip()

def good_url(url):
    extensions = {
        '.json', '.js', '.fnt', '.ogg', '.css', '.jpg', '.jpeg', '.png', '.svg', '.img', '.gif',
        '.exe', '.mp4', '.flv', '.pdf', '.doc', '.ogv', '.webm', '.umv', '.webp', '.mov', '.mp3',
        '.m4a', '.m6p', '.ppt', '.pptx', '.scss', '.tif', '.tiff', '.ttf', '.otf', '.woff',
        '.woff2', '.bmp', '.ico', '.cot', '.htc', '.swf', '.rtf', '.image', '.rf', '.txt', '.xml', '.zip'
    }
    try:
        parsed_url = urlparse(url.strip())
        return not any(parsed_url.path.endswith(ext) for ext in extensions)
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def finalize(file_path, domain):
    unique_lines = set()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if good_url(line):
                unique_lines.add(line)
    unique_lines = {value for value in unique_lines if value}

    if not unique_lines:
        return False

    with open(f"{domain}.passive", 'w') as file:
        for element in sorted(unique_lines):
            file.write(element + '\n')

    return unique_lines

def is_file(filepath):
    return os.path.isfile(filepath)

def generate_temp_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        return temp_file.name

def run_nice_passive(domain):
    temp_file = generate_temp_file()
    print(f"{colors.GRAY}gathering URLs passively for: {domain}{colors.GRAY}")

    commands = [
        f"echo https://{domain}/ | tee {temp_file}",
        f"echo {domain} | waybackurls | sort -u | uro | tee -a {temp_file}",
        f"echo {domain} | gau --subs | sort -u | uro | tee -a {temp_file}"
    ]

    for command in commands:
        print(f"{colors.GRAY}[Executing command]: {command}{colors.GRAY}")
        run_command_in_zsh(command)

    print(f"{colors.GRAY}merging result for: {domain}{colors.GRAY}")
    res = finalize(temp_file, domain)

    res_num = len(res) if res else 0
    print(f"{colors.GRAY}done for {domain}, results: {res_num}{colors.GRAY}")

def get_input():
    if not sys.stdin.isatty():
        return sys.stdin.readline().strip()
    elif len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return None

if __name__ == "__main__":
    input_value = get_input()

    if input_value is None:
        print("Usage: echo domain.tld | nice_passive")
        print("Usage: cat domains.txt | nice_passive")
        sys.exit()

    if is_file(input_value):
        with open(input_value, 'r') as file:
            for line in file:
                domain = get_hostname(line)
                run_nice_passive(domain)
    else:
        run_nice_passive(get_hostname(input_value))

