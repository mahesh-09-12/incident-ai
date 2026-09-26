import time
import requests

API_URL = "http://localhost:8000/api/v1"

def run_api_smoke_test():
    print("[TEST] Fetching incidents...")
    r = requests.get(f"{API_URL}/incidents")
    if r.status_code != 200:
        print(f"[TEST] Failed to fetch incidents: {r.text}")
        return
        
    incidents = r.json()
    target_incident = None
    
    # Find an incident with evidence
    for inc in incidents:
        inc_id = inc["id"]
        ev_req = requests.get(f"{API_URL}/incidents/{inc_id}/evidence")
        if ev_req.status_code == 200:
            evidences = ev_req.json()
            if len(evidences) > 0:
                target_incident = inc
                break
                
    if not target_incident:
        print("[TEST] Could not find any incident with evidence.")
        return
        
    print(f"[TEST] Selected Incident: {target_incident['id']} ({target_incident['title']})")
    
    # Start investigation
    print("[TEST] Starting investigation via API...")
    start_time = time.time()
    
    inv_req = requests.post(f"{API_URL}/incidents/{target_incident['id']}/investigations")
    if inv_req.status_code not in (200, 201):
        print(f"[TEST] Failed to start investigation: {inv_req.text}")
        return
        
    investigation = inv_req.json()
    inv_id = investigation["id"]
    print(f"[TEST] Investigation ID: {inv_id}")
    print(f"[TEST] Initial Status: {investigation['status']}")
    
    # Poll for completion
    while True:
        time.sleep(5)
        poll_req = requests.get(f"{API_URL}/incidents/{target_incident['id']}/investigations/{inv_id}")
        if poll_req.status_code != 200:
            print(f"[TEST] Failed to poll investigation: {poll_req.text}")
            return
            
        inv_status = poll_req.json()
        status = inv_status["status"]
        
        elapsed = time.time() - start_time
        print(f"[TEST] Elapsed: {elapsed:.0f}s - Status: {status}")
        
        if status in ("COMPLETED", "FAILED"):
            print(f"\n[TEST] Final Status: {status}")
            print(f"[TEST] Total Execution Time: {elapsed:.2f} seconds")
            
            if status == "COMPLETED":
                print("\n=== Investigation Result ===")
                print(f"Summary: {inv_status.get('summary')}")
                print(f"Root Cause: {inv_status.get('root_cause')}")
                print(f"Recommendations: {inv_status.get('recommendations')}")
                print(f"Hypotheses Count: len({inv_status.get('hypotheses', [])})")
            
            break

if __name__ == "__main__":
    run_api_smoke_test()
