#!/bin/bash
echo "🚀 Initializing LocalStack Pro with AWS services..."

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Create S3 buckets
echo "📦 Creating S3 buckets..."
aws --endpoint-url=http://localhost:4566 s3 mb s3://librechat-uploads 2>/dev/null && echo "  ✅ librechat-uploads" || echo "  ℹ️  Already exists"
aws --endpoint-url=http://localhost:4566 s3 mb s3://librechat-avatars 2>/dev/null && echo "  ✅ librechat-avatars" || echo "  ℹ️  Already exists"
aws --endpoint-url=http://localhost:4566 s3 mb s3://librechat-screenshots 2>/dev/null && echo "  ✅ librechat-screenshots" || echo "  ℹ️  Already exists"

# List buckets
echo ""
echo "📋 S3 Buckets:"
aws --endpoint-url=http://localhost:4566 s3 ls

echo ""
echo "✅ LocalStack Pro initialization complete!"
echo ""
echo "🌐 Access LibreChat at: http://localhost:3080"
echo "🔧 LocalStack dashboard: http://localhost:4566/_localstack/health"
