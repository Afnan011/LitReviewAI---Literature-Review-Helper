try:
    from google.adk.runners import InMemoryRunner
    print("InMemoryRunner found in google.adk.runners")
except ImportError:
    print("InMemoryRunner NOT found")
