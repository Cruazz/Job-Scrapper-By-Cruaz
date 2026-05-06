Write-Host "Setting up Job Aggregator..." -ForegroundColor Cyan

# Create virtual environment
if (!(Test-Path venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate and install
Write-Host "Installing dependencies..."
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Create .env if not exists
if (!(Test-Path .env)) {
    Write-Host "Creating .env from example..."
    Copy-Item .env.example .env
}

# Create data directory
if (!(Test-Path data)) {
    New-Item -ItemType Directory -Path data
}

Write-Host "Setup complete! Configure your .env and run 'python main.py'" -ForegroundColor Green
