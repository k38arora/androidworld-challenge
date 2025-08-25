# AndroidWorld Challenge - Goal 3 Deployment Guide

## 🎯 **Goal 3: Scaling, Observability & Reliability**

This guide covers the implementation of production-grade deployment, scaling, and observability for the AndroidWorld challenge.

---

## 🚀 **Quick Start**

### **Prerequisites**

- Google Cloud Project with billing enabled
- Kubernetes cluster (GKE recommended)
- kubectl configured
- Docker installed
- k6 installed for load testing

### **1. Deploy to Kubernetes**

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n androidworld
kubectl get pods -n androidworld-staging
```

### **2. Run Load Tests**

```bash
# Make the load test script executable
chmod +x load-testing/run-load-test.sh

# Run load test against local service
./load-testing/run-load-test.sh

# Run load test against deployed service
./load-testing/run-load-test.sh http://your-service-ip:80
```

### **3. View Observability Data**

```bash
# Check logs
kubectl logs -n androidworld deployment/androidworld-worker

# Check metrics
kubectl port-forward service/androidworld-service 8080:80 -n androidworld
curl http://localhost:8080/metrics
```

---

## 🏗️ **Architecture Overview**

### **Components**

1. **Kubernetes Deployment**: Scalable worker pods with HPA
2. **Web Server**: Health checks, metrics, and task execution
3. **Observability**: Google Cloud Logging, Trace, and Monitoring
4. **CI/CD Pipeline**: GitHub Actions with automated testing
5. **Load Testing**: k6-based performance testing

### **Scaling Strategy**

- **Horizontal Pod Autoscaler**: Scales based on CPU (70%) and memory (80%)
- **Min Replicas**: 3 (production), 1 (staging)
- **Max Replicas**: 20 (production), 5 (staging)
- **Scale Up**: Aggressive (100% increase in 15s)
- **Scale Down**: Conservative (10% decrease in 60s)

---

## 📊 **Kubernetes Deployment**

### **Namespaces**

- `androidworld`: Production environment
- `androidworld-staging`: Staging environment

### **Resources**

```bash
# Create namespaces
kubectl apply -f k8s/namespace.yaml

# Apply configuration
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy applications
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

### **Configuration**

Update the following files with your project details:

1. **k8s/configmap.yaml**: Set your Google Cloud Project ID
2. **k8s/secret.yaml**: Add your Genymotion credentials
3. **k8s/deployment.yaml**: Update image repository if needed

### **Verification**

```bash
# Check all resources
kubectl get all -n androidworld
kubectl get all -n androidworld-staging

# Check HPA status
kubectl get hpa -n androidworld
kubectl get hpa -n androidworld-staging

# Check pod metrics
kubectl top pods -n androidworld
```

---

## 🔍 **Observability & Tracing**

### **Google Cloud Integration**

The system automatically integrates with:

- **Cloud Logging**: Structured logs with trace correlation
- **Cloud Trace**: Distributed tracing with OpenTelemetry
- **Cloud Monitoring**: Custom metrics for task performance

### **Custom Metrics**

- `androidworld_task_duration`: Task execution time
- `androidworld_task_success_rate`: Task success rate
- `androidworld_tasks_total`: Total tasks processed

### **Trace Correlation**

Each task execution generates:

1. **Trace ID**: Unique identifier for the request
2. **Span ID**: Individual operation identifier
3. **Correlation**: Links logs, metrics, and traces

### **Example Trace JSON**

```json
{
  "trace_id": "projects/your-project/traces/abc123",
  "span_id": "def456",
  "task_id": "task_001",
  "service_name": "androidworld-worker",
  "project_id": "your-project",
  "timestamp": "2024-01-15T10:30:00Z",
  "trace_url": "https://console.cloud.google.com/traces/traces?project=your-project&tid=abc123"
}
```

### **Viewing Traces**

1. **Google Cloud Console**: Navigate to Cloud Trace
2. **Trace URL**: Use the generated trace_url in responses
3. **Log Correlation**: Search logs by trace_id

---

## 🚀 **CI/CD Pipeline**

### **GitHub Actions Workflow**

The pipeline includes:

1. **Testing**: Unit tests and smoke tests
2. **Building**: Docker image with optimizations
3. **Deployment**: Staging and production environments
4. **Smoke Tests**: Post-deployment verification
5. **Notifications**: Slack integration

### **Required Secrets**

```bash
# GitHub repository secrets
GCP_PROJECT_ID=your-project-id
GCP_SA_KEY=your-service-account-key
SLACK_WEBHOOK_URL=your-slack-webhook
```

### **Manual Deployment**

```bash
# Deploy to staging
gh workflow run ci-cd.yml -f environment=staging

# Deploy to production
gh workflow run ci-cd.yml -f environment=production
```

### **Pipeline Stages**

1. **Test**: Run pytest with coverage
2. **Build**: Build and push Docker image
3. **Deploy Staging**: Apply to staging namespace
4. **Deploy Production**: Apply to production namespace
5. **Notify**: Send results to Slack

---

## 📈 **Load Testing**

### **k6 Configuration**

The load test simulates:

- **Ramp Up**: Gradual increase in concurrent users
- **Sustained Load**: Maintain peak load for analysis
- **Ramp Down**: Gradual decrease to zero

### **Test Stages**

```
0-2m:   Ramp up to 10 users
2-5m:   Stay at 10 users
5-8m:   Ramp up to 50 users
8-13m:  Stay at 50 users
13-16m: Ramp up to 100 users
16-21m: Stay at 100 users
21-23m: Ramp down to 0 users
```

### **Performance Thresholds**

- **Response Time**: 95% < 5s, 99% < 10s
- **Error Rate**: < 5%
- **Success Rate**: > 90%

### **Running Tests**

```bash
# Basic load test
./load-testing/run-load-test.sh

# Custom configuration
./load-testing/run-load-test.sh http://your-service:80 10m ./results

# View results
ls -la load-testing/results/
cat load-testing/results/load_test_*.md
```

### **Test Scenarios**

The load test covers:

1. **Health Checks**: `/health`, `/ready` endpoints
2. **Task Execution**: POST `/task` with various payloads
3. **Metrics Collection**: `/metrics`, `/status`, `/trace`
4. **Concurrent Requests**: Multiple simultaneous users
5. **Error Handling**: Invalid data and edge cases

---

## 📊 **Monitoring & Alerting**

### **Key Metrics**

Monitor these metrics in Google Cloud Monitoring:

1. **Task Performance**

   - Average execution time
   - Success rate
   - Error rate

2. **System Resources**

   - CPU utilization
   - Memory usage
   - Pod count

3. **API Performance**
   - Request latency
   - Throughput
   - Error rates

### **Recommended Alerts**

```yaml
# High error rate
- condition: task_success_rate < 0.90
  duration: 5m
  severity: warning

# High latency
- condition: task_duration > 5000ms
  duration: 2m
  severity: critical

# Resource exhaustion
- condition: cpu_utilization > 80%
  duration: 5m
  severity: warning
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Pods Not Starting**

```bash
# Check pod status
kubectl describe pod -n androidworld <pod-name>

# Check logs
kubectl logs -n androidworld <pod-name>

# Check events
kubectl get events -n androidworld --sort-by='.lastTimestamp'
```

#### **HPA Not Scaling**

```bash
# Check HPA status
kubectl describe hpa -n androidworld androidworld-hpa

# Check metrics server
kubectl get apiservice v1beta1.metrics.k8s.io

# Verify resource requests/limits
kubectl get deployment -n androidworld -o yaml
```

#### **Observability Not Working**

```bash
# Check service account permissions
kubectl get serviceaccount -n androidworld

# Verify environment variables
kubectl exec -n androidworld <pod-name> -- env | grep GOOGLE

# Check OpenTelemetry setup
kubectl logs -n androidworld <pod-name> | grep -i opentelemetry
```

### **Debug Commands**

```bash
# Port forward to access service
kubectl port-forward service/androidworld-service 8080:80 -n androidworld

# Test endpoints locally
curl http://localhost:8080/health
curl http://localhost:8080/metrics

# Check resource usage
kubectl top pods -n androidworld
kubectl describe hpa -n androidworld
```

---

## 📋 **Verification Checklist**

### **Deployment**

- [ ] Namespaces created successfully
- [ ] ConfigMaps and Secrets applied
- [ ] Deployments running with correct replicas
- [ ] Services accessible
- [ ] HPA configured and working

### **Observability**

- [ ] Logs flowing to Google Cloud Logging
- [ ] Traces visible in Cloud Trace
- [ ] Custom metrics in Cloud Monitoring
- [ ] Health endpoints responding
- [ ] Metrics endpoint accessible

### **CI/CD**

- [ ] GitHub Actions workflow configured
- [ ] Secrets properly set
- [ ] Tests passing
- [ ] Deployment successful
- [ ] Smoke tests passing

### **Load Testing**

- [ ] k6 installed and working
- [ ] Load test script executable
- [ ] Service accessible for testing
- [ ] Tests completing successfully
- [ ] Reports generated

---

## 🎉 **Success Criteria**

When all items in the verification checklist are complete, you have successfully implemented:

✅ **Autoscaling**: Kubernetes HPA with resource-based scaling  
✅ **CI/CD Pipeline**: Automated testing, building, and deployment  
✅ **Observability**: Comprehensive logging, tracing, and monitoring  
✅ **Load Testing**: Performance validation with k6  
✅ **Production Deployment**: Staging and production environments

**Your AndroidWorld challenge is now production-ready with enterprise-grade scaling, observability, and reliability!** 🚀✨

---

## 📚 **Additional Resources**

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Google Cloud Observability](https://cloud.google.com/observability)
- [k6 Load Testing Guide](https://k6.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
