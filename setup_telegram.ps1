# Telegram Bot Setup Script for AlgoChat Pay
# Automates webhook configuration

Write-Host "🤖 Telegram Bot Setup for AlgoChat Pay" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure it first." -ForegroundColor Yellow
    exit 1
}

# Read bot token from .env
$envContent = Get-Content .env
$botToken = ($envContent | Select-String "TELEGRAM_BOT_TOKEN=(.+)").Matches.Groups[1].Value

if (-not $botToken -or $botToken -eq "YOUR_TELEGRAM_BOT_TOKEN_HERE") {
    Write-Host "❌ TELEGRAM_BOT_TOKEN not configured in .env!" -ForegroundColor Red
    Write-Host "Please add your Telegram bot token to .env file" -ForegroundColor Yellow
    Write-Host "`nGet your token from @BotFather on Telegram:" -ForegroundColor Cyan
    Write-Host "1. Open Telegram" -ForegroundColor White
    Write-Host "2. Search for @BotFather" -ForegroundColor White
    Write-Host "3. Type: /newbot" -ForegroundColor White
    Write-Host "4. Follow instructions to create bot" -ForegroundColor White
    Write-Host "5. Copy the token to your .env file" -ForegroundColor White
    exit 1
}

Write-Host "✅ Found Telegram bot token" -ForegroundColor Green

# Get ngrok URL
Write-Host "`n📡 Enter your ngrok HTTPS URL" -ForegroundColor Yellow
Write-Host "(Example: https://abc123.ngrok-free.app)" -ForegroundColor Gray
Write-Host "or press Enter to input manually later:" -ForegroundColor Gray
$ngrokUrl = Read-Host "ngrok URL"

if (-not $ngrokUrl) {
    Write-Host "`n⚠️  No ngrok URL provided" -ForegroundColor Yellow
    Write-Host "You can set the webhook manually later with this command:" -ForegroundColor Cyan
    Write-Host "Invoke-RestMethod `"https://api.telegram.org/bot$botToken/setWebhook?url=YOUR_NGROK_URL/webhook/telegram`"" -ForegroundColor White
    exit 0
}

# Remove trailing slash if present
$ngrokUrl = $ngrokUrl.TrimEnd('/')

# Construct webhook URL
$webhookUrl = "$ngrokUrl/webhook/telegram"

Write-Host "`n🔄 Setting Telegram webhook..." -ForegroundColor Cyan
Write-Host "Webhook URL: $webhookUrl" -ForegroundColor Gray

try {
    # Set webhook
    $apiUrl = "https://api.telegram.org/bot$botToken/setWebhook?url=$webhookUrl"
    $response = Invoke-RestMethod -Uri $apiUrl -Method Get

    if ($response.ok) {
        Write-Host "`n✅ Telegram webhook set successfully!" -ForegroundColor Green
        Write-Host "📍 Webhook URL: $webhookUrl" -ForegroundColor Cyan
        
        # Update .env file
        $newEnvContent = @()
        foreach ($line in $envContent) {
            if ($line -match "^TELEGRAM_WEBHOOK_URL=") {
                $newEnvContent += "TELEGRAM_WEBHOOK_URL=$webhookUrl"
            } else {
                $newEnvContent += $line
            }
        }
        $newEnvContent | Set-Content .env
        Write-Host "✅ Updated .env file" -ForegroundColor Green
        
        # Get webhook info
        Write-Host "`n📊 Webhook Information:" -ForegroundColor Cyan
        $infoUrl = "https://api.telegram.org/bot$botToken/getWebhookInfo"
        $info = Invoke-RestMethod -Uri $infoUrl -Method Get
        
        Write-Host "URL: $($info.result.url)" -ForegroundColor White
        Write-Host "Pending Updates: $($info.result.pending_update_count)" -ForegroundColor White
        
        # Test bot info
        Write-Host "`n🤖 Bot Information:" -ForegroundColor Cyan
        $botInfoUrl = "https://api.telegram.org/bot$botToken/getMe"
        $botInfo = Invoke-RestMethod -Uri $botInfoUrl -Method Get
        
        Write-Host "Bot Name: $($botInfo.result.first_name)" -ForegroundColor White
        Write-Host "Username: @$($botInfo.result.username)" -ForegroundColor White
        Write-Host "Bot ID: $($botInfo.result.id)" -ForegroundColor White
        
        Write-Host "`n✅ Setup Complete!" -ForegroundColor Green
        Write-Host "`n📱 Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Make sure your backend is running: uvicorn backend.main:app --reload" -ForegroundColor White
        Write-Host "2. Open Telegram and search for: @$($botInfo.result.username)" -ForegroundColor White
        Write-Host "3. Click 'Start' or type: /start" -ForegroundColor White
        Write-Host "4. Register your phone: /register +1234567890" -ForegroundColor White
        Write-Host "5. Test commands: balance, help, history" -ForegroundColor White
        
        # Copy bot username to clipboard
        Set-Clipboard -Value "@$($botInfo.result.username)"
        Write-Host "`n📋 Bot username copied to clipboard!" -ForegroundColor Green
        
    } else {
        Write-Host "`n❌ Failed to set webhook" -ForegroundColor Red
        Write-Host "Response: $($response | ConvertTo-Json -Depth 10)" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check your bot token is correct" -ForegroundColor White
    Write-Host "2. Verify ngrok URL is HTTPS (not HTTP)" -ForegroundColor White
    Write-Host "3. Ensure ngrok is running: ngrok http 8000" -ForegroundColor White
    Write-Host "4. Test webhook manually:" -ForegroundColor White
    Write-Host "   curl http://localhost:8000/webhook/telegram" -ForegroundColor Gray
    exit 1
}
