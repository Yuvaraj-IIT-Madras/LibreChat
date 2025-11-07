#!/usr/bin/env python3
"""
Dynamic Stack Generator v1.0
Generates optimized docker-compose configurations based on detected tech stack
Automatically configures microservices and integration points

INTEGRATED: Universal Database Adapter System for multi-database support
"""

import os
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import google.generativeai as genai
from tech_analyzer_v2 import TechStack

# Import Database Adapter Registry System
try:
    from database_adapter_registry import (
        DatabaseAdapterRegistry,
        DatabaseConfig,
        DatabaseAdapter
    )
    ADAPTER_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Database Adapter System not available: {e}")
    ADAPTER_SYSTEM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a microservice"""
    name: str
    image: str
    port: int
    environment: Dict[str, str]
    volumes: List[str]
    depends_on: List[str]
    command: str
    health_check: Dict
    networks: List[str]
    labels: Dict


class DynamicStackGenerator:
    """Generates docker-compose configurations dynamically"""

    def __init__(self, google_api_key: str = None):
        """Initialize generator with LLM capability and adapter support"""
        if not google_api_key:
            google_api_key = os.getenv("GOOGLE_KEY")
        
        if not google_api_key:
            raise ValueError("GOOGLE_KEY environment variable not set")
        
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        self.tech_stack = None
        self.database_config = None
        self.services = {}
        
        # Initialize Database Adapter Registry
        self.adapter_registry = None
        if ADAPTER_SYSTEM_AVAILABLE:
            try:
                self.adapter_registry = DatabaseAdapterRegistry()
                logger.info("✅ Database Adapter Registry initialized in StackGenerator")
            except Exception as e:
                logger.warning(f"Failed to initialize adapter registry: {e}")

    def generate_stack(self, tech_stack: TechStack, database_type: str = "postgresql",
                      enable_monitoring: bool = True, enable_ci_cd: bool = False) -> Dict:
        """Generate complete docker-compose configuration"""
        
        logger.info(f"🏗️  Generating stack for: {', '.join(tech_stack.languages)}")
        logger.info(f"📊 Database: {database_type}")
        
        self.tech_stack = tech_stack
        self.database_config = self._select_database_config(database_type)
        
        # Generate core services
        core_services = self._generate_core_services()
        
        # Generate database service
        db_services = self._generate_database_services(database_type)
        
        # Generate framework-specific services
        framework_services = self._generate_framework_services(tech_stack)
        
        # Generate monitoring services
        monitoring_services = self._generate_monitoring_services() if enable_monitoring else {}
        
        # Generate CI/CD services
        ci_services = self._generate_ci_cd_services() if enable_ci_cd else {}
        
        # Combine all services
        all_services = {
            **core_services,
            **db_services,
            **framework_services,
            **monitoring_services,
            **ci_services
        }
        
        # Generate docker-compose structure
        compose_config = {
            'version': '3.9',
            'services': self._build_service_configs(all_services),
            'networks': self._generate_networks(),
            'volumes': self._generate_volumes(all_services)
        }
        
        logger.info(f"✅ Generated {len(all_services)} services")
        return compose_config

    def _select_database_config(self, database_type: str) -> Dict:
        """Select database configuration - now using adapter registry"""
        
        # Try to use adapter system first
        if self.adapter_registry and ADAPTER_SYSTEM_AVAILABLE:
            try:
                db_config = DatabaseConfig(
                    db_type=database_type,
                    db_name="appdb",
                    host="localhost",
                    port=0,  # Let adapter set default
                    username="dbuser",
                    password="dbpassword123",
                    image=self._get_docker_image_for_database(database_type)
                )
                
                adapter = self.adapter_registry.get_adapter(database_type, db_config)
                docker_config = adapter.get_docker_config()
                
                logger.info(f"✅ Using adapter config for {database_type}")
                return docker_config
                
            except Exception as e:
                logger.warning(f"Adapter fallback for {database_type}: {e}")
        
        # Fallback to hardcoded configs if adapter not available
        db_configs = {
            "postgresql": {
                "image": "pgvector/pgvector:pg16",
                "port": 5432,
                "environment": {
                    "POSTGRES_DB": "appdb",
                    "POSTGRES_USER": "dbuser",
                    "POSTGRES_PASSWORD": "dbpassword123",
                    "POSTGRES_INITDB_ARGS": "-c max_connections=200"
                },
                "health_check": {
                    "test": ["CMD-SHELL", "pg_isready -U dbuser"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                },
                "extensions": ["pgvector"]
            },
            "mongodb": {
                "image": "mongo:7.0",
                "port": 27017,
                "environment": {
                    "MONGO_INITDB_ROOT_USERNAME": "admin",
                    "MONGO_INITDB_ROOT_PASSWORD": "mongopass123",
                    "MONGO_INITDB_DATABASE": "appdb"
                },
                "health_check": {
                    "test": ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            },
            "mysql": {
                "image": "mysql:8.0",
                "port": 3306,
                "environment": {
                    "MYSQL_ROOT_PASSWORD": "rootpass123",
                    "MYSQL_DATABASE": "appdb",
                    "MYSQL_USER": "dbuser",
                    "MYSQL_PASSWORD": "dbpass123"
                },
                "health_check": {
                    "test": ["CMD", "mysqladmin", "ping", "-h", "localhost"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            },
            "clickhouse": {
                "image": "clickhouse/clickhouse-server:latest",
                "port": 8123,
                "environment": {
                    "CLICKHOUSE_DB": "appdb"
                },
                "health_check": {
                    "test": ["CMD", "curl", "-f", "http://localhost:8123/ping"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            },
            "redis": {
                "image": "redis:7.2-alpine",
                "port": 6379,
                "environment": {},
                "health_check": {
                    "test": ["CMD", "redis-cli", "ping"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            }
        }
        
        return db_configs.get(database_type, db_configs["postgresql"])
    
    def _get_docker_image_for_database(self, database_type: str) -> str:
        """Get appropriate Docker image for database type"""
        image_mapping = {
            "postgresql": "pgvector/pgvector:pg16",
            "mongodb": "mongo:7.0",
            "mysql": "mysql:8.0",
            "clickhouse": "clickhouse/clickhouse-server:latest",
            "redis": "redis:7.2-alpine",
            "elasticsearch": "docker.elastic.co/elasticsearch/elasticsearch:8.0.0",
        }
        return image_mapping.get(database_type.lower(), "postgres:15")

    def _generate_core_services(self) -> Dict[str, ServiceConfig]:
        """Generate core infrastructure services"""
        services = {}
        
        # Vector Database (PostgreSQL with pgvector)
        services["vectordb"] = ServiceConfig(
            name="vectordb",
            image="pgvector/pgvector:pg16",
            port=5432,
            environment={
                "POSTGRES_DB": "rag_vectors",
                "POSTGRES_USER": "rag_user",
                "POSTGRES_PASSWORD": "rag_password_secure",
                "POSTGRES_INITDB_ARGS": "-c max_connections=300 -c shared_buffers=256MB"
            },
            volumes=["postgres_data:/var/lib/postgresql/data"],
            depends_on=[],
            command="postgres -c log_statement=all",
            health_check={
                "test": ["CMD-SHELL", "pg_isready -U rag_user -d rag_vectors"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5
            },
            networks=["rag-network"],
            labels={
                "service": "vector-database",
                "tier": "data"
            }
        )
        
        # Message Queue (Redis)
        services["redis"] = ServiceConfig(
            name="redis",
            image="redis:7.2-alpine",
            port=6379,
            environment={},
            volumes=["redis_data:/data"],
            depends_on=[],
            command="redis-server --appendonly yes --maxmemory 512mb",
            health_check={
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "5s",
                "timeout": "3s",
                "retries": 5
            },
            networks=["rag-network"],
            labels={
                "service": "message-queue",
                "tier": "infrastructure"
            }
        )
        
        # Search Engine (Meilisearch)
        services["meilisearch"] = ServiceConfig(
            name="meilisearch",
            image="getmeili/meilisearch:latest",
            port=7700,
            environment={
                "MEILI_ENV": "production",
                "MEILI_MASTER_KEY": "meilisearch_master_key_123",
                "MEILI_NO_ANALYTICS": "false"
            },
            volumes=["meilisearch_data:/meili_data"],
            depends_on=[],
            command="",
            health_check={
                "test": ["CMD", "curl", "-f", "http://localhost:7700/health"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5
            },
            networks=["rag-network"],
            labels={
                "service": "search-engine",
                "tier": "infrastructure"
            }
        )
        
        return services

    def _generate_database_services(self, database_type: str) -> Dict[str, ServiceConfig]:
        """Generate primary database service based on type"""
        services = {}
        db_config = self.database_config
        
        service_name = f"primary-{database_type}"
        
        environment = db_config["environment"].copy()
        
        # Add application-specific configurations
        if database_type == "postgresql":
            services[service_name] = ServiceConfig(
                name=service_name,
                image=db_config["image"],
                port=db_config["port"],
                environment=environment,
                volumes=[f"{service_name}_data:/var/lib/postgresql/data"],
                depends_on=[],
                command="postgres -c log_min_duration_statement=1000",
                health_check=db_config["health_check"],
                networks=["rag-network"],
                labels={
                    "service": "primary-database",
                    "tier": "data",
                    "database": database_type
                }
            )
        
        elif database_type == "mongodb":
            services[service_name] = ServiceConfig(
                name=service_name,
                image=db_config["image"],
                port=db_config["port"],
                environment=environment,
                volumes=[f"{service_name}_data:/data/db"],
                depends_on=[],
                command="mongod --auth --logpath=/var/log/mongodb/mongod.log",
                health_check=db_config["health_check"],
                networks=["rag-network"],
                labels={
                    "service": "primary-database",
                    "tier": "data",
                    "database": database_type
                }
            )
        
        elif database_type == "mysql":
            services[service_name] = ServiceConfig(
                name=service_name,
                image=db_config["image"],
                port=db_config["port"],
                environment=environment,
                volumes=[f"{service_name}_data:/var/lib/mysql"],
                depends_on=[],
                command="--default-authentication-plugin=mysql_native_password",
                health_check=db_config["health_check"],
                networks=["rag-network"],
                labels={
                    "service": "primary-database",
                    "tier": "data",
                    "database": database_type
                }
            )
        
        elif database_type == "clickhouse":
            services[service_name] = ServiceConfig(
                name=service_name,
                image=db_config["image"],
                port=db_config["port"],
                environment=environment,
                volumes=[f"{service_name}_data:/var/lib/clickhouse"],
                depends_on=[],
                command="",
                health_check=db_config["health_check"],
                networks=["rag-network"],
                labels={
                    "service": "primary-database",
                    "tier": "data",
                    "database": database_type
                }
            )
        
        return services

    def _generate_framework_services(self, tech_stack: TechStack) -> Dict[str, ServiceConfig]:
        """Generate services based on detected frameworks"""
        services = {}
        
        # RAG API Service (Python/FastAPI)
        if any(lang in tech_stack.languages for lang in ["python"]):
            services["rag_api"] = ServiceConfig(
                name="rag_api",
                image="rag_api:latest",
                port=8000,
                environment={
                    "PYTHONUNBUFFERED": "1",
                    "GOOGLE_KEY": os.getenv("GOOGLE_KEY", "your-key"),
                    "DATABASE_URL": "postgresql://rag_user:rag_password_secure@vectordb:5432/rag_vectors",
                    "REDIS_URL": "redis://redis:6379",
                    "EMBEDDINGS_MODEL": "models/embedding-001"
                },
                volumes=["./src:/app/src", "./scripts:/app/scripts"],
                depends_on=["vectordb", "redis"],
                command="python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
                health_check={
                    "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 3
                },
                networks=["rag-network"],
                labels={
                    "service": "rag-api",
                    "tier": "application"
                }
            )
        
        # Web Framework Service (Node.js)
        if any(lang in tech_stack.languages for lang in ["nodejs"]):
            services["web_app"] = ServiceConfig(
                name="web_app",
                image="node:18-alpine",
                port=3000,
                environment={
                    "NODE_ENV": "production",
                    "DATABASE_URL": self._build_db_connection_string(),
                    "REDIS_URL": "redis://redis:6379",
                    "API_PORT": "3000"
                },
                volumes=["./src:/app/src", "node_modules:/app/node_modules"],
                depends_on=["vectordb", "redis"],
                command="npm start",
                health_check={
                    "test": ["CMD", "curl", "-f", "http://localhost:3000/health"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 3
                },
                networks=["rag-network"],
                labels={
                    "service": "web-app",
                    "tier": "application"
                }
            )
        
        # Monitoring Service (Optional)
        if "prometheus" in tech_stack.other_tools or "datadog" in tech_stack.ci_cd_tools:
            services["prometheus"] = ServiceConfig(
                name="prometheus",
                image="prom/prometheus:latest",
                port=9090,
                environment={},
                volumes=["./prometheus.yml:/etc/prometheus/prometheus.yml"],
                depends_on=[],
                command="--config.file=/etc/prometheus/prometheus.yml",
                health_check={
                    "test": ["CMD", "curl", "-f", "http://localhost:9090/-/healthy"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 3
                },
                networks=["rag-network"],
                labels={
                    "service": "monitoring",
                    "tier": "observability"
                }
            )
        
        return services

    def _generate_monitoring_services(self) -> Dict[str, ServiceConfig]:
        """Generate monitoring and observability services"""
        services = {}
        
        # Grafana for dashboards
        services["grafana"] = ServiceConfig(
            name="grafana",
            image="grafana/grafana:latest",
            port=3001,
            environment={
                "GF_SECURITY_ADMIN_PASSWORD": "admin123",
                "GF_INSTALL_PLUGINS": "redis-datasource"
            },
            volumes=["grafana_data:/var/lib/grafana"],
            depends_on=["prometheus"],
            command="",
            health_check={
                "test": ["CMD", "curl", "-f", "http://localhost:3000/api/health"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 3
            },
            networks=["rag-network"],
            labels={
                "service": "grafana",
                "tier": "observability"
            }
        )
        
        return services

    def _generate_ci_cd_services(self) -> Dict[str, ServiceConfig]:
        """Generate CI/CD pipeline services"""
        services = {}
        
        # Gitea (self-hosted Git)
        services["gitea"] = ServiceConfig(
            name="gitea",
            image="gitea/gitea:latest",
            port=3000,
            environment={
                "GITEA__DATABASE__DB_TYPE": "postgres",
                "GITEA__DATABASE__HOST": "primary-postgresql",
                "GITEA__DATABASE__USER": "gitea",
                "GITEA__DATABASE__PASSWD": "gitea123"
            },
            volumes=["gitea_data:/data"],
            depends_on=["primary-postgresql"],
            command="",
            health_check={
                "test": ["CMD", "curl", "-f", "http://localhost:3000/api/v1/version"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 3
            },
            networks=["rag-network"],
            labels={
                "service": "gitea",
                "tier": "ci-cd"
            }
        )
        
        return services

    def _build_service_configs(self, services: Dict[str, ServiceConfig]) -> Dict:
        """Convert ServiceConfig objects to docker-compose format"""
        compose_services = {}
        
        for name, config in services.items():
            compose_services[name] = {
                "image": config.image,
                "ports": [f"{config.port}:{config.port}"],
                "environment": config.environment,
                "volumes": config.volumes,
                "depends_on": config.depends_on if config.depends_on else {},
                "networks": config.networks,
                "labels": config.labels
            }
            
            if config.command:
                compose_services[name]["command"] = config.command
            
            if config.health_check:
                compose_services[name]["healthcheck"] = config.health_check
        
        return compose_services

    def _build_db_connection_string(self) -> str:
        """Build connection string based on database type"""
        if not self.database_config:
            return ""
        
        db_type = self.database_config.get("type", "postgresql")
        
        if db_type == "postgresql":
            return f"postgresql://{self.database_config['environment'].get('POSTGRES_USER')}:{self.database_config['environment'].get('POSTGRES_PASSWORD')}@primary-postgresql:5432/{self.database_config['environment'].get('POSTGRES_DB')}"
        elif db_type == "mongodb":
            return f"mongodb://admin:{self.database_config['environment'].get('MONGO_INITDB_ROOT_PASSWORD')}@primary-mongodb:27017/appdb"
        elif db_type == "mysql":
            return f"mysql://{self.database_config['environment'].get('MYSQL_USER')}:{self.database_config['environment'].get('MYSQL_PASSWORD')}@primary-mysql:3306/{self.database_config['environment'].get('MYSQL_DATABASE')}"
        
        return ""

    def _generate_networks(self) -> Dict:
        """Generate network configurations"""
        return {
            "rag-network": {
                "driver": "bridge",
                "ipam": {
                    "config": [{"subnet": "172.20.0.0/16"}]
                }
            },
            "monitoring": {
                "driver": "bridge"
            }
        }

    def _generate_volumes(self, services: Dict[str, ServiceConfig]) -> Dict:
        """Generate volume configurations"""
        volumes = {}
        
        for name, config in services.items():
            for volume in config.volumes:
                if ':' in volume:
                    vol_name = volume.split(':')[0]
                    if not vol_name.startswith('.'):
                        volumes[vol_name] = {"driver": "local"}
        
        return volumes

    def generate_llm_optimizations(self) -> Dict:
        """Use LLM to suggest optimizations for the generated stack"""
        
        if not self.tech_stack:
            logger.warning("No tech stack configured")
            return {}
        
        prompt = f"""
Given this technology stack, suggest specific optimizations for a production deployment:

Languages: {', '.join(self.tech_stack.languages)}
Frameworks: {', '.join(self.tech_stack.frameworks)}
Databases: {', '.join(self.tech_stack.databases)}
Cloud: {', '.join(self.tech_stack.cloud_platforms)}
Testing: {', '.join(self.tech_stack.testing_frameworks)}

Provide in JSON format:
{{
  "resource_recommendations": {{}},
  "performance_tuning": {{}},
  "security_hardening": [],
  "scalability_strategies": [],
  "monitoring_setup": {{}}
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            import re
            import json
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"LLM optimization failed: {e}")
        
        return {}

    def save_docker_compose(self, config: Dict, output_path: str = "docker-compose.yml"):
        """Save docker-compose configuration to file"""
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"✅ Saved docker-compose configuration to {output_path}")

    def save_env_file(self, output_path: str = ".env.generated"):
        """Generate environment file"""
        env_content = f"""# Generated Environment Configuration

# API Keys
GOOGLE_KEY={os.getenv('GOOGLE_KEY', 'your-google-key')}

# Database Configuration
DB_HOST=primary-postgresql
DB_PORT=5432
DB_NAME=appdb
DB_USER=dbuser
DB_PASSWORD=dbpassword123

# Vector DB
VECTOR_DB_HOST=vectordb
VECTOR_DB_PORT=5432
VECTOR_DB_NAME=rag_vectors
VECTOR_DB_USER=rag_user
VECTOR_DB_PASSWORD=rag_password_secure

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379

# Search Engine
MEILI_HOST=http://meilisearch:7700
MEILI_MASTER_KEY=meilisearch_master_key_123

# RAG Configuration
RAG_API_URL=http://rag_api:8000
EMBEDDINGS_MODEL=models/embedding-001
EMBEDDINGS_PROVIDER=google
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Application
NODE_ENV=production
DEBUG=false
LOG_LEVEL=INFO
"""
        
        with open(output_path, 'w') as f:
            f.write(env_content)
        
        logger.info(f"✅ Generated environment file: {output_path}")


def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python stack_generator.py <database_type> [--with-monitoring] [--with-ci]")
        print("Database types: postgresql, mongodb, mysql, clickhouse, redis")
        sys.exit(1)
    
    database_type = sys.argv[1]
    enable_monitoring = "--with-monitoring" in sys.argv
    enable_ci = "--with-ci" in sys.argv
    
    # Example tech stack (in real usage, this comes from tech_analyzer_v2)
    example_stack = TechStack(
        languages=["python", "nodejs"],
        frameworks=["Django", "Express.js"],
        package_managers=["pip", "npm"],
        databases=["postgresql", "redis"],
        cloud_platforms=["Azure"],
        build_tools=["Docker"],
        testing_frameworks=["pytest", "jest"],
        ci_cd_tools=["GitHub Actions"],
        other_tools=["Kubernetes"],
        confidence=0.85,
        reasoning="Analyzed from requirements and configuration files"
    )
    
    generator = DynamicStackGenerator()
    config = generator.generate_stack(
        example_stack,
        database_type=database_type,
        enable_monitoring=enable_monitoring,
        enable_ci_cd=enable_ci
    )
    
    generator.save_docker_compose(config)
    generator.save_env_file()


if __name__ == "__main__":
    main()
