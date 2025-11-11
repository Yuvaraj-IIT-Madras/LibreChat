#!/bin/bash

echo "========================================="
echo "LocalStack FREE TIER Initialization"
echo "========================================="

# Wait for LocalStack
echo "Waiting for LocalStack to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
  if curl -s http://localhost:4566/_localstack/health > /dev/null 2>&1; then
    echo "✅ LocalStack is ready!"
    break
  fi
  attempt=$((attempt + 1))
  echo "Attempt $attempt/$max_attempts - waiting..."
  sleep 2
done

if [ $attempt -eq $max_attempts ]; then
  echo "❌ LocalStack failed to start"
  exit 1
fi

# Set AWS configuration
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo ""
echo "1. Creating S3 buckets (FREE)..."
aws --endpoint-url=http://localhost:4566 s3 mb s3://librechat-uploads 2>/dev/null && echo "  ✅ Created: librechat-uploads" || echo "  ℹ️  Bucket exists: librechat-uploads"
aws --endpoint-url=http://localhost:4566 s3 mb s3://librechat-avatars 2>/dev/null && echo "  ✅ Created: librechat-avatars" || echo "  ℹ️  Bucket exists: librechat-avatars"
aws --endpoint-url=http://localhost:4566 s3 mb s3://librechat-screenshots 2>/dev/null && echo "  ✅ Created: librechat-screenshots" || echo "  ℹ️  Bucket exists: librechat-screenshots"

echo ""
echo "2. Verifying S3 buckets..."
aws --endpoint-url=http://localhost:4566 s3 ls

echo ""
echo "========================================="
echo "✅ LocalStack FREE TIER setup complete!"
echo "========================================="
