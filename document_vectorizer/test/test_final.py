"""
Final integration test comparing document_vectorizer with pdf_vectorizer
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

test_pdf = "/Users/xiaohu/projects/km-agent_2/居住证办理.pdf"

if not os.path.exists(test_pdf):
    print(f"Test file not found: {test_pdf}")
    sys.exit(1)

print("=" * 80)
print("FINAL INTEGRATION TEST: document_vectorizer vs pdf_vectorizer")
print("=" * 80)

# Test with document_vectorizer (as PDFVectorizer)
print("\n[1] Testing document_vectorizer (as PDFVectorizer)")
print("-" * 80)

from document_vectorizer import PDFVectorizer as NewVectorizer, VectorizationProgress

new_vectorizer = NewVectorizer(collection_name="final_test_new")
new_progress = VectorizationProgress()

print("✓ Imported successfully")
print(f"  Collection: {new_vectorizer.collection_name}")

# Vectorize
result_new = new_vectorizer.vectorize_pdf(
    pdf_path=test_pdf,
    owner="final_test_user",
    display_filename="test_doc.pdf",
    verbose=False,
    progress_instance=new_progress
)

print(f"✓ Vectorized: {result_new['filename']}")
print(f"  Pages: {result_new['total_pages']}")
print(f"  Progress completed: {new_progress.is_completed}")

# Search
search_new = new_vectorizer.search(
    query="居住证办理",
    limit=2,
    mode="dual",
    owner="final_test_user",
    verbose=False
)

print(f"✓ Search completed")
print(f"  Summary results: {len(search_new.get('summary_results', []))}")
print(f"  Content results: {len(search_new.get('content_results', []))}")

# Get pages
pages_new = new_vectorizer.get_pages(
    filename="test_doc.pdf",
    page_numbers=[1, 2],
    fields=["page_number", "summary"],
    owner="final_test_user",
    verbose=False
)

print(f"✓ Get pages completed")
print(f"  Retrieved: {len(pages_new)} pages")
for p in pages_new:
    print(f"    Page {p['page_number']}: {p['summary'][:50]}...")

# Test with original pdf_vectorizer
print("\n[2] Testing original pdf_vectorizer")
print("-" * 80)

from pdf_vectorizer import PDFVectorizer as OldVectorizer

old_vectorizer = OldVectorizer(collection_name="final_test_old")

print("✓ Imported successfully")
print(f"  Collection: {old_vectorizer.collection_name}")

# Vectorize
result_old = old_vectorizer.vectorize_pdf(
    pdf_path=test_pdf,
    owner="final_test_user",
    display_filename="test_doc.pdf",
    verbose=False
)

print(f"✓ Vectorized: {result_old['filename']}")
print(f"  Pages: {result_old['total_pages']}")

# Search
search_old = old_vectorizer.search(
    query="居住证办理",
    limit=2,
    mode="dual",
    owner="final_test_user",
    verbose=False
)

print(f"✓ Search completed")
print(f"  Summary results: {len(search_old.get('summary_results', []))}")
print(f"  Content results: {len(search_old.get('content_results', []))}")

# Get pages
pages_old = old_vectorizer.get_pages(
    filename="test_doc.pdf",
    page_numbers=[1, 2],
    fields=["page_number", "summary"],
    owner="final_test_user",
    verbose=False
)

print(f"✓ Get pages completed")
print(f"  Retrieved: {len(pages_old)} pages")

# Compare results
print("\n[3] Comparing Results")
print("-" * 80)

# Compare vectorize results
assert result_new['total_pages'] == result_old['total_pages'], "Page count mismatch"
print(f"✓ Page count matches: {result_new['total_pages']}")

# Compare search results
assert len(search_new['summary_results']) == len(search_old['summary_results']), "Summary results count mismatch"
assert len(search_new['content_results']) == len(search_old['content_results']), "Content results count mismatch"
print(f"✓ Search result counts match")

# Compare get_pages results
assert len(pages_new) == len(pages_old), "Get pages count mismatch"
print(f"✓ Get pages count matches: {len(pages_new)}")

# Compare payload structure
if search_new['summary_results']:
    new_keys = set(search_new['summary_results'][0].keys())
    old_keys = set(search_old['summary_results'][0].keys())
    assert new_keys == old_keys, f"Payload structure mismatch: {new_keys} vs {old_keys}"
    print(f"✓ Payload structure matches: {new_keys}")

# Cleanup
print("\n[4] Cleanup")
print("-" * 80)
new_vectorizer.delete_document("test_doc.pdf", "final_test_user", verbose=False)
old_vectorizer.delete_document("test_doc.pdf", "final_test_user", verbose=False)
print("✓ Cleaned up test data")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - document_vectorizer is fully compatible!")
print("=" * 80)
