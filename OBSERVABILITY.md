# Observability Setup for Text-to-Image Application

This document describes the comprehensive observability setup for the text-to-image application, including LangTrace, OpenTelemetry, Prometheus metrics, and structured logging.

## 🏗️ Observability Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   LangTrace     │    │   Monitoring    │
│   (FastAPI)     │───▶│   (AI/ML Trace) │───▶│   Stack         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenTelemetry │    │   Prometheus    │    │   Grafana       │
│   (Distributed  │    │   (Metrics)     │    │   (Dashboards)  │
│    Tracing)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Jaeger        │    │   AlertManager  │    │   Structured    │
│   (Trace UI)    │    │   (Alerts)      │    │   Logging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Components

### **1. LangTrace - AI/ML Observability**
- **Purpose**: Specialized tracing for AI/ML model interactions
- **Features**:
  - Model performance tracking
  - Prompt/response analysis
  - Cost tracking
  - Model comparison
  - Latency monitoring

### **2. OpenTelemetry - Distributed Tracing**
- **Purpose**: End-to-end request tracing
- **Features**:
  - Request flow visualization
  - Performance bottleneck identification
  - Error correlation
  - Service dependency mapping

### **3. Prometheus - Metrics Collection**
- **Purpose**: Time-series metrics storage
- **Features**:
  - Request rates and latencies
  - Error rates
  - Resource utilization
  - Custom business metrics

### **4. Structured Logging**
- **Purpose**: Machine-readable logs
- **Features**:
  - JSON-formatted logs
  - Request correlation
  - Structured error reporting
  - Performance logging

## 📊 Metrics Collected

### **HTTP Metrics**
```prometheus
# Request count by method, endpoint, and status
http_requests_total{method="POST", endpoint="/generate", status="200"}

# Request duration histogram
http_request_duration_seconds{method="POST", endpoint="/generate"}

# Active requests gauge
active_requests
```

### **Business Metrics**
```prometheus
# Image generation metrics
image_generation_total{status="success"}
image_generation_total{status="error"}

# Image generation duration
image_generation_duration_seconds
```

### **LangTrace Metrics**
- Model invocation count
- Model response time
- Token usage
- Cost per request
- Model accuracy metrics

## 🔍 Tracing

### **Request Flow**
```
Client Request
    ↓
FastAPI Middleware (Request ID generation)
    ↓
OpenTelemetry Span (generate_image)
    ↓
LangTrace Span (replicate_sdxl)
    ↓
Replicate API Call
    ↓
Response Processing
    ↓
Metrics Recording
```

### **Span Attributes**
- **Request ID**: Unique identifier for each request
- **Prompt**: Input text (truncated for privacy)
- **Model**: Model identifier
- **Duration**: Processing time
- **Status**: Success/error
- **Error details**: Exception information

## 📝 Logging

### **Log Format**
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "info",
  "logger": "app.main",
  "event": "Image generation started",
  "request_id": "1705312200.123",
  "prompt": "a beautiful sunset...",
  "duration": 2.5
}
```

### **Log Levels**
- **INFO**: Normal operations, request processing
- **WARNING**: Non-critical issues
- **ERROR**: Application errors, API failures
- **DEBUG**: Detailed debugging information

## 🚨 Alerting

### **Alert Rules**
1. **High Error Rate**: >10% 5xx errors for 2 minutes
2. **High Latency**: 95th percentile >10 seconds for 2 minutes
3. **Image Generation Failure**: >5% failure rate for 2 minutes

### **Alert Severity**
- **Warning**: Performance degradation
- **Critical**: Service unavailability

## 📈 Dashboards

### **Grafana Dashboard Panels**
1. **Request Rate**: Requests per second by endpoint
2. **Response Time**: 95th percentile latency
3. **Success Rate**: Image generation success/error rates
4. **Active Requests**: Current concurrent requests
5. **Model Performance**: LangTrace model metrics
6. **Error Analysis**: Error distribution and trends

## 🛠️ Setup Instructions

### **1. Environment Variables**
```bash
# Required
REPLICATE_API_TOKEN=your-replicate-token
LANGTRACE_API_KEY=your-langtrace-key

# Optional
OTLP_ENDPOINT=http://jaeger-collector:4317
LOG_LEVEL=INFO
```

### **2. Kubernetes Deployment**
```bash
# Apply monitoring stack
kubectl apply -f k8s/eks/monitoring.yaml

# Apply application with observability
kubectl apply -f k8s/eks/
```

### **3. Access Observability Tools**
```bash
# Prometheus metrics
curl http://your-app-url/metrics

# Health check
curl http://your-app-url/health

# Application info
curl http://your-app-url/info
```

## 🔍 Monitoring Commands

### **Check Application Health**
```bash
# Check pod status
kubectl get pods -n text-to-image

# Check logs
kubectl logs -f deployment/text-to-image -n text-to-image

# Check metrics endpoint
kubectl port-forward svc/text-to-image-service 8080:80 -n text-to-image
curl http://localhost:8080/metrics
```

### **Monitor LangTrace**
```bash
# Check LangTrace spans
# Access LangTrace dashboard at https://langtrace.ai
```

### **Monitor Prometheus**
```bash
# Check ServiceMonitor
kubectl get servicemonitor -n text-to-image

# Check PrometheusRule
kubectl get prometheusrule -n text-to-image
```

## 📊 Key Performance Indicators (KPIs)

### **Application KPIs**
- **Request Rate**: Requests per second
- **Response Time**: 95th percentile latency
- **Error Rate**: Percentage of failed requests
- **Availability**: Uptime percentage

### **Model KPIs**
- **Generation Success Rate**: Successful image generations
- **Model Latency**: Time to generate image
- **Cost per Request**: API cost tracking
- **Model Quality**: User satisfaction metrics

### **Business KPIs**
- **User Engagement**: Active users
- **Feature Usage**: Most popular prompts
- **Performance Trends**: Daily/weekly patterns
- **Resource Utilization**: CPU/Memory usage

## 🔧 Troubleshooting

### **Common Issues**

1. **LangTrace Not Working**
   ```bash
   # Check API key
   kubectl get secret text-to-image-secrets -n text-to-image -o yaml
   
   # Check logs for LangTrace errors
   kubectl logs deployment/text-to-image -n text-to-image | grep langtrace
   ```

2. **Metrics Not Available**
   ```bash
   # Check metrics endpoint
   curl http://your-app-url/metrics
   
   # Check ServiceMonitor
   kubectl describe servicemonitor text-to-image-monitor -n text-to-image
   ```

3. **High Latency**
   ```bash
   # Check model performance
   kubectl logs deployment/text-to-image -n text-to-image | grep "duration"
   
   # Check Replicate API status
   curl https://status.replicate.com/
   ```

### **Debug Commands**
```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n text-to-image

# Check resource usage
kubectl top pods -n text-to-image

# Check events
kubectl get events -n text-to-image --sort-by='.lastTimestamp'
```

## 🔮 Future Enhancements

### **Advanced Observability**
- **Custom Metrics**: Business-specific KPIs
- **Anomaly Detection**: ML-based alerting
- **Cost Optimization**: Resource usage analysis
- **Performance Profiling**: Detailed bottleneck analysis

### **Integration Options**
- **ELK Stack**: Centralized logging
- **Datadog**: APM and monitoring
- **New Relic**: Application performance monitoring
- **Sentry**: Error tracking and performance monitoring

## 📚 Resources

- [LangTrace Documentation](https://docs.langtrace.ai/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/) 