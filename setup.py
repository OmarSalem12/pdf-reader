"""
Setup script for PDF Reader Package.
"""

from setuptools import setup, find_packages
import os
import typing


# Read the README file
def read_readme() -> str:
    """Read README.md file."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "PDF Reader Package - Extract data from encrypted PDF files"


# Read requirements
def read_requirements() -> typing.List[str]:
    """Read requirements.txt file."""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


setup(
    name="pdf-reader",
    version="1.0.0",
    author="PDF Reader Package",
    author_email="info@pdfreader.com",
    description="Extract data from encrypted PDF files and export to spreadsheets",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf-reader",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pdf-reader/issues",
        "Documentation": "https://pdf-reader.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/pdf-reader",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Filters",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.9.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "python-dateutil>=2.8.0",
        "python-dotenv>=1.0.0",
        "colorlog>=6.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "cli": [
            "tqdm>=4.65.0",
            "click>=8.1.0",
            "rich>=13.0.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "tqdm>=4.65.0",
            "click>=8.1.0",
            "rich>=13.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-reader=pdf_reader.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pdf_reader": ["*.txt", "*.md", "*.json"],
    },
    keywords="pdf, encryption, extraction, data, spreadsheet, excel, csv",
    platforms=["any"],
    license="MIT",
    zip_safe=False,
)
