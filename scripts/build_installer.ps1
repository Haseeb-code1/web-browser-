# Build Script for Standalone Executable (Neural Browser)
# This script packages the entire Python Web Browser into a single standalone installer/executable.
# The resulting executable will run on ANY Windows PC without requiring Python, PyQt6, or Ollama installed.

# Set progress preference to silent for faster execution
$ProgressPreference = 'SilentlyContinue'

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "     Neural Browser Standalone Executable Builder" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Check Python and Pip
Write-Host "[1/5] Checking Python environment..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in system PATH. Please install Python 3.10+."
    Exit 1
}

# 2. Check and Install Dependencies
Write-Host "[2/5] Ensuring required packaging libraries are installed..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install pyinstaller pillow requests pywin32 -r requirements.txt

# 3. Create Windows Multi-resolution Icon (.ico)
Write-Host "[3/5] Generating Windows application icon..." -ForegroundColor Yellow
$pngIconPath = "data/app_icon.png"
$icoIconPath = "data/app_icon.ico"

if (-not (Test-Path $icoIconPath)) {
    if (Test-Path $pngIconPath) {
        python -c "from PIL import Image; img = Image.open('data/app_icon.png'); img.save('data/app_icon.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])"
        Write-Host "Generated app_icon.ico" -ForegroundColor Green
    } else {
        Write-Host "Warning: data/app_icon.png not found. Using default executable icon." -ForegroundColor DarkYellow
    }
} else {
    Write-Host "Using existing data/app_icon.ico" -ForegroundColor Green
}

# 4. Clean previous builds
Write-Host "[4/5] Cleaning up old build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# 5. Run PyInstaller
Write-Host "[5/5] Compiling application into a single standalone executable..." -ForegroundColor Yellow
Write-Host "Please wait, this will package PyQt6, WebEngine, and all AI modules (can take 1-2 minutes)..." -ForegroundColor Cyan

# Build command arguments
# -F / --onefile : Single executable file
# -w / --windowed : Hide command prompt window on launch
# --add-data : Include initial data files (icon, config, bookmarks, extensions)
# --icon : Custom executable icon
# --name : Executable filename
python -m PyInstaller --clean `
            --name="NeuralBrowser" `
            --windowed `
            --onefile `
            --add-data "data;data" `
            --icon="data/app_icon.ico" `
            main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==================================================" -ForegroundColor Green
    Write-Host " 🎉 STANDALONE EXECUTABLE CREATED SUCCESSFULLY! 🎉" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "Location: dist\NeuralBrowser.exe" -ForegroundColor Green
    Write-Host "`nInstructions for other PCs:" -ForegroundColor Cyan
    Write-Host "1. Simply copy 'dist\NeuralBrowser.exe' to ANY Windows computer." -ForegroundColor Yellow
    Write-Host "2. Double-click to launch! No Python, libraries, or extra setup required." -ForegroundColor Yellow
    Write-Host "3. All bookmarks, settings, and AI key configurations will be saved" -ForegroundColor Yellow
    Write-Host "   automatically in a 'data\' folder right next to the executable." -ForegroundColor Yellow
    Write-Host "==================================================" -ForegroundColor Green
} else {
    Write-Host "`n==================================================" -ForegroundColor Red
    Write-Host " ❌ BUILD FAILED! Check console errors above. ❌" -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
    Exit 1
}
