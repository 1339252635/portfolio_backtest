import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

print("Starting backend...")
print(f"Python: {sys.version}")
print(f"Working directory: {os.getcwd()}")

try:
    from app import create_app
    print("Importing create_app... success")
    
    app = create_app()
    print("Creating app... success")
    
    print("Starting Flask server on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
