"""
Setup test data files for SuperMini QA testing.
"""
import os
import csv
from pathlib import Path
from PIL import Image
import io

def create_test_images():
    """Create test image files."""
    test_images_dir = Path(__file__).parent / "data" / "images"
    test_images_dir.mkdir(parents=True, exist_ok=True)
    
    # Valid test images
    test_images = [
        ("valid_image.png", (200, 150), "red"),
        ("large_image.jpg", (1920, 1080), "blue"),
        ("small_image.png", (50, 50), "green"),
        ("screenshot_mock.png", (1280, 720), "gray")
    ]
    
    for filename, size, color in test_images:
        img = Image.new('RGB', size, color=color)
        img.save(test_images_dir / filename)
    
    # Create a corrupted image file
    with open(test_images_dir / "corrupted_image.png", 'wb') as f:
        f.write(b"This is not a valid image file")
    
    return test_images_dir

def create_test_documents():
    """Create test document files."""
    test_docs_dir = Path(__file__).parent / "data" / "documents"
    test_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create text documents
    documents = {
        "simple_doc.txt": "This is a simple text document for testing RAG functionality.",
        "long_doc.txt": "Lorem ipsum dolor sit amet. " * 100,
        "empty_doc.txt": "",
        "special_chars.txt": "Document with special characters: àáâãäåæçèéêë",
        "code_doc.txt": """
def hello_world():
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self):
        self.value = 42
"""
    }
    
    for filename, content in documents.items():
        with open(test_docs_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Create a corrupted text file with invalid encoding
    with open(test_docs_dir / "corrupted_doc.txt", 'wb') as f:
        f.write(b'\xff\xfe\x00\x00Invalid UTF-8 content')
    
    return test_docs_dir

def create_test_csv_files():
    """Create test CSV files."""
    test_csv_dir = Path(__file__).parent / "data" / "csv"
    test_csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Simple CSV data
    simple_data = [
        ["name", "age", "city"],
        ["Alice", "25", "New York"],
        ["Bob", "30", "San Francisco"],
        ["Charlie", "35", "Chicago"]
    ]
    
    with open(test_csv_dir / "simple_data.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(simple_data)
    
    # Large CSV data
    large_data = [["id", "value", "category"]]
    for i in range(1000):
        large_data.append([str(i), str(i * 10), f"category_{i % 5}"])
    
    with open(test_csv_dir / "large_data.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(large_data)
    
    # CSV with missing values
    missing_data = [
        ["name", "score", "grade"],
        ["Alice", "95", "A"],
        ["Bob", "", "B"],
        ["Charlie", "87", ""],
        ["", "92", "A"]
    ]
    
    with open(test_csv_dir / "missing_data.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(missing_data)
    
    # Empty CSV
    with open(test_csv_dir / "empty_data.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["col1", "col2", "col3"])
    
    # Malformed CSV
    with open(test_csv_dir / "malformed_data.csv", 'w') as f:
        f.write("name,age,city\n")
        f.write("Alice,25,New York\n")
        f.write("Bob,30,San Francisco,Extra Column\n")  # Extra column
        f.write("Charlie,Not a number,Chicago\n")  # Invalid data type
    
    return test_csv_dir

def create_mock_responses():
    """Create mock AI response files."""
    responses_dir = Path(__file__).parent / "data" / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock Claude responses
    claude_responses = {
        "code_response.txt": '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
print(fibonacci(10))
''',
        "multimedia_response.txt": '''
This image shows a red square with dimensions 200x150 pixels. The image appears to be a solid color test image, commonly used for testing image processing functionality.
''',
        "rag_response.txt": '''
Based on the document analysis, the key points are:
1. This is a simple text document for testing
2. It contains basic content for RAG functionality validation
3. The document structure is straightforward and suitable for testing
''',
        "automation_response.txt": '''
#!/bin/bash
# Automation script for testing
echo "Starting automation task..."
mkdir -p ~/test_output
echo "Task completed successfully" > ~/test_output/result.txt
echo "Automation completed."
''',
        "analytics_response.txt": '''
import pandas as pd
import matplotlib.pyplot as plt

# Load and analyze the data
df = pd.read_csv('data.csv')
print(f"Dataset shape: {df.shape}")
print(f"Summary statistics:\\n{df.describe()}")

# Create visualization
plt.figure(figsize=(10, 6))
df.plot()
plt.title('Data Analysis Results')
plt.savefig('analysis_results.png')
'''
    }
    
    for filename, content in claude_responses.items():
        with open(responses_dir / filename, 'w') as f:
            f.write(content.strip())
    
    # Mock Ollama responses
    ollama_responses = {
        "ollama_code.txt": "print('Hello from Ollama!')",
        "ollama_general.txt": "This is a mock response from Ollama local model.",
        "ollama_error.txt": "Error: Model not available"
    }
    
    for filename, content in ollama_responses.items():
        with open(responses_dir / filename, 'w') as f:
            f.write(content)
    
    return responses_dir

def setup_all_test_data():
    """Set up all test data files."""
    print("Setting up test data...")
    
    images_dir = create_test_images()
    print(f"Created test images in: {images_dir}")
    
    docs_dir = create_test_documents()
    print(f"Created test documents in: {docs_dir}")
    
    csv_dir = create_test_csv_files()
    print(f"Created test CSV files in: {csv_dir}")
    
    responses_dir = create_mock_responses()
    print(f"Created mock responses in: {responses_dir}")
    
    print("Test data setup completed!")

if __name__ == "__main__":
    setup_all_test_data()