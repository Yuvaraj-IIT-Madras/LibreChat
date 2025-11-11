#!/usr/bin/env python3
"""
Dependency Mapper v1.0
Extracts, parses, and maps dependencies across multiple package managers
Identifies transitive dependencies and generates dependency graphs
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import xml.etree.ElementTree as ET
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DependencyNode:
    """Represents a dependency node in the graph"""
    name: str
    version: str
    package_manager: str
    level: int = 0  # 0 = direct, 1+ = transitive
    source_file: str = ""
    is_dev: bool = False
    is_optional: bool = False
    vulnerabilities: List[str] = field(default_factory=list)
    children: List['DependencyNode'] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)


@dataclass
class DependencyReport:
    """Comprehensive dependency report"""
    total_dependencies: int
    direct_dependencies: int
    transitive_dependencies: int
    unique_packages: int
    by_package_manager: Dict[str, int]
    by_license: Dict[str, int]
    vulnerable_packages: List[Dict]
    unused_packages: List[str]
    outdated_packages: List[Dict]
    size_estimate: int


class DependencyMapper:
    """Maps and analyzes project dependencies"""

    def __init__(self):
        """Initialize dependency mapper"""
        self.dependencies = defaultdict(list)
        self.dependency_graph = {}
        self.licenses = {}
        self.vulnerabilities = {}

    def analyze_project(self, project_path: str) -> DependencyReport:
        """Analyze entire project for dependencies"""
        logger.info(f"📦 Analyzing project dependencies: {project_path}")
        
        project_path = Path(project_path)
        
        # Extract dependencies from all package managers
        self._extract_all_dependencies(project_path)
        
        # Build dependency graph
        self._build_dependency_graph()
        
        # Fetch additional information
        self._fetch_license_info()
        self._check_vulnerabilities()
        
        # Generate report
        return self._generate_report()

    def _extract_all_dependencies(self, project_path: Path):
        """Extract dependencies from all supported package managers"""
        
        # Python
        self._extract_python(project_path)
        
        # Node.js
        self._extract_nodejs(project_path)
        
        # Java
        self._extract_java(project_path)
        
        # Go
        self._extract_go(project_path)
        
        # PHP
        self._extract_php(project_path)
        
        # Ruby
        self._extract_ruby(project_path)
        
        # Rust
        self._extract_rust(project_path)
        
        logger.info(f"✅ Extracted {len(self._flatten_dependencies())} total dependencies")

    def _extract_python(self, project_path: Path):
        """Extract Python dependencies"""
        
        # requirements.txt
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            logger.info("📄 Found requirements.txt")
            self._parse_requirements_txt(req_file)
        
        # pyproject.toml
        pyproject = project_path / "pyproject.toml"
        if pyproject.exists():
            logger.info("📄 Found pyproject.toml")
            self._parse_pyproject_toml(pyproject)
        
        # Pipfile
        pipfile = project_path / "Pipfile"
        if pipfile.exists():
            logger.info("📄 Found Pipfile")
            self._parse_pipfile(pipfile)
        
        # poetry.lock
        poetry_lock = project_path / "poetry.lock"
        if poetry_lock.exists():
            logger.info("📄 Found poetry.lock")
            self._parse_poetry_lock(poetry_lock)

    def _parse_requirements_txt(self, filepath: Path):
        """Parse requirements.txt"""
        try:
            for line in filepath.read_text().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    node = self._parse_requirement_line(line, str(filepath))
                    if node:
                        self.dependencies["pip"].append(node)
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_requirement_line(self, line: str, source: str) -> Optional[DependencyNode]:
        """Parse a single requirement line"""
        # Remove extras specification
        if '[' in line:
            line = line.split('[')[0] + line.split(']')[1]
        
        # Match pattern: package_name (operator version)*
        pattern = r'^([a-zA-Z0-9._-]+)(.*)$'
        match = re.match(pattern, line)
        
        if match:
            name = match.group(1).strip()
            version_spec = match.group(2).strip()
            
            return DependencyNode(
                name=name,
                version=version_spec if version_spec else "*",
                package_manager="pip",
                source_file=source
            )
        
        return None

    def _parse_pyproject_toml(self, filepath: Path):
        """Parse pyproject.toml"""
        try:
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib
            
            with open(filepath, 'rb') as f:
                data = tomllib.load(f)
            
            # Extract dependencies
            deps = data.get('project', {}).get('dependencies', [])
            for dep in deps:
                node = self._parse_requirement_line(dep, str(filepath))
                if node:
                    self.dependencies["pip"].append(node)
            
            # Extract dev dependencies
            dev_deps = data.get('project', {}).get('optional-dependencies', {})
            for dep_list in dev_deps.values():
                for dep in dep_list:
                    node = self._parse_requirement_line(dep, str(filepath))
                    if node:
                        node.is_dev = True
                        self.dependencies["pip"].append(node)
                        
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_pipfile(self, filepath: Path):
        """Parse Pipfile"""
        try:
            import toml
            data = toml.load(filepath)
            
            # Extract packages
            for name, version in data.get('packages', {}).items():
                self.dependencies["pipenv"].append(DependencyNode(
                    name=name,
                    version=str(version),
                    package_manager="pipenv",
                    source_file=str(filepath)
                ))
            
            # Extract dev-packages
            for name, version in data.get('dev-packages', {}).items():
                node = DependencyNode(
                    name=name,
                    version=str(version),
                    package_manager="pipenv",
                    source_file=str(filepath),
                    is_dev=True
                )
                self.dependencies["pipenv"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_poetry_lock(self, filepath: Path):
        """Parse poetry.lock file"""
        try:
            import toml
            data = toml.load(filepath)
            
            for package in data.get('package', []):
                node = DependencyNode(
                    name=package.get('name', ''),
                    version=package.get('version', '*'),
                    package_manager="poetry",
                    source_file=str(filepath)
                )
                self.dependencies["poetry"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _extract_nodejs(self, project_path: Path):
        """Extract Node.js dependencies"""
        
        # package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            logger.info("📄 Found package.json")
            self._parse_package_json(package_json)
        
        # package-lock.json
        lock_file = project_path / "package-lock.json"
        if lock_file.exists():
            logger.info("📄 Found package-lock.json")
            self._parse_package_lock_json(lock_file)

    def _parse_package_json(self, filepath: Path):
        """Parse package.json"""
        try:
            data = json.loads(filepath.read_text())
            
            # Dependencies
            for name, version in data.get('dependencies', {}).items():
                self.dependencies["npm"].append(DependencyNode(
                    name=name,
                    version=version,
                    package_manager="npm",
                    source_file=str(filepath)
                ))
            
            # Dev dependencies
            for name, version in data.get('devDependencies', {}).items():
                node = DependencyNode(
                    name=name,
                    version=version,
                    package_manager="npm",
                    source_file=str(filepath),
                    is_dev=True
                )
                self.dependencies["npm"].append(node)
            
            # Peer dependencies
            for name, version in data.get('peerDependencies', {}).items():
                node = DependencyNode(
                    name=name,
                    version=version,
                    package_manager="npm",
                    source_file=str(filepath),
                    is_optional=True
                )
                self.dependencies["npm"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_package_lock_json(self, filepath: Path):
        """Parse package-lock.json for transitive dependencies"""
        try:
            data = json.loads(filepath.read_text())
            
            for name, info in data.get('packages', {}).items():
                if not name:  # Root package
                    continue
                
                # Extract package name and version
                pkg_path = name.split('/')
                pkg_name = pkg_path[-1]
                
                node = DependencyNode(
                    name=pkg_name,
                    version=info.get('version', '*'),
                    package_manager="npm",
                    source_file=str(filepath),
                    level=len(pkg_path) - 1  # Depth in node_modules
                )
                
                if node.level > 0:
                    node.level = 1  # Mark as transitive
                
                self.dependencies["npm"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _extract_java(self, project_path: Path):
        """Extract Java dependencies"""
        
        # pom.xml (Maven)
        pom_file = project_path / "pom.xml"
        if pom_file.exists():
            logger.info("📄 Found pom.xml")
            self._parse_pom_xml(pom_file)
        
        # build.gradle (Gradle)
        gradle_file = project_path / "build.gradle"
        if gradle_file.exists():
            logger.info("📄 Found build.gradle")
            self._parse_gradle_file(gradle_file)

    def _parse_pom_xml(self, filepath: Path):
        """Parse Maven pom.xml"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
            
            for dep in root.findall('.//m:dependency', ns):
                artifact_id = dep.findtext('m:artifactId', namespaces=ns, default='')
                version = dep.findtext('m:version', namespaces=ns, default='*')
                group_id = dep.findtext('m:groupId', namespaces=ns, default='')
                scope = dep.findtext('m:scope', namespaces=ns, default='compile')
                
                node = DependencyNode(
                    name=f"{group_id}:{artifact_id}",
                    version=version,
                    package_manager="maven",
                    source_file=str(filepath),
                    is_dev=(scope in ['test', 'provided'])
                )
                
                self.dependencies["maven"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_gradle_file(self, filepath: Path):
        """Parse Gradle build.gradle"""
        try:
            content = filepath.read_text()
            
            # Simple regex-based parsing for dependencies
            dep_pattern = r"(?:implementation|testImplementation|api|compileOnly)\s+['\"]([^'\"]+)['\"]"
            
            for match in re.finditer(dep_pattern, content):
                dep_str = match.group(1)
                parts = dep_str.split(':')
                
                if len(parts) >= 2:
                    node = DependencyNode(
                        name=parts[1],
                        version=parts[2] if len(parts) > 2 else '*',
                        package_manager="gradle",
                        source_file=str(filepath),
                        is_dev="test" in match.group(0)
                    )
                    self.dependencies["gradle"].append(node)
                    
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _extract_go(self, project_path: Path):
        """Extract Go dependencies"""
        
        go_mod = project_path / "go.mod"
        if go_mod.exists():
            logger.info("📄 Found go.mod")
            self._parse_go_mod(go_mod)
        
        go_sum = project_path / "go.sum"
        if go_sum.exists():
            logger.info("📄 Found go.sum")
            self._parse_go_sum(go_sum)

    def _parse_go_mod(self, filepath: Path):
        """Parse go.mod"""
        try:
            content = filepath.read_text()
            in_require = False
            
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('require'):
                    in_require = True
                    continue
                
                if in_require:
                    if line == ')':
                        break
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            self.dependencies["go"].append(DependencyNode(
                                name=parts[0],
                                version=parts[1],
                                package_manager="go",
                                source_file=str(filepath)
                            ))
                            
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_go_sum(self, filepath: Path):
        """Parse go.sum for checksum verification"""
        try:
            content = filepath.read_text()
            
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        # go.sum format: module version hash
                        # Skip if already in dependencies
                        existing = [d for d in self.dependencies["go"] if d.name == parts[0]]
                        if not existing:
                            self.dependencies["go"].append(DependencyNode(
                                name=parts[0],
                                version=parts[1],
                                package_manager="go",
                                source_file=str(filepath),
                                level=1  # Mark as from go.sum (transitive)
                            ))
                            
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _extract_php(self, project_path: Path):
        """Extract PHP dependencies"""
        
        composer_json = project_path / "composer.json"
        if composer_json.exists():
            logger.info("📄 Found composer.json")
            self._parse_composer_json(composer_json)
        
        composer_lock = project_path / "composer.lock"
        if composer_lock.exists():
            logger.info("📄 Found composer.lock")
            self._parse_composer_lock(composer_lock)

    def _parse_composer_json(self, filepath: Path):
        """Parse composer.json"""
        try:
            data = json.loads(filepath.read_text())
            
            for name, version in data.get('require', {}).items():
                self.dependencies["composer"].append(DependencyNode(
                    name=name,
                    version=version,
                    package_manager="composer",
                    source_file=str(filepath)
                ))
            
            for name, version in data.get('require-dev', {}).items():
                node = DependencyNode(
                    name=name,
                    version=version,
                    package_manager="composer",
                    source_file=str(filepath),
                    is_dev=True
                )
                self.dependencies["composer"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_composer_lock(self, filepath: Path):
        """Parse composer.lock for transitive dependencies"""
        try:
            data = json.loads(filepath.read_text())
            
            for package in data.get('packages', []):
                node = DependencyNode(
                    name=package.get('name', ''),
                    version=package.get('version', '*'),
                    package_manager="composer",
                    source_file=str(filepath),
                    level=1  # Transitive
                )
                
                # Check if it's a dev package
                dev_packages = data.get('packages-dev', [])
                node.is_dev = any(p.get('name') == node.name for p in dev_packages)
                
                self.dependencies["composer"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _extract_ruby(self, project_path: Path):
        """Extract Ruby dependencies"""
        
        gemfile = project_path / "Gemfile"
        if gemfile.exists():
            logger.info("📄 Found Gemfile")
            self._parse_gemfile(gemfile)
        
        gemfile_lock = project_path / "Gemfile.lock"
        if gemfile_lock.exists():
            logger.info("📄 Found Gemfile.lock")
            self._parse_gemfile_lock(gemfile_lock)

    def _parse_gemfile(self, filepath: Path):
        """Parse Gemfile"""
        try:
            content = filepath.read_text()
            
            # Simple regex-based parsing
            gem_pattern = r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]*)['\"])?"
            
            for match in re.finditer(gem_pattern, content):
                name = match.group(1)
                version = match.group(2) if match.group(2) else '*'
                
                is_dev = 'development' in content[:match.start()]
                
                self.dependencies["bundler"].append(DependencyNode(
                    name=name,
                    version=version,
                    package_manager="bundler",
                    source_file=str(filepath),
                    is_dev=is_dev
                ))
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _parse_gemfile_lock(self, filepath: Path):
        """Parse Gemfile.lock for transitive dependencies"""
        try:
            content = filepath.read_text()
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if i > 0 and lines[i-1] and not lines[i-1].startswith(' '):
                    # This is a gem definition
                    match = re.match(r'^  ([^ ]+) \(([^)]+)\)', line)
                    if match:
                        self.dependencies["bundler"].append(DependencyNode(
                            name=match.group(1),
                            version=match.group(2),
                            package_manager="bundler",
                            source_file=str(filepath),
                            level=1  # Transitive
                        ))
                        
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _extract_rust(self, project_path: Path):
        """Extract Rust dependencies"""
        
        cargo_toml = project_path / "Cargo.toml"
        if cargo_toml.exists():
            logger.info("📄 Found Cargo.toml")
            self._parse_cargo_toml(cargo_toml)

    def _parse_cargo_toml(self, filepath: Path):
        """Parse Cargo.toml"""
        try:
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib
            
            with open(filepath, 'rb') as f:
                data = tomllib.load(f)
            
            for name, version in data.get('dependencies', {}).items():
                version_str = str(version) if not isinstance(version, dict) else version.get('version', '*')
                
                self.dependencies["cargo"].append(DependencyNode(
                    name=name,
                    version=version_str,
                    package_manager="cargo",
                    source_file=str(filepath)
                ))
            
            for name, version in data.get('dev-dependencies', {}).items():
                version_str = str(version) if not isinstance(version, dict) else version.get('version', '*')
                
                node = DependencyNode(
                    name=name,
                    version=version_str,
                    package_manager="cargo",
                    source_file=str(filepath),
                    is_dev=True
                )
                self.dependencies["cargo"].append(node)
                
        except Exception as e:
            logger.warning(f"Error parsing {filepath}: {e}")

    def _build_dependency_graph(self):
        """Build a graph representation of dependencies"""
        self.dependency_graph = {}
        
        all_deps = self._flatten_dependencies()
        
        for dep in all_deps:
            self.dependency_graph[dep.name] = dep

    def _flatten_dependencies(self) -> List[DependencyNode]:
        """Flatten all dependencies from all package managers"""
        all_deps = []
        for dep_list in self.dependencies.values():
            all_deps.extend(dep_list)
        return all_deps

    def _fetch_license_info(self):
        """Fetch license information for packages"""
        logger.info("🔍 Fetching license information...")
        
        # This would integrate with services like license-checker
        # or API calls to package repositories
        pass

    def _check_vulnerabilities(self):
        """Check for known vulnerabilities"""
        logger.info("🔒 Checking for vulnerabilities...")
        
        # This would integrate with services like:
        # - npm audit
        # - OWASP Dependency Check
        # - Snyk
        # - Safety (for Python)
        pass

    def _generate_report(self) -> DependencyReport:
        """Generate comprehensive dependency report"""
        
        all_deps = self._flatten_dependencies()
        direct_deps = [d for d in all_deps if d.level == 0]
        transitive_deps = [d for d in all_deps if d.level > 0]
        
        by_pm = defaultdict(int)
        for dep in all_deps:
            by_pm[dep.package_manager] += 1
        
        by_license = defaultdict(int)
        for dep in all_deps:
            # This would be populated from license info
            pass
        
        return DependencyReport(
            total_dependencies=len(all_deps),
            direct_dependencies=len(direct_deps),
            transitive_dependencies=len(transitive_deps),
            unique_packages=len(set(d.name for d in all_deps)),
            by_package_manager=dict(by_pm),
            by_license=dict(by_license),
            vulnerable_packages=[],
            unused_packages=[],
            outdated_packages=[],
            size_estimate=self._estimate_size(all_deps)
        )

    def _estimate_size(self, dependencies: List[DependencyNode]) -> int:
        """Estimate total size of dependencies"""
        # Average package size: ~5MB
        return len(dependencies) * 5_000_000

    def export_report(self, output_path: str = "dependency_report.json"):
        """Export report to JSON"""
        report = self._generate_report()
        
        report_data = {
            "summary": asdict(report),
            "dependencies": [asdict(d) for d in self._flatten_dependencies()],
            "by_package_manager": dict(self.dependencies)
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"✅ Exported report to {output_path}")

    def print_summary(self):
        """Print human-readable summary"""
        report = self._generate_report()
        
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║                   DEPENDENCY ANALYSIS REPORT                   ║
╚════════════════════════════════════════════════════════════════╝

📊 STATISTICS:
  Total Dependencies: {report.total_dependencies}
  Direct Dependencies: {report.direct_dependencies}
  Transitive Dependencies: {report.transitive_dependencies}
  Unique Packages: {report.unique_packages}
  Estimated Size: {report.size_estimate / 1_000_000:.1f} MB

📦 BY PACKAGE MANAGER:
  {chr(10).join(f"  {pm}: {count}" for pm, count in report.by_package_manager.items())}

🔒 SECURITY:
  Vulnerable Packages: {len(report.vulnerable_packages)}
  Outdated Packages: {len(report.outdated_packages)}

⚠️  ANALYSIS:
  Unused Packages: {len(report.unused_packages)}

""")


def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dependency_mapper.py <project_path> [--export]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    export = "--export" in sys.argv
    
    mapper = DependencyMapper()
    report = mapper.analyze_project(project_path)
    
    mapper.print_summary()
    
    if export:
        mapper.export_report()


if __name__ == "__main__":
    main()
