# K8s Cost Tool

Real-time Kubernetes cost visibility and optimization SaaS.

## Features

- **Cost by Namespace**: See exactly how much each namespace costs per month
- **Pod Count Tracking**: Monitor pod distribution across namespaces
- **Simple Dashboard**: Beautiful UI to visualize costs
- **RESTful API**: `/api/costs/by-namespace` endpoint

## Demo

Running live at: `http://your-codespaces-url/dashboard`

## API

- `GET /` - Health check
- `GET /api/costs/by-namespace` - Get costs per namespace
- `GET /dashboard` - View dashboard

## Getting Started

```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn kubernetes boto3
python main.py
```

Visit: `http://localhost:8000/dashboard`

## What's Next

- [ ] AWS billing API integration
- [ ] Helm chart for deployment
- [ ] Real K8s cluster integration
- [ ] User authentication