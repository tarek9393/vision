from setuptools import setup, find_packages

setup(
    name="labelvision",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'opencv-python>=4.8.1',
        'numpy>=1.26.0',
        'pytesseract>=0.3.10',
        'Pillow>=10.1.0',
        'customtkinter==5.2.0',
        'python-dotenv>=1.0.0',
    ],
)
