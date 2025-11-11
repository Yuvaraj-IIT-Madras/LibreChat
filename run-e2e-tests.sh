#!/bin/bash

echo "🧪 Running Playwright E2E Tests on LocalStack Setup"
echo "===================================================="

# Check if Playwright container exists
if ! docker ps -a | grep -q librechat-playwright; then
    echo "📦 Building and starting Playwright container..."
    docker compose -f docker-compose.localstack.yml up -d playwright
    echo "⏳ Waiting for Playwright container to be ready (30s)..."
    sleep 30
fi

# Check if LibreChat is running
if ! docker ps | grep -q "LibreChat-LocalStack.*Up"; then
    echo "❌ LibreChat is not running! Start it first with:"
    echo "   docker compose -f docker-compose.localstack.yml up -d"
    exit 1
fi

echo ""
echo "🎯 LibreChat URL: http://localhost:3080"
echo "📊 Test Runner: Playwright"
echo "☁️  Screenshot Storage: LocalStack S3 (librechat-screenshots)"
echo ""

# Run tests
echo "🚀 Executing Playwright tests..."
docker exec librechat-playwright npm run test:e2e

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests completed successfully!"
    echo ""
    echo "📸 Screenshots saved to LocalStack S3:"
    aws --endpoint-url=http://localhost:4566 s3 ls s3://librechat-screenshots/ --recursive
    echo ""
    echo "📊 Test report available at: ./e2e/playwright-report/index.html"
else
    echo ""
    echo "❌ Tests failed! Check logs:"
    echo "   docker logs librechat-playwright"
    echo ""
    echo "📸 Failure screenshots in LocalStack S3:"
    aws --endpoint-url=http://localhost:4566 s3 ls s3://librechat-screenshots/ --recursive
fi
