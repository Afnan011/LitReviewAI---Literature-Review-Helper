try:
    import fastapi
    import uvicorn
    print("Dependencies found")
except ImportError as e:
    print(f"Missing dependency: {e}")
