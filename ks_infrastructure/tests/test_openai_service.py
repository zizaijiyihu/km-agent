import sys
import os

# Add project root to path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ks_infrastructure.services.openai_service import ks_openai
from ks_infrastructure.configs.default import OPENAI_CONFIG

def test_openai_connection():
    print("Testing OpenAI Service...")
    try:
        client = ks_openai()
        print("Client created successfully.")
        
        model = OPENAI_CONFIG.get('model', 'DeepSeek-V3.1-Ksyun')
        print(f"Using model: {model}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好啊，你是谁？"}
            ],
            max_tokens=10
        )
        
        content = response.choices[0].message.content
        print(f"Response received: {content}")
        print("OpenAI Service Test Passed!")
        
    except Exception as e:
        print(f"OpenAI Service Test Failed: {e}")
        import traceback
        traceback.print_exc()

def test_openai_streaming():
    print("\nTesting OpenAI Service (Streaming)...")
    try:
        client = ks_openai()
        model = OPENAI_CONFIG.get('model', 'DeepSeek-V3.1-Ksyun')
        
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "请用一句话介绍你自己"}
            ],
            stream=True,
            max_tokens=50
        )
        
        print("Stream response received:")
        full_content = ""
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_content += content
        print("\n\nOpenAI Service Streaming Test Passed!")
        
    except Exception as e:
        print(f"\nOpenAI Service Streaming Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai_connection()
    test_openai_streaming()
