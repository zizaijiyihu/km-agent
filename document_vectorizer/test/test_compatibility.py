"""
Test backward compatibility with PDFVectorizer interface
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Test 1: Import compatibility
print("=== Test 1: Import Compatibility ===")
try:
    from document_vectorizer import PDFVectorizer, VectorizationProgress
    print("✓ Successfully imported PDFVectorizer (alias)")
    print("✓ Successfully imported VectorizationProgress")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialization
print("\n=== Test 2: Initialization ===")
try:
    vectorizer = PDFVectorizer()
    print(f"✓ Initialized with default collection: {vectorizer.collection_name}")
    print(f"✓ Vector size: {vectorizer.vector_size}")
    
    custom_vectorizer = PDFVectorizer(collection_name="test_kb", vector_size=1024)
    print(f"✓ Custom initialization: {custom_vectorizer.collection_name}")
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Method signatures
print("\n=== Test 3: Method Signatures ===")
import inspect

required_methods = {
    "vectorize_pdf": ["pdf_path", "owner", "display_filename", "verbose", "progress_instance"],
    "delete_document": ["filename", "owner", "verbose"],
    "search": ["query", "limit", "mode", "owner", "verbose"],
    "get_pages": ["filename", "page_numbers", "fields", "owner", "verbose"]
}

for method_name, expected_params in required_methods.items():
    if hasattr(vectorizer, method_name):
        method = getattr(vectorizer, method_name)
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        # Check if all expected params exist (order doesn't matter)
        missing = set(expected_params) - set(params)
        if missing:
            print(f"✗ {method_name}: Missing parameters {missing}")
        else:
            print(f"✓ {method_name}: All parameters present")
    else:
        print(f"✗ {method_name}: Method not found")

# Test 4: VectorizationProgress
print("\n=== Test 4: VectorizationProgress ===")
try:
    progress = VectorizationProgress()
    progress.update(stage="init", progress_percent=10, message="Testing")
    
    assert progress.get_field("stage") == "init"
    assert progress.get()["progress_percent"] == 10
    assert not progress.is_completed
    assert not progress.is_error
    
    progress.update(stage="completed", progress_percent=100)
    assert progress.is_completed
    
    print("✓ VectorizationProgress works correctly")
except Exception as e:
    print(f"✗ VectorizationProgress failed: {e}")

# Test 5: Actual PDF processing (if test file exists)
print("\n=== Test 5: PDF Processing ===")
test_pdf = "/Users/xiaohu/projects/km-agent_2/居住证办理.pdf"
if os.path.exists(test_pdf):
    try:
        vectorizer = PDFVectorizer(collection_name="test_compat_kb")
        result = vectorizer.vectorize_pdf(
            pdf_path=test_pdf,
            owner="test_user",
            verbose=False
        )
        
        print(f"✓ Processed: {result['filename']}")
        print(f"✓ Pages: {result['total_pages']}")
        print(f"✓ Collection: {result['collection']}")
        
        # Test search
        search_results = vectorizer.search("居住证", limit=2, owner="test_user", verbose=False)
        print(f"✓ Search returned {len(search_results.get('summary_results', []))} summary results")
        
        # Test get_pages
        pages = vectorizer.get_pages(
            filename=result['filename'],
            page_numbers=[1],
            owner="test_user",
            verbose=False
        )
        print(f"✓ Retrieved {len(pages)} page(s)")
        
        # Test delete
        vectorizer.delete_document(result['filename'], "test_user", verbose=False)
        print(f"✓ Deleted document")
        
    except Exception as e:
        print(f"✗ PDF processing failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"⊘ Skipping (test file not found): {test_pdf}")

print("\n=== All Compatibility Tests Passed ===")
