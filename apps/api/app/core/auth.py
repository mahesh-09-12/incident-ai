import os
from fastapi import Request, HTTPException
from clerk_backend_api import authenticate_request, AuthenticateRequestOptions
from app.core.config import settings

def get_current_user_id(request: Request) -> str:
    # Use Clerk's built-in authentication handler
    # Note: clerk-backend-api looks for the CLERK_SECRET_KEY env var by default if we don't pass it, 
    # but we can explicitly pass it using AuthenticateRequestOptions if we want to use the settings object
    try:
        request_state = authenticate_request(
            request,
            AuthenticateRequestOptions(
                secret_key=settings.CLERK_SECRET_KEY,
            )
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Catch clerk configuration errors or network errors during JWKS fetch
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {str(e)}")
    
    print(f"DEBUG: method={request.method}, url={request.url}, is_signed_in={request_state.is_signed_in}")
    if not request_state.is_signed_in:
        print(f"DEBUG: headers={request.headers}")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return request_state.payload.get("sub")
