"""
LangGraph Multi-Agent System for Incident Management
"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
import os
from datetime import datetime
from mcp_servers import (
    LogsMCPServer, MetricsMCPServer, KnowledgeBaseMCPServer,
    TicketingMCPServer, NotificationMCPServer
)

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


# ============= STATE DEFINITION =============

class AgentState(TypedDict):
    """State shared across all agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    incident_data: Dict[str, Any]
    incident_id: str

    # Agent outputs
    data_collection_result: Dict[str, Any]
    triage_result: Dict[str, Any]
    diagnosis_result: Dict[str, Any]
    remediation_result: Dict[str, Any]
    ticket_result: Dict[str, Any]
    report_result: Dict[str, Any]

    # Control flow
    next_agent: str
    is_complete: bool


# ============= AGENT NODES =============

def data_collection_agent(state: AgentState) -> AgentState:
    """Agent 1: Collect data from multiple sources"""
    print("🔍 Data Collection Agent: Starting data collection...")

    incident_data = state["incident_data"]
    incident_id = state["incident_id"]

    # Collect from MCP servers
    collected_data = {
        "logs": logs_server.parse_logs(incident_data.get("logs", "")),
        "metrics": metrics_server.get_metrics(incident_data.get("service")),
        "historical_metrics": metrics_server.get_historical_metrics(24),
        "similar_incidents": kb_server.search_similar(incident_data.get("description", "")),
        "timestamp": datetime.now().isoformat()
    }

    # If using real data collection
    try:
        from data_collection_agent import collect_incident_data, DataLake
        import json

        data_lake = DataLake(storage_path=os.getenv('DATA_LAKE_PATH', '/data/lake'))

        # Load data sources config
        with open('config/data_sources.json', 'r') as f:
            data_sources = json.load(f)

        real_data = collect_incident_data(incident_id, data_sources, data_lake)
        collected_data["real_data"] = real_data
        collected_data["data_lake_path"] = real_data.get("snapshot_path")
    except Exception as e:
        print(f"Real data collection skipped: {e}")
        collected_data["real_data"] = None

    state["data_collection_result"] = collected_data
    state["next_agent"] = "triage"

    message = AIMessage(
        content=f"✅ Data collected from {len(collected_data)} sources"
    )
    state["messages"].append(message)

    print(f"✅ Data Collection complete: {len(collected_data)} sources")
    return state


def triage_agent(state: AgentState) -> AgentState:
    """Agent 2: Classify incident severity"""
    print("🎯 Triage Agent: Classifying severity...")

    incident_data = state["incident_data"]
    collected_data = state["data_collection_result"]

    # Create triage prompt
    prompt = f"""
    Analyze this incident and classify its severity (Critical, High, Medium, Low):

    Incident: {incident_data.get('title', 'Unknown')}
    Description: {incident_data.get('description', 'N/A')}

    Data collected:
    - Error count: {collected_data['logs'].get('error_count', 0)}
    - CPU usage: {collected_data['metrics'].get('cpu_usage', 0):.1f}%
    - Memory usage: {collected_data['metrics'].get('memory_usage', 0):.1f}%
    - Error rate: {collected_data['metrics'].get('error_rate', 0):.1f}%

    Provide:
    1. Severity classification
    2. Reasoning (2-3 sentences)
    3. Priority score (1-10)

    Format: severity|reasoning|score
    """

    response = llm.invoke(prompt)
    result_text = response.content if hasattr(response, 'content') else str(response)

    # Parse response
    parts = result_text.split('|')
    if len(parts) >= 3:
        severity = parts[0].strip()
        reasoning = parts[1].strip()
        score = parts[2].strip()
    else:
        # Fallback parsing
        severity = "Medium"
        reasoning = result_text
        score = "5"

    triage_result = {
        "severity": severity,
        "reasoning": reasoning,
        "priority_score": score,
        "timestamp": datetime.now().isoformat()
    }

    state["triage_result"] = triage_result
    state["next_agent"] = "diagnosis"

    message = AIMessage(
        content=f"Severity: {severity} | Score: {score}"
    )
    state["messages"].append(message)

    print(f"✅ Triage complete: {severity} (score: {score})")
    return state


def diagnosis_agent(state: AgentState) -> AgentState:
    """Agent 3: Identify root cause"""
    print("🔬 Diagnosis Agent: Analyzing root cause...")

    incident_data = state["incident_data"]
    collected_data = state["data_collection_result"]
    triage_result = state["triage_result"]

    # Create diagnosis prompt
    prompt = f"""
    Identify the root cause of this {triage_result['severity']} severity incident:

    Incident: {incident_data.get('title')}
    Description: {incident_data.get('description')}

    Evidence:
    - Error patterns: {collected_data['logs'].get('error_patterns', [])}
    - CPU: {collected_data['metrics'].get('cpu_usage', 0):.1f}%
    - Memory: {collected_data['metrics'].get('memory_usage', 0):.1f}%
    - Network latency: {collected_data['metrics'].get('network_latency', 0):.1f}ms

    Similar past incidents:
    {collected_data.get('similar_incidents', [])}

    Provide:
    1. Root cause (concise)
    2. Supporting evidence (3 bullet points)
    3. Confidence level (Low/Medium/High)

    Format: root_cause|evidence1,evidence2,evidence3|confidence
    """

    response = llm.invoke(prompt)
    result_text = response.content if hasattr(response, 'content') else str(response)

    # Parse response
    parts = result_text.split('|')
    if len(parts) >= 3:
        root_cause = parts[0].strip()
        evidence = [e.strip() for e in parts[1].split(',')]
        confidence = parts[2].strip()
    else:
        root_cause = "Unable to determine root cause"
        evidence = ["Insufficient data"]
        confidence = "Low"

    diagnosis_result = {
        "root_cause": root_cause,
        "evidence": evidence,
        "confidence": confidence,
        "similar_incidents": [inc['incident_id'] for inc in collected_data.get('similar_incidents', [])][:3],
        "timestamp": datetime.now().isoformat()
    }

    state["diagnosis_result"] = diagnosis_result
    state["next_agent"] = "remediation"

    message = AIMessage(
        content=f"Root cause: {root_cause} (confidence: {confidence})"
    )
    state["messages"].append(message)

    print(f"✅ Diagnosis complete: {root_cause}")
    return state


def remediation_agent(state: AgentState) -> AgentState:
    """Agent 4: Suggest remediation steps"""
    print("🛠️ Remediation Agent: Generating solution...")

    diagnosis_result = state["diagnosis_result"]
    triage_result = state["triage_result"]

    # Get runbook if available
    root_cause_lower = diagnosis_result['root_cause'].lower()
    runbook_type = None
    if 'database' in root_cause_lower or 'connection' in root_cause_lower:
        runbook_type = 'database'
    elif 'cpu' in root_cause_lower or 'memory' in root_cause_lower:
        runbook_type = 'high_cpu'
    elif 'network' in root_cause_lower:
        runbook_type = 'network'

    runbook = kb_server.get_runbook(runbook_type) if runbook_type else {}

    # Create remediation prompt
    prompt = f"""
    Provide remediation steps for this incident:

    Root Cause: {diagnosis_result['root_cause']}
    Severity: {triage_result['severity']}
    Confidence: {diagnosis_result['confidence']}

    Runbook suggestions: {runbook.get('steps', [])}

    Provide:
    1. 5 specific remediation steps (numbered)
    2. Escalation path
    3. Estimated resolution time

    Be specific and actionable.
    """

    response = llm.invoke(prompt)
    result_text = response.content if hasattr(response, 'content') else str(response)

    # Extract steps (simple parsing)
    lines = result_text.split('\n')
    steps = [line.strip() for line in lines if line.strip() and any(line.startswith(str(i)) for i in range(1, 10))]

    if not steps:
        steps = runbook.get('steps', [
            "Investigate logs for detailed error messages",
            "Check system resource usage",
            "Review recent changes or deployments",
            "Apply relevant fixes based on findings",
            "Monitor system stability"
        ])

    remediation_result = {
        "steps": steps[:5],
        "escalation": runbook.get('escalation', f"Escalate to engineering team if not resolved in 30 minutes"),
        "eta": "15-30 minutes" if triage_result['severity'] in ['High', 'Critical'] else "1-2 hours",
        "runbook_used": runbook_type,
        "timestamp": datetime.now().isoformat()
    }

    state["remediation_result"] = remediation_result
    state["next_agent"] = "ticketing"

    message = AIMessage(
        content=f"Remediation plan created with {len(steps)} steps"
    )
    state["messages"].append(message)

    print(f"✅ Remediation complete: {len(steps)} steps")
    return state


def ticketing_agent(state: AgentState) -> AgentState:
    """Agent 5: Create incident ticket"""
    print("📋 Ticketing Agent: Creating ticket...")

    incident_data = state["incident_data"]
    triage_result = state["triage_result"]
    diagnosis_result = state["diagnosis_result"]
    remediation_result = state["remediation_result"]

    # Create ticket
    ticket_data = {
        "title": incident_data.get('title', 'Incident'),
        "severity": triage_result['severity'],
        "description": f"""
Root Cause: {diagnosis_result['root_cause']}

Evidence:
{chr(10).join('- ' + e for e in diagnosis_result['evidence'])}

Remediation Steps:
{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(remediation_result['steps']))}

Escalation: {remediation_result['escalation']}
ETA: {remediation_result['eta']}
        """.strip()
    }

    ticket = ticketing_server.create_ticket(ticket_data)

    state["ticket_result"] = ticket
    state["next_agent"] = "reporting"

    message = AIMessage(
        content=f"Ticket created: {ticket['id']}"
    )
    state["messages"].append(message)

    print(f"✅ Ticket created: {ticket['id']}")
    return state


def reporting_agent(state: AgentState) -> AgentState:
    """Agent 6: Generate final report"""
    print("📄 Reporting Agent: Generating report...")

    incident_id = state["incident_id"]
    incident_data = state["incident_data"]
    data_collection_result = state["data_collection_result"]
    triage_result = state["triage_result"]
    diagnosis_result = state["diagnosis_result"]
    remediation_result = state["remediation_result"]
    ticket_result = state["ticket_result"]

    report = {
        "incident_id": incident_id,
        "ticket_id": ticket_result['id'],
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "title": incident_data.get('title'),
            "severity": triage_result['severity'],
            "priority_score": triage_result['priority_score'],
            "root_cause": diagnosis_result['root_cause'],
            "confidence": diagnosis_result['confidence']
        },
        "data_collection": {
            "sources": len(data_collection_result),
            "timestamp": data_collection_result.get('timestamp')
        },
        "analysis": {
            "triage": triage_result,
            "diagnosis": diagnosis_result,
            "remediation": remediation_result
        },
        "ticket": ticket_result,
        "next_steps": remediation_result['steps']
    }

    state["report_result"] = report
    state["is_complete"] = True
    state["next_agent"] = "end"

    # Send notification for Critical/High severity
    if triage_result['severity'] in ['Critical', 'High']:
        notification_server.send_alert(
            triage_result['severity'],
            f"Incident {incident_id}: {diagnosis_result['root_cause']}"
        )

    message = AIMessage(
        content=f"Report generated for incident {incident_id}"
    )
    state["messages"].append(message)

    print(f"✅ Report complete for {incident_id}")
    return state


# ============= GRAPH CONSTRUCTION =============

def create_incident_workflow():
    """Create the LangGraph workflow"""

    # Define the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("data_collection", data_collection_agent)
    workflow.add_node("triage", triage_agent)
    workflow.add_node("diagnosis", diagnosis_agent)
    workflow.add_node("remediation", remediation_agent)
    workflow.add_node("ticketing", ticketing_agent)
    workflow.add_node("reporting", reporting_agent)

    # Define edges (sequential flow)
    workflow.add_edge("data_collection", "triage")
    workflow.add_edge("triage", "diagnosis")
    workflow.add_edge("diagnosis", "remediation")
    workflow.add_edge("remediation", "ticketing")
    workflow.add_edge("ticketing", "reporting")
    workflow.add_edge("reporting", END)

    # Set entry point
    workflow.set_entry_point("data_collection")

    # Compile the graph
    app = workflow.compile()

    return app


# ============= MAIN EXECUTION =============

def process_incident(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an incident through the multi-agent workflow

    Args:
        incident_data: Dictionary containing incident information

    Returns:
        Dictionary with complete analysis results
    """

    # Generate incident ID
    incident_id = incident_data.get(
        'incident_id',
        f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=f"Analyze incident: {incident_data.get('title')}")],
        "incident_data": incident_data,
        "incident_id": incident_id,
        "data_collection_result": {},
        "triage_result": {},
        "diagnosis_result": {},
        "remediation_result": {},
        "ticket_result": {},
        "report_result": {},
        "next_agent": "data_collection",
        "is_complete": False
    }

    # Create and run workflow
    print(f"\n🚀 Starting incident analysis for {incident_id}...")
    print("=" * 60)

    workflow = create_incident_workflow()
    final_state = workflow.invoke(initial_state)

    print("=" * 60)
    print(f"✅ Incident analysis complete!\n")

    # Return results
    return {
        "status": "completed",
        "incident_id": incident_id,
        "report": final_state["report_result"],
        "triage": final_state["triage_result"],
        "diagnosis": final_state["diagnosis_result"],
        "remediation": final_state["remediation_result"],
        "ticket": final_state["ticket_result"],
        "timestamp": datetime.now().isoformat()
    }