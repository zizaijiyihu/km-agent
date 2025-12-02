
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from km_agent.tools import AgentTools

# Mock dependencies
class MockVectorizer:
    pass

class MockUserInfoService:
    pass

def test_tool_registration():
    tools = AgentTools(vectorizer=MockVectorizer(), user_info_service=MockUserInfoService())
    definitions = tools.get_tool_definitions()
    
    found = False
    for tool in definitions:
        if tool['function']['name'] == 'get_latest_ai_news':
            found = True
            print("Found get_latest_ai_news tool definition:")
            print(json.dumps(tool, indent=2, ensure_ascii=False))
            break
    
    if found:
        print("\nSUCCESS: Tool registered correctly.")
    else:
        print("\nFAILURE: Tool not found.")

if __name__ == "__main__":
    test_tool_registration()
