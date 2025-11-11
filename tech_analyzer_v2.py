#!/usr/bin/env python3
"""
Advanced Tech Analyzer v2.0
Intelligently detects technologies, frameworks, and dependencies using LLM
Generates optimized .documentignore patterns
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict
import google.generativeai as genai
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TechStack:
    """Represents detected technology stack"""
    languages: List[str]
    frameworks: List[str]
    package_managers: List[str]
    databases: List[str]
    cloud_platforms: List[str]
    build_tools: List[str]
    testing_frameworks: List[str]
    ci_cd_tools: List[str]
    other_tools: List[str]
    confidence: float
    reasoning: str


@dataclass
class Dependency:
    """Represents a single dependency"""
    name: str
    version: str
    file_path: str
    package_manager: str
    dependency_type: str  # direct, dev, optional, peer
    transitive_deps: List[str]


class AdvancedTechAnalyzer:
    """Enhanced tech analyzer using LLM for intelligent detection"""

    def __init__(self, google_api_key: str = None):
        """Initialize analyzer with Gemini API"""
        if not google_api_key:
            google_api_key = os.getenv("GOOGLE_KEY")
        
        if not google_api_key:
            raise ValueError("GOOGLE_KEY environment variable not set")
        
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Pattern definitions for detection
        self.patterns = self._load_patterns()
        self.detected_stack = None
        self.dependencies_found = []

    def _load_patterns(self) -> Dict:
        """Load detection patterns for various technologies"""
        return {
            "python": {
                "markers": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "*.py"],
                "package_manager": ["pip", "poetry", "pipenv", "conda"],
                "config_files": ["setup.cfg", "setup.py", "pyproject.toml"]
            },
            "nodejs": {
                "markers": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
                "package_manager": ["npm", "yarn", "pnpm"],
                "config_files": ["package.json", "tsconfig.json", "webpack.config.js", ".babelrc"]
            },
            "java": {
                "markers": ["pom.xml", "build.gradle", "*.java", "settings.gradle"],
                "package_manager": ["maven", "gradle"],
                "config_files": ["pom.xml", "build.gradle", "gradle.properties"]
            },
            "go": {
                "markers": ["go.mod", "go.sum", "*.go", "Makefile"],
                "package_manager": ["go", "dep"],
                "config_files": ["go.mod", "go.sum"]
            },
            "rust": {
                "markers": ["Cargo.toml", "Cargo.lock", "*.rs"],
                "package_manager": ["cargo"],
                "config_files": ["Cargo.toml"]
            },
            "php": {
                "markers": ["composer.json", "composer.lock", "*.php"],
                "package_manager": ["composer"],
                "config_files": ["composer.json"]
            },
            "dotnet": {
                "markers": ["*.csproj", "*.sln", "package.config", "*.vbproj"],
                "package_manager": ["nuget", "dotnet"],
                "config_files": ["*.csproj", "packages.config"]
            },
            "ruby": {
                "markers": ["Gemfile", "Gemfile.lock", "*.rb"],
                "package_manager": ["bundler", "gem"],
                "config_files": ["Gemfile"]
            }
        }

    def analyze_project(self, project_path: str) -> TechStack:
        """Analyze entire project for technologies"""
        logger.info(f"🔍 Analyzing project: {project_path}")
        
        project_path = Path(project_path)
        
        # Phase 1: Pattern-based detection
        detected_techs = self._pattern_based_detection(project_path)
        logger.info(f"✅ Pattern detection found: {detected_techs}")
        
        # Phase 2: File content analysis
        file_analysis = self._analyze_file_contents(project_path, detected_techs)
        
        # Phase 3: LLM-based intelligence
        tech_stack = self._llm_analysis(project_path, detected_techs, file_analysis)
        logger.info(f"🤖 LLM Analysis: {tech_stack.reasoning}")
        
        self.detected_stack = tech_stack
        return tech_stack

    def _pattern_based_detection(self, project_path: Path) -> Set[str]:
        """Detect technologies using file patterns"""
        detected = set()
        
        for tech, patterns_dict in self.patterns.items():
            for marker in patterns_dict["markers"]:
                # Check for exact files
                if marker.startswith("*."):
                    ext = marker.replace("*", "")
                    if list(project_path.rglob(f"*{ext}")):
                        detected.add(tech)
                        break
                else:
                    if list(project_path.rglob(marker)):
                        detected.add(tech)
                        break
        
        return detected

    def _analyze_file_contents(self, project_path: Path, detected_techs: Set[str]) -> Dict:
        """Analyze file contents for deeper insights"""
        analysis = {
            "frameworks": [],
            "databases": [],
            "libraries": [],
            "test_frameworks": [],
            "build_tools": [],
            "container_tech": [],
            "ci_cd": [],
            "monitoring": [],
            "file_statistics": {}
        }
        
        # Count files by type
        file_counts = defaultdict(int)
        
        for filepath in project_path.rglob("*"):
            if filepath.is_file() and not any(part.startswith(".") for part in filepath.parts):
                suffix = filepath.suffix.lower()
                file_counts[suffix] += 1
                
                # Scan key files
                if filepath.name in ["package.json", "requirements.txt", "pom.xml", "Gemfile"]:
                    self._scan_dependency_file(filepath, analysis)
                
                if "docker" in filepath.name.lower():
                    analysis["container_tech"].append("docker")
                
                if ".yml" in filepath.name or ".yaml" in filepath.name:
                    self._scan_config_file(filepath, analysis)
        
        analysis["file_statistics"] = dict(file_counts)
        return analysis

    def _scan_dependency_file(self, filepath: Path, analysis: Dict):
        """Scan package/dependency files"""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            # Framework detection
            frameworks_regex = [
                (r'react', 'React'),
                (r'vue', 'Vue.js'),
                (r'angular', 'Angular'),
                (r'express', 'Express.js'),
                (r'django', 'Django'),
                (r'flask', 'Flask'),
                (r'spring', 'Spring'),
                (r'fastapi', 'FastAPI'),
                (r'nestjs', 'NestJS'),
                (r'rails', 'Rails'),
            ]
            
            for pattern, name in frameworks_regex:
                if re.search(pattern, content, re.IGNORECASE):
                    if name not in analysis["frameworks"]:
                        analysis["frameworks"].append(name)
            
            # Database detection
            db_regex = [
                (r'postgres|postgresql', 'PostgreSQL'),
                (r'mongodb', 'MongoDB'),
                (r'mysql', 'MySQL'),
                (r'redis', 'Redis'),
                (r'elasticsearch', 'Elasticsearch'),
                (r'dynamodb', 'DynamoDB'),
                (r'clickhouse', 'ClickHouse'),
            ]
            
            for pattern, name in db_regex:
                if re.search(pattern, content, re.IGNORECASE):
                    if name not in analysis["databases"]:
                        analysis["databases"].append(name)
            
            # Testing framework detection
            test_regex = [
                (r'jest', 'Jest'),
                (r'pytest', 'Pytest'),
                (r'mocha', 'Mocha'),
                (r'junit', 'JUnit'),
                (r'rspec', 'RSpec'),
            ]
            
            for pattern, name in test_regex:
                if re.search(pattern, content, re.IGNORECASE):
                    if name not in analysis["test_frameworks"]:
                        analysis["test_frameworks"].append(name)
                        
        except Exception as e:
            logger.warning(f"Could not scan {filepath}: {e}")

    def _scan_config_file(self, filepath: Path, analysis: Dict):
        """Scan configuration files for insights"""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore').lower()
            
            ci_cd_tools = {
                'github': 'GitHub Actions',
                'gitlab': 'GitLab CI',
                'jenkins': 'Jenkins',
                'circleci': 'CircleCI',
                'travisci': 'Travis CI',
            }
            
            for tool, name in ci_cd_tools.items():
                if tool in content:
                    if name not in analysis["ci_cd"]:
                        analysis["ci_cd"].append(name)
                        
        except Exception as e:
            logger.warning(f"Could not scan config {filepath}: {e}")

    def _llm_analysis(self, project_path: Path, detected_techs: Set[str], 
                      file_analysis: Dict) -> TechStack:
        """Use LLM for intelligent tech stack analysis"""
        
        # Prepare project summary
        summary = self._prepare_project_summary(project_path, detected_techs, file_analysis)
        
        prompt = f"""
Analyze this project and provide comprehensive technology stack information:

PROJECT SUMMARY:
{summary}

DETECTED PATTERNS: {', '.join(detected_techs)}
FRAMEWORKS: {', '.join(file_analysis.get('frameworks', []))}
DATABASES: {', '.join(file_analysis.get('databases', []))}
CONTAINERS: {', '.join(file_analysis.get('container_tech', []))}
CI/CD: {', '.join(file_analysis.get('ci_cd', []))}

Please provide:
1. Confirmed technologies and frameworks
2. Likely databases used
3. Build and deployment tools
4. Testing frameworks
5. Cloud platform indicators
6. Any specialized tools or services
7. Confidence level (0-1)
8. Brief reasoning

Format as JSON with keys: languages, frameworks, package_managers, databases, 
cloud_platforms, build_tools, testing_frameworks, ci_cd_tools, other_tools, 
confidence, reasoning
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                tech_data = json.loads(json_match.group())
            else:
                tech_data = json.loads(response_text)
            
            return TechStack(
                languages=tech_data.get('languages', []),
                frameworks=tech_data.get('frameworks', []),
                package_managers=tech_data.get('package_managers', []),
                databases=tech_data.get('databases', []),
                cloud_platforms=tech_data.get('cloud_platforms', []),
                build_tools=tech_data.get('build_tools', []),
                testing_frameworks=tech_data.get('testing_frameworks', []),
                ci_cd_tools=tech_data.get('ci_cd_tools', []),
                other_tools=tech_data.get('other_tools', []),
                confidence=float(tech_data.get('confidence', 0.7)),
                reasoning=tech_data.get('reasoning', 'LLM analysis complete')
            )
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fallback to basic analysis
            return self._create_default_stack(detected_techs, file_analysis)

    def _prepare_project_summary(self, project_path: Path, detected_techs: Set[str],
                                 file_analysis: Dict) -> str:
        """Prepare a concise project summary for LLM"""
        total_files = sum(file_analysis.get('file_statistics', {}).values())
        
        top_extensions = sorted(
            file_analysis.get('file_statistics', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return f"""
Total Files: {total_files}
Top File Types: {', '.join(f'{ext}({count})' for ext, count in top_extensions)}
Detected Technologies: {', '.join(detected_techs)}
Frameworks: {', '.join(file_analysis.get('frameworks', []))}
Databases: {', '.join(file_analysis.get('databases', []))}
Has Docker: {len(file_analysis.get('container_tech', [])) > 0}
Has CI/CD Config: {len(file_analysis.get('ci_cd', [])) > 0}
"""

    def _create_default_stack(self, detected_techs: Set[str], file_analysis: Dict) -> TechStack:
        """Create default stack when LLM analysis fails"""
        return TechStack(
            languages=list(detected_techs),
            frameworks=file_analysis.get('frameworks', []),
            package_managers=[self.patterns[t]['package_manager'][0] for t in detected_techs if t in self.patterns],
            databases=file_analysis.get('databases', []),
            cloud_platforms=[],
            build_tools=file_analysis.get('build_tools', []),
            testing_frameworks=file_analysis.get('test_frameworks', []),
            ci_cd_tools=file_analysis.get('ci_cd', []),
            other_tools=file_analysis.get('container_tech', []),
            confidence=0.6,
            reasoning="Fallback analysis based on pattern detection"
        )

    def extract_dependencies(self, project_path: str) -> List[Dependency]:
        """Extract all dependencies from the project"""
        logger.info(f"📦 Extracting dependencies from {project_path}")
        
        project_path = Path(project_path)
        dependencies = []
        
        # Python dependencies
        dependencies.extend(self._extract_python_deps(project_path))
        
        # Node.js dependencies
        dependencies.extend(self._extract_nodejs_deps(project_path))
        
        # Java dependencies
        dependencies.extend(self._extract_java_deps(project_path))
        
        # Go dependencies
        dependencies.extend(self._extract_go_deps(project_path))
        
        # PHP dependencies
        dependencies.extend(self._extract_php_deps(project_path))
        
        self.dependencies_found = dependencies
        logger.info(f"✅ Found {len(dependencies)} dependencies")
        return dependencies

    def _extract_python_deps(self, project_path: Path) -> List[Dependency]:
        """Extract Python dependencies"""
        deps = []
        
        # requirements.txt
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            for line in req_file.read_text().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    dep = self._parse_requirement_line(line, str(req_file), 'pip')
                    if dep:
                        deps.append(dep)
        
        # pyproject.toml
        pyproject = project_path / "pyproject.toml"
        if pyproject.exists():
            deps.extend(self._parse_pyproject_toml(pyproject))
        
        return deps

    def _parse_requirement_line(self, line: str, file_path: str, pm: str) -> Dependency:
        """Parse a requirement line"""
        # Handle comments
        line = line.split('#')[0].strip()
        
        # Parse package and version
        for op in ['>=', '<=', '==', '~=', '!=', '>', '<']:
            if op in line:
                parts = line.split(op)
                name = parts[0].strip()
                version = op + parts[1].strip() if len(parts) > 1 else "*"
                return Dependency(
                    name=name,
                    version=version,
                    file_path=file_path,
                    package_manager=pm,
                    dependency_type="direct",
                    transitive_deps=[]
                )
        
        # No version specified
        return Dependency(
            name=line,
            version="*",
            file_path=file_path,
            package_manager=pm,
            dependency_type="direct",
            transitive_deps=[]
        )

    def _parse_pyproject_toml(self, filepath: Path) -> List[Dependency]:
        """Parse pyproject.toml for dependencies"""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        deps = []
        try:
            with open(filepath, 'rb') as f:
                data = tomllib.load(f)
            
            # Extract dependencies
            for dep_name, version in data.get('project', {}).get('dependencies', {}).items():
                deps.append(Dependency(
                    name=dep_name,
                    version=str(version),
                    file_path=str(filepath),
                    package_manager="pip",
                    dependency_type="direct",
                    transitive_deps=[]
                ))
            
            # Extract dev dependencies
            for dep_name, version in data.get('project', {}).get('optional-dependencies', {}).items():
                deps.append(Dependency(
                    name=dep_name,
                    version=str(version),
                    file_path=str(filepath),
                    package_manager="pip",
                    dependency_type="dev",
                    transitive_deps=[]
                ))
        except Exception as e:
            logger.warning(f"Could not parse {filepath}: {e}")
        
        return deps

    def _extract_nodejs_deps(self, project_path: Path) -> List[Dependency]:
        """Extract Node.js dependencies"""
        deps = []
        
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                package_data = json.loads(package_json.read_text())
                
                # Regular dependencies
                for dep_name, version in package_data.get('dependencies', {}).items():
                    deps.append(Dependency(
                        name=dep_name,
                        version=version,
                        file_path=str(package_json),
                        package_manager="npm",
                        dependency_type="direct",
                        transitive_deps=[]
                    ))
                
                # Dev dependencies
                for dep_name, version in package_data.get('devDependencies', {}).items():
                    deps.append(Dependency(
                        name=dep_name,
                        version=version,
                        file_path=str(package_json),
                        package_manager="npm",
                        dependency_type="dev",
                        transitive_deps=[]
                    ))
                
                # Peer dependencies
                for dep_name, version in package_data.get('peerDependencies', {}).items():
                    deps.append(Dependency(
                        name=dep_name,
                        version=version,
                        file_path=str(package_json),
                        package_manager="npm",
                        dependency_type="peer",
                        transitive_deps=[]
                    ))
            except Exception as e:
                logger.warning(f"Could not parse package.json: {e}")
        
        return deps

    def _extract_java_deps(self, project_path: Path) -> List[Dependency]:
        """Extract Java dependencies from pom.xml"""
        deps = []
        
        pom_xml = project_path / "pom.xml"
        if pom_xml.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(pom_xml)
                root = tree.getroot()
                
                ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                
                # Regular dependencies
                for dep in root.findall('.//maven:dependency', ns):
                    artifact_id = dep.findtext('maven:artifactId', namespaces=ns)
                    version = dep.findtext('maven:version', namespaces=ns)
                    group_id = dep.findtext('maven:groupId', namespaces=ns)
                    
                    if artifact_id and version:
                        deps.append(Dependency(
                            name=f"{group_id}:{artifact_id}",
                            version=version,
                            file_path=str(pom_xml),
                            package_manager="maven",
                            dependency_type="direct",
                            transitive_deps=[]
                        ))
            except Exception as e:
                logger.warning(f"Could not parse pom.xml: {e}")
        
        return deps

    def _extract_go_deps(self, project_path: Path) -> List[Dependency]:
        """Extract Go dependencies"""
        deps = []
        
        go_mod = project_path / "go.mod"
        if go_mod.exists():
            try:
                for line in go_mod.read_text().split('\n'):
                    if line.startswith('require'):
                        # Parse require directive
                        parts = line.split()
                        if len(parts) >= 3:
                            deps.append(Dependency(
                                name=parts[1],
                                version=parts[2],
                                file_path=str(go_mod),
                                package_manager="go",
                                dependency_type="direct",
                                transitive_deps=[]
                            ))
            except Exception as e:
                logger.warning(f"Could not parse go.mod: {e}")
        
        return deps

    def _extract_php_deps(self, project_path: Path) -> List[Dependency]:
        """Extract PHP dependencies"""
        deps = []
        
        composer_json = project_path / "composer.json"
        if composer_json.exists():
            try:
                composer_data = json.loads(composer_json.read_text())
                
                for dep_name, version in composer_data.get('require', {}).items():
                    deps.append(Dependency(
                        name=dep_name,
                        version=version,
                        file_path=str(composer_json),
                        package_manager="composer",
                        dependency_type="direct",
                        transitive_deps=[]
                    ))
                
                for dep_name, version in composer_data.get('require-dev', {}).items():
                    deps.append(Dependency(
                        name=dep_name,
                        version=version,
                        file_path=str(composer_json),
                        package_manager="composer",
                        dependency_type="dev",
                        transitive_deps=[]
                    ))
            except Exception as e:
                logger.warning(f"Could not parse composer.json: {e}")
        
        return deps

    def generate_documentignore(self, project_path: str, output_path: str = ".documentignore") -> str:
        """Generate optimized .documentignore file"""
        
        if not self.detected_stack:
            self.analyze_project(project_path)
        
        if not self.dependencies_found:
            self.extract_dependencies(project_path)
        
        logger.info("🔧 Generating .documentignore...")
        
        # Get dependency folder names
        dep_folders = self._get_dependency_folders(self.dependencies_found)
        
        # Build ignore patterns
        ignore_patterns = self._build_ignore_patterns(
            self.detected_stack,
            dep_folders,
            project_path
        )
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write("# Generated by Advanced Tech Analyzer v2.0\n")
            f.write(f"# Tech Stack: {', '.join(self.detected_stack.languages)}\n")
            f.write(f"# Databases: {', '.join(self.detected_stack.databases)}\n")
            f.write(f"# Confidence: {self.detected_stack.confidence:.2%}\n\n")
            
            for category, patterns in ignore_patterns.items():
                if patterns:
                    f.write(f"# {category}\n")
                    for pattern in patterns:
                        f.write(f"{pattern}\n")
                    f.write("\n")
        
        logger.info(f"✅ Generated {output_path}")
        return output_path

    def _get_dependency_folders(self, dependencies: List[Dependency]) -> Set[str]:
        """Extract folder names likely containing dependencies"""
        folders = set()
        
        # Common dependency folders
        dep_folders = {
            'node_modules', 'venv', '.venv', 'env', '.env',
            'vendor', 'target', 'build', 'dist', '.gradle',
            'eggs', '__pycache__', '.pytest_cache', '.mypy_cache',
            'site-packages', '.tox', '.vscode', '.idea'
        }
        
        folders.update(dep_folders)
        
        # Add specific dependency names
        for dep in dependencies:
            # Add package manager specific patterns
            if dep.package_manager == 'npm':
                folders.add('node_modules')
            elif dep.package_manager == 'pip':
                folders.add('venv')
                folders.add('__pycache__')
            elif dep.package_manager == 'maven':
                folders.add('target')
            elif dep.package_manager == 'gradle':
                folders.add('build')
        
        return folders

    def _build_ignore_patterns(self, tech_stack: TechStack, dep_folders: Set[str],
                               project_path: str) -> Dict[str, List[str]]:
        """Build comprehensive ignore patterns"""
        
        patterns = {
            "Dependency Folders": [
                f"**/{folder}/",
                f"./{folder}/",
            ],
            "Build Artifacts": [
                "**/*.o",
                "**/*.so",
                "**/*.a",
                "**/*.pyc",
                "**/__pycache__/",
                "**/.pytest_cache/",
                "**/build/",
                "**/dist/",
                "**/.gradle/",
            ],
            "IDE & Editors": [
                "**/.vscode/",
                "**/.idea/",
                "**/*.swp",
                "**/*.swo",
                "**/.DS_Store",
                "**/Thumbs.db",
            ],
            "Version Control": [
                "**/.git/",
                "**/.gitignore",
                "**/.hg/",
                "**/.svn/",
            ],
            "Package Manager Locks": [
                "**/package-lock.json",
                "**/yarn.lock",
                "**/pnpm-lock.yaml",
                "**/Gemfile.lock",
                "**/Pipfile.lock",
            ],
            "Testing Artifacts": [
                "**/.coverage",
                "**/.nyc_output/",
                "**/coverage/",
                "**/test-results/",
                "**/junit/",
            ],
            "Log Files": [
                "**/*.log",
                "**/*_log/",
                "**/logs/",
            ],
            "Temporary Files": [
                "**/*.tmp",
                "**/*.temp",
                "**/*.bak",
                "**/*.swp",
                "**/._*",
            ],
            "OS-Specific": [
                "**/.DS_Store",
                "**/Thumbs.db",
                "**/.windows",
            ]
        }
        
        # Add language-specific patterns
        for lang in tech_stack.languages:
            if lang == "python":
                patterns["Python Specific"] = [
                    "**/*.pyc",
                    "**/__pycache__/",
                    "**/.mypy_cache/",
                    "**/.pyre/",
                    "**/*.egg-info/",
                    "**/dist/",
                    "**/build/",
                ]
            elif lang == "nodejs":
                patterns["Node.js Specific"] = [
                    "**/node_modules/",
                    "**/.npm/",
                    "**/npm-debug.log",
                    "**/yarn-error.log",
                ]
            elif lang == "java":
                patterns["Java Specific"] = [
                    "**/target/",
                    "**/*.class",
                    "**/*.jar",
                    "**/out/",
                ]
        
        # Add dependency-specific folders
        dep_patterns = [f"**/{folder}/" for folder in sorted(dep_folders)]
        patterns["Dependency Folders"] = dep_patterns
        
        return patterns

    def get_stack_summary(self) -> str:
        """Get human-readable stack summary"""
        if not self.detected_stack:
            return "No analysis performed yet"
        
        stack = self.detected_stack
        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║                    TECHNOLOGY STACK SUMMARY                    ║
╚════════════════════════════════════════════════════════════════╝

📱 LANGUAGES:
  {', '.join(stack.languages) if stack.languages else 'None detected'}

🔧 FRAMEWORKS:
  {', '.join(stack.frameworks) if stack.frameworks else 'None detected'}

📦 PACKAGE MANAGERS:
  {', '.join(stack.package_managers) if stack.package_managers else 'None detected'}

💾 DATABASES:
  {', '.join(stack.databases) if stack.databases else 'None detected'}

☁️  CLOUD PLATFORMS:
  {', '.join(stack.cloud_platforms) if stack.cloud_platforms else 'None detected'}

🔨 BUILD TOOLS:
  {', '.join(stack.build_tools) if stack.build_tools else 'None detected'}

✅ TESTING FRAMEWORKS:
  {', '.join(stack.testing_frameworks) if stack.testing_frameworks else 'None detected'}

🔄 CI/CD TOOLS:
  {', '.join(stack.ci_cd_tools) if stack.ci_cd_tools else 'None detected'}

🛠️  OTHER TOOLS:
  {', '.join(stack.other_tools) if stack.other_tools else 'None detected'}

📊 CONFIDENCE: {stack.confidence:.0%}

📝 REASONING:
  {stack.reasoning}
"""
        return summary


def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tech_analyzer_v2.py <project_path> [--generate-ignore]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    generate_ignore = "--generate-ignore" in sys.argv
    
    analyzer = AdvancedTechAnalyzer()
    
    # Analyze project
    tech_stack = analyzer.analyze_project(project_path)
    print(analyzer.get_stack_summary())
    
    # Extract dependencies
    dependencies = analyzer.extract_dependencies(project_path)
    print(f"\n📦 Found {len(dependencies)} dependencies")
    
    # Generate .documentignore
    if generate_ignore:
        output_file = analyzer.generate_documentignore(project_path)
        print(f"✅ Generated: {output_file}")


if __name__ == "__main__":
    main()
