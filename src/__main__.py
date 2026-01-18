"""
Application entry point - Ensures correct environment variable loading

Run with: python -m src.main
or for development: python -m uvicorn src.main:app --reload
"""

# FIRST: Load environment variables
from src.env_loader import *  # noqa: F401, F403

import os
print("\n" + "="*80)
print("ENVIRONMENT VARIABLE CHECK")
print("="*80)
print(f"OPENAI_API_KEY loaded: {bool(os.environ.get('OPENAI_API_KEY'))}")
print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'development')}")
print("="*80 + "\n")

# Now import the application
if __name__ == "__main__":
    from src.main import app
    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
        reload=True
    )

