#!/usr/bin/env python3

import os
import shutil
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from collections import Counter

#--------------------------------------------------------------------------------------------------
# Categorizing Files

# Define categories and subcategories
categories = {
    "Programming": ["Python", "Java", "C"],
    "AI": ["Machine_Learning", "Neural_Networks", "RAG"],
    "Math": ["Linear_Algebra", "Calculus"],
    "Database": ["SQL", "NoSQL", "PostgreSQL"],
    "Security": ["Cryptography", "DDOS_Attacks", "Network_Security"],
    "Others": []
}

# Prompt the user to enter the root folder path
root_folder = input("Enter the root folder path given to you, it is written after " "+" "python3 categorize_and_report.py"": ")


# Normalize the path (in case user provides a Windows-style path)
root_folder = os.path.normpath(root_folder)

print(f"Using root folder: {root_folder}")

# Check if the provided path exists
if not os.path.isdir(root_folder):
    print(f"Error: {root_folder} is not a valid directory.")
    sys.exit(1)

# Lock for thread synchronization
lock = Lock()

# Track processed files
processed_files = set()

# Track the expected and actual categories
file_categories = {}

# Ensure directory structure exists
def create_directories():
    for category, subcategories in categories.items():
        for subcategory in subcategories:
            os.makedirs(os.path.join(root_folder, category, subcategory), exist_ok=True)
    os.makedirs(os.path.join(root_folder, "Others"), exist_ok=True)

# Check for exact word match in filename
def is_word_in_file(word, file):
    # Match the word using word boundaries and also allow underscores and dashes
    pattern = r'\b' + re.escape(word.lower()) + r'(\b|_|-)'
    return re.search(pattern, file.lower())


# Move a file to the correct category
def move_file(file, file_path):
    global processed_files, file_categories

    with lock:
        if file in processed_files:
            return  # Skip already processed files
        processed_files.add(file)

    file_moved = False
    expected_category = None

    # Iterate through categories and subcategories
    for category, subcategories in categories.items():
        for subcategory in subcategories:
            if is_word_in_file(subcategory, file):
                expected_category = subcategory
                dest_dir = os.path.join(root_folder, category, subcategory)
                dest_path = os.path.join(dest_dir, file)
                os.makedirs(dest_dir, exist_ok=True)
                print(f"Moving file {file} to subcategory folder: {dest_path}")
                shutil.move(file_path, dest_path)
                file_categories[file] = (expected_category, subcategory)
                return  # File moved, stop further processing

        # If no subcategory matches, check the base category
        if is_word_in_file(category, file):
            expected_category = category
            dest_dir = os.path.join(root_folder, category)
            dest_path = os.path.join(dest_dir, file)
            os.makedirs(dest_dir, exist_ok=True)
            print(f"Moving file {file} to main category folder: {dest_path}")
            shutil.move(file_path, dest_path)
            file_categories[file] = (expected_category, category)
            return  # File moved, stop further processing

    # If no matches, move to "Others"
    dest_dir = os.path.join(root_folder, "Others")
    dest_path = os.path.join(dest_dir, file)
    os.makedirs(dest_dir, exist_ok=True)
    print(f"Moving file {file} to 'Others' folder: {dest_path}")
    shutil.move(file_path, dest_path)
    file_categories[file] = (expected_category, "Others")

# Process files in a specific category
def process_files():
    for file in os.listdir(root_folder):
        file_path = os.path.join(root_folder, file)
        if os.path.isfile(file_path) and file.endswith(".pdf"):
            move_file(file, file_path)

# Main function for organizing files
def organize_files():
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.submit(process_files)


#--------------------------------------------------------------------------------------------------
# Analysis Report 

# Function to calculate correctness score
def calculate_correctness(file_categories):
    correctly_categorized = 0
    incorrectly_categorized = 0

    # Compare the actual category with the expected category
    for file, (expected, actual) in file_categories.items():
        if expected == actual:
            correctly_categorized += 1
        else:
            incorrectly_categorized += 1

    total_processed = correctly_categorized + incorrectly_categorized
    if total_processed > 0:
        correctness_score = (correctly_categorized / total_processed) * 100
    else:
        correctness_score = 0

    return correctness_score

def generate_report(folder_path, categories):
    # To track the count of files in each category
    file_counts = Counter()
    total_files = 0

    for category in categories:
        # Construct the path for the category
        category_folder = os.path.join(folder_path, category)
        # Count all PDF files in the category and its subdirectories
        pdf_count = sum(
            len([file for file in files if file.endswith(".pdf")]) 
            for _, _, files in os.walk(category_folder)
        )
        file_counts[category] = pdf_count
        total_files += pdf_count

    # Handle case where no files exist
    if total_files == 0:
        print("No PDF files found in the specified folder.")
        return

    # Calculate percentage for each category
    percentages = {category: (count / total_files) * 100 for category, count in file_counts.items()}

    # Display the report
    print("\nAnalysis Report:")
    for category, percentage in percentages.items():
        print(f"{category}: {percentage:.2f}%")

    # Calculate correctness score
    correctness_score = calculate_correctness(file_categories)

    print(f"Correctness Score: {correctness_score:.2f}%")



if __name__ == "__main__":
    create_directories() # Ensure directories exist
    organize_files() # Organize files into categories
    category_list = ["Programming", "AI", "Math", "Database", "Security", "Others"] # List of categories to analyze
    generate_report(root_folder, category_list) # Generate Analysis Report for Organized Files
