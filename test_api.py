import os
import dotenv

dotenv.load_dotenv()
print("QWEN BASE URL:", os.getenv("QWEN_BASE_URL"))
print("QWEN API KEY:", os.getenv("QWEN_API_KEY"))

print("DEEPSEEK BASE URL:", os.getenv("DEEPSEEK_BASE_URL"))
print("DEEPSEEK API KEY:", os.getenv("DEEPSEEK_API_KEY"))