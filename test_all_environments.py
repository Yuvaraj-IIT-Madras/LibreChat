#!/usr/bin/env python3
"""
Integration test suite for RAG + Agentic Data Stack
Tests local, Codespaces, and Azure deployments
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnvironmentTester:
    """Test RAG system across environments"""
    
    def __init__(self, environment: str = "local"):
        self.environment = environment
        self.results = {
            'environment': environment,
            'timestamp': time.time(),
            'tests': [],
            'passed': 0,
            'failed': 0
        }
    
    def run_all_tests(self) -> Dict:
        """Run all integration tests"""
        print("\n" + "="*70)
        print(f"🧪 RAG Integration Tests - {self.environment.upper()}".center(70))
        print("="*70 + "\n")
        
        tests = [
            ("Connectivity Tests", self.test_connectivity),
            ("Database Tests", self.test_database),
            ("Service Health", self.test_service_health),
            ("RAG Pipeline", self.test_rag_pipeline),
            ("API Endpoints", self.test_api_endpoints),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"Running: {test_name}")
            try:
                result = test_func()
                if result:
                    logger.info(f"✅ {test_name} PASSED")
                    self.results['passed'] += 1
                else:
                    logger.error(f"❌ {test_name} FAILED")
                    self.results['failed'] += 1
                self.results['tests'].append({'name': test_name, 'passed': result})
            except Exception as e:
                logger.error(f"❌ {test_name} ERROR: {e}")
                self.results['failed'] += 1
                self.results['tests'].append({'name': test_name, 'passed': False, 'error': str(e)})
            print()
        
        return self.results
    
    def test_connectivity(self) -> bool:
        """Test basic connectivity"""
        logger.info("Testing network connectivity...")
        
        services = {
            'PostgreSQL': ('localhost', 5432),
            'Redis': ('localhost', 6379),
            'Meilisearch': ('localhost', 7700),
            'LibreChat': ('localhost', 3080),
        }
        
        if self.environment == "codespaces":
            # Use Codespaces endpoints
            services = {
                'PostgreSQL': ('postgres', 5432),
                'Redis': ('redis', 6379),
                'Meilisearch': ('meilisearch', 7700),
                'LibreChat': ('librechat', 3080),
            }
        
        all_reachable = True
        for service, (host, port) in services.items():
            try:
                cmd = f"nc -zv {host} {port} 2>&1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"  ✅ {service} ({host}:{port})")
                else:
                    logger.warning(f"  ⚠️  {service} ({host}:{port}) - Not responding")
                    all_reachable = False
            except Exception as e:
                logger.warning(f"  ⚠️  {service} - {str(e)}")
                all_reachable = False
        
        return all_reachable
    
    def test_database(self) -> bool:
        """Test database connectivity and tables"""
        logger.info("Testing database...")
        
        # Try connecting to PostgreSQL
        try:
            if self.environment == "local":
                cmd = "sudo -u postgres psql -d rag_demo -c 'SELECT COUNT(*) FROM documents;' -t"
            else:
                cmd = "psql -h postgres -U postgres -d rag_demo -c 'SELECT COUNT(*) FROM documents;' -t"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                count = result.stdout.strip()
                logger.info(f"  ✅ Database connected ({count} documents)")
                return True
            else:
                logger.warning(f"  ⚠️  Database query failed: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"  ⚠️  Database error: {e}")
            return False
    
    def test_service_health(self) -> bool:
        """Test service health endpoints"""
        logger.info("Testing service health...")
        
        endpoints = [
            ('http://localhost:3080/health', 'LibreChat'),
            ('http://localhost:8000/health', 'RAG API'),
            ('http://localhost:7700/health', 'Meilisearch'),
        ]
        
        if self.environment == "codespaces":
            endpoints = [
                ('http://librechat:3080/health', 'LibreChat'),
                ('http://rag-api:8000/health', 'RAG API'),
                ('http://meilisearch:7700/health', 'Meilisearch'),
            ]
        
        all_healthy = True
        for url, name in endpoints:
            try:
                cmd = f"curl -s -f {url} 2>&1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"  ✅ {name} is healthy")
                else:
                    logger.warning(f"  ⚠️  {name} not responding")
                    all_healthy = False
            except Exception as e:
                logger.warning(f"  ⚠️  {name} error: {e}")
                all_healthy = False
        
        return all_healthy
    
    def test_rag_pipeline(self) -> bool:
        """Test RAG pipeline functionality"""
        logger.info("Testing RAG pipeline...")
        
        try:
            # Run RAG pipeline script
            result = subprocess.run(
                ['python3', 'rag_pipeline.py'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/home/yuvaraj/Projects/Claude Code VS Code Extension/claude-skill-demo-project/hello-world'
            )
            
            if result.returncode == 0 and 'COMPLETE' in result.stdout:
                logger.info("  ✅ RAG pipeline executed successfully")
                return True
            else:
                logger.warning(f"  ⚠️  RAG pipeline error: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"  ⚠️  RAG pipeline test failed: {e}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints"""
        logger.info("Testing API endpoints...")
        
        endpoints = [
            ('GET', 'http://localhost:8000/', 'Root'),
            ('GET', 'http://localhost:8000/docs', 'API Docs'),
            ('GET', 'http://localhost:8000/health', 'Health Check'),
        ]
        
        all_working = True
        for method, url, name in endpoints:
            try:
                cmd = f"curl -s -f -X {method} {url} 2>&1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"  ✅ {name} endpoint working")
                else:
                    logger.warning(f"  ⚠️  {name} endpoint not responding")
                    all_working = False
            except Exception as e:
                logger.warning(f"  ⚠️  {name} error: {e}")
                all_working = False
        
        return all_working
    
    def generate_report(self, output_file: str = "test_results.json") -> None:
        """Generate test report"""
        logger.info(f"Generating report: {output_file}")
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info("✅ Report saved")


def main():
    """Main test runner"""
    # Detect environment
    environment = "local"
    if "CODESPACES" in Path("/proc/environ").read_text() if Path("/proc/environ").exists() else "":
        environment = "codespaces"
    elif "AZURE" in sys.argv:
        environment = "azure"
    
    # Allow override
    if len(sys.argv) > 1:
        environment = sys.argv[1].lower()
    
    logger.info(f"Detected environment: {environment}")
    
    # Run tests
    tester = EnvironmentTester(environment)
    results = tester.run_all_tests()
    
    # Print summary
    print("="*70)
    print("TEST SUMMARY".center(70))
    print("="*70)
    print(f"Environment: {environment}")
    print(f"Total Tests: {len(results['tests'])}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['failed'] == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {results['failed']} tests failed")
    print("="*70 + "\n")
    
    # Generate report
    tester.generate_report(f"test_results_{environment}.json")
    
    # Exit code
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
