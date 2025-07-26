# setup.py
from setuptools import setup, find_packages

setup(
    name="aimm",
    version="2.0.0",
    description="AI Multimedia and Management Assistant",
    author="SuperMini Team",
    author_email="support@aimm.app",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "anthropic>=0.7.0",
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "psutil>=5.9.0",
        "chromadb>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "aimm=aimm.main:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)