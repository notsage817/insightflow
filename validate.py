#!/usr/bin/env python3
"""
Validation script for Semantix Chat project
"""

import os
import json
from pathlib import Path

def validate_backend():
    """Validate backend structure and files"""
    print("🔍 Validating backend...")
    
    backend_path = Path("backend")
    required_files = [
        "main.py",
        "requirements.txt",
        "Dockerfile",
        ".env.example",
        "config/settings.py",
        "models/chat.py",
        "services/conversation.py",
        "services/llm.py",
        "services/file_processor.py",
        "routers/chat.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (backend_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing backend files: {missing_files}")
        return False
    
    print("✅ Backend structure valid")
    return True

def validate_frontend():
    """Validate frontend structure and files"""
    print("🔍 Validating frontend...")
    
    frontend_path = Path("frontend")
    required_files = [
        "package.json",
        "Dockerfile",
        "nginx.conf",
        "public/index.html",
        "src/index.js",
        "src/App.js",
        "src/services/api.js",
        "src/styles/index.css"
    ]
    
    required_components = [
        "src/components/ChatArea.js",
        "src/components/ChatInput.js",
        "src/components/FileUploadModal.js",
        "src/components/Message.js",
        "src/components/ModelSelector.js",
        "src/components/Sidebar.js"
    ]
    
    missing_files = []
    for file_path in required_files + required_components:
        if not (frontend_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing frontend files: {missing_files}")
        return False
    
    # Validate package.json
    try:
        with open(frontend_path / "package.json") as f:
            package_data = json.load(f)
            
        required_deps = ["react", "react-dom", "axios", "react-markdown", "lucide-react"]
        missing_deps = []
        
        for dep in required_deps:
            if dep not in package_data.get("dependencies", {}):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing frontend dependencies: {missing_deps}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return False
    
    print("✅ Frontend structure valid")
    return True

def validate_docker():
    """Validate Docker configuration"""
    print("🔍 Validating Docker configuration...")
    
    required_files = [
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        ".dockerignore"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing Docker files: {missing_files}")
        return False
    
    print("✅ Docker configuration valid")
    return True

def validate_documentation():
    """Validate documentation and configuration"""
    print("🔍 Validating documentation...")
    
    required_files = [
        "README.md",
        "CLAUDE.md",
        ".gitignore"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing documentation files: {missing_files}")
        return False
    
    print("✅ Documentation valid")
    return True

def main():
    """Main validation function"""
    print("🧪 Validating Semantix Chat Project")
    print("=" * 50)
    
    validators = [
        ("Backend", validate_backend),
        ("Frontend", validate_frontend),
        ("Docker", validate_docker),
        ("Documentation", validate_documentation)
    ]
    
    results = []
    for name, validator in validators:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} validation failed: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nValidation Score: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 Project validation successful!")
        print("The project structure is complete and ready for deployment.")
        print("\nNext steps:")
        print("1. Set up your API keys in backend/.env")
        print("2. Run: ./start.sh or docker-compose up --build")
        print("3. Access the application at http://localhost:3000")
    else:
        print("\n⚠️  Validation failed. Please fix the issues above.")
    
    return passed == len(results)

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)