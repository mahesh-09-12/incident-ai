import urllib.request
from pathlib import Path
from fastapi import HTTPException
import cloudinary
import cloudinary.utils

from app.core.config import settings
from app.features.evidence.model import Evidence

def init_cloudinary():
    if settings.is_cloudinary_enabled:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

def get_evidence_content_bytes(evidence: Evidence) -> bytes:
    # Local fallback for existing evidence
    if evidence.storage_path:
        path = Path(evidence.storage_path)
        if path.exists():
            return path.read_bytes()
            
    # Cloudinary storage
    if not settings.is_cloudinary_enabled:
        raise HTTPException(status_code=500, detail="Cloudinary is not enabled but evidence has no local storage path")
        
    if not evidence.cloudinary_public_id:
        raise HTTPException(status_code=404, detail="Evidence content not found")
        
    # Generate signed URL
    url, _ = cloudinary.utils.cloudinary_url(
        evidence.cloudinary_public_id,
        resource_type=evidence.cloudinary_resource_type or "raw",
        type=evidence.cloudinary_delivery_type or "authenticated",
        sign_url=True
    )
    
    # Fetch content from Cloudinary
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch evidence from storage: {e}")

# Initialize Cloudinary configuration on module load
init_cloudinary()
