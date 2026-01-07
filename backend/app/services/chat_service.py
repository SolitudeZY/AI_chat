from openai import AsyncOpenAI
from app.core.config import settings
import json
import os
import base64

class ChatService:
    def __init__(self):
        self.clients = {}
        
        if settings.QWEN_API_KEY:
            self.clients['qwen'] = AsyncOpenAI(
                api_key=settings.QWEN_API_KEY,
                base_url=settings.QWEN_BASE_URL
            )
        
        if settings.DEEPSEEK_API_KEY:
            self.clients['deepseek'] = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )

    def get_client(self, model_name: str):
        if 'qwen' in model_name.lower():
            return self.clients.get('qwen')
        elif 'deepseek' in model_name.lower():
            return self.clients.get('deepseek')
        # Default to qwen if available, else deepseek
        if self.clients.get('qwen'):
            return self.clients['qwen']
        return self.clients.get('deepseek')

    def _process_messages_for_api(self, messages):
        """
        Intercepts messages containing local localhost URLs and converts them to Base64 
        so the LLM can read them.
        """
        processed_messages = []
        for msg in messages:
            if isinstance(msg.get('content'), list):
                new_content = []
                for item in msg['content']:
                    if item.get('type') == 'image_url':
                        url = item['image_url']['url']
                        # Check if it is a local URL
                        if "localhost" in url and "/uploads/" in url:
                            try:
                                # Extract filename
                                filename = url.split("/uploads/")[-1]
                                # Assuming uploads directory is in the current working directory
                                filepath = os.path.join("uploads", filename)
                                
                                if os.path.exists(filepath):
                                    with open(filepath, "rb") as image_file:
                                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                                        # Guess mime type
                                        ext = filename.split('.')[-1].lower()
                                        mime_type = "image/jpeg"
                                        if ext == 'png': mime_type = "image/png"
                                        elif ext == 'webp': mime_type = "image/webp"
                                        elif ext == 'gif': mime_type = "image/gif"
                                        
                                        new_content.append({
                                            "type": "image_url",
                                            "image_url": {"url": f"data:{mime_type};base64,{encoded_string}"}
                                        })
                                else:
                                    # File not found, keep URL (will likely fail but what else to do?)
                                    new_content.append(item)
                            except Exception as e:
                                print(f"Error processing local image: {e}")
                                new_content.append(item)
                        else:
                            new_content.append(item)
                    else:
                        new_content.append(item)
                processed_messages.append({**msg, "content": new_content})
            else:
                processed_messages.append(msg)
        return processed_messages

    async def chat_completion_stream(self, messages, model="qwen-plus"):
        client = self.get_client(model)
        if not client:
            yield "Error: Model client not configured."
            return

        # Process messages to handle local images
        api_messages = self._process_messages_for_api(messages)

        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=api_messages,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

chat_service = ChatService()
