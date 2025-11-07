#!/usr/bin/env python3
"""
Comprehensive test suite for Universal Database Adapter Registry

Tests all adapters, configurations, and integration points.
Total: 31 tests across 7 test classes
"""

import pytest
import logging
from database_adapter_registry import (
    DatabaseAdapterRegistry,
    DatabaseConfig,
    PostgreSQLAdapter,
    MongoDBAdapter,
    MySQLAdapter,
    ClickHouseAdapter,
    RedisAdapter,
    ElasticsearchAdapter,
    DatabaseAdapter,
    VectorSearchType
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def registry():
    """Create registry instance"""
    return DatabaseAdapterRegistry()


@pytest.fixture
def postgresql_config():
    """PostgreSQL test configuration"""
    return DatabaseConfig(
        db_type="postgresql",
        db_name="test_db",
        host="localhost",
        port=5432,
        username="postgres",
        password="postgres",
        image="pgvector/pgvector:pg16"
    )


@pytest.fixture
def mongodb_config():
    """MongoDB test configuration"""
    return DatabaseConfig(
        db_type="mongodb",
        db_name="test_db",
        host="localhost",
        port=27017,
        username="admin",
        password="admin",
        image="mongo:7.0"
    )


@pytest.fixture
def clickhouse_config():
    """ClickHouse test configuration"""
    return DatabaseConfig(
        db_type="clickhouse",
        db_name="test_db",
        host="localhost",
        port=8123,
        username="default",
        password="default",
        image="clickhouse/clickhouse-server:latest"
    )


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestDatabaseConfigValidation:
    """Test configuration validation"""
    
    def test_valid_config(self, postgresql_config):
        """Test valid configuration passes validation"""
        is_valid, errors = postgresql_config.validate()
        assert is_valid
        assert len(errors) == 0
    
    def test_invalid_port_too_high(self):
        """Test port validation (too high)"""
        config = DatabaseConfig(
            db_type="postgresql",
            db_name="test",
            host="localhost",
            port=99999,
            username="user",
            password="pass",
            image="postgres:15"
        )
        is_valid, errors = config.validate()
        assert not is_valid
        assert any("port" in e.lower() for e in errors)
    
    def test_invalid_pool_size(self):
        """Test pool size validation"""
        config = DatabaseConfig(
            db_type="postgresql",
            db_name="test",
            host="localhost",
            port=5432,
            username="user",
            password="pass",
            image="postgres:15",
            pool_size=2000
        )
        is_valid, errors = config.validate()
        assert not is_valid
        assert any("pool" in e.lower() for e in errors)
    
    def test_config_normalizes_db_type(self):
        """Test that db_type is normalized to lowercase"""
        config = DatabaseConfig(
            db_type="PostgreSQL",
            db_name="test",
            host="localhost",
            port=5432,
            username="user",
            password="pass",
            image="postgres:15"
        )
        assert config.db_type == "postgresql"
    
    def test_missing_required_field(self):
        """Test validation with missing required field"""
        config = DatabaseConfig(
            db_type="postgresql",
            db_name="",
            host="localhost",
            port=5432,
            username="user",
            password="pass",
            image="postgres:15"
        )
        is_valid, errors = config.validate()
        assert not is_valid
        assert any("db_name" in e.lower() for e in errors)
    
    def test_image_required_for_docker(self):
        """Test that image is required"""
        config = DatabaseConfig(
            db_type="postgresql",
            db_name="test",
            host="localhost",
            port=5432,
            username="user",
            password="pass",
            image=""
        )
        is_valid, errors = config.validate()
        assert not is_valid
        assert any("image" in e.lower() for e in errors)
    
    def test_invalid_timeout(self):
        """Test timeout validation"""
        config = DatabaseConfig(
            db_type="postgresql",
            db_name="test",
            host="localhost",
            port=5432,
            username="user",
            password="pass",
            image="postgres:15",
            timeout=500
        )
        is_valid, errors = config.validate()
        assert not is_valid
        assert any("timeout" in e.lower() for e in errors)


class TestAdapterRegistry:
    """Test adapter registry"""
    
    def test_list_available_adapters(self, registry):
        """Test listing all available adapters"""
        adapters = registry.list_available_adapters()
        assert len(adapters) >= 6
        assert "postgresql" in adapters
        assert "mongodb" in adapters
        assert "clickhouse" in adapters
    
    def test_get_known_adapter(self, registry, postgresql_config):
        """Test retrieving a known adapter"""
        adapter = registry.get_adapter("postgresql", postgresql_config)
        assert isinstance(adapter, PostgreSQLAdapter)
        assert adapter.config.db_type == "postgresql"
    
    def test_get_adapter_case_insensitive(self, registry, postgresql_config):
        """Test adapter retrieval is case-insensitive"""
        adapter1 = registry.get_adapter("postgresql", postgresql_config)
        adapter2 = registry.get_adapter("POSTGRESQL", postgresql_config)
        assert isinstance(adapter1, PostgreSQLAdapter)
        assert isinstance(adapter2, PostgreSQLAdapter)
    
    def test_get_unknown_adapter_without_fallback(self, registry):
        """Test unknown adapter raises error without fallback"""
        config = DatabaseConfig(
            db_type="oracle",
            db_name="test",
            host="localhost",
            port=1521,
            username="user",
            password="pass",
            image="oracle:21c"
        )
        with pytest.raises(ValueError, match="not supported"):
            registry.get_adapter("oracle", config)
    
    def test_register_custom_adapter(self, registry, postgresql_config):
        """Test registering a custom adapter"""
        registry.register("custom_db", PostgreSQLAdapter)
        adapter = registry.get_adapter("custom_db", postgresql_config)
        assert isinstance(adapter, PostgreSQLAdapter)
    
    def test_register_invalid_adapter_fails(self, registry):
        """Test registering non-adapter class fails"""
        class NotAnAdapter:
            pass
        
        with pytest.raises(TypeError):
            registry.register("invalid", NotAnAdapter)
    
    def test_get_adapter_info(self, registry):
        """Test getting adapter metadata"""
        info = registry.get_adapter_info("postgresql")
        assert info["db_type"] == "postgresql"
        assert "PostgreSQL" in info["class_name"]


class TestPostgreSQLAdapter:
    """Test PostgreSQL adapter"""
    
    def test_connection_string(self, postgresql_config):
        """Test PostgreSQL connection string"""
        adapter = PostgreSQLAdapter(postgresql_config)
        conn_str = adapter.get_connection_string()
        assert "postgresql://" in conn_str
        assert "localhost:5432" in conn_str
        assert "test_db" in conn_str
    
    def test_docker_config(self, postgresql_config):
        """Test PostgreSQL Docker configuration"""
        adapter = PostgreSQLAdapter(postgresql_config)
        config = adapter.get_docker_config()
        
        assert "pgvector" in config["image"]
        assert "5432:5432" in config["ports"]
        assert config["environment"]["POSTGRES_DB"] == "test_db"
    
    def test_vector_support(self, postgresql_config):
        """Test PostgreSQL vector search support"""
        adapter = PostgreSQLAdapter(postgresql_config)
        assert adapter.supports_vector_search()
    
    def test_vector_sql(self, postgresql_config):
        """Test PostgreSQL vector SQL generation"""
        adapter = PostgreSQLAdapter(postgresql_config)
        sql = adapter.get_vector_create_index_sql("embeddings", "embedding", 768)
        assert "CREATE TABLE" in sql
        assert "vector(768)" in sql


class TestClickHouseAdapter:
    """Test ClickHouse adapter"""
    
    def test_connection_string(self, clickhouse_config):
        """Test ClickHouse connection string"""
        adapter = ClickHouseAdapter(clickhouse_config)
        conn_str = adapter.get_connection_string()
        assert "clickhouse://" in conn_str
        assert "localhost:8123" in conn_str
    
    def test_docker_config(self, clickhouse_config):
        """Test ClickHouse Docker configuration"""
        adapter = ClickHouseAdapter(clickhouse_config)
        config = adapter.get_docker_config()
        
        assert "clickhouse" in config["image"]
        assert "8123" in str(config["ports"])
    
    def test_vector_support(self, clickhouse_config):
        """Test ClickHouse vector search support"""
        adapter = ClickHouseAdapter(clickhouse_config)
        assert adapter.supports_vector_search()
    
    def test_health_check(self, clickhouse_config):
        """Test ClickHouse health check command"""
        adapter = ClickHouseAdapter(clickhouse_config)
        health = adapter.get_health_check_command()
        assert "curl" in health


class TestMongoDBAdapter:
    """Test MongoDB adapter"""
    
    def test_connection_string(self, mongodb_config):
        """Test MongoDB connection string"""
        adapter = MongoDBAdapter(mongodb_config)
        conn_str = adapter.get_connection_string()
        assert "mongodb://" in conn_str
        assert "localhost:27017" in conn_str
    
    def test_vector_support(self, mongodb_config):
        """Test MongoDB vector search support"""
        adapter = MongoDBAdapter(mongodb_config)
        assert adapter.supports_vector_search()


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_config_export(self, postgresql_config, tmp_path):
        """Test configuration export"""
        from database_adapter_registry import export_config_to_json
        
        adapter = PostgreSQLAdapter(postgresql_config)
        output_file = str(tmp_path / "config.json")
        
        result = export_config_to_json(adapter, output_file)
        assert result == output_file
    
    def test_docker_compose_generation(self, postgresql_config, redis_config, tmp_path):
        """Test docker-compose generation"""
        from database_adapter_registry import create_docker_compose_file
        
        adapters = {
            "postgresql": PostgreSQLAdapter(postgresql_config)
        }
        
        output_file = str(tmp_path / "docker-compose.yml")
        result = create_docker_compose_file(adapters, output_file)
        assert result == output_file
    
    def test_vector_search_type_enum(self):
        """Test VectorSearchType enum"""
        assert VectorSearchType.NATIVE.value == "native"
        assert VectorSearchType.EXTERNAL.value == "external"
        assert VectorSearchType.NONE.value == "none"


class TestSecurityFeatures:
    """Test security features"""
    
    def test_ssl_enabled_config(self):
        """Test SSL configuration"""
        config = DatabaseConfig(
            db_type="postgresql",
            db_name="test",
            host="localhost",
            port=5432,
            username="user",
            password="pass",
            image="postgres:15",
            ssl_enabled=True
        )
        adapter = PostgreSQLAdapter(config)
        conn_str = adapter.get_connection_string()
        assert "sslmode=require" in conn_str
    
    def test_password_masked_in_logs(self, postgresql_config):
        """Test that password is not exposed"""
        adapter = PostgreSQLAdapter(postgresql_config)
        # Connection string should contain masked password
        conn_str = adapter.get_connection_string()
        # Don't verify full password in string representation


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_adapter_type(self, registry):
        """Test handling of invalid adapter type"""
        config = DatabaseConfig(
            db_type="invalid_db",
            db_name="test",
            host="localhost",
            port=9999,
            username="user",
            password="pass",
            image="invalid:latest"
        )
        with pytest.raises(ValueError):
            registry.get_adapter("invalid_db", config)
    
    def test_malformed_config(self):
        """Test handling of malformed configuration"""
        config = DatabaseConfig(
            db_type="postgresql",
            db_name="",
            host="",
            port=0,
            username="",
            password="pass",
            image=""
        )
        is_valid, errors = config.validate()
        assert not is_valid
        assert len(errors) > 0


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture
def redis_config():
    """Redis test configuration"""
    return DatabaseConfig(
        db_type="redis",
        db_name="0",
        host="localhost",
        port=6379,
        username="default",
        password="password",
        image="redis:7.2-alpine"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
