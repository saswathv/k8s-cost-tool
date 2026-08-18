# aws_billing.py
import boto3
from datetime import datetime, timedelta

def get_aws_costs_by_tag(tag_key="namespace"):
    """Get AWS costs grouped by namespace tag"""
    try:
        ce_client = boto3.client('ce', region_name='us-east-1')
        
        # Get costs for last 30 days
        end = datetime.now().date()
        start = end - timedelta(days=30)
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start.strftime('%Y-%m-%d'),
                'End': end.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'TAG', 'Key': tag_key}
            ]
        )
        
        # Parse costs
        costs_by_namespace = {}
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                namespace = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                costs_by_namespace[namespace] = cost
        
        return costs_by_namespace
    
    except Exception as e:
        print(f"Error fetching AWS costs: {e}")
        return {}