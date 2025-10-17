"""
Script de prueba rápida para verificar que la API funciona correctamente
"""

import requests
import sys

API_BASE = "http://localhost:8000"

def test_endpoint(name, method, url, data=None):
    """Prueba un endpoint y retorna el resultado"""
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{url}", timeout=5)
        elif method == "POST":
            response = requests.post(f"{API_BASE}{url}", json=data, timeout=5)
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {method:6} {url:40} → {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌ {method:6} {url:40} → Connection Error")
        return False
    except Exception as e:
        print(f"❌ {method:6} {url:40} → {str(e)[:30]}")
        return False

def main():
    print("\n" + "=" * 80)
    print("  🧪 CTM Investment Agent API - Quick Test")
    print("=" * 80 + "\n")
    
    tests = []
    
    # Test 1: Health Check
    print("📡 Testing System Endpoints...")
    tests.append(test_endpoint("Health Check", "GET", "/ok"))
    tests.append(test_endpoint("Server Info", "GET", "/info"))
    tests.append(test_endpoint("Root", "GET", "/"))
    
    # Test 2: Assistants
    print("\n🤖 Testing Assistant Endpoints...")
    tests.append(test_endpoint(
        "Create Assistant", 
        "POST", 
        "/assistants",
        {"graph_id": "agent", "name": "Test Assistant"}
    ))
    tests.append(test_endpoint(
        "Search Assistants",
        "POST",
        "/assistants/search",
        {"graph_id": "agent", "limit": 10}
    ))
    tests.append(test_endpoint("List Assistants", "GET", "/assistants"))
    
    # Test 3: Threads
    print("\n💬 Testing Thread Endpoints...")
    thread_response = requests.post(f"{API_BASE}/threads", json={})
    if thread_response.status_code == 200:
        thread_id = thread_response.json()["thread_id"]
        tests.append(True)
        print(f"✅ POST   /threads                                → 200 (ID: {thread_id[:8]}...)")
        
        tests.append(test_endpoint("Get Thread", "GET", f"/threads/{thread_id}"))
        tests.append(test_endpoint("Get Thread State", "GET", f"/threads/{thread_id}/state"))
        tests.append(test_endpoint("Get Messages", "GET", f"/threads/{thread_id}/messages"))
    else:
        tests.append(False)
        print(f"❌ POST   /threads                                → {thread_response.status_code}")
    
    # Test 4: Runs (si tenemos thread y assistant)
    print("\n🚀 Testing Run Endpoints...")
    assistant_response = requests.post(
        f"{API_BASE}/assistants",
        json={"graph_id": "agent", "name": "Test Run Assistant"}
    )
    
    if assistant_response.status_code == 200 and thread_response.status_code == 200:
        assistant_id = assistant_response.json()["assistant_id"]
        
        run_data = {
            "assistant_id": assistant_id,
            "input": {
                "project_title": "Test Project",
                "project_description": "Quick test of the agent",
                "messages": []
            }
        }
        
        tests.append(test_endpoint(
            "Create Run & Wait",
            "POST",
            f"/threads/{thread_id}/runs/wait",
            run_data
        ))
        tests.append(test_endpoint("List Runs", "GET", f"/threads/{thread_id}/runs"))
    else:
        print("⚠️  Skipping run tests (no thread or assistant available)")
    
    # Resumen
    print("\n" + "=" * 80)
    passed = sum(tests)
    total = len(tests)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"  📊 Results: {passed}/{total} tests passed ({percentage:.1f}%)")
    
    if percentage == 100:
        print("  🎉 All tests passed! API is working correctly.")
    elif percentage >= 70:
        print("  ⚠️  Most tests passed, but some endpoints may need attention.")
    else:
        print("  ❌ Many tests failed. Check if the server is running correctly.")
    
    print("=" * 80 + "\n")
    
    # Exit code
    sys.exit(0 if percentage == 100 else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted")
        sys.exit(1)
