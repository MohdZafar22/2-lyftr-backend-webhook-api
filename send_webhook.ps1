# ---------------------------------------
# Lyftr Webhook Test Script (Windows)
# ---------------------------------------

# Webhook secret (must match WEBHOOK_SECRET env variable)
$secret = "testsecret"

# Webhook request body (DO NOT change formatting after signature generation)
$BODY = '{"message_id":"m1","from":"+919876543210","to":"+14155550100","ts":"2025-01-15T10:00:00Z","text":"Hello"}'

Write-Host "Request Body:"
Write-Host $BODY
Write-Host "--------------------------------"

# Convert request body to bytes
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($BODY)

# Create HMAC-SHA256 instance
$hmac = [System.Security.Cryptography.HMACSHA256]::new(
    [System.Text.Encoding]::UTF8.GetBytes($secret)
)

# Generate hex-encoded signature
$signature = ($hmac.ComputeHash($bodyBytes) | ForEach-Object { $_.ToString("x2") }) -join ""

Write-Host "Generated X-Signature:"
Write-Host $signature
Write-Host "--------------------------------"

# Send POST request to webhook endpoint
$response = curl -Method POST `
    -Headers @{
        "Content-Type" = "application/json"
        "X-Signature"  = $signature
    } `
    -Body $BODY `
    http://localhost:8000/webhook

Write-Host "Webhook Response:"
Write-Host $response
