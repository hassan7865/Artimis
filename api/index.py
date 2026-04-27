import os
import sys

# Add the src directory to the path so lead_engine can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from lead_engine.api.main import app

# Vercel needs the app object
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
