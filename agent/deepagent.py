"""
Complete Deep Agent Demo: SubAgents, ToolMiddleware, write_todos, interrupt_on
Uses Ollama + LangGraph checkpointer for state persistence
"""

import os
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent

app = FastAPI()

OLLAMA_HOST = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama2")

llm = ChatOllama(model=MODEL_NAME, base_url=OLLAMA_HOST, temperature=0)
checkpointer = MemorySaver()

# ============================================================================
# TOOLS
# ============================================================================

@tool
def search_db(query: str) -> str:
    """Search product database."""
    db = {"laptop": "Dell XPS - $1200", "phone": "iPhone 15 - $999"}
    return db.get(query.lower(), "Product not found")

@tool
def check_inventory(product: str) -> str:
    """Check product inventory."""
    inventory = {"laptop": 15, "phone": 32}
    return f"{product}: {inventory.get(product, 0)} units"

@tool
def get_pricing_info(product: str) -> str:
    """Get detailed pricing."""
    pricing = {"laptop": {"base": 1200, "discount": 10}, "phone": {"base": 999, "discount": 5}}
    info = pricing.get(product.lower(), {})
    return f"Pricing for {product}: {info}"

@tool
def approve_decision(decision: str, details: str) -> str:
    """Requires human approval before execution."""
    return f"[APPROVAL NEEDED] Decision: {decision}. Details: {details}"

# ============================================================================
# AGENT CONFIG
# ============================================================================

def get_main_agent(thread_id: str):
    """Create main agent with subagents."""

    search_subagent = {
        "name": "product-searcher",
        "description": "Search and find products in database",
        "system_prompt": "You are a product search specialist. Use search_db and check_inventory tools.",
        "tools": [search_db, check_inventory],
    }

    pricing_subagent = {
        "name": "pricing-analyst",
        "description": "Analyze pricing and discounts",
        "system_prompt": "You are a pricing analyst. Use get_pricing_info tool to provide detailed pricing.",
        "tools": [get_pricing_info],
    }

    agent = create_deep_agent(
        model=llm,
        tools=[approve_decision],
        system_prompt="You coordinate product inquiries. Use subagents for searches and pricing. Write todos for complex tasks.",
        subagents=[search_subagent, pricing_subagent],
        checkpointer=checkpointer,
        interrupt_on={
            "approve_decision": {
                "allowed_decisions": ["approve", "edit", "reject"]
            }
        },
    )

    return agent

# ============================================================================
# MODELS
# ============================================================================

class TaskRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None

class TaskResponse(BaseModel):
    response: str
    thread_id: str
    status: str

class InterruptResponse(BaseModel):
    pending_action: str
    thread_id: str
    options: list[str]

class InterruptResolution(BaseModel):
    thread_id: str
    decision: str
    feedback: Optional[str] = None

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/task", response_model=TaskResponse)
def execute_task(request: TaskRequest):
    """Execute task with main agent + subagents."""
    try:
        thread_id = request.thread_id or str(uuid.uuid4())
        agent = get_main_agent(thread_id)

        result = agent.invoke(
            {"messages": [{"role": "user", "content": request.query}]},
            config={"configurable": {"thread_id": thread_id}},
        )

        response = result["messages"][-1]["content"] if result.get("messages") else "No response"
        todos = result.get("todos", [])

        return TaskResponse(
            response=f"{response}\n\n**TODOs:** {todos}",
            thread_id=thread_id,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/task/stream")
def stream_task(request: TaskRequest):
    """Stream task execution with real-time updates."""
    thread_id = request.thread_id or str(uuid.uuid4())
    agent = get_main_agent(thread_id)

    def generate():
        try:
            for event in agent.stream(
                {"messages": [{"role": "user", "content": request.query}]},
                config={"configurable": {"thread_id": thread_id}},
            ):
                if "messages" in event:
                    msg = event["messages"][-1]
                    content = msg.get("content", "")
                    if content:
                        yield f"data: {{'content': '{content}', 'thread_id': '{thread_id}'}}\n\n"
        except Exception as e:
            yield f"data: {{'error': '{str(e)}'}}\n\n"

    return generate()

@app.get("/task/{thread_id}/interrupt")
def check_interrupt(thread_id: str):
    """Check if task has pending interruptions."""
    try:
        agent = get_main_agent(thread_id)
        state = checkpointer.get_tuple(thread_id)

        if state and state.pending_writes:
            return InterruptResponse(
                pending_action="approval_required",
                thread_id=thread_id,
                options=["approve", "edit", "reject"]
            )

        return {"status": "no_interruption"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/task/{thread_id}/resume")
def resume_with_input(thread_id: str, resolution: InterruptResolution):
    """Resume interrupted task with user decision."""
    try:
        agent = get_main_agent(thread_id)

        result = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": f"User decision: {resolution.decision}. Feedback: {resolution.feedback}"}
                ]
            },
            config={"configurable": {"thread_id": thread_id}},
        )

        response = result["messages"][-1]["content"] if result.get("messages") else "Task resumed"

        return TaskResponse(
            response=response,
            thread_id=thread_id,
            status="resumed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "features": ["subagents", "write_todos", "interrupt_on", "tools_middleware"]
    }