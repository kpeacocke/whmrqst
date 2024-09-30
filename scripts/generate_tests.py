#!/usr/bin/env python3
import os
import re

WIKI_DIR = "docs/requirements"
TEST_DIR = "tests"

def sanitize_filename(filename):
    """
    Converts a string into a valid file name by removing unsafe characters.
    """
    # Remove non-alphanumeric characters (except spaces), replace spaces with underscores, and lowercase everything.
    filename = re.sub(r'[^\w\s-]', '', filename).strip().lower()
    return re.sub(r'[\s]+', '_', filename)

def parse_requirements_from_md(md_file_path):
    # Simple parser for demo purposes. Customize as needed.
    requirements = []
    with open(md_file_path, 'r') as md_file:
        for line in md_file:
            if line.strip().startswith("## "):  # Assuming requirements sections start with "##"
                requirements.append(line.strip().replace("## ", ""))
    return requirements

def generate_test_file(requirement):
    # Create a more detailed template for Copilot suggestions
    test_template = f"""
import pytest

# Auto-generated test for: {requirement}

# This test will validate the functionality of the feature described in the requirement: "{requirement}".
# Here are some scenarios we need to test:
# 1. [Describe scenario 1 related to {requirement}]
# 2. [Describe scenario 2 related to {requirement}]
# 3. [Describe scenario 3 related to {requirement}]
# 
# Replace the placeholder 'assert True' statements with real test cases.

def test_{sanitize_filename(requirement)}():
    # TODO: Implement test cases based on scenarios listed above
    # Example:
    # assert some_function_call() == expected_result

    assert True  # Placeholder for scenario 1
    assert True  # Placeholder for scenario 2
    assert True  # Placeholder for scenario 3
"""
    return test_template

def main():
    if not os.path.exists(TEST_DIR):
        os.makedirs(TEST_DIR)

    md_files = [os.path.join(WIKI_DIR, f) for f in os.listdir(WIKI_DIR) if f.endswith(".md")]

    for md_file in md_files:
        requirements = parse_requirements_from_md(md_file)
        for req in requirements:
            # Sanitize the requirement to use it in the filename
            sanitized_filename = sanitize_filename(req)
            test_content = generate_test_file(req)

            # Use the sanitized filename without the numbering
            test_file_path = os.path.join(TEST_DIR, f"test_{sanitized_filename}.py")

            print(f"Generating test for requirement: {req} -> {test_file_path}")

            with open(test_file_path, 'w') as test_file:
                test_file.write(test_content)

if __name__ == "__main__":
    main()