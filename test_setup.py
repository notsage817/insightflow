#!/usr/bin/env python3
"""
Test script to verify the application setup and basic functionality
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def test_backend_dependencies():
    """Test if backend dependencies can be imported"""
    print("Testing backend dependencies...")
    
    try:
        os.chdir('backend')
        
        # Test basic imports
        import fastapi
        import uvicorn
        import openai
        import anthropic
        import PyPDF2
        from dotenv import load_dotenv
        
        print("✅ All backend dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Backend dependency error: {e}")
        return False
    finally:
        os.chdir('..')

def test_frontend_dependencies():
    """Test if frontend dependencies are available"""
    print("Testing frontend dependencies...")
    
    try:
        os.chdir('frontend')
        
        # Check if node_modules exists or package.json is present
        if Path('package.json').exists():
            print("✅ Frontend package.json found")
            if Path('node_modules').exists():
                print("✅ Frontend node_modules found")
            else:
                print("⚠️  Frontend dependencies not installed. Run 'npm install' in frontend directory")
            return True
        else:
            print("❌ Frontend package.json not found")
            return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False
    finally:
        os.chdir('..')

def test_backend_startup():
    """Test if backend can start up"""
    print("Testing backend startup...")
    
    try:
        os.chdir('backend')
        
        # Start backend in background
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app', 
            '--host', '127.0.0.1', '--port', '5669'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for startup
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get('http://127.0.0.1:5669/health', timeout=10)
            if response.status_code == 200:
                print("✅ Backend started successfully")
                print(f"✅ Health check passed: {response.json()}")
                result = True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                result = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to backend: {e}")
            result = False
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
        
        return result
        
    except Exception as e:
        print(f"❌ Backend startup error: {e}")
        return False
    finally:
        os.chdir('..')

def main():
    """Run all tests"""
    print("🧪 Testing Semantix Chat Application Setup\n")
    
    tests = [
        ("Backend Dependencies", test_backend_dependencies),
        ("Frontend Dependencies", test_frontend_dependencies),
        ("Backend Startup", test_backend_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("1. Set your API keys in backend/.env")
        print("2. Run: docker-compose up --build")
        print("3. Access at: http://localhost:3000")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        
    return passed == len(results)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)