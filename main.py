# main.py
from fastapi import FastAPI
from kubernetes import client, config
import os
from aws_billing import get_aws_costs_by_tag

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "K8s Cost Tool"}

@app.get("/api/costs/by-namespace")
def costs_by_namespace():
    """Get real K8s pods + calculate costs"""
    try:
        # Load K8s config (works in-cluster or with kubeconfig)
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces()
        
        # Count pods per namespace + calculate resource requests
        namespace_data = {}
        for pod in pods.items:
            ns = pod.metadata.namespace
            if ns not in namespace_data:
                namespace_data[ns] = {"pods": 0, "cpu": 0, "memory": 0}
            
            namespace_data[ns]["pods"] += 1
            
            # Sum CPU/Memory requests
            for container in pod.spec.containers:
                if container.resources.requests:
                    cpu_str = container.resources.requests.get('cpu', '0')
                    mem_str = container.resources.requests.get('memory', '0')
                    
                    # Parse CPU (e.g., "500m" = 0.5)
                    if cpu_str.endswith('m'):
                        namespace_data[ns]["cpu"] += int(cpu_str[:-1]) / 1000
                    else:
                        namespace_data[ns]["cpu"] += float(cpu_str or 0)
                    
                    # Parse Memory (e.g., "512Mi" = 512)
                    if mem_str.endswith('Mi'):
                        namespace_data[ns]["memory"] += int(mem_str[:-2])
                    elif mem_str.endswith('Gi'):
                        namespace_data[ns]["memory"] += int(mem_str[:-2]) * 1024
        
        # Calculate costs
        # Pricing: $0.05 per CPU per hour, $0.01 per GB per hour
        result = []
        for ns, data in namespace_data.items():
            cpu_cost = data["cpu"] * 0.05 * 730  # 730 hours per month
            mem_cost = (data["memory"] / 1024) * 0.01 * 730
            total = cpu_cost + mem_cost
            
            result.append({
                "namespace": ns,
                "pod_count": data["pods"],
                "cpu_cores": round(data["cpu"], 2),
                "memory_gb": round(data["memory"] / 1024, 2),
                "cpu_cost_monthly": round(cpu_cost, 2),
                "memory_cost_monthly": round(mem_cost, 2),
                "cost_per_month": round(total, 2)
            })
        
        return sorted(result, key=lambda x: x['cost_per_month'], reverse=True)
    
    except Exception as e:
        return {"error": str(e), "note": "Make sure you have K8s access or kubeconfig configured"}

@app.get("/dashboard")
async def dashboard():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard.html")

@app.get("/api/costs/aws")
def costs_from_aws():
    """Get real AWS billing costs by namespace"""
    return get_aws_costs_by_tag()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)