import os

def test_proxy_ts_exists_and_configured():
    # The tests run from apps/api
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web"))
    proxy_path = os.path.join(web_dir, "proxy.ts")
    assert os.path.exists(proxy_path), f"{proxy_path} must exist"
    
    with open(proxy_path, "r") as f:
        content = f.read()
        
    assert "'/__clerk/(.*)'" in content, "matcher must include /__clerk/(.*)"
    assert "'/dashboard(.*)'" in content, "must protect dashboard"
    assert "'/incidents(.*)'" in content, "must protect incidents"

def test_client_ts_auth_retrieval():
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web"))
    client_path = os.path.join(web_dir, "lib/api/client.ts")
    assert os.path.exists(client_path)
    
    with open(client_path, "r") as f:
        content = f.read()
        
    assert "window.Clerk" not in content, "must not use global window.Clerk"
    assert "setAuthTokenResolver" in content, "must provide mechanism to set auth token resolver"
    assert "getTokenResolver()" in content, "must call token resolver"
