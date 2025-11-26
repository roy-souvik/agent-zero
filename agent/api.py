from fastapi import FastAPI, Query, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from rag_pipeline import (
    query_rag, add_document, semantic_search,
    get_traces_api, get_stats_api, export_traces_api
)

app = FastAPI()

# ==================== RAG Endpoints ====================

@app.post("/chat")
async def chat(question: str):
    """Chat endpoint with automatic tracing"""
    response = query_rag(question)
    return {"response": response}


@app.post("/add-document")
async def add_doc(text: str):
    """Add document endpoint with automatic tracing"""
    result = add_document(text)
    return result


@app.get("/search")
async def search(query: str, k: int = 3):
    """Search endpoint with automatic tracing"""
    results = semantic_search(query, k=k)
    return {"results": [r.page_content for r in results]}


class Doc(BaseModel):
    text: str

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

@app.post("/add")
async def add_doc(request: Request):
    try:
        data = await request.json()
        text = data.get("text")
        if not text:
            return {"error": "Missing 'text' field"}
        return add_document(text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/query")
async def query_doc(request: Request):
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            return {"error": "Missing 'question' field"}
        return {"answer": query_rag(question)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/respond")
def respond(data: Query):
    return {"response": f"Echo: {data.text}"}

# ==================== Observability Endpoints ====================

@app.get("/traces")
async def get_traces(operation: str = None, limit: int = 100):
    """Get traces in JSON format"""
    return JSONResponse(get_traces_api(operation=operation, limit=limit))


@app.get("/stats")
async def get_stats():
    """Get tracing statistics"""
    return JSONResponse(get_stats_api())


@app.post("/export-traces")
async def export_traces(filepath: str = "traces.json"):
    """Export traces to JSON file"""
    return export_traces_api(filepath)


# ==================== Tracing Dashboard HTML ====================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Simple dashboard to view traces"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tracing Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #e2e8f0; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            h1 { color: #38bdf8; margin-bottom: 30px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; }
            .card h3 { color: #38bdf8; margin-bottom: 10px; font-size: 14px; }
            .card .value { font-size: 28px; font-weight: bold; color: #10b981; }
            .card .unit { font-size: 12px; color: #94a3b8; }
            .table-container { background: #1e293b; border: 1px solid #334155; border-radius: 8px; overflow: auto; }
            table { width: 100%; border-collapse: collapse; }
            th { background: #0f172a; color: #38bdf8; text-align: left; padding: 12px; border-bottom: 1px solid #334155; font-size: 12px; }
            td { padding: 12px; border-bottom: 1px solid #334155; font-size: 13px; }
            tr:hover { background: #0f172a; }
            .success { color: #10b981; }
            .error { color: #ef4444; }
            .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
            .tab { padding: 8px 16px; background: #334155; border: none; color: #e2e8f0; cursor: pointer; border-radius: 4px; }
            .tab.active { background: #38bdf8; color: #0f172a; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            button { background: #38bdf8; color: #0f172a; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #0ea5e9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Tracing & Observability Dashboard</h1>

            <div class="tabs">
                <button class="tab active" onclick="switchTab('stats')">Statistics</button>
                <button class="tab" onclick="switchTab('traces')">Traces</button>
                <button class="tab" onclick="switchTab('export')">Export</button>
            </div>

            <!-- Stats Tab -->
            <div id="stats" class="tab-content active">
                <div class="grid" id="statsGrid">
                    <div class="card"><p>Loading...</p></div>
                </div>
            </div>

        <!-- Traces Tab -->
            <div id="traces" class="tab-content">
                <input type="text" id="operationFilter" placeholder="Filter by operation..." style="padding: 8px; margin-bottom: 15px; width: 100%; background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 4px;">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Operation</th>
                                <th>Duration (ms)</th>
                                <th>Status</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody id="tracesTable">
                            <tr><td colspan="5">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Export Tab -->
            <div id="export" class="tab-content">
                <div class="card">
                    <h3>Export Traces</h3>
                    <p style="margin-bottom: 15px;">Download all traces as JSON for analysis</p>
                    <button onclick="exportTraces()">📥 Export as JSON</button>
                </div>
            </div>
        </div>

        <script>
            function switchTab(tabName) {
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');

                if (tabName === 'stats') loadStats();
                if (tabName === 'traces') loadTraces();
            }

            async function loadStats() {
                const res = await fetch('/stats');
                const data = await res.json();

                let html = '';
                for (const [op, stats] of Object.entries(data)) {
                    html += `
                        <div class="card">
                            <h3>${op}</h3>
                            <p>Calls: <span class="value">${stats.count}</span></p>
                            <p>Avg Duration: <span class="value">${stats.avg_duration?.toFixed(2)}</span><span class="unit">ms</span></p>
                            <p>Errors: <span class="value" style="color: ${stats.errors > 0 ? '#ef4444' : '#10b981'}">${stats.errors}</span></p>
                        </div>
                    `;
                }
                document.getElementById('statsGrid').innerHTML = html || '<p>No data yet</p>';
            }

            async function loadTraces() {
                const operation = document.getElementById('operationFilter').value;
                const url = operation ? `/traces?operation=${operation}` : '/traces';
                const res = await fetch(url);
                const traces = await res.json();

                let html = '';
                traces.forEach(trace => {
                    html += `
                        <tr>
                            <td>${new Date(trace.timestamp).toLocaleTimeString()}</td>
                            <td>${trace.operation}</td>
                            <td>${trace.duration_ms.toFixed(2)}</td>
                            <td><span class="${trace.status === 'success' ? 'success' : 'error'}">${trace.status}</span></td>
                            <td>${trace.error ? trace.error : 'OK'}</td>
                        </tr>
                    `;
                });
                document.getElementById('tracesTable').innerHTML = html || '<tr><td colspan="5">No traces</td></tr>';
            }

            async function exportTraces() {
                const res = await fetch('/traces');
                const traces = await res.json();
                const blob = new Blob([JSON.stringify(traces, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `traces-${new Date().toISOString()}.json`;
                a.click();
            }

            // Auto-refresh stats every 2 seconds
            setInterval(() => {
                if (document.querySelector('.tab.active').textContent.includes('Statistics')) {
                    loadStats();
                }
            }, 2000);

            // Load initial data
            loadStats();
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)