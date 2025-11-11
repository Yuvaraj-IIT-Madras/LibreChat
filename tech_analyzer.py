#!/usr/bin/env python3
"""
Technology Stack Analyzer - Uses LLM to detect tech stack and generate .documentignore patterns
"""

import os
import json
import pathspec
from pathlib import Path
from typing import Set, List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Common tech stack detection patterns
TECH_PATTERNS = {
    "nodejs": [
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "node_modules/",
        "npm-debug.log",
        ".npm",
    ],
    "python": [
        "requirements.txt",
        "setup.py",
        "Pipfile",
        "poetry.lock",
        "pyproject.toml",
        "*.egg-info/",
        "__pycache__/",
        "*.pyc",
        ".venv/",
        "venv/",
    ],
    "java": [
        "pom.xml",
        "build.gradle",
        "settings.gradle",
        "target/",
        "build/",
        ".gradle/",
        "*.class",
        "*.jar",
    ],
    "go": [
        "go.mod",
        "go.sum",
        "vendor/",
        "dist/",
    ],
    "rust": [
        "Cargo.toml",
        "Cargo.lock",
        "target/",
    ],
    "dotnet": [
        "*.csproj",
        "*.sln",
        "bin/",
        "obj/",
        ".vs/",
        "packages/",
    ],
    "ruby": [
        "Gemfile",
        "Gemfile.lock",
        ".bundle/",
        "vendor/bundle/",
    ],
    "php": [
        "composer.json",
        "composer.lock",
        "vendor/",
    ],
}

# Tech stack specific ignore patterns
TECH_IGNORE_PATTERNS = {
    "nodejs": [
        "node_modules/",
        "npm-debug.log*",
        "yarn-error.log*",
        ".npm/",
        "dist/",
        "build/",
    ],
    "python": [
        "__pycache__/",
        "*.egg-info/",
        ".Python",
        "*.pyc",
        "*.pyo",
        ".venv/",
        "venv/",
        "env/",
        ".eggs/",
        "*.egg",
        ".pytest_cache/",
        ".coverage",
    ],
    "java": [
        "target/",
        "build/",
        ".gradle/",
        "*.class",
        "*.jar",
        ".m2/",
    ],
    "go": [
        "vendor/",
        "dist/",
    ],
    "rust": [
        "target/",
    ],
    "dotnet": [
        "bin/",
        "obj/",
        ".vs/",
        "packages/",
    ],
    "ruby": [
        ".bundle/",
        "vendor/bundle/",
    ],
    "php": [
        "vendor/",
    ],
}


def detect_technologies(directory: str) -> Set[str]:
    """Detect technologies used in the directory by scanning for config files (including nested)"""
    detected_techs = set()
    directory_path = Path(directory)

    for tech, patterns in TECH_PATTERNS.items():
        for pattern in patterns:
            # Check for files or directories
            try:
                if pattern.endswith("/"):
                    # Check for directory (recursive)
                    if (directory_path / pattern.rstrip("/")).exists():
                        detected_techs.add(tech)
                        break
                    # Also check for nested occurrences
                    if list(directory_path.glob(f"**/{pattern.rstrip('/')}")):
                        detected_techs.add(tech)
                        break
                else:
                    # Check for file using glob (recursive)
                    if list(directory_path.glob(pattern)):
                        detected_techs.add(tech)
                        break
                    # Also check for nested occurrences
                    if list(directory_path.glob(f"**/{pattern}")):
                        detected_techs.add(tech)
                        break
            except Exception:
                continue

    return detected_techs


def analyze_with_llm(directory: str, detected_techs: Set[str]) -> Dict:
    """Use LLM to analyze the project and recommend ignore patterns"""

    tech_list = ", ".join(sorted(detected_techs)) if detected_techs else "unknown"

    prompt = f"""Analyze this software project and provide ignore patterns for .documentignore file.

Directory: {directory}
Detected Technologies: {tech_list}

For this technology stack, provide:
1. A comprehensive list of directories to ignore (node_modules, build artifacts, dependencies, caches, etc.)
2. File patterns to ignore (compiled files, logs, cache files, etc.)
3. Framework/library specific directories unique to these technologies

Respond in JSON format:
{{
    "detected_techs": ["list of technologies"],
    "directories_to_ignore": ["dir1/", "dir2/", ...],
    "file_patterns_to_ignore": ["*.pyc", "*.log", "*.jar", ...],
    "framework_specific": ["framework-specific patterns"],
    "reasoning": "Brief explanation of why these patterns"
}}

Be comprehensive and include patterns for commonly used libraries, package managers, build systems, and caches."""

    response = model.generate_content(prompt)
    
    try:
        # Extract JSON from response (handle markdown code blocks and comments)
        response_text = response.text
        
        # Remove markdown code block wrapper if present
        if response_text.strip().startswith("```"):
            response_text = response_text.strip()
            # Remove opening ```json or ```
            response_text = response_text[response_text.find("\n") + 1:]
            # Remove closing ```
            response_text = response_text[:response_text.rfind("```")]
        
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_str = response_text[json_start:json_end]
        
        # Remove JavaScript-style comments from JSON
        import re
        json_str = re.sub(r'//.*?(?=\n|")', '', json_str)  # Remove // comments
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
        
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️  Could not parse LLM response as JSON: {e}")
        print(f"Raw response (first 500 chars): {response.text[:500]}")
        return {"error": str(e)}


def generate_documentignore_content(analysis: Dict) -> str:
    """Generate .documentignore file content from LLM analysis"""

    content = """# Auto-generated .documentignore file
# Generated by tech_analyzer.py using LLM analysis
# Customize as needed for your specific project

"""

    if "reasoning" in analysis:
        content += f"# Analysis: {analysis['reasoning']}\n\n"

    # Git files
    content += """# Git files
.git/
.gitignore
.gitattributes

# Archives
*.zip
*.tar
*.gz
*.rar
*.7z
*.tar.gz
*.tar.bz2

# Compiled files
*.pyc
*.pyo
*.class
*.o
*.exe
*.dll
*.so

"""

    # Add directories to ignore
    if "directories_to_ignore" in analysis:
        content += "# Build and dependency directories\n"
        for dir_pattern in analysis["directories_to_ignore"]:
            if not dir_pattern.endswith("/"):
                dir_pattern += "/"
            content += f"{dir_pattern}\n"
        content += "\n"

    # Add file patterns
    if "file_patterns_to_ignore" in analysis:
        content += "# Log and cache files\n"
        for file_pattern in analysis["file_patterns_to_ignore"]:
            content += f"{file_pattern}\n"
        content += "\n"

    # Add framework specific patterns
    if "framework_specific" in analysis:
        content += "# Framework and library specific\n"
        for pattern in analysis["framework_specific"]:
            content += f"{pattern}\n"
        content += "\n"

    # Add IDE files
    content += """# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
*.sublime-project
*.sublime-workspace

# Environment files
.env
.env.local
.env.*.local

# Lock files (use original, not generated)
# (Keep package-lock.json, yarn.lock, etc. for reproduction)

"""

    return content


def count_files_with_patterns(directory: str, documentignore_path: str) -> Dict:
    """Count files that would be ingested vs ignored"""

    try:
        with open(documentignore_path, "r") as f:
            ignore_patterns = f.read()
    except FileNotFoundError:
        print(f"⚠️  {documentignore_path} not found")
        return {}

    spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns.splitlines())

    total_files = 0
    ingested_files = 0
    ignored_files = 0
    ignored_directories = 0
    unsupported_files = 0

    supported_extensions = {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".go",
        ".rs",
        ".cs",
        ".rb",
        ".php",
        ".cpp",
        ".c",
        ".h",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".toml",
        ".md",
        ".txt",
        ".sql",
        ".html",
        ".css",
        ".scss",
        ".less",
        ".pdf",
    }

    for root, dirs, files in os.walk(directory):
        rel_root = os.path.relpath(root, directory)

        # Check if directory should be ignored
        if rel_root != "." and spec.match_file(rel_root + "/"):
            ignored_directories += len(dirs)
            dirs.clear()
            continue

        for file in files:
            total_files += 1
            rel_file = os.path.relpath(os.path.join(root, file), directory)

            if spec.match_file(rel_file):
                ignored_files += 1
            else:
                _, ext = os.path.splitext(file)
                if ext.lower() in supported_extensions or file in [
                    "Dockerfile",
                    "Makefile",
                    "README",
                ]:
                    ingested_files += 1
                else:
                    unsupported_files += 1

    return {
        "total_files": total_files,
        "ingested_files": ingested_files,
        "ignored_files": ignored_files,
        "ignored_directories": ignored_directories,
        "unsupported_files": unsupported_files,
        "ingestion_percentage": round((ingested_files / total_files * 100), 2) if total_files > 0 else 0,
    }


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tech_analyzer.py <directory> [--update-ignore]")
        print(
            "       --update-ignore: Update .documentignore with LLM-generated patterns"
        )
        sys.exit(1)

    target_directory = sys.argv[1]
    update_ignore = "--update-ignore" in sys.argv

    if not os.path.isdir(target_directory):
        print(f"❌ Directory not found: {target_directory}")
        sys.exit(1)

    print(f"\n🔍 Analyzing technology stack in: {target_directory}\n")

    # Step 1: Detect technologies
    print("📱 Detecting technologies...")
    detected_techs = detect_technologies(target_directory)
    print(f"✅ Found: {', '.join(sorted(detected_techs)) if detected_techs else 'Generic project'}\n")

    # Step 2: Analyze with LLM
    print("🤖 Consulting LLM for comprehensive ignore patterns...")
    analysis = analyze_with_llm(target_directory, detected_techs)

    if "error" in analysis:
        print(f"❌ LLM analysis failed: {analysis['error']}")
        sys.exit(1)

    print("✅ LLM analysis complete\n")

    # Display analysis
    print("=" * 70)
    print("🧠 LLM ANALYSIS RESULTS")
    print("=" * 70)
    if "reasoning" in analysis:
        print(f"\n📋 Reasoning: {analysis['reasoning']}\n")

    if "detected_techs" in analysis:
        print(f"Detected Technologies: {', '.join(analysis['detected_techs'])}")

    print(f"\nDirectories to ignore: {len(analysis.get('directories_to_ignore', []))}")
    for d in analysis.get("directories_to_ignore", [])[:10]:
        print(f"  - {d}")
    if len(analysis.get("directories_to_ignore", [])) > 10:
        print(f"  ... and {len(analysis['directories_to_ignore']) - 10} more")

    print(f"\nFile patterns to ignore: {len(analysis.get('file_patterns_to_ignore', []))}")
    for f in analysis.get("file_patterns_to_ignore", [])[:10]:
        print(f"  - {f}")
    if len(analysis.get("file_patterns_to_ignore", [])) > 10:
        print(f"  ... and {len(analysis['file_patterns_to_ignore']) - 10} more")

    print(f"\nFramework-specific patterns: {len(analysis.get('framework_specific', []))}")
    for p in analysis.get("framework_specific", [])[:10]:
        print(f"  - {p}")
    if len(analysis.get("framework_specific", [])) > 10:
        print(f"  ... and {len(analysis['framework_specific']) - 10} more")

    # Step 3: Generate .documentignore content
    print("\n" + "=" * 70)
    new_ignore_content = generate_documentignore_content(analysis)

    if update_ignore:
        ignore_file = os.path.join(
            os.path.dirname(__file__), ".documentignore"
        )
        with open(ignore_file, "w") as f:
            f.write(new_ignore_content)
        print(f"\n✅ Updated: {ignore_file}\n")

        # Step 4: Count files with new patterns
        print("📊 Running file count analysis with updated patterns...\n")
        counts = count_files_with_patterns(target_directory, ignore_file)

        if counts:
            print("=" * 70)
            print("📈 FILE INGESTION ANALYSIS")
            print("=" * 70)
            print(f"Total files: {counts['total_files']}")
            print(
                f"✅ Files for RAG ingestion: {counts['ingested_files']} ({counts['ingestion_percentage']}%)"
            )
            print(
                f"⏭️  Files ignored: {counts['ignored_files']} + {counts['ignored_directories']} directories"
            )
            print(f"❌ Unsupported file types: {counts['unsupported_files']}")
            print("=" * 70)
    else:
        print("\n📄 Generated .documentignore content (use --update-ignore to apply):\n")
        print(new_ignore_content)
        print("\n💡 Tip: Run with --update-ignore to save and analyze with new patterns")


if __name__ == "__main__":
    main()
