# LocalStack AWS Services - Azure Equivalent Mapping

## Overview

This document maps the **24 Azure services** from the Azure deployment to their **AWS equivalents** that can be simulated using **LocalStack**.

**LocalStack Status:** Running at `http://localhost:4566`

---

## 📊 Service Mapping Summary

| Azure Service | AWS Equivalent | LocalStack Support | Status |
|--------------|----------------|-------------------|--------|
| **Compute (4)** |
| Azure Container Instances | ECS Fargate | ✅ Full | Pro |
| Azure Container Registry | ECR | ✅ Full | Community |
| Azure Kubernetes Service | EKS | ✅ Full | Pro |
| Azure Container Apps | App Runner | ⚠️ Limited | Pro |
| **Database (3)** |
| PostgreSQL Flexible Server | RDS PostgreSQL | ✅ Full | Pro |
| Cosmos DB (MongoDB) | DocumentDB | ✅ Full | Pro |
| Redis Cache | ElastiCache | ✅ Full | Pro |
| **Storage (3)** |
| Blob Storage | S3 | ✅ Full | Community |
| Azure Files | EFS | ✅ Full | Pro |
| Disk Storage | EBS | ✅ Full | Community |
| **Networking (5)** |
| Virtual Network | VPC | ✅ Full | Community |
| Network Security Groups | Security Groups | ✅ Full | Community |
| Application Gateway | ALB | ✅ Full | Pro |
| Private Endpoint | VPC Endpoint | ✅ Full | Pro |
| Load Balancer | ELB/NLB | ✅ Full | Pro |
| **Monitoring (4)** |
| Application Insights | X-Ray | ✅ Full | Pro |
| Log Analytics | CloudWatch Logs | ✅ Full | Community |
| Azure Monitor | CloudWatch | ✅ Full | Community |
| Action Groups | SNS | ✅ Full | Community |
| **Security (3)** |
| Key Vault | Secrets Manager | ✅ Full | Community |
| Azure AD | IAM + Cognito | ✅ Full | Community |
| Defender for Cloud | Security Hub | ⚠️ Limited | Pro |
| **Optional (5)** |
| Front Door | CloudFront | ✅ Full | Pro |
| CDN | CloudFront | ✅ Full | Pro |
| Static Web Apps | S3 + CloudFront | ✅ Full | Community |
| Azure Functions | Lambda | ✅ Full | Community |
| Event Hub | Kinesis | ✅ Full | Pro |

**Legend:**
- ✅ Full = Fully supported in LocalStack
- ⚠️ Limited = Partial support
- Community = Available in free tier
- Pro = Requires LocalStack Pro ($35/month or free trial)

---

## 🚀 Quick Start with LocalStack

### 1. LocalStack Configuration

Create `docker-compose.localstack.yml`:

```yaml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    container_name: localstack-librechat
    ports:
      - "4566:4566"            # LocalStack Gateway
      - "4510-4559:4510-4559"  # External services port range
    environment:
      # Core configuration
      - SERVICES=s3,dynamodb,sqs,sns,lambda,ecs,ecr,rds,secretsmanager,cloudwatch,logs,iam,cognito,kinesis,elasticache,efs,ec2,vpc,elb,cloudfront
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
      - DOCKER_HOST=unix:///var/run/docker.sock
      
      # AWS credentials (fake, for compatibility)
      - AWS_DEFAULT_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      
      # Persistence
      - PERSISTENCE=1
      
      # Pro features (if you have license)
      # - LOCALSTACK_API_KEY=${LOCALSTACK_API_KEY}
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "./localstack-data:/tmp/localstack/data"
      - "./localstack-init:/etc/localstack/init/ready.d"  # Init scripts
    networks:
      - librechat-network

networks:
  librechat-network:
    name: librechat-network
```

### 2. AWS CLI Configuration for LocalStack

```bash
# Install AWS CLI (if not already installed)
pip install awscli awscli-local

# Configure AWS CLI for LocalStack
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Or use awslocal (wrapper that auto-configures endpoints)
alias aws='awslocal'
```

### 3. Environment Variables for LibreChat

Create `.env.localstack`:

```bash
# AWS LocalStack Configuration
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1

# S3 (replaces Azure Blob Storage)
AWS_S3_BUCKET_NAME=librechat-uploads
S3_ENDPOINT=http://localhost:4566

# DynamoDB (alternative to Cosmos DB)
DYNAMODB_TABLE_NAME=librechat-conversations
DYNAMODB_ENDPOINT=http://localhost:4566

# Secrets Manager (replaces Azure Key Vault)
SECRETS_MANAGER_ENDPOINT=http://localhost:4566

# ElastiCache/Redis (replaces Azure Redis)
REDIS_URI=redis://localhost:6379

# RDS PostgreSQL (replaces Azure PostgreSQL)
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/analytics

# CloudWatch (replaces Application Insights)
CLOUDWATCH_ENDPOINT=http://localhost:4566

# Lambda (replaces Azure Functions)
LAMBDA_ENDPOINT=http://localhost:4566
```

---

## 📦 Service-by-Service Setup

### **COMPUTE SERVICES**

#### 1. Amazon ECR (Azure Container Registry)

**Create Container Registry:**
```bash
# Create ECR repository
awslocal ecr create-repository \
  --repository-name librechat \
  --region us-east-1

# Tag and push image
docker tag librechat:latest localhost:4566/librechat:latest
docker push localhost:4566/librechat:latest

# List images
awslocal ecr describe-repositories
awslocal ecr list-images --repository-name librechat
```

**LocalStack Support:** ✅ Community Edition

---

#### 2. Amazon ECS Fargate (Azure Container Instances)

**Create ECS Cluster:**
```bash
# Create cluster
awslocal ecs create-cluster \
  --cluster-name librechat-cluster

# Register task definition
cat > task-definition.json <<EOF
{
  "family": "librechat-task",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "librechat",
      "image": "localhost:4566/librechat:latest",
      "cpu": 2048,
      "memory": 4096,
      "portMappings": [
        {
          "containerPort": 3080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "MONGO_URI", "value": "mongodb://localhost:27017/LibreChat"},
        {"name": "POSTGRES_URL", "value": "postgresql://localhost:5432/analytics"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/librechat",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096"
}
EOF

awslocal ecs register-task-definition \
  --cli-input-json file://task-definition.json

# Run task
awslocal ecs run-task \
  --cluster librechat-cluster \
  --task-definition librechat-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345]}"
```

**LocalStack Support:** ✅ Pro Edition

---

#### 3. Amazon EKS (Azure Kubernetes Service)

**Create EKS Cluster:**
```bash
# Create EKS cluster (requires LocalStack Pro)
awslocal eks create-cluster \
  --name librechat-cluster \
  --role-arn arn:aws:iam::000000000000:role/eks-role \
  --resources-vpc-config subnetIds=subnet-12345,subnet-67890

# Get cluster info
awslocal eks describe-cluster --name librechat-cluster
```

**LocalStack Support:** ✅ Pro Edition

---

#### 4. AWS Lambda (Azure Functions)

**Create Lambda Function:**
```bash
# Create function code
cat > lambda-function.py <<EOF
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from LocalStack Lambda!'
    }
EOF

# Zip it
zip function.zip lambda-function.py

# Create Lambda function
awslocal lambda create-function \
  --function-name librechat-processor \
  --runtime python3.11 \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --handler lambda-function.handler \
  --zip-file fileb://function.zip

# Invoke function
awslocal lambda invoke \
  --function-name librechat-processor \
  --payload '{"key": "value"}' \
  output.json

cat output.json
```

**LocalStack Support:** ✅ Community Edition

---

### **DATABASE SERVICES**

#### 5. Amazon RDS PostgreSQL (Azure PostgreSQL)

**Create RDS Instance:**
```bash
# Create DB instance
awslocal rds create-db-instance \
  --db-instance-identifier librechat-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.5 \
  --master-username postgres \
  --master-user-password postgres123 \
  --allocated-storage 20

# Wait for available status
awslocal rds wait db-instance-available \
  --db-instance-identifier librechat-postgres

# Get endpoint
awslocal rds describe-db-instances \
  --db-instance-identifier librechat-postgres \
  --query 'DBInstances[0].Endpoint.Address'

# Connect to database
PGPASSWORD=postgres123 psql -h localhost -U postgres -d postgres

# Create analytics database
CREATE DATABASE analytics;
CREATE EXTENSION IF NOT EXISTS vector;
```

**LocalStack Support:** ✅ Pro Edition

**Alternative (Community):** Use regular PostgreSQL container and connect via localhost

---

#### 6. Amazon DocumentDB (Azure Cosmos DB with MongoDB API)

**Create DocumentDB Cluster:**
```bash
# Create cluster
awslocal docdb create-db-cluster \
  --db-cluster-identifier librechat-docdb \
  --engine docdb \
  --master-username admin \
  --master-user-password password123

# Create instance
awslocal docdb create-db-instance \
  --db-instance-identifier librechat-docdb-instance \
  --db-instance-class db.t3.medium \
  --engine docdb \
  --db-cluster-identifier librechat-docdb

# Get endpoint
awslocal docdb describe-db-clusters \
  --db-cluster-identifier librechat-docdb \
  --query 'DBClusters[0].Endpoint'
```

**LocalStack Support:** ✅ Pro Edition

**Alternative (Community):** Use regular MongoDB container
```bash
docker run -d \
  --name mongodb-local \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  mongo:latest

# Connection string
MONGO_URI=mongodb://admin:password123@localhost:27017/LibreChat?authSource=admin
```

---

#### 7. Amazon ElastiCache Redis (Azure Cache for Redis)

**Create Redis Cluster:**
```bash
# Create cache cluster
awslocal elasticache create-cache-cluster \
  --cache-cluster-id librechat-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# Get endpoint
awslocal elasticache describe-cache-clusters \
  --cache-cluster-id librechat-redis \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint'
```

**LocalStack Support:** ✅ Pro Edition

**Alternative (Community):** Use regular Redis container
```bash
docker run -d \
  --name redis-local \
  -p 6379:6379 \
  redis:latest

# Connection string
REDIS_URI=redis://localhost:6379
```

---

### **STORAGE SERVICES**

#### 8. Amazon S3 (Azure Blob Storage)

**Create S3 Buckets:**
```bash
# Create main uploads bucket
awslocal s3 mb s3://librechat-uploads

# Create additional buckets
awslocal s3 mb s3://librechat-avatars
awslocal s3 mb s3://librechat-screenshots
awslocal s3 mb s3://librechat-exports
awslocal s3 mb s3://librechat-imports
awslocal s3 mb s3://librechat-backups

# List buckets
awslocal s3 ls

# Upload file
echo "Test content" > test.txt
awslocal s3 cp test.txt s3://librechat-uploads/

# List files
awslocal s3 ls s3://librechat-uploads/

# Set bucket policy (public read)
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::librechat-uploads/*"
    }
  ]
}
EOF

awslocal s3api put-bucket-policy \
  --bucket librechat-uploads \
  --policy file://bucket-policy.json

# Enable versioning
awslocal s3api put-bucket-versioning \
  --bucket librechat-uploads \
  --versioning-configuration Status=Enabled

# Enable CORS
cat > cors.json <<EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

awslocal s3api put-bucket-cors \
  --bucket librechat-uploads \
  --cors-configuration file://cors.json
```

**LocalStack Support:** ✅ Community Edition

**LibreChat S3 Configuration:**
```bash
# In .env file
S3_ENDPOINT=http://localhost:4566
S3_BUCKET=librechat-uploads
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

---

#### 9. Amazon EFS (Azure Files)

**Create EFS File System:**
```bash
# Create file system
awslocal efs create-file-system \
  --creation-token librechat-efs \
  --performance-mode generalPurpose \
  --throughput-mode bursting

# Get file system ID
FS_ID=$(awslocal efs describe-file-systems \
  --query 'FileSystems[0].FileSystemId' \
  --output text)

# Create mount target
awslocal efs create-mount-target \
  --file-system-id $FS_ID \
  --subnet-id subnet-12345 \
  --security-groups sg-12345

# Mount EFS (in EC2 or container)
sudo mount -t efs $FS_ID:/ /mnt/efs
```

**LocalStack Support:** ✅ Pro Edition

**Alternative (Community):** Use Docker volumes
```bash
docker volume create librechat-shared-data
```

---

#### 10. Amazon EBS (Azure Disk Storage)

**Create EBS Volume:**
```bash
# Create volume
awslocal ec2 create-volume \
  --availability-zone us-east-1a \
  --size 100 \
  --volume-type gp3

# Attach to instance
awslocal ec2 attach-volume \
  --volume-id vol-12345 \
  --instance-id i-12345 \
  --device /dev/sdf
```

**LocalStack Support:** ✅ Community Edition

---

### **NETWORKING SERVICES**

#### 11. Amazon VPC (Azure Virtual Network)

**Create VPC:**
```bash
# Create VPC
VPC_ID=$(awslocal ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' \
  --output text)

# Create subnets
APP_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --query 'Subnet.SubnetId' \
  --output text)

DB_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1a \
  --query 'Subnet.SubnetId' \
  --output text)

CONTAINER_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.3.0/24 \
  --availability-zone us-east-1a \
  --query 'Subnet.SubnetId' \
  --output text)

GATEWAY_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.4.0/24 \
  --availability-zone us-east-1a \
  --query 'Subnet.SubnetId' \
  --output text)

# Create internet gateway
IGW_ID=$(awslocal ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)

awslocal ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID

# Create route table
RT_ID=$(awslocal ec2 create-route-table \
  --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' \
  --output text)

awslocal ec2 create-route \
  --route-table-id $RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID
```

**LocalStack Support:** ✅ Community Edition

---

#### 12. Security Groups (Azure NSG)

**Create Security Groups:**
```bash
# Create app security group
APP_SG=$(awslocal ec2 create-security-group \
  --group-name librechat-app-sg \
  --description "LibreChat application security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Allow HTTP/HTTPS
awslocal ec2 authorize-security-group-ingress \
  --group-id $APP_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

awslocal ec2 authorize-security-group-ingress \
  --group-id $APP_SG \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Create database security group
DB_SG=$(awslocal ec2 create-security-group \
  --group-name librechat-db-sg \
  --description "Database security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Allow PostgreSQL from app subnet
awslocal ec2 authorize-security-group-ingress \
  --group-id $DB_SG \
  --protocol tcp \
  --port 5432 \
  --source-group $APP_SG

# Allow MongoDB
awslocal ec2 authorize-security-group-ingress \
  --group-id $DB_SG \
  --protocol tcp \
  --port 27017 \
  --source-group $APP_SG

# Allow Redis
awslocal ec2 authorize-security-group-ingress \
  --group-id $DB_SG \
  --protocol tcp \
  --port 6379 \
  --source-group $APP_SG
```

**LocalStack Support:** ✅ Community Edition

---

#### 13. Application Load Balancer (Azure Application Gateway)

**Create ALB:**
```bash
# Create load balancer
LB_ARN=$(awslocal elbv2 create-load-balancer \
  --name librechat-alb \
  --subnets $APP_SUBNET $GATEWAY_SUBNET \
  --security-groups $APP_SG \
  --scheme internet-facing \
  --type application \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Create target group
TG_ARN=$(awslocal elbv2 create-target-group \
  --name librechat-targets \
  --protocol HTTP \
  --port 3080 \
  --vpc-id $VPC_ID \
  --health-check-path /api/health \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create listener
awslocal elbv2 create-listener \
  --load-balancer-arn $LB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN

# Get DNS name
awslocal elbv2 describe-load-balancers \
  --load-balancer-arns $LB_ARN \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

**LocalStack Support:** ✅ Pro Edition

---

#### 14. VPC Endpoint (Azure Private Endpoint)

**Create VPC Endpoint:**
```bash
# Create VPC endpoint for S3
awslocal ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids $RT_ID

# Create interface endpoint for Secrets Manager
awslocal ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.us-east-1.secretsmanager \
  --subnet-ids $APP_SUBNET \
  --security-group-ids $APP_SG
```

**LocalStack Support:** ✅ Pro Edition

---

#### 15. Network Load Balancer (Azure Load Balancer)

**Create NLB:**
```bash
# Create network load balancer
NLB_ARN=$(awslocal elbv2 create-load-balancer \
  --name librechat-nlb \
  --subnets $APP_SUBNET \
  --type network \
  --scheme internal \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)
```

**LocalStack Support:** ✅ Pro Edition

---

### **MONITORING SERVICES**

#### 16. AWS X-Ray (Azure Application Insights)

**Configure X-Ray:**
```bash
# Create sampling rule
cat > sampling-rule.json <<EOF
{
  "SamplingRule": {
    "RuleName": "LibreChatRule",
    "ResourceARN": "*",
    "Priority": 1000,
    "FixedRate": 0.05,
    "ReservoirSize": 1,
    "ServiceName": "librechat",
    "ServiceType": "*",
    "Host": "*",
    "HTTPMethod": "*",
    "URLPath": "*",
    "Version": 1
  }
}
EOF

awslocal xray create-sampling-rule \
  --cli-input-json file://sampling-rule.json

# In your Node.js app
npm install aws-xray-sdk

# Add to app.js
const AWSXRay = require('aws-xray-sdk');
AWSXRay.config([AWSXRay.plugins.ECSPlugin]);
const app = AWSXRay.express.openSegment('LibreChat', app);
// ... your routes ...
app.use(AWSXRay.express.closeSegment());
```

**LocalStack Support:** ✅ Pro Edition

---

#### 17. CloudWatch Logs (Azure Log Analytics)

**Create Log Groups:**
```bash
# Create log groups
awslocal logs create-log-group \
  --log-group-name /aws/ecs/librechat

awslocal logs create-log-group \
  --log-group-name /aws/lambda/analytics

awslocal logs create-log-group \
  --log-group-name /aws/e2e/playwright

# Create log stream
awslocal logs create-log-stream \
  --log-group-name /aws/ecs/librechat \
  --log-stream-name librechat-api

# Put log events
awslocal logs put-log-events \
  --log-group-name /aws/ecs/librechat \
  --log-stream-name librechat-api \
  --log-events timestamp=$(date +%s000),message="Application started"

# Query logs
awslocal logs filter-log-events \
  --log-group-name /aws/ecs/librechat \
  --filter-pattern "ERROR"

# Tail logs
awslocal logs tail /aws/ecs/librechat --follow
```

**LocalStack Support:** ✅ Community Edition

---

#### 18. CloudWatch Metrics (Azure Monitor)

**Create Custom Metrics:**
```bash
# Put metric data
awslocal cloudwatch put-metric-data \
  --namespace "LibreChat" \
  --metric-name "APIRequests" \
  --value 1 \
  --dimensions Service=API,Environment=Development

# Get metric statistics
awslocal cloudwatch get-metric-statistics \
  --namespace "LibreChat" \
  --metric-name "APIRequests" \
  --dimensions Name=Service,Value=API \
  --start-time 2025-11-09T00:00:00Z \
  --end-time 2025-11-09T23:59:59Z \
  --period 3600 \
  --statistics Sum

# Create alarm
awslocal cloudwatch put-metric-alarm \
  --alarm-name high-cpu-usage \
  --alarm-description "Triggers when CPU usage is high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

**LocalStack Support:** ✅ Community Edition

---

#### 19. Amazon SNS (Azure Action Groups)

**Create SNS Topics:**
```bash
# Create topic
TOPIC_ARN=$(awslocal sns create-topic \
  --name librechat-alerts \
  --query 'TopicArn' \
  --output text)

# Subscribe to email
awslocal sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol email \
  --notification-endpoint your-email@example.com

# Publish message
awslocal sns publish \
  --topic-arn $TOPIC_ARN \
  --subject "Alert: High CPU Usage" \
  --message "CPU usage exceeded 80%"

# Subscribe CloudWatch alarm to SNS
awslocal cloudwatch put-metric-alarm \
  --alarm-name high-cpu-usage \
  --alarm-actions $TOPIC_ARN \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

**LocalStack Support:** ✅ Community Edition

---

### **SECURITY SERVICES**

#### 20. AWS Secrets Manager (Azure Key Vault)

**Create Secrets:**
```bash
# Create secret
awslocal secretsmanager create-secret \
  --name librechat/api-keys \
  --description "LibreChat API keys" \
  --secret-string '{
    "OPENAI_API_KEY": "sk-test123",
    "ANTHROPIC_API_KEY": "ant-test456",
    "GOOGLE_API_KEY": "gcp-test789",
    "MONGO_URI": "mongodb://admin:pass@localhost:27017",
    "POSTGRES_URL": "postgresql://user:pass@localhost:5432/db",
    "JWT_SECRET": "your-jwt-secret",
    "REDIS_URI": "redis://localhost:6379"
  }'

# Get secret value
awslocal secretsmanager get-secret-value \
  --secret-id librechat/api-keys \
  --query 'SecretString' \
  --output text | jq

# Update secret
awslocal secretsmanager update-secret \
  --secret-id librechat/api-keys \
  --secret-string '{"OPENAI_API_KEY": "sk-new-key"}'

# List secrets
awslocal secretsmanager list-secrets

# Delete secret
awslocal secretsmanager delete-secret \
  --secret-id librechat/api-keys \
  --force-delete-without-recovery
```

**Use in Application:**
```javascript
// Node.js example
const { SecretsManagerClient, GetSecretValueCommand } = require("@aws-sdk/client-secrets-manager");

const client = new SecretsManagerClient({
  endpoint: "http://localhost:4566",
  region: "us-east-1",
  credentials: {
    accessKeyId: "test",
    secretAccessKey: "test"
  }
});

async function getSecret(secretName) {
  const command = new GetSecretValueCommand({ SecretId: secretName });
  const response = await client.send(command);
  return JSON.parse(response.SecretString);
}

// Usage
const secrets = await getSecret("librechat/api-keys");
const OPENAI_API_KEY = secrets.OPENAI_API_KEY;
```

**LocalStack Support:** ✅ Community Edition

---

#### 21. AWS IAM + Cognito (Azure AD)

**Create IAM Roles:**
```bash
# Create IAM role for ECS tasks
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

awslocal iam create-role \
  --role-name LibreChatECSRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
awslocal iam attach-role-policy \
  --role-name LibreChatECSRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonECSTaskExecutionRolePolicy

# Create Cognito User Pool (for authentication)
USER_POOL_ID=$(awslocal cognito-idp create-user-pool \
  --pool-name librechat-users \
  --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
  --query 'UserPool.Id' \
  --output text)

# Create app client
CLIENT_ID=$(awslocal cognito-idp create-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-name librechat-web \
  --query 'UserPoolClient.ClientId' \
  --output text)

# Create user
awslocal cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username testuser \
  --temporary-password TempPass123! \
  --user-attributes Name=email,Value=test@example.com

# Authenticate user
awslocal cognito-idp admin-initiate-auth \
  --user-pool-id $USER_POOL_ID \
  --client-id $CLIENT_ID \
  --auth-flow ADMIN_NO_SRP_AUTH \
  --auth-parameters USERNAME=testuser,PASSWORD=TempPass123!
```

**LocalStack Support:** ✅ Community Edition

---

#### 22. AWS Security Hub (Azure Defender for Cloud)

**Enable Security Hub:**
```bash
# Enable Security Hub
awslocal securityhub enable-security-hub

# Get findings
awslocal securityhub get-findings \
  --filters '{"SeverityLabel": [{"Value": "CRITICAL", "Comparison": "EQUALS"}]}'
```

**LocalStack Support:** ⚠️ Limited (Pro Edition)

---

### **OPTIONAL SERVICES**

#### 23. Amazon CloudFront (Azure Front Door / CDN)

**Create CloudFront Distribution:**
```bash
# Create distribution
cat > distribution-config.json <<EOF
{
  "CallerReference": "librechat-$(date +%s)",
  "Comment": "LibreChat CDN",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-librechat-uploads",
        "DomainName": "librechat-uploads.s3.localhost.localstack.cloud:4566",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-librechat-uploads",
    "ViewerProtocolPolicy": "allow-all",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0
  }
}
EOF

DISTRIBUTION_ID=$(awslocal cloudfront create-distribution \
  --distribution-config file://distribution-config.json \
  --query 'Distribution.Id' \
  --output text)

# Get distribution domain
awslocal cloudfront get-distribution \
  --id $DISTRIBUTION_ID \
  --query 'Distribution.DomainName' \
  --output text
```

**LocalStack Support:** ✅ Pro Edition

---

#### 24. Amazon Kinesis (Azure Event Hub)

**Create Kinesis Stream:**
```bash
# Create stream
awslocal kinesis create-stream \
  --stream-name librechat-events \
  --shard-count 1

# Put record
awslocal kinesis put-record \
  --stream-name librechat-events \
  --partition-key user123 \
  --data "{'event': 'message_sent', 'user': 'user123'}"

# Get shard iterator
SHARD_ITERATOR=$(awslocal kinesis get-shard-iterator \
  --stream-name librechat-events \
  --shard-id shardId-000000000000 \
  --shard-iterator-type LATEST \
  --query 'ShardIterator' \
  --output text)

# Get records
awslocal kinesis get-records \
  --shard-iterator $SHARD_ITERATOR

# Create consumer
awslocal kinesis subscribe-to-shard \
  --consumer-arn arn:aws:kinesis:us-east-1:000000000000:stream/librechat-events/consumer/my-consumer \
  --shard-id shardId-000000000000 \
  --starting-position '{"Type": "LATEST"}'
```

**LocalStack Support:** ✅ Pro Edition

---

## 🔧 Complete LibreChat LocalStack Setup

### Full Initialization Script

Create `localstack-init/01-setup.sh`:

```bash
#!/bin/bash

# Wait for LocalStack to be ready
echo "Waiting for LocalStack..."
awslocal s3 ls 2>/dev/null
while [ $? -ne 0 ]; do
  sleep 2
  awslocal s3 ls 2>/dev/null
done
echo "LocalStack is ready!"

# 1. Create S3 buckets
echo "Creating S3 buckets..."
awslocal s3 mb s3://librechat-uploads
awslocal s3 mb s3://librechat-avatars
awslocal s3 mb s3://librechat-screenshots
awslocal s3 mb s3://librechat-exports

# 2. Create Secrets Manager secrets
echo "Creating secrets..."
awslocal secretsmanager create-secret \
  --name librechat/api-keys \
  --secret-string '{
    "OPENAI_API_KEY": "'${OPENAI_API_KEY:-sk-test123}'",
    "ANTHROPIC_API_KEY": "'${ANTHROPIC_API_KEY:-ant-test456}'",
    "JWT_SECRET": "'${JWT_SECRET:-jwt-secret-123}'",
    "MONGO_URI": "mongodb://mongodb:27017/LibreChat",
    "POSTGRES_URL": "postgresql://postgres:postgres@postgres:5432/analytics",
    "REDIS_URI": "redis://redis:6379"
  }'

# 3. Create CloudWatch log groups
echo "Creating log groups..."
awslocal logs create-log-group --log-group-name /aws/ecs/librechat
awslocal logs create-log-group --log-group-name /aws/lambda/analytics
awslocal logs create-log-group --log-group-name /aws/e2e/playwright

# 4. Create SNS topic for alerts
echo "Creating SNS topic..."
TOPIC_ARN=$(awslocal sns create-topic --name librechat-alerts --query 'TopicArn' --output text)
echo "Topic ARN: $TOPIC_ARN"

# 5. Create VPC and subnets
echo "Creating VPC..."
VPC_ID=$(awslocal ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
awslocal ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# 6. Create security groups
echo "Creating security groups..."
SG_ID=$(awslocal ec2 create-security-group \
  --group-name librechat-sg \
  --description "LibreChat security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 3080 \
  --cidr 0.0.0.0/0

# 7. Create ECR repository
echo "Creating ECR repository..."
awslocal ecr create-repository --repository-name librechat

echo "✅ LocalStack initialization complete!"
```

Make it executable:
```bash
chmod +x localstack-init/01-setup.sh
```

### Updated docker-compose.yml

Create `docker-compose.localstack.yml`:

```yaml
version: '3.8'

services:
  # LocalStack
  localstack:
    image: localstack/localstack:latest
    container_name: localstack-librechat
    ports:
      - "4566:4566"
      - "4510-4559:4510-4559"
    environment:
      - SERVICES=s3,dynamodb,sqs,sns,lambda,ecs,ecr,rds,secretsmanager,cloudwatch,logs,iam,cognito,kinesis,elasticache,efs,ec2,vpc,elb,cloudfront,xray
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
      - DOCKER_HOST=unix:///var/run/docker.sock
      - AWS_DEFAULT_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - PERSISTENCE=1
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "./localstack-data:/tmp/localstack/data"
      - "./localstack-init:/etc/localstack/init/ready.d"
    networks:
      - librechat-network

  # MongoDB (local, not using DocumentDB)
  mongodb:
    image: mongo:latest
    container_name: librechat-mongodb
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password123
    volumes:
      - mongodb-data:/data/db
    networks:
      - librechat-network

  # PostgreSQL (local, not using RDS)
  postgres:
    image: pgvector/pgvector:pg15
    container_name: librechat-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=analytics
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - librechat-network

  # Redis (local, not using ElastiCache)
  redis:
    image: redis:latest
    container_name: librechat-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - librechat-network

  # Meilisearch
  meilisearch:
    image: getmeili/meilisearch:latest
    container_name: librechat-meilisearch
    ports:
      - "7700:7700"
    environment:
      - MEILI_MASTER_KEY=masterkey123
    volumes:
      - meili-data:/meili_data
    networks:
      - librechat-network

  # LibreChat API (using LocalStack S3)
  librechat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: librechat-api
    ports:
      - "3080:3080"
    environment:
      # AWS LocalStack
      - AWS_ENDPOINT_URL=http://localstack:4566
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_DEFAULT_REGION=us-east-1
      
      # S3 Configuration
      - S3_ENDPOINT=http://localstack:4566
      - S3_BUCKET=librechat-uploads
      - S3_FORCE_PATH_STYLE=true
      
      # Databases
      - MONGO_URI=mongodb://admin:password123@mongodb:27017/LibreChat?authSource=admin
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/analytics
      - REDIS_URI=redis://redis:6379
      
      # Meilisearch
      - MEILI_HOST=http://meilisearch:7700
      - MEILI_MASTER_KEY=masterkey123
      
      # Secrets Manager
      - SECRETS_MANAGER_ENDPOINT=http://localstack:4566
      - USE_SECRETS_MANAGER=true
      - SECRET_NAME=librechat/api-keys
      
      # CloudWatch
      - CLOUDWATCH_ENDPOINT=http://localstack:4566
      - ENABLE_CLOUDWATCH_LOGS=true
      - LOG_GROUP_NAME=/aws/ecs/librechat
      
      # X-Ray
      - AWS_XRAY_DAEMON_ADDRESS=localstack:2000
      - ENABLE_XRAY=true
      
      # Application
      - HOST=0.0.0.0
      - PORT=3080
    depends_on:
      - localstack
      - mongodb
      - postgres
      - redis
      - meilisearch
    networks:
      - librechat-network
    volumes:
      - ./librechat.yaml:/app/librechat.yaml

  # Analytics Stack (using LocalStack)
  analytics:
    build:
      context: ./azure
      dockerfile: Dockerfile.agentic-analytics
    container_name: librechat-analytics
    environment:
      - AWS_ENDPOINT_URL=http://localstack:4566
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_DEFAULT_REGION=us-east-1
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/analytics
      - S3_BUCKET=librechat-exports
      - CLOUDWATCH_LOG_GROUP=/aws/lambda/analytics
    depends_on:
      - localstack
      - postgres
    networks:
      - librechat-network

  # E2E Testing (using LocalStack S3 for screenshots)
  playwright:
    build:
      context: ./azure
      dockerfile: Dockerfile.playwright-e2e
    container_name: librechat-playwright
    environment:
      - AWS_ENDPOINT_URL=http://localstack:4566
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_DEFAULT_REGION=us-east-1
      - S3_BUCKET=librechat-screenshots
      - CLOUDWATCH_LOG_GROUP=/aws/e2e/playwright
      - BASE_URL=http://librechat:3080
    depends_on:
      - localstack
      - librechat
    networks:
      - librechat-network

volumes:
  mongodb-data:
  postgres-data:
  redis-data:
  meili-data:

networks:
  librechat-network:
    name: librechat-network
```

---

## 🚀 Deploy Everything

### 1. Start LocalStack and Services

```bash
# Create init directory
mkdir -p localstack-init

# Create initialization script (see above)
nano localstack-init/01-setup.sh
chmod +x localstack-init/01-setup.sh

# Start all services
docker-compose -f docker-compose.localstack.yml up -d

# Check LocalStack logs
docker logs -f localstack-librechat

# Verify S3 buckets created
awslocal s3 ls

# Verify secrets created
awslocal secretsmanager list-secrets

# Verify log groups created
awslocal logs describe-log-groups
```

### 2. Verify Everything Works

```bash
# Test S3 upload
echo "Test file" > test.txt
awslocal s3 cp test.txt s3://librechat-uploads/
awslocal s3 ls s3://librechat-uploads/

# Test Secrets Manager
awslocal secretsmanager get-secret-value \
  --secret-id librechat/api-keys \
  --query 'SecretString' --output text | jq

# Test CloudWatch Logs
awslocal logs tail /aws/ecs/librechat --follow

# Access LibreChat
curl http://localhost:3080/api/health

# Check all containers
docker ps
```

### 3. Access Services

- **LibreChat:** http://localhost:3080
- **LocalStack:** http://localhost:4566
- **Meilisearch:** http://localhost:7700
- **PostgreSQL:** localhost:5432
- **MongoDB:** localhost:27017
- **Redis:** localhost:6379

---

## 💰 Cost Comparison

| Deployment Type | Monthly Cost | Notes |
|----------------|-------------|-------|
| **Azure PaaS (Dev)** | $156 | 11 required services |
| **Azure PaaS (Prod)** | $896 | All 24 services |
| **LocalStack Community** | $0 | Limited features |
| **LocalStack Pro** | $35 | All AWS services |
| **Docker Compose (Local)** | $0 | No cloud costs |

---

## 📚 Next Steps

1. ✅ **LocalStack Running** - Already confirmed
2. 🔧 **Initialize Services** - Run init script
3. 🚀 **Deploy LibreChat** - Use docker-compose.localstack.yml
4. 🧪 **Test Integration** - Verify S3, Secrets, Logs work
5. 📊 **Monitor** - Check CloudWatch logs and metrics
6. 🎯 **Production** - Migrate to real AWS when ready

---

## 🆘 Troubleshooting

### LocalStack Not Starting
```bash
# Check logs
docker logs localstack-librechat

# Restart with clean slate
docker-compose -f docker-compose.localstack.yml down -v
docker-compose -f docker-compose.localstack.yml up -d
```

### S3 Not Working
```bash
# Verify bucket exists
awslocal s3 ls

# Check endpoint configuration
echo $AWS_ENDPOINT_URL

# Test with curl
curl http://localhost:4566/_localstack/health
```

### Secrets Not Loading
```bash
# Check if secret exists
awslocal secretsmanager list-secrets

# Get secret value
awslocal secretsmanager get-secret-value --secret-id librechat/api-keys

# Update .env to use Secrets Manager
USE_SECRETS_MANAGER=true
SECRET_NAME=librechat/api-keys
```

---

## 🎉 Summary

You now have a **complete AWS-equivalent setup using LocalStack** that mirrors all 24 Azure services:

✅ **Storage:** S3 (replaces Blob Storage, Files)
✅ **Compute:** ECS/Lambda (replaces Container Instances, Functions)
✅ **Database:** RDS/DocumentDB/ElastiCache (replaces PostgreSQL, Cosmos DB, Redis)
✅ **Networking:** VPC/Security Groups/ALB (replaces VNet, NSG, App Gateway)
✅ **Monitoring:** CloudWatch/X-Ray (replaces Application Insights, Log Analytics)
✅ **Security:** Secrets Manager/IAM/Cognito (replaces Key Vault, Azure AD)

**Total Cost:** $0 (Community) or $35/month (Pro)

Compare to Azure: $156-896/month 💰

Ready to deploy! 🚀
