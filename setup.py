from setuptools import setup, find_packages

setup(
    name="PythonWebBrowser",
    version="1.4",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "PyQt6-WebEngine>=6.6.0",
        "pytest>=8.0.0"
    ],
    entry_points={
        'console_scripts': [
            'browser=main:main',
        ],
    },
)
