"""
Run full Gatekeeper system - API + Dashboard
"""

import subprocess
import time
import webbrowser
from pathlib import Path

print("=" * 80)
print("🚀 STARTING GATEKEEPER SYSTEM")
print("=" * 80)

# Create necessary directories
Path("temp").mkdir(exist_ok=True)
Path("data/documents").mkdir(parents=True, exist_ok=True)

print("\n📚 Step 1: Starting FastAPI backend...")
print("   Command: python -m uvicorn backend.api:app --reload --port 8000")

# Start FastAPI in background
api_process = subprocess.Popen(
    ["python", "-m", "uvicorn", "backend.api:app", "--reload", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for API to start
time.sleep(3)

print("✅ FastAPI backend started on http://localhost:8000")
print("   API docs: http://localhost:8000/docs")

print("\n📊 Step 2: Starting Streamlit dashboard...")
print("   Command: streamlit run frontend/dashboard.py")

# Start Streamlit
dashboard_process = subprocess.Popen(
    ["streamlit", "run", "frontend/dashboard.py", "--server.port=8501"]
)

time.sleep(3)

print("✅ Streamlit dashboard started on http://localhost:8501")

print("\n" + "=" * 80)
print("🎉 GATEKEEPER SYSTEM RUNNING")
print("=" * 80)

print("""
📌 AVAILABLE ENDPOINTS:

Backend (FastAPI):
  - Health: http://localhost:8000/health
  - API Docs: http://localhost:8000/docs
  - Query: POST /query
  - Analytics: GET /analytics
  - Documents: GET /documents

Frontend (Streamlit):
  - Dashboard: http://localhost:8501
  - Query Interface
  - Document Management
  - Cache Statistics
  - System Settings

🔄 Press Ctrl+C to stop all services
""")

try:
    # Keep running
    api_process.wait()
    dashboard_process.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Stopping Gatekeeper system...")
    api_process.terminate()
    dashboard_process.terminate()
    print("✅ System stopped")