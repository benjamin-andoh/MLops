# Advanced Monitoring Guide

## Overview

This guide covers setting up comprehensive monitoring for your fraud detection ML endpoint using Application Insights and Azure ML. It includes custom metrics, alerting rules, KQL queries, and dashboard creation.

## Custom Metrics in Application Insights

### 1. View Standard Metrics

Navigate to Azure Portal > Application Insights > Metrics and view:

- **Request Rate**: Count of requests per minute
- **Response Time**: p50, p95, p99 latency
- **Failure Rate**: Percentage of failed requests
- **Availability**: Endpoint uptime percentage

### 2. Custom Log Queries

Your `score.py` already logs predictions. View them in **Logs**:

**All Predictions (last hour):**

```kql
traces
| where timestamp > ago(1h)
| where message contains "Prediction result"
| project timestamp, message, severityLevel
| order by timestamp desc
```

**Request/Response Correlation:**

```kql
requests
| where timestamp > ago(1h)
| join kind=inner (
    traces
    | where message contains "Prediction result"
) on operation_Id
| project timestamp, name, resultCode, duration, message
| order by timestamp desc
```

**Error Analysis:**

```kql
exceptions
| where timestamp > ago(24h)
| summarize error_count=count() by type, outerMessage
| order by error_count desc
```

**Latency Distribution:**

```kql
requests
| where timestamp > ago(1h)
| summarize
    p50=percentile(duration, 50),
    p95=percentile(duration, 95),
    p99=percentile(duration, 99),
    avg_duration=avg(duration),
    request_count=count()
| project p50, p95, p99, avg_duration, request_count
```

## Alert Configuration

### 1. Create Alert Rules in Azure Portal

Navigate to Application Insights > Alerts > + Create > Alert rule

### 2. Recommended Alerts

**High Error Rate Alert:**

- **Condition**:
  ```kql
  requests
  | where timestamp > ago(5m)
  | summarize error_rate = countif(resultCode >= 400) * 100.0 / count()
  | where error_rate > 5
  ```
- **Threshold**: Error rate > 5%
- **Evaluation frequency**: Every 5 minutes
- **Action**: Email, SMS, or webhook

**High Latency Alert:**

- **Condition**:
  ```kql
  requests
  | where timestamp > ago(5m)
  | summarize p95_latency = percentile(duration, 95)
  | where p95_latency > 2000
  ```
- **Threshold**: p95 latency > 2000ms
- **Evaluation frequency**: Every 5 minutes

**Endpoint Availability Alert:**

- **Condition**:
  ```kql
  requests
  | where timestamp > ago(5m)
  | summarize availability = countif(resultCode < 500) * 100.0 / count()
  | where availability < 99
  ```
- **Threshold**: Availability < 99%
- **Evaluation frequency**: Every 5 minutes

**Model Drift Alert (based on drift_monitor.py):**

- Run drift monitor on schedule
- Alert if any feature shows drift=true in report.json
- Can be integrated into GitHub Actions workflow

### 3. Create Alert Action Groups

1. Navigate to Monitor > Alerts > Action groups > + Create
2. Add actions:
   - Email/SMS: Send to ops team
   - Webhook: Trigger PagerDuty, Slack, or Teams
   - Azure Function: Custom response automation

## Dashboard Creation

### 1. Create Azure Dashboard

Navigate to Azure Portal > Dashboard > + New dashboard

**Add tiles:**

- Metrics chart: Request rate over time
- Metrics chart: p95 latency over time
- Metrics chart: Error rate percentage
- Log query: Recent errors (exceptions table)
- Log query: Top 10 slowest requests

### 2. Application Insights Dashboard

Navigate to Application Insights > Application Dashboard

This auto-generates:

- Server response time
- Server requests
- Failed requests
- Availability results

### 3. Custom Workbook (Recommended)

Navigate to Application Insights > Workbooks > + New

**Add sections:**

**Section 1: Overview**

```kql
requests
| where timestamp > ago(24h)
| summarize
    total_requests=count(),
    avg_duration=avg(duration),
    error_count=countif(resultCode >= 400)
| extend error_rate = error_count * 100.0 / total_requests
```

**Section 2: Latency Trends**

```kql
requests
| where timestamp > ago(24h)
| summarize
    p50=percentile(duration, 50),
    p95=percentile(duration, 95),
    p99=percentile(duration, 99)
    by bin(timestamp, 1h)
| render timechart
```

**Section 3: Error Breakdown**

```kql
exceptions
| where timestamp > ago(24h)
| summarize count() by type
| render piechart
```

**Section 4: Deployment Comparison (for canary)**

```kql
requests
| where timestamp > ago(1h)
| summarize
    avg_duration=avg(duration),
    request_count=count(),
    error_count=countif(resultCode >= 400)
    by cloud_RoleName
| extend error_rate = error_count * 100.0 / request_count
```

## Azure ML Monitoring

### 1. Model Data Collection

Enable data collection in your deployment:

```powershell
az ml online-deployment update --name fraud-deployment --endpoint-name scotia-fraud-detection-endpoint --workspace-name mlops-scotia-ws2 --resource-group mlops-rg --set data_collector.collections.model_inputs.enabled=true data_collector.collections.model_outputs.enabled=true
```

### 2. View Collected Data

Navigate to Azure ML Studio > Endpoints > scotia-fraud-detection-endpoint > Monitoring

View:

- Request/response logs
- Model input distribution
- Model output distribution
- Data drift metrics

### 3. Model Performance Monitoring

Track model metrics over time:

- Prediction distribution (is it shifting?)
- Feature distribution (data drift)
- Error patterns (which inputs cause failures?)

## Continuous Monitoring Checklist

Daily:

- [ ] Check endpoint availability (should be > 99%)
- [ ] Review error rate (should be < 1%)
- [ ] Check p95 latency (should be < 500ms)

Weekly:

- [ ] Run drift detection script (scripts/drift_monitor.py)
- [ ] Review model performance trends
- [ ] Check alert history and false positives

Monthly:

- [ ] Analyze long-term performance trends
- [ ] Review and update alert thresholds
- [ ] Update dashboards with new metrics

## PowerShell Commands for Quick Checks

**Get recent deployment logs:**

```powershell
az ml online-deployment get-logs --name fraud-deployment --endpoint-name scotia-fraud-detection-endpoint --workspace-name mlops-scotia-ws2 --resource-group mlops-rg --lines 200
```

**Get endpoint status:**

```powershell
az ml online-endpoint show --name scotia-fraud-detection-endpoint --workspace-name mlops-scotia-ws2 --resource-group mlops-rg
```

**Invoke endpoint for testing:**

```powershell
$endpoint = "https://scotia-fraud-detection-endpoint.eastus.inference.ml.azure.com/score"
$key = "<your_primary_key>"
Invoke-RestMethod -Uri $endpoint -Method Post -Headers @{ "Authorization" = "Bearer $key" } -ContentType "application/json" -Body (Get-Content -Raw test_data.json)
```

## Next Steps

1. Set up alerts for critical metrics
2. Create a custom workbook for your team
3. Schedule regular drift monitoring runs
4. Integrate monitoring with your incident response process
5. Document baseline performance metrics for comparison

## Resources

- [Application Insights Documentation](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure ML Monitoring](https://docs.microsoft.com/azure/machine-learning/how-to-monitor-online-endpoints)
- [KQL Quick Reference](https://docs.microsoft.com/azure/data-explorer/kusto/query/)
