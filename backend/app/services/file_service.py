import io
import base64
import os
import uuid
from pypdf import PdfReader
from docx import Document

UPLOAD_DIR = "uploads"

def save_image(image_data: bytes, ext: str) -> str:
    """Save image bytes to disk and return the URL."""
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(image_data)
        
    # Assuming backend is on localhost:8000. In prod, use env var.
    return f"http://localhost:8000/uploads/{filename}"

async def process_file(file_content: bytes, filename: str) -> dict:
    filename_lower = filename.lower()
    result = {"text": "", "images": []}
    
    try:
        if filename_lower.endswith('.pdf'):
            reader = PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                # Extract text
                extracted = page.extract_text()
                if extracted:
                    result["text"] += extracted + "\n"
                
                # Extract images
                if page.images:
                    for image in page.images:
                        ext = image.name.split('.')[-1].lower()
                        # Normalize extension
                        if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                            ext = 'jpg'
                            
                        image_url = save_image(image.data, ext)
                        
                        result["images"].append({
                            "content": image_url,
                            "mime_type": f"image/{ext}",
                            "name": image.name
                        })

        elif filename_lower.endswith('.docx'):
            doc = Document(io.BytesIO(file_content))
            for para in doc.paragraphs:
                result["text"] += para.text + "\n"

        elif filename_lower.endswith('.txt'):
            result["text"] = file_content.decode('utf-8')

        elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            ext = filename_lower.split('.')[-1]
            image_url = save_image(file_content, ext)
            mime_type = f"image/{ext}"
            if ext == 'jpg': mime_type = "image/jpeg"
            
            result["images"].append({
                "content": image_url,
                "mime_type": mime_type,
                "name": filename
            })
        
        else:
            return {"error": "Unsupported file format."}

        return result

    except Exception as e:
        return {"error": f"Error processing file: {str(e)}"}
