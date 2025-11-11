# Playwright E2E Testing with LocalStack

## 🎯 Overview

Your LocalStack setup now includes **Playwright E2E testing** that saves screenshots to **LocalStack S3** instead of local storage.

---

## ✅ What's Configured

| Component | Status | Purpose |
|-----------|--------|---------|
| **Playwright Container** | ✅ Ready | Runs E2E tests in isolated environment |
| **LocalStack S3** | ✅ Ready | Stores test screenshots & artifacts |
| **LibreChat App** | ✅ Running | Test target at http://localhost:3080 |
| **Test Suite** | ✅ Ready | 9 test specs available |

---

## 🚀 Quick Start

### **Option 1: Run All Tests (Recommended)**

```bash
./run-e2e-tests.sh
```

This script will:
1. Build/start Playwright container if needed
2. Run all E2E tests
3. Upload screenshots to LocalStack S3
4. Show test results

---

### **Option 2: Manual Test Execution**

#### **Step 1: Start Playwright Container**
```bash
# Build and start the Playwright service
docker compose -f docker-compose.localstack.yml up -d playwright

# Wait for container to be ready (30 seconds)
sleep 30

# Check status
docker ps | grep playwright
```

#### **Step 2: Run Tests**

```bash
# Run all tests
docker exec librechat-playwright npm run test:e2e

# Run specific test file
docker exec librechat-playwright npx playwright test specs/landing.spec.ts

# Run tests in headed mode (with browser UI)
docker exec librechat-playwright npx playwright test --headed

# Run tests in debug mode
docker exec librechat-playwright npx playwright test --debug

# Run specific browser
docker exec librechat-playwright npx playwright test --project=chromium
```

#### **Step 3: View Results**

```bash
# Check test screenshots in LocalStack S3
aws --endpoint-url=http://localhost:4566 s3 ls s3://librechat-screenshots/ --recursive

# Download screenshots from LocalStack
aws --endpoint-url=http://localhost:4566 s3 sync s3://librechat-screenshots/ ./test-screenshots/

# View HTML report
docker exec librechat-playwright npx playwright show-report
```

---

## 📋 Available Test Suites

Located in `e2e/specs/`:

1. **landing.spec.ts** - Landing page tests
2. **messages.spec.ts** - Message functionality
3. **nav.spec.ts** - Navigation tests
4. **settings.spec.ts** - Settings page tests
5. **popup.spec.ts** - Popup dialogs
6. **keys.spec.ts** - Keyboard shortcuts
7. **a11y.spec.ts** - Accessibility tests
8. **comprehensive-ui.spec.ts** - Full UI tests
9. **comprehensive-screens.spec.ts** - Screenshot tests

---

## 🔧 Configuration

### **Environment Variables**

Set these in `.env` or pass directly:

```bash
# Test user credentials
E2E_USER_EMAIL=test@example.com
E2E_USER_PASSWORD=testpassword123

# Base URL (default: http://api:3080 inside Docker network)
BASE_URL=http://api:3080

# Run headless (default: true)
HEADLESS=true

# LocalStack S3 configuration
AWS_ENDPOINT_URL=http://localstack:4566
S3_BUCKET=librechat-screenshots
```

### **Playwright Config**

Main config: `e2e/playwright.config.ts`

```typescript
use: {
  baseURL: 'http://localhost:3080',  // Changed to http://api:3080 in Docker
  video: 'on-first-retry',
  trace: 'retain-on-failure',
  screenshot: 'only-on-failure',
}
```

---

## 📸 Screenshot Storage in LocalStack S3

### **How It Works**

1. Tests run and capture screenshots
2. Screenshots uploaded to LocalStack S3: `s3://librechat-screenshots/`
3. Access screenshots via AWS CLI or LocalStack dashboard

### **View Screenshots**

```bash
# List all screenshots
aws --endpoint-url=http://localhost:4566 s3 ls s3://librechat-screenshots/ --recursive

# Download specific screenshot
aws --endpoint-url=http://localhost:4566 s3 cp \
  s3://librechat-screenshots/test-screenshot.png \
  ./screenshot.png

# Download all screenshots
aws --endpoint-url=http://localhost:4566 s3 sync \
  s3://librechat-screenshots/ \
  ./test-screenshots/

# View screenshot URLs (LocalStack)
# http://localhost:4566/librechat-screenshots/screenshot-name.png
```

### **Clean Up Old Screenshots**

```bash
# Delete all screenshots
aws --endpoint-url=http://localhost:4566 s3 rm \
  s3://librechat-screenshots/ --recursive

# Delete specific pattern
aws --endpoint-url=http://localhost:4566 s3 rm \
  s3://librechat-screenshots/ --recursive \
  --exclude "*" --include "failed-*"
```

---

## 🐛 Debugging Tests

### **View Playwright Container Logs**

```bash
docker logs librechat-playwright -f
```

### **Interactive Shell**

```bash
# Access Playwright container
docker exec -it librechat-playwright bash

# Run tests interactively
cd /app
npx playwright test --headed --debug
```

### **VNC Access (Visual Debugging)**

The Playwright container includes VNC for visual debugging:

```bash
# Expose VNC port
docker compose -f docker-compose.localstack.yml up -d

# Connect to VNC
# Host: localhost:5900
# Password: playwright

# Use VNC viewer to see tests running in real-time
```

---

## 📊 Test Reports

### **HTML Report**

```bash
# Generate HTML report
docker exec librechat-playwright npx playwright test --reporter=html

# View report
docker exec librechat-playwright npx playwright show-report

# Or copy report to host
docker cp librechat-playwright:/app/e2e/playwright-report ./playwright-report
# Open ./playwright-report/index.html in browser
```

### **JSON Report**

```bash
# Generate JSON report
docker exec librechat-playwright npx playwright test --reporter=json > test-results.json

# Parse results
cat test-results.json | jq '.suites[].specs[].title'
```

---

## 🔄 CI/CD Integration

### **Run Tests in CI**

```yaml
# Example GitHub Actions workflow
jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start LocalStack & LibreChat
        run: |
          docker compose -f docker-compose.localstack.yml up -d
          sleep 60
      
      - name: Run Playwright Tests
        run: ./run-e2e-tests.sh
      
      - name: Upload Screenshots to S3
        if: failure()
        run: |
          aws --endpoint-url=http://localhost:4566 s3 sync \
            s3://librechat-screenshots/ \
            ./test-screenshots/
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: e2e/playwright-report/
```

---

## 🎯 Common Test Scenarios

### **Test User Registration**

```bash
docker exec librechat-playwright npx playwright test specs/landing.spec.ts -g "registration"
```

### **Test Message Sending**

```bash
docker exec librechat-playwright npx playwright test specs/messages.spec.ts
```

### **Test Settings**

```bash
docker exec librechat-playwright npx playwright test specs/settings.spec.ts
```

### **Test Accessibility**

```bash
docker exec librechat-playwright npx playwright test specs/a11y.spec.ts
```

---

## 🆘 Troubleshooting

### **Issue: Playwright container won't start**

```bash
# Check logs
docker logs librechat-playwright

# Rebuild container
docker compose -f docker-compose.localstack.yml up -d --build playwright
```

### **Issue: Tests can't reach LibreChat**

```bash
# Verify LibreChat is running
docker ps | grep LibreChat-LocalStack

# Check network connectivity
docker exec librechat-playwright curl http://api:3080/api/health

# Check BASE_URL environment variable
docker exec librechat-playwright env | grep BASE_URL
```

### **Issue: Screenshots not saving to S3**

```bash
# Verify S3 bucket exists
aws --endpoint-url=http://localhost:4566 s3 ls | grep screenshots

# Create bucket if missing
aws --endpoint-url=http://localhost:4566 s3 mb s3://librechat-screenshots

# Check AWS credentials in container
docker exec librechat-playwright env | grep AWS
```

### **Issue: Tests timeout**

```bash
# Increase timeout in playwright.config.ts
expect: {
  timeout: 30000,  // Increase from 10000
}

# Or set in test file
test.setTimeout(60000);
```

---

## 📈 Performance Tips

1. **Run tests in parallel** (for faster execution):
   ```bash
   docker exec librechat-playwright npx playwright test --workers=4
   ```

2. **Run only failed tests**:
   ```bash
   docker exec librechat-playwright npx playwright test --last-failed
   ```

3. **Skip slow tests** in development:
   ```typescript
   test.skip('slow test', async ({ page }) => {
     // This test will be skipped
   });
   ```

4. **Use test tags**:
   ```typescript
   test('quick test @fast', async ({ page }) => {
     // Run with: npx playwright test --grep @fast
   });
   ```

---

## 🎊 Summary

✅ **Playwright E2E tests** configured for LocalStack  
✅ **Screenshots** saved to LocalStack S3  
✅ **9 test suites** ready to run  
✅ **VNC support** for visual debugging  
✅ **CI/CD ready** with Docker integration  

**Run tests now:**
```bash
./run-e2e-tests.sh
```

Or manually:
```bash
docker compose -f docker-compose.localstack.yml up -d playwright
docker exec librechat-playwright npm run test:e2e
```

---

## 📚 Resources

- [Playwright Docs](https://playwright.dev/)
- [LocalStack S3 Docs](https://docs.localstack.cloud/user-guide/aws/s3/)
- [LibreChat E2E Tests](./e2e/specs/)
- [Test Configuration](./e2e/playwright.config.ts)
