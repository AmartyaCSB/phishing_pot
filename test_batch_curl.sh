#!/bin/bash
# Cross-platform curl-based testing for batch email classification API

echo "🚀 Email Classification API - Batch Testing (curl)"
echo "============================================================"

# Check if server is running
echo "🔍 Checking server status..."
if curl -s -f "http://localhost:8000/" > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server not accessible"
    echo "💡 Make sure to start the server first: python run.py"
    exit 1
fi

# Test single file upload
echo ""
echo "🧪 Testing Single File Upload"
echo "----------------------------------------"

if [ -f "email/sample-201.eml" ]; then
    echo "📤 Uploading: email/sample-201.eml"
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -F "file=@email/sample-201.eml" \
        "http://localhost:8000/classify/upload")
    
    http_code=$(echo "$response" | tail -n1)
    json_response=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Single file upload successful!"
        echo "📊 Response: $json_response" | head -c 200
        echo "..."
    else
        echo "❌ Single file upload failed (HTTP $http_code)"
        echo "Response: $json_response"
    fi
else
    echo "❌ Sample file not found: email/sample-201.eml"
fi

# Test batch upload
echo ""
echo "🧪 Testing Batch Upload"
echo "----------------------------------------"

# Find sample files
sample_files=(email/sample-*.eml)
if [ ${#sample_files[@]} -ge 2 ]; then
    # Take first 3 files for testing
    files_to_test=("${sample_files[@]:0:3}")
    
    echo "📧 Selected ${#files_to_test[@]} files for batch testing:"
    for file in "${files_to_test[@]}"; do
        echo "   • $(basename "$file")"
    done
    
    echo ""
    echo "📤 Uploading batch of ${#files_to_test[@]} files..."
    
    # Build curl command with multiple files
    curl_cmd="curl -s -w \"\n%{http_code}\" -X POST"
    for file in "${files_to_test[@]}"; do
        curl_cmd="$curl_cmd -F \"files=@$file\""
    done
    curl_cmd="$curl_cmd \"http://localhost:8000/classify/batch\""
    
    response=$(eval $curl_cmd)
    http_code=$(echo "$response" | tail -n1)
    json_response=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Batch upload successful!"
        echo "📊 Response summary:"
        
        # Extract key information using basic text processing
        total_files=$(echo "$json_response" | grep -o '"total_files":[0-9]*' | cut -d':' -f2)
        successful=$(echo "$json_response" | grep -o '"successful_classifications":[0-9]*' | cut -d':' -f2)
        failed=$(echo "$json_response" | grep -o '"failed_classifications":[0-9]*' | cut -d':' -f2)
        
        echo "   • Total Files: $total_files"
        echo "   • Successful: $successful"
        echo "   • Failed: $failed"
        
    else
        echo "❌ Batch upload failed (HTTP $http_code)"
        echo "Response: $json_response"
    fi
else
    echo "❌ Need at least 2 sample files for batch testing"
    echo "Available files: ${#sample_files[@]}"
fi

# Test API endpoints
echo ""
echo "🧪 Testing API Endpoints"
echo "----------------------------------------"

endpoints=(
    "GET:/docs:API Documentation"
    "GET:/models:Model Information"
)

for endpoint_info in "${endpoints[@]}"; do
    IFS=':' read -r method endpoint description <<< "$endpoint_info"
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "http://localhost:8000$endpoint")
    
    if [ "$http_code" = "200" ]; then
        echo "✅ $description: OK"
    else
        echo "❌ $description: HTTP $http_code"
    fi
done

# Test error handling
echo ""
echo "🧪 Testing Error Handling"
echo "----------------------------------------"

# Create a temporary non-EML file
echo "This is not an EML file" > temp_test.txt

echo "📤 Testing with invalid file type..."
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    -F "file=@temp_test.txt" \
    "http://localhost:8000/classify/upload")

if [ "$http_code" = "400" ]; then
    echo "✅ Correctly rejected non-EML file"
else
    echo "⚠️  Unexpected response for invalid file: HTTP $http_code"
fi

# Clean up
rm -f temp_test.txt

echo ""
echo "🎉 Batch API testing completed!"
echo ""
echo "💡 Usage Examples:"
echo "   • Single file: curl -X POST -F \"file=@email.eml\" http://localhost:8000/classify/upload"
echo "   • Batch files: curl -X POST -F \"files=@email1.eml\" -F \"files=@email2.eml\" http://localhost:8000/classify/batch"
echo "   • Web interface: http://localhost:8000"
echo ""
echo "📚 Try the interactive web interface:"
echo "   1. Open http://localhost:8000 in your browser"
echo "   2. Select multiple .eml files"
echo "   3. Click 'Classify X Emails' for batch processing"
