# main.py
from fastapi import FastAPI
from kubernetes import client, config

app = FastAPI()

@app.get("/dashboard")
async def dashboard():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard.html")

@app.get("/")
def read_root():
    return {"message": "K8s Cost Tool - MVP"}

@app.get("/api/costs/by-namespace")
def costs_by_namespace():
    """Get namespaces + pod count (mock data for MVP)"""
    namespace_pods = {}
    
    try:
        # Try to load K8s config
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        # Connect to real K8s cluster
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces()
        
        # Count pods per namespace
        for pod in pods.items:
            ns = pod.metadata.namespace
            namespace_pods[ns] = namespace_pods.get(ns, 0) + 1
            
    except:
        # Fallback to mock data (when no K8s cluster available)
        namespace_pods = {
            "default": 5,
            "kube-system": 8,
            "monitoring": 3,
            "app-team": 12
        }
    
    # Cost calculation: $0.10 per pod per day
    result = []
    for ns, count in namespace_pods.items():
        cost = count * 0.10 * 30  # Monthly estimate
        result.append({
            "namespace": ns,
            "pod_count": count,
            "cost_per_month": round(cost, 2)
        })
    
    return sorted(result, key=lambda x: x['cost_per_month'], reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)