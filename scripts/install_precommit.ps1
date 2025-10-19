<#
Installs pre-commit in the active Python environment and installs git hooks.

Usage:
  Open PowerShell, activate your virtualenv, then run:
    .\scripts\install_precommit.ps1
#>

Write-Host "Installing pre-commit and dependencies..."

# Ensure pip is available
python -m pip install --upgrade pip

# Install pre-commit and common linters
python -m pip install pre-commit black==23.9.1 isort==5.12.0 flake8==6.0.0 flake8-bugbear

Write-Host "Installing git hooks via pre-commit..."
pre-commit install

Write-Host "Running pre-commit on all files to ensure codebase is formatted and passes checks..."
pre-commit run --all-files

Write-Host "Done. If any hooks failed, fix issues and re-run the script after addressing them."
