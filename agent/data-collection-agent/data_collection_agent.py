"""
Data Collection Agent - Gathers data from multiple sources
"""
from crewai import Agent, Task
from langchain_community.chat_models import ChatOllama
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
import subprocess


# ============= DATA SOURCE TOOLS =============

class LogCollectionTool:
    """Collect logs from various sources"""

    def collect_docker_logs(self, container_name: str, since_minutes: int = 60) -> Dict:
        """Collect Docker container logs"""
        try:
            cmd = f"docker logs --since {since_minutes}m {container_name}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)

            return {
                "source": "docker",
                "container": container_name,
                "logs": result.stdout,
                "errors": result.stderr,
                "timestamp": datetime.now().isoformat(),
                "log_count": len(result.stdout.split('\n'))
            }
        except Exception as e:
            return {"error": str(e), "source": "docker"}

    def collect_system_logs(self, log_path: str = "/var/log/syslog") -> Dict:
        """Collect system logs"""
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()[-1000:]  # Last 1000 lines

            return {
                "source": "system",
                "path": log_path,
                "logs": ''.join(lines),
                "log_count": len(lines),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "system"}

    def collect_application_logs(self, app_log_dir: str = "/app/logs") -> List[Dict]:
        """Collect application logs from directory"""
        logs = []
        try:
            import os
            for filename in os.listdir(app_log_dir):
                if filename.endswith('.log'):
                    with open(os.path.join(app_log_dir, filename), 'r') as f:
                        content = f.read()
                    logs.append({
                        "source": "application",
                        "filename": filename,
                        "content": content,
                        "size": len(content),
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            logs.append({"error": str(e), "source": "application"})

        return logs

    def parse_json_logs(self, log_content: str) -> List[Dict]:
        """Parse JSON formatted logs"""
        parsed = []
        for line in log_content.split('\n'):
            try:
                if line.strip():
                    parsed.append(json.loads(line))
            except:
                continue
        return parsed


class MetricsCollectionTool:
    """Collect metrics from monitoring systems"""

    def collect_prometheus_metrics(self, prometheus_url: str, query: str) -> Dict:
        """Collect metrics from Prometheus"""
        try:
            response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={'query': query},
                timeout=10
            )
            return {
                "source": "prometheus",
                "query": query,
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "prometheus"}

    def collect_system_metrics(self) -> Dict:
        """Collect system metrics using psutil"""
        try:
            import psutil

            return {
                "source": "system_metrics",
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "per_cpu": psutil.cpu_percent(interval=1, percpu=True)
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "network": psutil.net_io_counters()._asdict(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "system_metrics"}

    def collect_docker_stats(self, container_name: str) -> Dict:
        """Collect Docker container stats"""
        try:
            cmd = f"docker stats {container_name} --no-stream --format json"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)

            stats = json.loads(result.stdout) if result.stdout else {}
            return {
                "source": "docker_stats",
                "container": container_name,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "docker_stats"}


class AlertCollectionTool:
    """Collect alerts from monitoring systems"""

    def collect_alertmanager_alerts(self, alertmanager_url: str) -> Dict:
        """Collect alerts from Alertmanager"""
        try:
            response = requests.get(
                f"{alertmanager_url}/api/v2/alerts",
                timeout=10
            )
            return {
                "source": "alertmanager",
                "alerts": response.json(),
                "alert_count": len(response.json()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "alertmanager"}

    def collect_email_alerts(self, imap_server: str, email: str, password: str) -> List[Dict]:
        """Collect alerts from email"""
        try:
            import imaplib
            import email as email_lib
            from email.header import decode_header

            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email, password)
            mail.select("inbox")

            # Search for recent alerts
            _, messages = mail.search(None, 'UNSEEN SUBJECT "ALERT"')

            alerts = []
            for num in messages[0].split()[-10:]:  # Last 10 alerts
                _, msg = mail.fetch(num, "(RFC822)")
                email_body = msg[0][1]
                email_message = email_lib.message_from_bytes(email_body)

                subject = decode_header(email_message["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                alerts.append({
                    "subject": subject,
                    "from": email_message.get("From"),
                    "date": email_message.get("Date"),
                    "body": email_message.get_payload()
                })

            mail.close()
            mail.logout()

            return {
                "source": "email_alerts",
                "alerts": alerts,
                "alert_count": len(alerts),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "email_alerts"}


class CloudProviderTool:
    """Collect data from cloud providers"""

    def collect_aws_cloudwatch_logs(self, log_group: str, region: str = 'us-east-1') -> Dict:
        """Collect logs from AWS CloudWatch"""
        try:
            import boto3

            client = boto3.client('logs', region_name=region)

            response = client.filter_log_events(
                logGroupName=log_group,
                startTime=int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
            )

            return {
                "source": "aws_cloudwatch",
                "log_group": log_group,
                "events": response['events'],
                "event_count": len(response['events']),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "aws_cloudwatch"}

    def collect_aws_metrics(self, namespace: str, metric_name: str) -> Dict:
        """Collect metrics from AWS CloudWatch"""
        try:
            import boto3

            cloudwatch = boto3.client('cloudwatch')

            response = cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                StartTime=datetime.now() - timedelta(hours=1),
                EndTime=datetime.now(),
                Period=300,
                Statistics=['Average', 'Maximum']
            )

            return {
                "source": "aws_metrics",
                "namespace": namespace,
                "metric": metric_name,
                "datapoints": response['Datapoints'],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "aws_metrics"}

    def collect_gcp_logs(self, project_id: str, filter_str: str) -> Dict:
        """Collect logs from GCP"""
        try:
            from google.cloud import logging

            client = logging.Client(project=project_id)

            entries = list(client.list_entries(filter_=filter_str, max_results=100))

            return {
                "source": "gcp_logs",
                "project": project_id,
                "entries": [entry.payload for entry in entries],
                "entry_count": len(entries),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "gcp_logs"}


class APMTool:
    """Collect data from APM (Application Performance Monitoring) tools"""

    def collect_datadog_metrics(self, api_key: str, app_key: str, query: str) -> Dict:
        """Collect metrics from Datadog"""
        try:
            from datadog import initialize, api

            options = {
                'api_key': api_key,
                'app_key': app_key
            }
            initialize(**options)

            end = int(datetime.now().timestamp())
            start = end - 3600

            result = api.Metric.query(start=start, end=end, query=query)

            return {
                "source": "datadog",
                "query": query,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "datadog"}

    def collect_newrelic_data(self, api_key: str, account_id: str, nrql_query: str) -> Dict:
        """Collect data from New Relic"""
        try:
            headers = {'Api-Key': api_key}
            url = f"https://insights-api.newrelic.com/v1/accounts/{account_id}/query"

            response = requests.get(
                url,
                headers=headers,
                params={'nrql': nrql_query},
                timeout=10
            )

            return {
                "source": "newrelic",
                "query": nrql_query,
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "newrelic"}


class DatabaseTool:
    """Collect data from databases"""

    def collect_postgres_slow_queries(self, connection_string: str) -> Dict:
        """Collect slow queries from PostgreSQL"""
        try:
            import psycopg2

            conn = psycopg2.connect(connection_string)
            cursor = conn.cursor()

            query = """
            SELECT query, calls, total_time, mean_time, rows
            FROM pg_stat_statements
            ORDER BY mean_time DESC
            LIMIT 50;
            """

            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            return {
                "source": "postgres_slow_queries",
                "queries": [
                    {
                        "query": r[0],
                        "calls": r[1],
                        "total_time": r[2],
                        "mean_time": r[3],
                        "rows": r[4]
                    }
                    for r in results
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "postgres_slow_queries"}

    def collect_mongodb_errors(self, connection_string: str) -> Dict:
        """Collect errors from MongoDB"""
        try:
            from pymongo import MongoClient

            client = MongoClient(connection_string)
            db = client.admin

            # Get server status
            status = db.command("serverStatus")

            return {
                "source": "mongodb_errors",
                "connections": status['connections'],
                "opcounters": status['opcounters'],
                "network": status['network'],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "source": "mongodb_errors"}


# ============= DATA LAKE STORAGE =============

class DataLake:
    """Store collected data in a structured data lake"""

    def __init__(self, storage_path: str = "/data/lake"):
        self.storage_path = storage_path
        self._ensure_structure()

    def _ensure_structure(self):
        """Create data lake directory structure"""
        import os
        folders = [
            'logs', 'metrics', 'alerts', 'traces',
            'cloud', 'apm', 'databases', 'raw'
        ]
        for folder in folders:
            os.makedirs(f"{self.storage_path}/{folder}", exist_ok=True)

    def store_data(self, data: Dict, category: str, incident_id: str) -> str:
        """Store data in appropriate category"""
        import os

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{incident_id}_{timestamp}_{data.get('source', 'unknown')}.json"
        filepath = os.path.join(self.storage_path, category, filename)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return filepath

    def get_incident_data(self, incident_id: str) -> Dict[str, List[Dict]]:
        """Retrieve all data for an incident"""
        import os

        incident_data = {
            'logs': [],
            'metrics': [],
            'alerts': [],
            'traces': [],
            'cloud': [],
            'apm': [],
            'databases': []
        }

        for category in incident_data.keys():
            category_path = os.path.join(self.storage_path, category)
            if os.path.exists(category_path):
                for filename in os.listdir(category_path):
                    if filename.startswith(incident_id):
                        with open(os.path.join(category_path, filename), 'r') as f:
                            incident_data[category].append(json.load(f))

        return incident_data

    def create_data_snapshot(self, incident_id: str) -> Dict:
        """Create a consolidated snapshot of all data"""
        all_data = self.get_incident_data(incident_id)

        snapshot = {
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "logs_count": len(all_data['logs']),
                "metrics_count": len(all_data['metrics']),
                "alerts_count": len(all_data['alerts']),
                "total_sources": sum(len(v) for v in all_data.values())
            },
            "data": all_data
        }

        return snapshot


# ============= DATA COLLECTION AGENT =============

def create_data_collection_agent(llm) -> Agent:
    """Create the Data Collection Agent"""

    agent = Agent(
        role="Data Collection Specialist",
        goal="""Gather comprehensive data from multiple sources for incident analysis.
        Collect logs, metrics, alerts, traces, and system information from all available sources.""",
        backstory="""You are an expert in data collection and aggregation.
        You know how to efficiently gather data from various sources including:
        - Docker containers and system logs
        - Prometheus, Grafana, and other monitoring tools
        - Cloud providers (AWS, GCP, Azure)
        - APM tools (Datadog, New Relic)
        - Databases and application logs
        - Alert systems and email notifications

        You organize collected data into a structured data lake for easy analysis.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return agent


def collect_incident_data(
    incident_id: str,
    sources: Dict[str, Any],
    data_lake: DataLake
) -> Dict[str, Any]:
    """
    Main function to collect data from all configured sources

    Args:
        incident_id: Unique incident identifier
        sources: Dictionary of configured data sources
        data_lake: DataLake instance for storage

    Returns:
        Dictionary containing all collected data
    """

    log_tool = LogCollectionTool()
    metrics_tool = MetricsCollectionTool()
    alert_tool = AlertCollectionTool()
    cloud_tool = CloudProviderTool()
    apm_tool = APMTool()
    db_tool = DatabaseTool()

    collected_data = {
        "incident_id": incident_id,
        "collection_timestamp": datetime.now().isoformat(),
        "sources_attempted": [],
        "sources_successful": [],
        "data_summary": {}
    }

    # Collect Docker logs
    if sources.get('docker_containers'):
        for container in sources['docker_containers']:
            collected_data["sources_attempted"].append(f"docker:{container}")
            data = log_tool.collect_docker_logs(container)
            if 'error' not in data:
                filepath = data_lake.store_data(data, 'logs', incident_id)
                collected_data["sources_successful"].append(f"docker:{container}")

    # Collect system metrics
    if sources.get('system_metrics'):
        collected_data["sources_attempted"].append("system_metrics")
        data = metrics_tool.collect_system_metrics()
        if 'error' not in data:
            filepath = data_lake.store_data(data, 'metrics', incident_id)
            collected_data["sources_successful"].append("system_metrics")

    # Collect Prometheus metrics
    if sources.get('prometheus'):
        for query in sources['prometheus'].get('queries', []):
            collected_data["sources_attempted"].append(f"prometheus:{query}")
            data = metrics_tool.collect_prometheus_metrics(
                sources['prometheus']['url'],
                query
            )
            if 'error' not in data:
                filepath = data_lake.store_data(data, 'metrics', incident_id)
                collected_data["sources_successful"].append(f"prometheus:{query}")

    # Collect alerts
    if sources.get('alertmanager'):
        collected_data["sources_attempted"].append("alertmanager")
        data = alert_tool.collect_alertmanager_alerts(sources['alertmanager']['url'])
        if 'error' not in data:
            filepath = data_lake.store_data(data, 'alerts', incident_id)
            collected_data["sources_successful"].append("alertmanager")

    # Collect AWS data
    if sources.get('aws'):
        if sources['aws'].get('cloudwatch_logs'):
            for log_group in sources['aws']['cloudwatch_logs']:
                collected_data["sources_attempted"].append(f"aws_logs:{log_group}")
                data = cloud_tool.collect_aws_cloudwatch_logs(log_group)
                if 'error' not in data:
                    filepath = data_lake.store_data(data, 'cloud', incident_id)
                    collected_data["sources_successful"].append(f"aws_logs:{log_group}")

    # Create final snapshot
    snapshot = data_lake.create_data_snapshot(incident_id)
    collected_data["data_summary"] = snapshot["summary"]
    collected_data["snapshot_path"] = data_lake.store_data(
        snapshot,
        'raw',
        f"{incident_id}_snapshot"
    )

    return collected_data