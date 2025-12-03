import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from document_vectorizer.vectorizer import DocumentVectorizer

def test_universal_vectorizer():
    # Test files
    pdf_path = "/Users/xiaohu/projects/km-agent_2/居住证办理.pdf"
    excel_path = "/Users/xiaohu/projects/km-agent_2/金山云HR服务台_问答库_20251010.xlsx"
    
    vectorizer = DocumentVectorizer(collection_name="test_universal_kb")
    owner = "test_admin"

    print("=== Testing Universal Document Vectorizer ===")

    # 1. Test PDF
    if os.path.exists(pdf_path):
        print(f"\n[1] Vectorizing PDF: {pdf_path}")
        try:
            res = vectorizer.vectorize_file(pdf_path, owner)
            print(f"Result: {json.dumps(res, indent=2)}")
        except Exception as e:
            print(f"PDF Error: {e}")
    else:
        print(f"Skipping PDF test (file not found): {pdf_path}")

    # 2. Test Excel (with chunking)
    if os.path.exists(excel_path):
        print(f"\n[2] Vectorizing Excel: {excel_path}")
        try:
            res = vectorizer.vectorize_file(
                excel_path, 
                owner, 
                chunk_size=250, 
                summary_columns=["标准问题"]
            )
            print(f"Result: {json.dumps(res, indent=2)}")
        except Exception as e:
            print(f"Excel Error: {e}")
    else:
        print(f"Skipping Excel test (file not found): {excel_path}")

    # 3. Test Search (Cross-modal)
    print("\n[3] Testing Cross-modal Search")
    queries = ["如何办理居住证", "社保公积金"]
    
    for q in queries:
        print(f"\nQuery: {q}")
        results = vectorizer.search(q, limit=2, owner=owner)
        
        for type_, items in results.items():
            print(f"  {type_}:")
            for item in items:
                print(f"    - [{item['filename']}] (Score: {item['score']:.3f})")
                print(f"      Summary: {item['summary'][:50]}...")

if __name__ == "__main__":
    test_universal_vectorizer()
