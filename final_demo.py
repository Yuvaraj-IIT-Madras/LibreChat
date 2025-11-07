#!/usr/bin/env python3
"""
🚀 QUICK DEMO: Universal Database Adapter System in LibreChat

Tests all 6 pre-tested database adapters with proper configuration.
Each adapter is instantiated and tested for basic functionality.

Run: python3 final_demo.py
"""

import sys
import logging
from database_adapter_registry import DatabaseAdapterRegistry, DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def demo_adapter(db_type: str, default_port: int, docker_image: str):
    """Demo a single database adapter"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {db_type.upper()} Adapter")
    print(f"{'='*80}")
    
    try:
        # Create configuration with proper defaults
        config = DatabaseConfig(
            db_type=db_type,
            db_name="demo_db",
            host="localhost",
            port=default_port,
            username="user",
            password="password",
            image=docker_image
        )
        
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            print(f"❌ Validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        print(f"✅ Configuration valid")
        print(f"   Port: {config.port}")
        
        # Create registry and get adapter
        registry = DatabaseAdapterRegistry()
        adapter = registry.get_adapter(db_type, config)
        print(f"✅ Adapter created: {adapter.__class__.__name__}")
        
        # Get connection string
        conn_str = adapter.get_connection_string()
        print(f"📍 Connection: {conn_str[:65]}...")
        
        # Get Docker config
        docker = adapter.get_docker_config()
        print(f"🐳 Docker image: {docker.get('image', 'N/A')}")
        print(f"🔌 Docker ports: {docker.get('ports', [])}")
        
        # Check vector search support
        if adapter.supports_vector_search():
            print(f"✅ Vector search: SUPPORTED")
        else:
            print(f"⚠️  Vector search: NOT SUPPORTED")
        
        # Get health check
        health = adapter.get_health_check_command()
        print(f"🏥 Health check: {health[:60]}...")
        
        print(f"✅ {db_type.upper()}: ALL CHECKS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ {db_type.upper()}: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run demo for all 6 pre-tested adapters"""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "🚀 UNIVERSAL DATABASE ADAPTER SYSTEM - QUICK DEMO".center(78) + "║")
    print("║" + "LibreChat Integration".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # Define adapters with their default ports and images
    adapters = [
        ("postgresql", 5432, "pgvector/pgvector:pg16"),
        ("mongodb", 27017, "mongo:7.0"),
        ("mysql", 3306, "mysql:8.0"),
        ("clickhouse", 8123, "clickhouse/clickhouse-server:latest"),
        ("redis", 6379, "redis:7.2-alpine"),
        ("elasticsearch", 9200, "docker.elastic.co/elasticsearch/elasticsearch:8.0.0"),
    ]
    
    results = {}
    
    # Run demo for each adapter
    for db_type, port, image in adapters:
        passed = demo_adapter(db_type, port, image)
        results[db_type] = "✅ PASS" if passed else "❌ FAIL"
    
    # Print summary
    print(f"\n\n{'='*80}")
    print(f"📊 DEMO SUMMARY - All 6 Pre-Tested Adapters")
    print(f"{'='*80}\n")
    
    passed_count = sum(1 for status in results.values() if "PASS" in status)
    total_count = len(results)
    
    for db_type, status in results.items():
        print(f"  {db_type.upper():20} {status}")
    
    print(f"\n{'─'*80}")
    print(f"  Total Passed: {passed_count}/{total_count} ({100*passed_count//total_count}%)")
    print(f"{'─'*80}\n")
    
    if passed_count == total_count:
        print("🎉 ALL ADAPTERS PASSED! System ready for integration with LibreChat.\n")
        return 0
    else:
        print(f"⚠️  {total_count - passed_count} adapter(s) failed. Review errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
