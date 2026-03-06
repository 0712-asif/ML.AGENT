# 🧪 AutoML Platform Verification Script

def verify_setup():
    """Verify that the AutoML Platform is set up correctly."""
    print("🔍 Verifying AutoML Platform Setup...")
    
    import os
    import sys
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version OK")
    
    # Check required directories
    required_dirs = [
        "project",
        "project/dashboard",
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            return False
    
    # Check required files
    required_files = [
        "README.md",
        "requirements.txt", 
        "project/api_server.py",
        "project/dashboard/index.html",
        "project/dashboard/style.css",
        "project/dashboard/script.js",
        "start.sh",
        "start.bat",
        "Dockerfile",
        ".gitignore"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            return False
    
    # Check if we can import required packages
    try:
        import fastapi
        print(f"✅ FastAPI version: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not installed - run: pip install -r requirements.txt")
        return False
    
    try:
        import pandas
        print(f"✅ Pandas version: {pandas.__version__}")
    except ImportError:
        print("❌ Pandas not installed - run: pip install -r requirements.txt")
        return False
        
    try:
        import sklearn
        print(f"✅ Scikit-learn version: {sklearn.__version__}")
    except ImportError:
        print("❌ Scikit-learn not installed - run: pip install -r requirements.txt")
        return False
    
    # Create necessary directories if they don't exist
    os.makedirs("project/models", exist_ok=True)
    os.makedirs("project/datasets", exist_ok=True) 
    os.makedirs("project/logs", exist_ok=True)
    os.makedirs("project/runs", exist_ok=True)
    print("✅ Created necessary directories")
    
    print("\n🎉 Setup verification complete!")
    print("\n🚀 To start the platform:")
    print("   ./start.sh      (Linux/Mac)")
    print("   start.bat       (Windows)")  
    print("   OR")
    print("   cd project && uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload")
    print("\n📱 Dashboard: http://localhost:8000")
    print("📋 API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    verify_setup()