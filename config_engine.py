#!/usr/bin/env python3
"""
Configuration Engine v1.0
Dynamically configures microservices and integration points
Optimizes stack based on detected technologies and dependencies

INTEGRATED: Universal Database Adapter System for multi-database support
"""

import os
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import google.generativeai as genai
from enum import Enum

# Import Database Adapter Registry System
try:
    from database_adapter_registry import (
        DatabaseAdapterRegistry,
        DatabaseConfig,
        DatabaseAdapter
    )
    ADAPTER_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database Adapter System not available: {e}")
    ADAPTER_SYSTEM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    CLICKHOUSE = "clickhouse"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"


class CacheStrategy(Enum):
    """Cache strategy options"""
    REDIS = "redis"
    MEMCACHED = "memcached"
    DISTRIBUTED = "distributed"
    NONE = "none"


class LoggingStrategy(Enum):
    """Logging strategy options"""
    ELK = "elk"  # Elasticsearch, Logstash, Kibana
    SPLUNK = "splunk"
    DATADOG = "datadog"
    CLOUDWATCH = "cloudwatch"
    BASIC = "basic"


@dataclass
class MicroserviceConfig:
    """Configuration for a microservice"""
    name: str
    image: str
    port: int
    environment: Dict[str, str]
    resources: Dict[str, Any]  # cpu, memory limits
    scaling: Dict[str, Any]  # min/max replicas
    health_check: Dict
    dependencies: List[str]
    volumes: List[str]
    networks: List[str]
    security: Dict  # capabilities, readonly_root_filesystem, etc.
    labels: Dict
    logging_config: Dict


class ConfigurationEngine:
    """Intelligently configures microservice stacks"""

    def __init__(self, google_api_key: str = None):
        """Initialize configuration engine"""
        if not google_api_key:
            google_api_key = os.getenv("GOOGLE_KEY")
        
        if not google_api_key:
            raise ValueError("GOOGLE_KEY environment variable not set")
        
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        self.configurations = {}
        self.optimization_recommendations = {}
        
        # Initialize Database Adapter Registry
        self.adapter_registry = None
        if ADAPTER_SYSTEM_AVAILABLE:
            try:
                self.adapter_registry = DatabaseAdapterRegistry()
                logger.info("✅ Database Adapter Registry initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize adapter registry: {e}")

    def get_database_adapter(self, database_type: str, 
                            host: str = "localhost",
                            port: int = 0,
                            db_name: str = "appdb",
                            username: str = "user",
                            password: str = "password",
                            ssl_enabled: bool = False) -> Optional[DatabaseAdapter]:
        """
        Get a database adapter instance
        
        Args:
            database_type: Type of database (postgresql, mongodb, etc.)
            host: Database host
            port: Database port (0 = default for type)
            db_name: Database name
            username: Database username
            password: Database password
            ssl_enabled: Enable SSL/TLS
            
        Returns:
            DatabaseAdapter instance or None if not available
        """
        if not ADAPTER_SYSTEM_AVAILABLE or not self.adapter_registry:
            logger.warning(f"Adapter system not available for {database_type}")
            return None
        
        try:
            # Get docker image for database
            docker_image = self._get_docker_image_for_database(database_type)
            
            # Create database configuration
            db_config = DatabaseConfig(
                db_type=database_type,
                db_name=db_name,
                host=host,
                port=port if port > 0 else 0,  # Let adapter set default
                username=username,
                password=password,
                ssl_enabled=ssl_enabled,
                image=docker_image,
                pool_size=20,
                timeout=30
            )
            
            # Validate configuration
            is_valid, errors = db_config.validate()
            if not is_valid:
                logger.error(f"Invalid database config: {errors}")
                return None
            
            # Get adapter from registry
            adapter = self.adapter_registry.get_adapter(database_type, db_config)
            logger.info(f"✅ Adapter acquired for {database_type}")
            return adapter
            
        except Exception as e:
            logger.error(f"Error getting adapter for {database_type}: {e}")
            return None
    
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

    def generate_config(self, 
                       tech_stack_analysis: Dict,
                       database_type: DatabaseType = DatabaseType.POSTGRESQL,
                       environment: str = "production",
                       scale: str = "medium") -> Dict:
        """
        Generate complete configuration for the stack
        
        Args:
            tech_stack_analysis: Output from tech_analyzer_v2
            database_type: Primary database choice
            environment: production, staging, development
            scale: small, medium, large, xlarge
        """
        
        logger.info(f"⚙️  Generating configuration for {environment} environment")
        logger.info(f"📊 Scale: {scale}, Database: {database_type.value}")
        
        # Get LLM recommendations
        recommendations = self._get_llm_recommendations(
            tech_stack_analysis,
            database_type.value,
            environment,
            scale
        )
        
        # Generate microservice configurations
        microservices = self._generate_microservices(
            tech_stack_analysis,
            recommendations,
            environment,
            scale
        )
        
        # Generate resource allocations
        resources = self._allocate_resources(
            microservices,
            environment,
            scale
        )
        
        # Generate networking configuration
        networking = self._configure_networking(microservices)
        
        # Generate security configuration
        security = self._configure_security(environment)
        
        # Generate logging and monitoring
        observability = self._configure_observability(environment)
        
        config = {
            "metadata": {
                "environment": environment,
                "scale": scale,
                "database": database_type.value,
                "tech_stack": tech_stack_analysis,
                "recommendations": recommendations
            },
            "microservices": microservices,
            "resources": resources,
            "networking": networking,
            "security": security,
            "observability": observability
        }
        
        self.configurations[f"{environment}-{database_type.value}"] = config
        return config

    def _get_llm_recommendations(self, tech_stack: Dict, database: str,
                                 environment: str, scale: str) -> Dict:
        """Get LLM-powered recommendations for configuration"""
        
        prompt = f"""
Given this technology stack and deployment parameters, provide configuration recommendations:

TECH STACK:
- Languages: {', '.join(tech_stack.get('languages', []))}
- Frameworks: {', '.join(tech_stack.get('frameworks', []))}
- Databases: {', '.join(tech_stack.get('databases', []))}
- Primary DB: {database}
- Testing: {', '.join(tech_stack.get('testing_frameworks', []))}

DEPLOYMENT CONTEXT:
- Environment: {environment}
- Scale: {scale}

Provide recommendations in JSON format:
{{
  "cache_strategy": "redis|memcached|none",
  "logging_strategy": "elk|splunk|datadog|cloudwatch",
  "message_queue": "rabbitmq|kafka|redis",
  "resource_recommendations": {{
    "api_cpu_requests": "100m",
    "api_memory_requests": "256Mi",
    "api_cpu_limits": "1000m",
    "api_memory_limits": "1Gi",
    "worker_replicas": 2,
    "scaling_targets": {{"cpu_threshold": 70, "memory_threshold": 80}}
  }},
  "security_recommendations": [],
  "optimization_tips": [],
  "potential_bottlenecks": [],
  "monitoring_priorities": []
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"LLM recommendation failed: {e}")
        
        return self._default_recommendations(environment, scale)

    def _default_recommendations(self, environment: str, scale: str) -> Dict:
        """Provide default recommendations"""
        
        scale_config = {
            "small": {
                "api_cpu_requests": "100m",
                "api_memory_requests": "128Mi",
                "api_cpu_limits": "500m",
                "api_memory_limits": "512Mi",
                "worker_replicas": 1,
                "scaling_targets": {"cpu_threshold": 80, "memory_threshold": 90}
            },
            "medium": {
                "api_cpu_requests": "250m",
                "api_memory_requests": "256Mi",
                "api_cpu_limits": "1000m",
                "api_memory_limits": "1Gi",
                "worker_replicas": 2,
                "scaling_targets": {"cpu_threshold": 70, "memory_threshold": 80}
            },
            "large": {
                "api_cpu_requests": "500m",
                "api_memory_requests": "512Mi",
                "api_cpu_limits": "2000m",
                "api_memory_limits": "2Gi",
                "worker_replicas": 4,
                "scaling_targets": {"cpu_threshold": 60, "memory_threshold": 75}
            },
            "xlarge": {
                "api_cpu_requests": "1000m",
                "api_memory_requests": "1Gi",
                "api_cpu_limits": "4000m",
                "api_memory_limits": "4Gi",
                "worker_replicas": 8,
                "scaling_targets": {"cpu_threshold": 50, "memory_threshold": 70}
            }
        }
        
        env_config = {
            "production": {
                "cache_strategy": "redis",
                "logging_strategy": "datadog",
                "message_queue": "kafka",
                "replicas": 3
            },
            "staging": {
                "cache_strategy": "redis",
                "logging_strategy": "splunk",
                "message_queue": "rabbitmq",
                "replicas": 2
            },
            "development": {
                "cache_strategy": "redis",
                "logging_strategy": "basic",
                "message_queue": "redis",
                "replicas": 1
            }
        }
        
        return {
            "cache_strategy": env_config[environment]["cache_strategy"],
            "logging_strategy": env_config[environment]["logging_strategy"],
            "message_queue": env_config[environment]["message_queue"],
            "resource_recommendations": scale_config[scale],
            "security_recommendations": [
                "Enable network policies",
                "Use secrets management",
                "Implement RBAC"
            ],
            "optimization_tips": [
                "Use connection pooling",
                "Implement caching",
                "Optimize database queries"
            ]
        }

    def _generate_microservices(self, tech_stack: Dict, recommendations: Dict,
                                environment: str, scale: str) -> Dict[str, MicroserviceConfig]:
        """Generate microservice configurations"""
        
        services = {}
        
        # API Service
        services["api"] = self._create_api_service(tech_stack, recommendations, environment)
        
        # Worker Service (if applicable)
        if self._should_have_worker(tech_stack):
            services["worker"] = self._create_worker_service(recommendations, environment)
        
        # Cache Service
        if recommendations.get("cache_strategy") != "none":
            services["cache"] = self._create_cache_service(recommendations)
        
        # Message Queue Service
        if recommendations.get("message_queue"):
            services["queue"] = self._create_queue_service(recommendations)
        
        return services

    def _create_api_service(self, tech_stack: Dict, recommendations: Dict,
                           environment: str) -> MicroserviceConfig:
        """Create API service configuration"""
        
        primary_framework = tech_stack.get('frameworks', ['Unknown'])[0]
        primary_lang = tech_stack.get('languages', ['python'])[0]
        
        # Determine image
        if 'nodejs' in tech_stack.get('languages', []):
            image = "node:18-alpine"
            port = 3000
        elif 'python' in tech_stack.get('languages', []):
            image = "python:3.12-slim"
            port = 8000
        elif 'java' in tech_stack.get('languages', []):
            image = "openjdk:21-jdk-slim"
            port = 8080
        else:
            image = "node:18-alpine"
            port = 3000
        
        resource_rec = recommendations.get("resource_recommendations", {})
        
        return MicroserviceConfig(
            name="api",
            image=image,
            port=port,
            environment={
                "NODE_ENV" if "node" in image else "ENVIRONMENT": environment,
                "LOG_LEVEL": "INFO" if environment == "production" else "DEBUG",
                "CACHE_ENABLED": "true",
                "DATABASE_POOL_SIZE": "20"
            },
            resources={
                "requests": {
                    "cpu": resource_rec.get("api_cpu_requests", "250m"),
                    "memory": resource_rec.get("api_memory_requests", "256Mi")
                },
                "limits": {
                    "cpu": resource_rec.get("api_cpu_limits", "1000m"),
                    "memory": resource_rec.get("api_memory_limits", "1Gi")
                }
            },
            scaling={
                "min_replicas": 1 if environment == "development" else 3,
                "max_replicas": 10,
                "target_cpu_utilization_percentage": 70
            },
            health_check={
                "http_get": {
                    "path": "/health",
                    "port": port
                },
                "initial_delay_seconds": 10,
                "period_seconds": 10,
                "timeout_seconds": 5,
                "failure_threshold": 3
            },
            dependencies=["cache", "database"],
            volumes=["logs:/var/log/app"],
            networks=["app-network"],
            security={
                "read_only_root_filesystem": True,
                "run_as_non_root": True,
                "capabilities": {
                    "drop": ["ALL"],
                    "add": ["NET_BIND_SERVICE"]
                }
            },
            labels={
                "tier": "api",
                "framework": primary_framework,
                "language": primary_lang
            },
            logging_config={
                "driver": "json-file",
                "options": {
                    "max-size": "10m",
                    "max-file": "3"
                }
            }
        )

    def _create_worker_service(self, recommendations: Dict,
                              environment: str) -> MicroserviceConfig:
        """Create worker/background job service configuration"""
        
        resource_rec = recommendations.get("resource_recommendations", {})
        
        return MicroserviceConfig(
            name="worker",
            image="python:3.12-slim",
            port=8001,
            environment={
                "WORKER_TYPE": "celery",
                "QUEUE_BROKER": recommendations.get("message_queue", "redis"),
                "LOG_LEVEL": "INFO"
            },
            resources={
                "requests": {
                    "cpu": "200m",
                    "memory": "256Mi"
                },
                "limits": {
                    "cpu": "1000m",
                    "memory": "1Gi"
                }
            },
            scaling={
                "min_replicas": resource_rec.get("worker_replicas", 1),
                "max_replicas": 20,
                "target_cpu_utilization_percentage": 75
            },
            health_check={
                "exec": {
                    "command": ["celery", "inspect", "active"]
                },
                "initial_delay_seconds": 30,
                "period_seconds": 30
            },
            dependencies=["queue"],
            volumes=["logs:/var/log/app"],
            networks=["app-network"],
            security={
                "read_only_root_filesystem": False,
                "run_as_non_root": True
            },
            labels={
                "tier": "worker",
                "role": "background-job"
            },
            logging_config={
                "driver": "json-file",
                "options": {
                    "max-size": "10m",
                    "max-file": "3"
                }
            }
        )

    def _create_cache_service(self, recommendations: Dict) -> MicroserviceConfig:
        """Create cache service configuration"""
        
        cache_strategy = recommendations.get("cache_strategy", "redis")
        
        if cache_strategy == "redis":
            image = "redis:7.2-alpine"
            port = 6379
        elif cache_strategy == "memcached":
            image = "memcached:alpine"
            port = 11211
        else:
            image = "redis:7.2-alpine"
            port = 6379
        
        return MicroserviceConfig(
            name="cache",
            image=image,
            port=port,
            environment={},
            resources={
                "requests": {
                    "cpu": "100m",
                    "memory": "128Mi"
                },
                "limits": {
                    "cpu": "500m",
                    "memory": "512Mi"
                }
            },
            scaling={
                "min_replicas": 1,
                "max_replicas": 3
            },
            health_check={
                "tcp_socket": {
                    "port": port
                },
                "initial_delay_seconds": 5,
                "period_seconds": 10
            },
            dependencies=[],
            volumes=["cache_data:/data"],
            networks=["app-network"],
            security={},
            labels={
                "tier": "cache",
                "type": cache_strategy
            },
            logging_config={
                "driver": "json-file",
                "options": {
                    "max-size": "5m",
                    "max-file": "2"
                }
            }
        )

    def _create_queue_service(self, recommendations: Dict) -> MicroserviceConfig:
        """Create message queue service configuration"""
        
        queue_type = recommendations.get("message_queue", "redis")
        
        if queue_type == "kafka":
            image = "confluentinc/cp-kafka:latest"
            port = 9092
        elif queue_type == "rabbitmq":
            image = "rabbitmq:3.12-alpine"
            port = 5672
        else:  # redis
            image = "redis:7.2-alpine"
            port = 6379
        
        return MicroserviceConfig(
            name="queue",
            image=image,
            port=port,
            environment=self._queue_environment(queue_type),
            resources={
                "requests": {
                    "cpu": "200m",
                    "memory": "256Mi"
                },
                "limits": {
                    "cpu": "1000m",
                    "memory": "1Gi"
                }
            },
            scaling={
                "min_replicas": 1,
                "max_replicas": 5
            },
            health_check={
                "tcp_socket": {
                    "port": port
                },
                "initial_delay_seconds": 10,
                "period_seconds": 10
            },
            dependencies=[],
            volumes=[f"queue_data_{queue_type}:/var/lib/{queue_type}"],
            networks=["app-network"],
            security={},
            labels={
                "tier": "queue",
                "type": queue_type
            },
            logging_config={
                "driver": "json-file",
                "options": {
                    "max-size": "10m",
                    "max-file": "3"
                }
            }
        )

    def _queue_environment(self, queue_type: str) -> Dict:
        """Get environment variables for queue service"""
        if queue_type == "kafka":
            return {
                "KAFKA_BROKER_ID": "1",
                "KAFKA_ZOOKEEPER_CONNECT": "zookeeper:2181",
                "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://kafka:9092"
            }
        elif queue_type == "rabbitmq":
            return {
                "RABBITMQ_DEFAULT_USER": "guest",
                "RABBITMQ_DEFAULT_PASS": "guest"
            }
        return {}

    def _should_have_worker(self, tech_stack: Dict) -> bool:
        """Determine if worker service is needed"""
        frameworks = tech_stack.get('frameworks', [])
        return any(fw in frameworks for fw in ['Django', 'FastAPI', 'Flask', 'Spring'])

    def _allocate_resources(self, microservices: Dict, environment: str,
                           scale: str) -> Dict:
        """Allocate and optimize resources"""
        return {
            "environment": environment,
            "scale": scale,
            "total_cpu_request": self._sum_resource(microservices, "cpu", "requests"),
            "total_memory_request": self._sum_resource(microservices, "memory", "requests"),
            "total_cpu_limit": self._sum_resource(microservices, "cpu", "limits"),
            "total_memory_limit": self._sum_resource(microservices, "memory", "limits")
        }

    def _sum_resource(self, services: Dict, resource: str, resource_type: str) -> str:
        """Sum resource allocations across services"""
        total = 0
        for service in services.values():
            if isinstance(service, MicroserviceConfig):
                val = service.resources.get(resource_type, {}).get(resource, "0")
                # Parse CPU/memory values
                if resource == "cpu":
                    total += self._parse_cpu(val)
                else:
                    total += self._parse_memory(val)
        
        if resource == "cpu":
            return f"{int(total)}m"
        else:
            return f"{int(total)}Mi"

    def _parse_cpu(self, cpu_str: str) -> int:
        """Parse CPU string to millicores"""
        if 'm' in cpu_str:
            return int(cpu_str.replace('m', ''))
        else:
            return int(float(cpu_str) * 1000)

    def _parse_memory(self, mem_str: str) -> int:
        """Parse memory string to Mi"""
        if 'Mi' in mem_str:
            return int(mem_str.replace('Mi', ''))
        elif 'Gi' in mem_str:
            return int(float(mem_str.replace('Gi', '')) * 1024)
        else:
            return int(mem_str)

    def _configure_networking(self, microservices: Dict) -> Dict:
        """Configure networking for microservices"""
        return {
            "networks": {
                "app-network": {
                    "driver": "bridge",
                    "ipam": {
                        "config": [{"subnet": "172.20.0.0/16"}]
                    }
                }
            },
            "service_mesh": {
                "enabled": False,
                "type": "istio"
            },
            "ingress": {
                "enabled": True,
                "class": "nginx",
                "tls": True,
                "annotations": {
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            }
        }

    def _configure_security(self, environment: str) -> Dict:
        """Configure security settings"""
        return {
            "network_policies": True,
            "pod_security_standards": "restricted" if environment == "production" else "baseline",
            "rbac_enabled": True,
            "secrets_manager": "vault" if environment == "production" else "kubernetes",
            "image_scanning": environment == "production",
            "encryption": {
                "in_transit": True,
                "at_rest": environment == "production"
            }
        }

    def _configure_observability(self, environment: str) -> Dict:
        """Configure monitoring and logging"""
        return {
            "metrics": {
                "enabled": True,
                "provider": "prometheus",
                "retention": "30d" if environment == "production" else "7d"
            },
            "logging": {
                "enabled": True,
                "provider": "datadog" if environment == "production" else "loki",
                "retention": "30d" if environment == "production" else "7d",
                "log_level": "ERROR" if environment == "production" else "DEBUG"
            },
            "tracing": {
                "enabled": environment == "production",
                "provider": "jaeger",
                "sampling_rate": 0.1 if environment == "production" else 1.0
            },
            "alerting": {
                "enabled": environment == "production",
                "provider": "alertmanager",
                "channels": ["slack", "pagerduty"] if environment == "production" else ["slack"]
            }
        }

    def export_config(self, key: str, output_format: str = "yaml") -> str:
        """Export configuration to file"""
        if key not in self.configurations:
            raise ValueError(f"Configuration '{key}' not found")
        
        config = self.configurations[key]
        
        if output_format == "yaml":
            return yaml.dump(config, default_flow_style=False, sort_keys=False)
        elif output_format == "json":
            return json.dumps(config, indent=2, default=str)
        else:
            raise ValueError(f"Unknown format: {output_format}")

    def save_config(self, key: str, output_path: str):
        """Save configuration to file"""
        config = self.export_config(key, output_format="yaml")
        
        with open(output_path, 'w') as f:
            f.write(config)
        
        logger.info(f"✅ Saved configuration to {output_path}")


def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python config_engine.py <environment> <database> [--scale=medium]")
        print("Environments: production, staging, development")
        print("Databases: postgresql, mongodb, mysql, clickhouse")
        sys.exit(1)
    
    environment = sys.argv[1]
    database = sys.argv[2]
    scale = "medium"
    
    for arg in sys.argv[3:]:
        if arg.startswith("--scale="):
            scale = arg.split("=")[1]
    
    # Example tech stack
    example_stack = {
        "languages": ["python", "nodejs"],
        "frameworks": ["Django", "Express"],
        "databases": ["postgresql"],
        "testing_frameworks": ["pytest"],
        "other_tools": ["docker"]
    }
    
    engine = ConfigurationEngine()
    config = engine.generate_config(
        example_stack,
        DatabaseType[database.upper()],
        environment,
        scale
    )
    
    key = f"{environment}-{database}"
    engine.save_config(key, f"config-{key}.yaml")


if __name__ == "__main__":
    main()
