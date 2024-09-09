from setuptools import setup, find_packages

setup(
    name="resume_parser",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pytesseract==0.3.10",
        "pdf2image==1.16.3",
        "Pillow==9.5.0",
    ],
)