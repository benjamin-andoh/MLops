# Canary Deployment Guide

## Overview

Canary deployments allow you to safely test new model versions by routing a small percentage of traffic to the new model while keeping most traffic on the stable version. This enables you to monitor performance and catch issues before a full rollout.

## Setup

### 1. Deploy Canary Model

Deploy the canary model alongside your stable deployment:

```powershell
az ml online-deployment create --file canary-deployment.yml --resource-group mlops-rg --workspace-name mlops-scotia-ws2
```

### 2. Split Traffic

Route a small percentage of traffic to the canary (e.g., 80% stable, 20% canary):

```powershell
az ml online-endpoint update --name scotia-fraud-detection-endpoint --workspace-name mlops-scotia-ws2 --resource-group mlops-rg --traffic fraud-deployment=80 fraud-canary=20
```

## Monitoring

### Compare Metrics Between Deployments

**Application Insights KQL Query:**

```kql
requests
| where timestamp > ago(1h)
| summarize
    avg_duration=avg(duration),
    request_count=count(),
    error_rate=countif(resultCode >= 400) * 100.0 / count()
    by cloud_RoleName
| order by cloud_RoleName
```

**Azure ML Studio:**

- Navigate to Endpoints > scotia-fraud-detection-endpoint > Deployments
- Compare metrics for `fraud-deployment` vs `fraud-canary`
- Look at: latency (p50, p95, p99), error rate, throughput

### Key Metrics to Monitor

1. **Latency**: Should be similar between deployments
2. **Error Rate**: Should not increase in canary
3. **Prediction Distribution**: Check if predictions differ significantly
4. **Resource Utilization**: CPU, memory should be stable

## Promote Canary

If canary performs well after monitoring period (e.g., 24-48 hours), promote it:

```powershell
# Shift all traffic to canary
az ml online-endpoint update --name scotia-fraud-detection-endpoint --workspace-name mlops-scotia-ws2 --resource-group mlops-rg --traffic fraud-canary=100 fraud-deployment=0
```

## Rollback

If issues are detected in canary, immediately rollback:

```powershell
# Revert all traffic to stable deployment
az ml online-endpoint update --name scotia-fraud-detection-endpoint --workspace-name mlops-scotia-ws2 --resource-group mlops-rg --traffic fraud-deployment=100 fraud-canary=0
```

## Best Practices

1. **Start Small**: Begin with 5-10% traffic to canary
2. **Monitor Actively**: Check metrics every few hours during initial rollout
3. **Set Alerts**: Configure alerts for error rate spikes or latency increases
4. **Document Changes**: Keep track of what changed between versions
5. **Gradual Rollout**: Increase canary traffic in stages (10% → 25% → 50% → 100%)
6. **Keep Stable Deployment**: Don't delete old deployment until canary is fully validated

## Automated Canary Workflow

For automated canary deployments, see `.github/workflows/canary-rollout.yml` (if available) or integrate canary logic into your CI/CD pipeline.
