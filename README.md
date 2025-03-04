# URL Shortener - Architecture Comparison

A comprehensive comparison of URL shortener service deployment using Monolithic, IaaS (Microservices), and Serverless architectures.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Deployment Instructions](#deployment-instructions)
- [Performance Testing](#performance-testing)
- [Cleanup](#cleanup)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Monitoring](#monitoring)

## Architecture Overview

### Project Structure
```
url-shortener/
├── monolithic/
│   ├── app.py
│   └── template.yaml
├── iaas/
│   ├── creator-service/
│   │   └── app.py
│   ├── redirector-service/
│   │   └── app.py
│   └── template.yaml
├── serverless/
│   └── template.yaml
├── tests/
│   └── performance_test.py
└── requirements.txt
```

## Prerequisites

1. AWS CLI installed and configured
2. Python 3.9 or higher
3. Required Python packages:
```bash
pip install requests pandas matplotlib psutil
```

## Deployment Instructions

### Monolithic Deployment

1. Deploy the stack:
```bash
cd monolithic
aws cloudformation create-stack \
  --stack-name url-shortener-mono \
  --template-body file://template.yaml \
  --parameters \
    ParameterKey=KeyName,ParameterValue=your-key-pair \
    ParameterKey=VpcId,ParameterValue=your-vpc-id \
    ParameterKey=SubnetId,ParameterValue=your-subnet-id \
  --capabilities CAPABILITY_IAM
```

2. Get the endpoint:
```bash
export MONO_URL=$(aws cloudformation describe-stacks \
  --stack-name url-shortener-mono \
  --query 'Stacks[0].Outputs[?OutputKey==`InstancePublicDNS`].OutputValue' \
  --output text)
```

3. Test the deployment:
```bash
# Create short URL
curl "http://$MONO_URL:5000/create/https://www.example.com"

# Use short URL
curl -L "http://$MONO_URL:5000/ABC123"
```

### IaaS (Microservices) Deployment

1. Deploy the stack:
```bash
cd iaas
aws cloudformation create-stack \
  --stack-name url-shortener-iaas \
  --template-body file://template.yaml \
  --parameters \
    ParameterKey=KeyName,ParameterValue=your-key-pair \
    ParameterKey=VpcId,ParameterValue=your-vpc-id \
    ParameterKey=SubnetId,ParameterValue=your-subnet1-id \
    ParameterKey=SubnetId2,ParameterValue=your-subnet2-id \
  --capabilities CAPABILITY_IAM
```

2. Get the endpoints:
```bash
export CREATOR_URL=$(aws cloudformation describe-stacks \
  --stack-name url-shortener-iaas \
  --query 'Stacks[0].Outputs[?OutputKey==`CreatorServiceURL`].OutputValue' \
  --output text)

export REDIRECTOR_URL=$(aws cloudformation describe-stacks \
  --stack-name url-shortener-iaas \
  --query 'Stacks[0].Outputs[?OutputKey==`RedirectorServiceURL`].OutputValue' \
  --output text)
```

3. Test the deployment:
```bash
# Create short URL
curl "$CREATOR_URL/create/https://www.example.com"

# Use short URL
curl -L "$REDIRECTOR_URL/ABC123"
```

### Serverless Deployment

1. Deploy the stack:
```bash
cd serverless
sam build
sam deploy --guided
```

2. Get the API endpoint:
```bash
export API_URL=$(aws cloudformation describe-stacks \
  --stack-name url-shortener-serverless \
  --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
  --output text)
```

3. Test the deployment:
```bash
# Create short URL
curl "$API_URL/create/https://www.example.com"

# Use short URL
curl -L "$API_URL/ABC123"
```

## Performance Testing

### Setup
```bash
# Set environment variables for endpoints
export MONO_URL=http://your-monolithic-endpoint:5000
export IAAS_CREATOR_URL=http://your-iaas-creator-endpoint
export IAAS_REDIRECTOR_URL=http://your-iaas-redirector-endpoint
export SERVERLESS_URL=https://your-api-gateway-url/prod
```

### Run Tests
```bash
cd tests
python performance_test.py
```

### Test Scenarios
```python
scenarios = [
    (100, 10),    # Light load
    (500, 50),    # Medium load
    (1000, 100)   # Heavy load
]
```

### Results
Results will be saved as:
- `performance_comparison_TIMESTAMP.png`  # Performance graphs
- `performance_stats_TIMESTAMP.csv`      # Detailed metrics

## Cleanup

```bash
# Remove Monolithic Stack
aws cloudformation delete-stack --stack-name url-shortener-mono

# Remove IaaS Stack
aws cloudformation delete-stack --stack-name url-shortener-iaas

# Remove Serverless Stack
aws cloudformation delete-stack --stack-name url-shortener-serverless
```

## Troubleshooting

### Connection Issues
```bash
# Check security groups
aws ec2 describe-security-groups --group-ids your-security-group-id

# Check instance status
aws ec2 describe-instance-status --instance-ids your-instance-id
```

### Performance Issues
```bash
# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=your-instance-id \
  --start-time $(date -u +%Y-%m-%dT%H:%M:%S -d '1 hour ago') \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average
```

## Security Considerations

1. API Security
   - Implement rate limiting
   - Add authentication if needed
   - Use HTTPS endpoints

2. Network Security
   - Configure security groups properly
   - Use private subnets where possible
   - Implement VPC endpoints

3. Access Control
   - Use IAM roles with least privilege
   - Regularly rotate credentials
   - Monitor AWS CloudTrail

## Monitoring

### Key Metrics
1. Performance Metrics
   - Response Time
   - Throughput
   - Error Rate
   - Success Rate

2. Resource Metrics
   - CPU Usage
   - Memory Usage
   - Network I/O
   - Disk Usage

3. Cost Metrics
   - Resource Utilization
   - Request Count
   - Data Transfer
