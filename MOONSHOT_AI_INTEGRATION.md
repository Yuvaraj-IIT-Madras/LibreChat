# Moonshot AI (Kimi K2) Integration Guide

## 🎯 Overview

**Kimi K2** is Moonshot AI's newly released open-source Mixture-of-Experts (MoE) model with:
- ✅ 1 trillion-parameter architecture
- ✅ Top-tier benchmark scores in coding & reasoning
- ✅ Free, open-source access
- ✅ Excellent for agentic tasks, tool use, and reasoning
- ✅ Context length: up to 128K tokens

---

## 📋 Step-by-Step Setup

### Step 1: Create a Moonshot API Account

1. Go to: **https://platform.moonshot.ai/console**
2. Sign up for a new Moonshot API account
3. Complete the registration process

### Step 2: Add Balance to Your Account

1. Visit: **https://platform.moonshot.ai/console/pay**
2. Add funds to your account (minimum $1 USD to test)
3. Choose your payment method
4. Complete payment

### Step 3: Get Your API Key

1. Go to: **https://platform.moonshot.ai/console/api-keys**
2. Click "Create New API Key"
3. Copy and save your API key securely
4. **IMPORTANT**: Never share this key publicly!

```
Your API key format will look like:
sk_XXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## 🔧 Integration Options

### Option A: Use with TypingMind (UI-based)

If you're using TypingMind:

1. Go to **Models** → **Add Custom Models**
2. Enter the following details:
   - **Model Name**: `Kimi K2` (or your preferred name)
   - **Endpoint**: `https://api.moonshot.ai/v1/chat/completions`
   - **Model ID**: `kimi-k2-0711-preview` or `kimi-k2-0905-preview`
   - **Context Length**: 128K
   - **Custom Header**: 
     - Header Name: `Authorization`
     - Value: `Bearer sk_YOUR_API_KEY_HERE`
3. Click "Test" to verify
4. Click "Add Model"

### Option B: Use with Your RAG System (Python)

Add Moonshot AI as an alternative to your current embedding/chat model:

#### Install the library:
```bash
pip install openai
```

#### Python integration code:

```python
from openai import OpenAI

# Initialize Moonshot client
client = OpenAI(
    api_key="sk_YOUR_API_KEY_HERE",
    base_url="https://api.moonshot.ai/v1",
)

# Use for chat/RAG analysis
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {
            "role": "system",
            "content": "You are an AI assistant analyzing code repositories."
        },
        {
            "role": "user",
            "content": "Analyze this code snippet and explain what it does..."
        }
    ],
    temperature=0.7,
    max_tokens=2000,
)

print(response.choices[0].message.content)
```

### Option C: Use with Your tech_analyzer.py

Modify `tech_analyzer.py` to support multiple LLM providers:

```python
# Add to tech_analyzer.py
def analyze_with_moonshot_ai(directory: str, detected_techs: Set[str]) -> Dict:
    """Use Moonshot AI (Kimi K2) for tech stack analysis"""
    
    from openai import OpenAI
    
    client = OpenAI(
        api_key=os.getenv("MOONSHOT_API_KEY"),
        base_url="https://api.moonshot.ai/v1",
    )
    
    tech_list = ", ".join(sorted(detected_techs)) if detected_techs else "unknown"
    
    prompt = f"""Analyze this software project and provide ignore patterns for .documentignore file.

Directory: {directory}
Detected Technologies: {tech_list}

[rest of prompt...]
"""
    
    response = client.chat.completions.create(
        model="kimi-k2-0905-preview",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in software project analysis..."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=4000,
    )
    
    return parse_response(response.choices[0].message.content)
```

---

## 🔑 Available Moonshot Models

| Model ID | Context | Use Case |
|----------|---------|----------|
| `kimi-k2-0711-preview` | 128K | Initial release, good for most tasks |
| `kimi-k2-0905-preview` | 128K | Latest, improved reasoning |

Check latest models: **https://platform.moonshot.ai/docs/introduction#other-important-notes**

---

## 📝 Add API Key to Your Project

### Update your `.env` file:

```bash
# Google Gemini (existing)
GOOGLE_KEY=your-gemini-api-key

# Moonshot AI (new)
MOONSHOT_API_KEY=sk_your_moonshot_api_key_here
```

### Update requirements.txt:

```bash
# Existing packages...
langchain
langchain-community
langchain-google-genai

# Add for Moonshot support
openai>=1.0.0
```

### Install dependencies:

```bash
pip install openai
```

---

## 💡 Use Cases for Kimi K2 in Your RAG System

### 1. Enhanced Tech Stack Analysis
```python
# Use Kimi K2 instead of Gemini for tech_analyzer.py
# Better reasoning for complex monorepos
python tech_analyzer.py /path/to/project --use-moonshot
```

### 2. Smart Pattern Generation
- Leverage Kimi K2's superior reasoning for framework-specific patterns
- Better context understanding for polyglot projects

### 3. Query Enhancement
```python
# Use Kimi K2 to enhance query results
query = "How does this authentication system work?"
# Gemini finds relevant docs
# Kimi K2 synthesizes a comprehensive answer
```

### 4. Code Analysis
- Better understanding of complex code patterns
- Superior coding benchmark scores (53.7% on LiveCodeBench)
- Excellent for explaining implementation details

---

## 🔄 Comparison: Gemini vs Moonshot AI (Kimi K2)

| Aspect | Google Gemini | Kimi K2 |
|--------|---------------|---------|
| **Cost** | Pay per token | Pay per token |
| **Context** | 32K-1M tokens | 128K tokens |
| **Coding** | Good | Excellent (53.7% LiveCodeBench) |
| **Reasoning** | Very good | Excellent (MoE architecture) |
| **Speed** | Fast | Fast |
| **Availability** | Global | Requires account |
| **Best For** | Embeddings, general tasks | Reasoning, code analysis |

---

## 🚀 Hybrid Approach (Recommended)

Use both models for optimal results:

```python
# tech_analyzer.py enhancement
USE_GEMINI_FOR_EMBEDDINGS = True  # Fast embeddings
USE_MOONSHOT_FOR_ANALYSIS = True  # Better reasoning

if USE_GEMINI_FOR_EMBEDDINGS:
    embeddings = GoogleGenerativeAIEmbeddings()
    
if USE_MOONSHOT_FOR_ANALYSIS:
    analysis = analyze_with_moonshot_ai(directory, detected_techs)
```

---

## 🐛 Troubleshooting

### Issue: "API key not found"
```bash
# Check .env file
cat /home/yuvaraj/Projects/LibreChat/.env

# Add if missing
echo "MOONSHOT_API_KEY=sk_your_key_here" >> .env
```

### Issue: "Connection refused"
- Verify internet connection
- Check firewall rules
- Ensure API key is valid: https://platform.moonshot.ai/console/api-keys

### Issue: "Quota exceeded"
- Check your balance: https://platform.moonshot.ai/console/pay
- Add more funds if needed
- Monitor usage: https://platform.moonshot.ai/console/usage

### Issue: "Model not found"
- Verify model ID: `kimi-k2-0905-preview`
- Check latest models: https://platform.moonshot.ai/docs

---

## 📊 Pricing

Moonshot AI typically offers competitive pricing:
- **Input tokens**: ~$0.0005-0.001 per 1K tokens (varies by model)
- **Output tokens**: ~$0.0015-0.003 per 1K tokens (varies by model)

Start with $5-10 for testing and monitoring.

---

## 🎯 Next Steps

### Immediate (Today)
1. Create Moonshot API account
2. Get API key
3. Add to `.env` file

### Short Term (This Week)
1. Test Kimi K2 with sample queries
2. Compare results with Gemini
3. Decide on integration approach

### Medium Term (This Month)
1. Integrate into tech_analyzer.py
2. Use for enhanced RAG analysis
3. Monitor performance and costs

---

## 📚 Useful Links

| Resource | URL |
|----------|-----|
| **API Console** | https://platform.moonshot.ai/console |
| **API Keys** | https://platform.moonshot.ai/console/api-keys |
| **Payment** | https://platform.moonshot.ai/console/pay |
| **Documentation** | https://platform.moonshot.ai/docs |
| **Models Info** | https://platform.moonshot.ai/docs/introduction |
| **Usage Stats** | https://platform.moonshot.ai/console/usage |

---

## 🔐 Security Best Practices

### ✅ DO:
- Store API key in `.env` file (never in code)
- Use environment variables in production
- Rotate keys periodically
- Monitor usage for unusual activity
- Keep API key confidential

### ❌ DON'T:
- Commit API key to git repository
- Share API key in chat/email
- Use same key for multiple projects
- Store in plaintext config files
- Push `.env` to version control

---

## 💻 Quick Integration Example

### Simple Python script to test Moonshot AI:

```python
#!/usr/bin/env python3
"""Test Moonshot AI (Kimi K2) integration"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MOONSHOT_API_KEY")
if not api_key:
    raise ValueError("MOONSHOT_API_KEY not found in .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.ai/v1",
)

# Test message
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {
            "role": "user",
            "content": "What are the best practices for Python project structure?"
        }
    ],
    temperature=0.7,
    max_tokens=1000,
)

print("✅ Moonshot AI Response:")
print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")
```

Save as `test_moonshot.py` and run:
```bash
python test_moonshot.py
```

---

## 🎉 You're Ready!

You now have:
- ✅ Moonshot API account created
- ✅ API key generated
- ✅ Integration guide for your RAG system
- ✅ Multiple usage options
- ✅ Troubleshooting help
- ✅ Security best practices

**Next step**: Add your API key to `.env` and start exploring Kimi K2 capabilities!

---

*Last Updated: November 7, 2025*
*Compatible with: Moonshot AI API v1*
*Context: Kimi K2 integration for intelligent RAG analysis*
