# Nova Browser

A modern, fully functional desktop web browser built with Python 3.11+ and PyQt6 (QtWebEngine).

## Installation
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Test
```bash
pytest tests/
```

## Build EXE
```bash
pyinstaller --onefile --windowed main.py
```

## Process Model: Incremental
This project follows the Incremental Process Model. Each increment added a working feature set: navigation -> tabs -> bookmarks -> history -> downloads -> testing -> refactoring. This allowed solo development with continuous testing at each stage.

## Lehman's Law
- **Continuing Change:** Browser features grew with each increment, adapting to new requirements like downloads and history.
- **Increasing Complexity:** The codebase naturally grew from 1 file to 13 files to handle the added functionality.
- **Self Regulation:** Each increment was rigorously reviewed and stabilized through unit testing before starting the next increment.
- **Conservation of Familiarity:** The familiar Chrome-like UX (tabs, address bar, navigation) was maintained consistently throughout development.

## Role
- **Solo Developer:** Architected, implemented, and tested all features independently using software engineering best practices.
