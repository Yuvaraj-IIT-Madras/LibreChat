#!/usr/bin/env python3
"""
Quick script to count files that would be ingested without actually connecting to the database.
This helps us analyze which files pass the .documentignore filter.
"""
import os
import argparse
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

# --- File Handlers ---
DOCUMENT_LOADERS = {
    ".txt", ".pdf", ".csv", ".py", ".html", ".md", ".js", ".ts", ".java"
}

def load_ignore_patterns(ignore_file_path):
    """Loads ignore patterns from a .documentignore file."""
    if not os.path.exists(ignore_file_path):
        return PathSpec.from_lines(GitWildMatchPattern, [])
    with open(ignore_file_path, 'r') as f:
        patterns = f.readlines()
    return PathSpec.from_lines(GitWildMatchPattern, patterns)

def count_files(directory_path, ignore_spec):
    """Recursively count files that would be loaded vs ignored."""
    loaded_files = []
    ignored_dirs = []
    ignored_files = []
    unsupported_files = []
    
    for root, dirs, files in os.walk(directory_path):
        # Create a relative path from the directory_path for matching
        relative_root = os.path.relpath(root, directory_path)
        if ignore_spec.match_file(relative_root):
            ignored_dirs.append(root)
            # Don't recurse into ignored directories
            dirs.clear()
            continue

        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, directory_path)
            
            if ignore_spec.match_file(relative_file_path):
                ignored_files.append(file_path)
                continue

            ext = os.path.splitext(file)[1].lower()
            if ext in DOCUMENT_LOADERS:
                loaded_files.append(file_path)
            else:
                unsupported_files.append(file_path)

    return loaded_files, ignored_files, ignored_dirs, unsupported_files

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Count files that would be ingested.")
    parser.add_argument("path", type=str, help="The path to the directory to analyze.")
    args = parser.parse_args()

    print(f"\n📂 Analyzing directory: {args.path}\n")

    # Load ignore patterns
    ignore_file_path = "/home/yuvaraj/Projects/LibreChat/.documentignore"
    ignore_spec = load_ignore_patterns(ignore_file_path)
    print(f"✓ Loaded ignore patterns from: {ignore_file_path}\n")

    # Count files
    loaded, ignored_files, ignored_dirs, unsupported = count_files(args.path, ignore_spec)

    print("=" * 70)
    print("📊 FILE INGESTION ANALYSIS REPORT")
    print("=" * 70)
    
    print(f"\n✅ FILES FOR INGESTION (vectorization): {len(loaded)}")
    if loaded and len(loaded) <= 20:
        for f in loaded:
            print(f"   - {f}")
    elif loaded:
        for f in loaded[:10]:
            print(f"   - {f}")
        print(f"   ... and {len(loaded) - 10} more files")
    
    print(f"\n⏭️  IGNORED FILES (by .documentignore): {len(ignored_files)}")
    if ignored_files and len(ignored_files) <= 10:
        for f in ignored_files:
            print(f"   - {f}")
    elif ignored_files:
        for f in ignored_files[:5]:
            print(f"   - {f}")
        print(f"   ... and {len(ignored_files) - 5} more files")
    
    print(f"\n⏭️  IGNORED DIRECTORIES: {len(ignored_dirs)}")
    if ignored_dirs and len(ignored_dirs) <= 10:
        for d in ignored_dirs:
            print(f"   - {d}")
    elif ignored_dirs:
        for d in ignored_dirs[:5]:
            print(f"   - {d}")
        print(f"   ... and {len(ignored_dirs) - 5} more directories")
    
    print(f"\n❌ UNSUPPORTED FILES (won't be ingested): {len(unsupported)}")
    if unsupported and len(unsupported) <= 10:
        for f in unsupported[:10]:
            print(f"   - {f}")
    elif unsupported:
        for f in unsupported[:5]:
            print(f"   - {f}")
        print(f"   ... and {len(unsupported) - 5} more files")
    
    print("\n" + "=" * 70)
    print("📈 SUMMARY")
    print("=" * 70)
    total_files = len(loaded) + len(ignored_files) + len(unsupported)
    print(f"Total files analyzed: {total_files}")
    print(f"Files for RAG ingestion: {len(loaded)} ({100*len(loaded)//total_files if total_files > 0 else 0}%)")
    print(f"Files ignored: {len(ignored_files) + len(unsupported)} ({100*(len(ignored_files)+len(unsupported))//total_files if total_files > 0 else 0}%)")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
