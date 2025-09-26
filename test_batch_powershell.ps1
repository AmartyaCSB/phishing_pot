# PowerShell script to test batch email classification API
# Usage: .\test_batch_powershell.ps1

Write-Host "🚀 Email Classification API - Batch Testing (PowerShell)" -ForegroundColor Green
Write-Host "=" * 60

# Check if server is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Server not accessible: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Make sure to start the server first: python run.py" -ForegroundColor Yellow
    exit 1
}

# Test single file upload
Write-Host "`n🧪 Testing Single File Upload" -ForegroundColor Cyan
Write-Host "-" * 40

$singleFile = "email\sample-201.eml"
if (Test-Path $singleFile) {
    try {
        Write-Host "📤 Uploading: $singleFile"
        $startTime = Get-Date
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/classify/upload" -Method Post -Form @{
            file = Get-Item $singleFile
        } -TimeoutSec 60
        
        $elapsed = (Get-Date) - $startTime
        
        Write-Host "✅ Success! ($($elapsed.TotalSeconds.ToString('F2'))s)" -ForegroundColor Green
        Write-Host "🏷️  Classification: $($response.classification)"
        Write-Host "📊 Confidence: $($response.confidence_scores[0].score.ToString('F2'))"
        Write-Host "⏱️  Processing Time: $($response.processing_time_ms)ms"
        
    } catch {
        Write-Host "❌ Single file test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Sample file not found: $singleFile" -ForegroundColor Red
}

# Test batch upload
Write-Host "`n🧪 Testing Batch Upload" -ForegroundColor Cyan
Write-Host "-" * 40

# Get multiple sample files
$emailFiles = Get-ChildItem -Path "email\sample-*.eml" | Select-Object -First 5

if ($emailFiles.Count -ge 2) {
    Write-Host "📧 Selected $($emailFiles.Count) files for batch testing:"
    foreach ($file in $emailFiles) {
        Write-Host "   • $($file.Name)"
    }
    
    try {
        Write-Host "`n📤 Uploading batch of $($emailFiles.Count) files..."
        $startTime = Get-Date
        
        # Create form data for batch upload
        $form = @{}
        for ($i = 0; $i -lt $emailFiles.Count; $i++) {
            $form["files"] = $emailFiles[$i]
        }
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/classify/batch" -Method Post -Form $form -TimeoutSec 120
        
        $elapsed = (Get-Date) - $startTime
        
        Write-Host "✅ Batch processing successful! ($($elapsed.TotalSeconds.ToString('F2'))s)" -ForegroundColor Green
        
        Write-Host "`n📊 BATCH SUMMARY:"
        Write-Host "   • Total Files: $($response.total_files)"
        Write-Host "   • Successful: $($response.successful_classifications)"
        Write-Host "   • Failed: $($response.failed_classifications)"
        Write-Host "   • Total Processing Time: $($response.total_processing_time_ms.ToString('F0'))ms"
        
        $avgTime = $response.total_processing_time_ms / [Math]::Max(1, $response.total_files)
        Write-Host "   • Average Time per File: $($avgTime.ToString('F0'))ms"
        
        Write-Host "`n📋 INDIVIDUAL RESULTS:"
        for ($i = 0; $i -lt $response.results.Count; $i++) {
            $result = $response.results[$i]
            $classification = if ($result.classification) { $result.classification } else { "unknown" }
            $confidence = if ($result.confidence_scores.Count -gt 0) { $result.confidence_scores[0].score } else { 0 }
            
            Write-Host "   $($i + 1). $($result.file_name)"
            Write-Host "      🏷️  $classification ($($confidence.ToString('F2')) confidence)"
            Write-Host "      ⏱️  $($result.processing_time_ms)ms"
            
            if ($result.error) {
                Write-Host "      ❌ Error: $($result.error)" -ForegroundColor Red
            }
        }
        
    } catch {
        Write-Host "❌ Batch processing failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Need at least 2 sample files for batch testing" -ForegroundColor Red
}

# Test API endpoints
Write-Host "`n🧪 Testing API Endpoints" -ForegroundColor Cyan
Write-Host "-" * 40

$endpoints = @(
    @{ Method = "GET"; Endpoint = "/docs"; Description = "API Documentation" },
    @{ Method = "GET"; Endpoint = "/models"; Description = "Model Information" }
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000$($endpoint.Endpoint)" -Method $endpoint.Method -TimeoutSec 10 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($endpoint.Description): OK" -ForegroundColor Green
        } else {
            Write-Host "❌ $($endpoint.Description): $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $($endpoint.Description): Error - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Performance test
Write-Host "`n🧪 Testing Performance" -ForegroundColor Cyan
Write-Host "-" * 40

if (Test-Path $singleFile) {
    Write-Host "📊 Testing sequential requests..."
    $times = @()
    
    for ($i = 1; $i -le 3; $i++) {
        try {
            $startTime = Get-Date
            
            $response = Invoke-RestMethod -Uri "http://localhost:8000/classify/upload" -Method Post -Form @{
                file = Get-Item $singleFile
            } -TimeoutSec 60
            
            $elapsed = (Get-Date) - $startTime
            $times += $elapsed.TotalSeconds
            
            Write-Host "   Request $i`: $($elapsed.TotalSeconds.ToString('F2'))s"
            
        } catch {
            Write-Host "   Request $i`: Failed - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    if ($times.Count -gt 0) {
        $avgTime = ($times | Measure-Object -Average).Average
        $minTime = ($times | Measure-Object -Minimum).Minimum
        $maxTime = ($times | Measure-Object -Maximum).Maximum
        
        Write-Host "📈 Average response time: $($avgTime.ToString('F2'))s"
        Write-Host "📈 Min/Max: $($minTime.ToString('F2'))s / $($maxTime.ToString('F2'))s"
    }
}

Write-Host "`n🎉 Batch API testing completed!" -ForegroundColor Green
Write-Host "`n💡 Usage Examples:" -ForegroundColor Yellow
Write-Host "   • Single file: POST /classify/upload"
Write-Host "   • Multiple files: POST /classify/batch"
Write-Host "   • Web interface: http://localhost:8000"

Write-Host "`n📚 Try the interactive web interface:" -ForegroundColor Cyan
Write-Host "   1. Open http://localhost:8000 in your browser"
Write-Host "   2. Select multiple .eml files"
Write-Host "   3. Click 'Classify X Emails' for batch processing"
