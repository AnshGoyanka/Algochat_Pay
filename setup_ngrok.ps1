# AlgoChat Pay - ngrok Setup Script for Windows
# This script helps set up ngrok for WhatsApp webhook testing/production

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  AlgoChat Pay - ngrok Setup for WhatsApp Webhook" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok is installed
Write-Host "[1/5] Checking if ngrok is installed..." -ForegroundColor Yellow
$ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue

if (-not $ngrokInstalled) {
    Write-Host "❌ ngrok not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install ngrok:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://ngrok.com/download" -ForegroundColor White
    Write-Host "2. Extract ngrok.exe to a folder" -ForegroundColor White
    Write-Host "3. Add to PATH or run from the extracted folder" -ForegroundColor White
    Write-Host ""
    Write-Host "Quick install with Chocolatey:" -ForegroundColor Yellow
    Write-Host "   choco install ngrok" -ForegroundColor White
    Write-Host ""
    Write-Host "Or with Scoop:" -ForegroundColor Yellow
    Write-Host "   scoop install ngrok" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ ngrok is installed" -ForegroundColor Green
Write-Host ""

# Check if backend is running
Write-Host "[2/5] Checking if FastAPI backend is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Backend is running on port 8000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend not detected on port 8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please start the backend first:" -ForegroundColor White
    Write-Host "   python -m uvicorn backend.main:app --reload" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}
Write-Host ""

# Check for ngrok auth token
Write-Host "[3/5] Checking ngrok authentication..." -ForegroundColor Yellow
$ngrokConfig = "$env:USERPROFILE\.ngrok2\ngrok.yml"
if (Test-Path $ngrokConfig) {
    Write-Host "✅ ngrok config found" -ForegroundColor Green
} else {
    Write-Host "⚠️  ngrok not authenticated" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get better performance and avoid limits:" -ForegroundColor White
    Write-Host "1. Sign up at: https://dashboard.ngrok.com/signup" -ForegroundColor White
    Write-Host "2. Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host "3. Run: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Cyan
    Write-Host ""
}
Write-Host ""

# Start ngrok in background
Write-Host "[4/5] Starting ngrok tunnel..." -ForegroundColor Yellow
Write-Host "Creating tunnel: localhost:8000 -> public HTTPS URL" -ForegroundColor White
Write-Host ""

# Start ngrok in a new window
Start-Process -FilePath "ngrok" -ArgumentList "http 8000 --log=stdout" -WindowStyle Normal

# Wait for ngrok to start
Write-Host "Waiting for ngrok to initialize..." -ForegroundColor White
Start-Sleep -Seconds 3

# Get ngrok public URL
Write-Host ""
Write-Host "[5/5] Fetching ngrok public URL..." -ForegroundColor Yellow
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    $publicUrl = $ngrokApi.tunnels[0].public_url
    
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  ✅ ngrok Tunnel Active!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Public URL: " -NoNewline -ForegroundColor White
    Write-Host "$publicUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your WhatsApp Webhook URL:" -ForegroundColor Yellow
    Write-Host "$publicUrl/webhook/whatsapp" -ForegroundColor Green
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "  Next Steps - Configure Twilio" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Go to Twilio Console:" -ForegroundColor White
    Write-Host "   https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Click on 'Sandbox Settings' or your WhatsApp number" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Set 'WHEN A MESSAGE COMES IN' to:" -ForegroundColor White
    Write-Host "   $publicUrl/webhook/whatsapp" -ForegroundColor Green
    Write-Host ""
    Write-Host "4. HTTP Method: POST" -ForegroundColor White
    Write-Host ""
    Write-Host "5. Click 'Save'" -ForegroundColor White
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "  Test Your Webhook" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Send a WhatsApp message to: +1 415 523 8886" -ForegroundColor White
    Write-Host "With code: join <your-sandbox-code>" -ForegroundColor White
    Write-Host ""
    Write-Host "Then try: balance" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "  Monitoring" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "ngrok Dashboard: http://localhost:4040" -ForegroundColor Cyan
    Write-Host "Backend Logs: Check your terminal running uvicorn" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  NOTE: ngrok URL changes when you restart!" -ForegroundColor Yellow
    Write-Host "   Update Twilio webhook URL after each restart" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop ngrok when done" -ForegroundColor White
    Write-Host ""
    
    # Copy webhook URL to clipboard
    try {
        "$publicUrl/webhook/whatsapp" | Set-Clipboard
        Write-Host "✅ Webhook URL copied to clipboard!" -ForegroundColor Green
        Write-Host ""
    } catch {
        # Clipboard not available, skip
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Could not fetch ngrok URL" -ForegroundColor Red
    Write-Host "Please check ngrok dashboard manually at: http://localhost:4040" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Keep this window open to maintain the tunnel..." -ForegroundColor Yellow
Write-Host ""

# Keep script running
Read-Host "Press Enter to stop ngrok and exit"

# Stop ngrok
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "ngrok tunnel stopped" -ForegroundColor Yellow
