# Intelligent Document Filtering with LLM-Based Tech Stack Analysis

## Overview

This system uses an LLM (Google Gemini) to intelligently analyze your project's technology stack and automatically generate comprehensive `.documentignore` patterns. This ensures that all language-specific, framework-specific, and build-tool-specific artifacts are properly excluded from RAG ingestion.

## Architecture

### 1. **Tech Stack Detection** (`tech_analyzer.py`)
The script performs two-phase detection:

#### Phase 1: Static Pattern Matching
Scans for common configuration files to detect technologies:
- **Node.js**: `package.json`, `package-lock.json`, `yarn.lock`
- **Python**: `requirements.txt`, `setup.py`, `Pipfile`, `poetry.lock`, `pyproject.toml`
- **Java**: `pom.xml`, `build.gradle`, `settings.gradle`
- **Go**: `go.mod`, `go.sum`
- **Rust**: `Cargo.toml`, `Cargo.lock`
- **.NET**: `*.csproj`, `*.sln`
- **Ruby**: `Gemfile`, `Gemfile.lock`
- **PHP**: `composer.json`, `composer.lock`

#### Phase 2: LLM-Based Analysis
Sends detected technologies to Gemini with a prompt asking for:
1. Complete list of directories to ignore (dependencies, builds, caches)
2. File patterns to ignore (compiled files, logs, archives)
3. Framework-specific patterns (migrations, static files, test artifacts)
4. Detailed reasoning for each pattern

### 2. **.documentignore Generation**
The LLM response is parsed and converted into a `.gitignore`-compatible file with sections:
- Git/version control files
- Archives and compressed files
- Compiled and binary files
- Build and dependency directories
- Log and cache files
- Framework-specific patterns
- IDE and editor files
- Environment configuration

## Usage

### Basic Analysis (Display Only)
```bash
python tech_analyzer.py /path/to/project
```

This will:
1. Detect the tech stack
2. Consult LLM for patterns
3. Display the generated patterns
4. NOT modify `.documentignore`

### Apply and Analyze (Update + Count)
```bash
python tech_analyzer.py /path/to/project --update-ignore
```

This will:
1. Detect the tech stack
2. Consult LLM for patterns
3. **Update** `.documentignore` with new patterns
4. Analyze file counts with the new patterns
5. Display statistics (total files, ingested files, ignored files)

## Example: Crawlio Project Analysis

### Before LLM Analysis
- **Ignore Patterns**: Generic (node_modules, build artifacts only)
- **Files for Ingestion**: 539 (47%)
- **Files Ignored**: 585 (52%)
- **Problem**: Python-specific patterns missing (migrations, caches, test artifacts)

### After LLM Analysis
Generated patterns now include:
```
# Node.js specific
node_modules/
.next/
.nuxt/
dist/
build/

# Python specific
venv/
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
pylint.d/

# Framework specific
scrapy.cfg
**/scrapy_cache/
pytest.ini
tox.ini
**/alembic/
**/migrations/

# Testing artifacts
.coverage/
htmlcov/
.nyc_output/

# Development
.env
.env.*
.vscode/
.idea/
```

### Results
- **Files for Ingestion**: 64 (57.14%)
- **Files Ignored**: 33 + 794 directories
- **Efficiency**: 52% of files properly excluded from RAG processing

## Key Benefits

### 1. **Technology-Agnostic**
Works with any tech stack:
- ✅ Node.js/JavaScript/TypeScript projects
- ✅ Python/Django/Flask projects
- ✅ Java/Spring/Gradle projects
- ✅ Polyglot projects (Node.js + Python + Java)

### 2. **Future-Proof**
When you add new technologies to your project:
1. Run: `python tech_analyzer.py /path/to/project --update-ignore`
2. LLM automatically detects the new tech
3. `.documentignore` is updated with appropriate patterns
4. No manual pattern research needed

### 3. **Performance Optimization**
- **Before**: 539 files ingested (47%)
- **After**: 64 files ingested (57.14% of reduced set)
- **Reduction**: ~90% fewer files processed by RAG
- **Benefits**: Faster ingestion, lower embeddings cost, better signal-to-noise ratio

### 4. **Best Practices**
LLM-generated patterns include industry best practices:
- Lock files (handled specially for reproducibility)
- Secret files (`.env`, `.secret`)
- IDE settings (`.vscode/`, `.idea/`)
- Certificate/key files (`.pem`, `.key`, `.crt`)

## Supported LLM Models

Currently configured to use:
- **Model**: `gemini-2.0-flash` (fast, cost-effective)
- **Alternative**: Can be switched to `gemini-1.5-pro` for more detailed analysis

To change the model, edit `tech_analyzer.py`:
```python
model = genai.GenerativeModel("gemini-2.0-flash")  # Change this
```

## Integration with RAG Pipeline

After updating `.documentignore`:

```bash
# 1. Update patterns based on tech stack
python tech_analyzer.py /home/yuvaraj/Documents/Archive/crawlio --update-ignore

# 2. Run ingestion with optimized patterns
python ingest.py /home/yuvaraj/Documents/Archive/crawlio

# 3. Query the RAG database
python query.py "how do I deploy this application?"
```

## File Structure

```
/home/yuvaraj/Projects/LibreChat/
├── tech_analyzer.py          # Main intelligence script
├── .documentignore           # Auto-generated ignore patterns
├── ingest.py                 # RAG ingestion pipeline
├── query.py                  # Vector similarity search
├── count_files.py            # File analysis utility
└── INTELLIGENT_FILTERING_GUIDE.md  # This guide
```

## Customization

### Adding Custom Patterns
Edit `.documentignore` to add project-specific patterns:
```
# Project specific
*.tmp
*.bak
secrets/
private/
```

### Regenerating Patterns
If you've manually edited `.documentignore`, you can regenerate it:
```bash
python tech_analyzer.py /path/to/project --update-ignore
```

This will preserve your custom additions as long as they're not in the auto-generated section.

## Performance Considerations

### Ingestion Speed Impact
- **Fewer files processed**: ~90% reduction
- **Fewer embeddings generated**: Proportional reduction
- **Database queries**: Faster (smaller vector space)
- **API costs**: Reduced (fewer embeddings)

### For Large Monorepos
With multiple tech stacks (Node.js + Python + Java):
```bash
# Analyze once, benefit from all tech-specific patterns
python tech_analyzer.py /path/to/monorepo --update-ignore
```

The LLM will detect all technologies and generate comprehensive patterns for all of them.

## Troubleshooting

### Issue: LLM returns non-JSON response
**Solution**: Check internet connection and API key in `.env`

### Issue: Too many files still being ingested
**Solution**: Review generated patterns and add custom sections to `.documentignore`

### Issue: Important files are being ignored
**Solution**: Review the file patterns in `.documentignore` and comment out overly broad patterns

## Future Enhancements

1. **Multi-language detection**: Parse source files to infer additional technologies
2. **Context-aware filtering**: Ask LLM what the project does and ignore irrelevant files
3. **Pattern versioning**: Track `.documentignore` changes over time
4. **Performance metrics**: Log ingestion time before/after for comparison
5. **Feedback loop**: Learn from user corrections to improve patterns

## Example Output

```
🔍 Analyzing technology stack in: /home/yuvaraj/Documents/Archive/crawlio

📱 Detecting technologies...
✅ Found: nodejs, python

🤖 Consulting LLM for comprehensive ignore patterns...
✅ LLM analysis complete

======================================================================
🧠 LLM ANALYSIS RESULTS
======================================================================

📋 Reasoning: This list covers common artifacts produced during...

Detected Technologies: nodejs, python

Directories to ignore: 27
File patterns to ignore: 44
Framework-specific patterns: 15

======================================================================
✅ Updated: /home/yuvaraj/Projects/LibreChat/.documentignore

📊 Running file count analysis with updated patterns...

======================================================================
📈 FILE INGESTION ANALYSIS
======================================================================
Total files: 112
✅ Files for RAG ingestion: 64 (57.14%)
⏭️  Files ignored: 33 + 794 directories
❌ Unsupported file types: 15
======================================================================
```

## Questions & Support

For issues or questions:
1. Check the generated `.documentignore` file
2. Review LLM reasoning in the output
3. Verify your project structure matches expected patterns
4. Ensure `.env` has valid `GOOGLE_KEY` for Gemini API access
