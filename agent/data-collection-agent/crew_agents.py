"""
CrewAI Multi-Agent System for Incident Management
"""
from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOllama
from mcp_servers import (
    LogsMCPServer, MetricsMCPServer, KnowledgeBaseMCPServer,
    TicketingMCPServer, NotificationMCPServer
)
import os
from typing import Dict, Any
from datetime import datetime

# Initialize MCP Servers
logs_server = LogsMCPServer()
metrics_server = MetricsMCPServer()
kb_server = KnowledgeBaseMCPServer()
ticketing_server = TicketingMCPServer()
notification_server = NotificationMCPServer()

# Initialize LLM
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
    base_url=os.getenv("OLLAMA_URL", "http://ollama:11434")
)


# Define Custom Tools (wrapping MCP servers)
class LogAnalysisTool:
    def run(self, log_data: str) -> str:
        result = logs_server.parse_logs(log_data)
        return str(result)

class MetricsRetrievalTool:
    def run(self, service: str = None) -> str:
        result = metrics_server.get_metrics(service)
        return str(result)

class KnowledgeSearchTool:
    def run(self, query: str) -> str:
        result = kb_server.search_similar(query)
        return str(result)

class RunbookTool:
    def run(self, issue_type: str) -> str:
        result = kb_server.get_runbook(issue_type)
        return str(result)

class TicketCreationTool:
    def run(self, incident_data: str) -> str:
        import json
        data = json.loads(incident_data) if isinstance(incident_data, str) else incident_data
        result = ticketing_server.create_ticket(data)
        return str(result)

class NotificationTool:
    def run(self, severity: str, message: str) -> str:
        result = notification_server.send_alert(severity, message)
        return str(result)


# Create Agents
triage_agent = Agent(
    role="Incident Triage Specialist",
    goal="Analyze incoming incidents and classify severity based on logs and metrics",
    backstory="""You are an expert in incident triage with 10 years of experience.
    You quickly assess incident severity by analyzing logs, error patterns, and system metrics.
    You classify incidents as Critical, High, Medium, or Low based on impact and urgency.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

diagnosis_agent = Agent(
    role="Root Cause Analyst",
    goal="Identify the root cause of incidents by analyzing logs, metrics, and historical data",
    backstory="""You are a seasoned troubleshooting expert who excels at finding root causes.
    You use log analysis, metrics correlation, and knowledge base searches to pinpoint issues.
    You provide clear, actionable insights about what went wrong and why.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

remediation_agent = Agent(
    role="Remediation Expert",
    goal="Suggest actionable remediation steps and escalation paths",
    backstory="""You are a solutions architect specializing in incident resolution.
    You provide step-by-step remediation plans based on runbooks and past incidents.
    You know when to escalate and to whom, ensuring rapid resolution.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

report_agent = Agent(
    role="Incident Report Generator",
    goal="Create comprehensive incident reports for post-mortem analysis",
    backstory="""You are a technical writer specializing in incident documentation.
    You create clear, detailed reports that help teams learn from incidents.
    Your reports include timeline, impact, root cause, and lessons learned.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

ticketing_agent = Agent(
    role="Ticketing Automation Specialist",
    goal="Create and manage incident tickets in the ticketing system",
    backstory="""You are an automation expert who ensures all incidents are properly tracked.
    You create tickets with all relevant information and route them to the right teams.
    You update tickets as the incident progresses.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)


def create_incident_crew(incident_data: Dict[str, Any]) -> Crew:
    """Create a crew to handle the incident"""

    # Task 1: Triage
    triage_task = Task(
        description=f"""Analyze the following incident data and classify its severity:

        Incident Data: {incident_data}

        Analyze:
        1. Log patterns and error counts
        2. System metrics (CPU, memory, errors)
        3. Services affected
        4. Potential user impact

        Classify severity as: Critical, High, Medium, or Low
        Provide reasoning for the classification.""",
        agent=triage_agent,
        expected_output="Severity classification with detailed reasoning"
    )

    # Task 2: Diagnosis
    diagnosis_task = Task(
        description=f"""Based on the triage results, identify the root cause:

        Incident: {incident_data}

        Investigate:
        1. Search knowledge base for similar incidents
        2. Analyze error patterns and metrics
        3. Correlate timeline of events
        4. Identify probable root cause

        Provide a clear diagnosis with supporting evidence.""",
        agent=diagnosis_agent,
        expected_output="Root cause analysis with evidence",
        context=[triage_task]
    )

    # Task 3: Remediation
    remediation_task = Task(
        description=f"""Suggest remediation steps for the diagnosed issue:

        Based on the diagnosis, provide:
        1. Step-by-step remediation plan
        2. Relevant runbook procedures
        3. Escalation path if needed
        4. Estimated resolution time

        Make recommendations actionable and prioritized.""",
        agent=remediation_agent,
        expected_output="Detailed remediation plan with steps and escalation path",
        context=[diagnosis_task]
    )

    # Task 4: Ticketing
    ticketing_task = Task(
        description=f"""Create an incident ticket with all relevant information:

        Include:
        1. Incident title and description
        2. Severity classification
        3. Root cause summary
        4. Remediation steps
        5. Auto-assign to appropriate team

        Format the ticket data properly.""",
        agent=ticketing_agent,
        expected_output="Ticket creation confirmation with ticket ID",
        context=[triage_task, diagnosis_task, remediation_task]
    )

    # Task 5: Reporting
    report_task = Task(
        description=f"""Generate a comprehensive incident report:

        Create a report including:
        1. Executive summary
        2. Timeline of events
        3. Impact assessment
        4. Root cause analysis
        5. Remediation actions taken
        6. Lessons learned
        7. Prevention recommendations

        Format for easy reading and future reference.""",
        agent=report_agent,
        expected_output="Comprehensive incident report",
        context=[triage_task, diagnosis_task, remediation_task, ticketing_task]
    )

    # Create and return crew
    crew = Crew(
        agents=[triage_agent, diagnosis_agent, remediation_agent, ticketing_agent, report_agent],
        tasks=[triage_task, diagnosis_task, remediation_task, ticketing_task, report_task],
        process=Process.sequential,
        verbose=True
    )

    return crew


def process_incident(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to process an incident using the multi-agent system

    Workflow:
    1. Data Collection Agent gathers data from multiple sources
    2. Data stored in Data Lake
    3. Triage Agent classifies severity
    4. Diagnosis Agent analyzes root cause
    5. Remediation Agent suggests fixes
    6. Report & Ticketing Agents document everything
    """
    from data_collection_agent import (
        collect_incident_data,
        create_data_collection_agent,
        DataLake
    )
    import json
    import os

    incident_id = incident_data.get('incident_id', f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    # Initialize Data Lake
    data_lake = DataLake(storage_path=os.getenv('DATA_LAKE_PATH', '/data/lake'))

    # Load data source configuration
    with open('config/data_sources.json', 'r') as f:
        data_sources = json.load(f)

    # Step 1: Data Collection Agent - Gather data from all sources
    print(f"🔍 Data Collection Agent: Gathering data for {incident_id}...")

    collection_result = collect_incident_data(
        incident_id=incident_id,
        sources=data_sources,
        data_lake=data_lake
    )

    print(f"✅ Collected data from {len(collection_result['sources_successful'])} sources")
    print(f"📊 Data Summary: {collection_result['data_summary']}")

    # Step 2: Retrieve consolidated data from Data Lake
    lake_data = data_lake.get_incident_data(incident_id)

    # Enrich incident data with collected data
    incident_data.update({
        "incident_id": incident_id,
        "data_lake_snapshot": lake_data,
        "collection_summary": collection_result,
        "logs_collected": lake_data.get('logs', []),
        "metrics_collected": lake_data.get('metrics', []),
        "alerts_collected": lake_data.get('alerts', []),
        "cloud_data": lake_data.get('cloud', []),
        "apm_data": lake_data.get('apm', []),
        "database_data": lake_data.get('databases', [])
    })

    # Step 3: Create and run the analysis crew
    print(f"🤖 Starting Multi-Agent Analysis...")
    crew = create_incident_crew(incident_data)
    result = crew.kickoff()

    # Step 4: Send notification based on severity
    if "Critical" in str(result) or "High" in str(result):
        notification_server.send_alert(
            severity="Critical" if "Critical" in str(result) else "High",
            message=f"New incident processed: {incident_data.get('title', 'Unnamed Incident')}"
        )

    return {
        "status": "completed",
        "incident_id": incident_id,
        "data_collection": {
            "sources_attempted": len(collection_result['sources_attempted']),
            "sources_successful": len(collection_result['sources_successful']),
            "data_summary": collection_result['data_summary']
        },
        "analysis_result": result,
        "data_lake_path": collection_result.get('snapshot_path'),
        "timestamp": datetime.now().isoformat()
    }