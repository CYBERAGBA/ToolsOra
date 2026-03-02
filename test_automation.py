#!/usr/bin/env python
"""
Test suite for the Automation module endpoints
Tests all CRUD operations and workflows
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/modules/automation"

def test_create_task():
    """Test: Create a scheduled task"""
    payload = {
        "task_type": "sync",
        "frequency": "weekly",
        "execution_time": "09:00",
        "description": "Weekly API sync process",
        "enabled": True
    }
    
    response = requests.post(f"{BASE_URL}/schedule-task", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    print("✓ test_create_task passed")
    return data.get('task_id')

def test_list_tasks():
    """Test: List all scheduled tasks"""
    response = requests.get(f"{BASE_URL}/tasks-list")
    assert response.status_code == 200
    data = response.json()
    assert 'tasks' in data
    print(f"✓ test_list_tasks passed - found {len(data['tasks'])} task(s)")
    return data['tasks']

def test_generate_report():
    """Test: Generate a report"""
    payload = {
        "report_type": "user_stats",
        "output_format": "excel",
        "recipients": "admin@example.com",
        "frequency": "once"
    }
    
    response = requests.post(f"{BASE_URL}/generate-report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    print("✓ test_generate_report passed")

def test_send_notification():
    """Test: Send notification email"""
    payload = {
        "notification_type": "newsletter",
        "subject": "Weekly Newsletter",
        "body": "This is our weekly update...",
        "recipients": "subscriber1@example.com,subscriber2@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/send-notification", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert data['sent_count'] >= 2
    print(f"✓ test_send_notification passed - sent to {data['sent_count']} recipient(s)")

def test_create_workflow():
    """Test: Create a workflow"""
    payload = {
        "workflow_name": "Auto-send invoice on new order",
        "trigger": "new_user",
        "action": "send_email",
        "details": "Send welcome email with invoice template",
        "enabled": True
    }
    
    response = requests.post(f"{BASE_URL}/create-workflow", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    print("✓ test_create_workflow passed")
    return data['workflow_id']

def test_get_logs():
    """Test: Retrieve execution logs"""
    response = requests.get(f"{BASE_URL}/logs")
    assert response.status_code == 200
    data = response.json()
    assert 'logs' in data
    print(f"✓ test_get_logs passed - found {len(data['logs'])} log(s)")
    for log in data['logs'][:3]:
        print(f"  - {log['task_name']}: {log['status']}")

def test_get_stats():
    """Test: Get monitoring statistics"""
    response = requests.get(f"{BASE_URL}/stats")
    assert response.status_code == 200
    data = response.json()
    assert 'total_tasks' in data
    assert 'total_workflows' in data
    print(f"✓ test_get_stats passed")
    print(f"  - Total tasks: {data['total_tasks']}")
    print(f"  - Total workflows: {data['total_workflows']}")
    print(f"  - Success (24h): {data['success_24h']}")

def test_automation_page():
    """Test: Load the Automation UI page"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Automatisation" in response.text or "Automation" in response.text
    print("✓ test_automation_page passed")

def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("🤖 AUTOMATION MODULE TEST SUITE")
    print("="*60 + "\n")
    
    try:
        # Page load
        test_automation_page()
        
        # Tasks
        task_id = test_create_task()
        test_list_tasks()
        
        # Reports
        test_generate_report()
        
        # Notifications
        test_send_notification()
        
        # Workflows
        workflow_id = test_create_workflow()
        
        # Monitoring
        test_get_logs()
        test_get_stats()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED (8/8)")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        return False
    except requests.exceptions.ConnectionError:
        print("\n✗ CONNECTION ERROR: Flask server is not running on localhost:5000\n")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        return False
    
    return True

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for Flask server to start...")
    for i in range(10):
        try:
            requests.get("http://localhost:5000/", timeout=1)
            print("Server is ready!\n")
            break
        except:
            time.sleep(1)
            if i == 9:
                print("Server did not start. Exiting.")
                exit(1)
    
    success = run_all_tests()
    exit(0 if success else 1)
