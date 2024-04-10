import os
import yaml
import re
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio


def find_pubspec_files(start_path):
    """Recursively find all pubspec.yaml files in the subdirectories of start_path."""
    pubspec_files = []
    for root, _, files in os.walk(start_path):
        for file in files:
            if file == "pubspec.yaml":
                pubspec_files.append(os.path.join(root, file))
    return pubspec_files

def is_valid_library(entry):
    """Check if the library entry is followed by a colon and then a number."""
    return bool(re.match(r'.*:\s*\d+', entry))

def extract_libraries(pubspec_files):
    """Extract libraries from dependencies, dev_dependencies, and dependency_overrides."""
    libraries = set()
    for file in pubspec_files:
        with open(file, 'r') as f:
            content = yaml.safe_load(f)
            for section in ['dependencies', 'dev_dependencies', 'dependency_overrides']:
                if section in content:
                    for key, value in content[section].items():
                        entry = f"{key}: {value}"
                        if is_valid_library(entry):
                            libraries.add(key)
    return libraries

async def get_latest_version(library_name):
    url = f"https://pub.dev/packages/{library_name}/versions"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                version_tag = soup.find('td', {'class': 'version'}).extract()
                if version_tag:
                    map[library_name] = version_tag.text.strip()
                    return library_name, version_tag.text.strip()
                else:
                    return "Version information not found."
            else:
                return "Failed to retrieve the page."

map = dict()
async def main():
    start_path = '.'  # Assuming the script is run from the root of your project
    pubspec_files = find_pubspec_files(start_path)
    libraries = extract_libraries(pubspec_files)

    tasks = [get_latest_version(library) for library in libraries]
    results = await asyncio.gather(*tasks)
    for library, version in map.items():
        print(f"The latest version of {library} is: {version}")


if __name__ == "__main__":
    asyncio.run(main())
