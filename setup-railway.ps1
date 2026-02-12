#!/usr/bin/env pwsh
# Railway Deployment Helper Script
# Run this after Git is installed and you have your GitHub repo URL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Productivity Tracker - Railway Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
$gitVersion = git --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Then restart PowerShell and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
Write-Host ""

# Get user information
$userName = Read-Host "Enter your GitHub username"
$userEmail = Read-Host "Enter your email"
$repoUrl = Read-Host "Enter your GitHub repo URL (https://github.com/..."

Write-Host ""
Write-Host "Configuring Git..." -ForegroundColor Cyan

# Configure Git
git config --global user.name "$userName"
git config --global user.email "$userEmail"

Write-Host "✅ Git configured" -ForegroundColor Green
Write-Host ""

# Initialize repository
Write-Host "Initializing Git repository..." -ForegroundColor Cyan
git init

# Add all files
Write-Host "Adding files..." -ForegroundColor Cyan
git add .

# Create initial commit
Write-Host "Creating commit..." -ForegroundColor Cyan
git commit -m "Initial commit - productivity tracker app"

# Rename branch to main
Write-Host "Setting up main branch..." -ForegroundColor Cyan
git branch -M main

# Add remote
Write-Host "Adding remote repository..." -ForegroundColor Cyan
git remote add origin $repoUrl

# Push to GitHub
Write-Host "Pushing to GitHub (this may take a moment)..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your code is now on GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Go to https://railway.app" -ForegroundColor Cyan
    Write-Host "2. Sign up with GitHub" -ForegroundColor Cyan
    Write-Host "3. Click 'New Project' → 'Deploy from GitHub repo'" -ForegroundColor Cyan
    Write-Host "4. Select 'productivity-tracker'" -ForegroundColor Cyan
    Write-Host "5. Follow RAILWAY_DEPLOYMENT.md for next steps" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Error during deployment!" -ForegroundColor Red
    Write-Host "Check the error messages above." -ForegroundColor Yellow
}
