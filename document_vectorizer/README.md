# Document Vectorizer

通用文档向量化服务，完全兼容 `pdf_vectorizer` 接口。

## 特性

- **多格式支持**: PDF (.pdf), Excel (.xlsx, .xls)
- **向后兼容**: 完全兼容 `PDFVectorizer` 的所有接口和参数
- **统一存储**: 所有文档类型存储在同一个 Qdrant collection 中
- **双路检索**: Summary Vector + Content Vector
- **进度跟踪**: 实时进度更新

## 快速开始

### 作为 PDFVectorizer 的替代品使用

```python
# 原有代码无需修改
from document_vectorizer import PDFVectorizer

vectorizer = PDFVectorizer()

# 所有原有方法都可以正常使用
result = vectorizer.vectorize_pdf(
    pdf_path="document.pdf",
    owner="user123",
    verbose=True
)

# 搜索
results = vectorizer.search("query", owner="user123")

# 获取页面
pages = vectorizer.get_pages("document.pdf", [1, 2, 3], owner="user123")

# 删除文档
vectorizer.delete_document("document.pdf", "user123")
```

### 使用新的通用接口

```python
from document_vectorizer import DocumentVectorizer

vectorizer = DocumentVectorizer()

# 自动识别文件类型并处理
vectorizer.vectorize_file("document.pdf", owner="user123")
vectorizer.vectorize_file("data.xlsx", owner="user123", chunk_size=250)
```

## 兼容性说明

### 完全兼容的方法

1. **`__init__(collection_name, vector_size)`**
   - 默认 collection: `pdf_knowledge_base`
   - 默认 vector_size: `4096`

2. **`vectorize_pdf(pdf_path, owner, display_filename, verbose, progress_instance)`**
   - 所有参数保持一致
   - 返回值结构相同

3. **`delete_document(filename, owner, verbose)`**
   - 完全兼容

4. **`search(query, limit, mode, owner, verbose)`**
   - 返回值结构完全一致
   - 支持 dual/summary/content 三种模式

5. **`get_pages(filename, page_numbers, fields, owner, verbose)`**
   - 完全兼容

6. **`VectorizationProgress`**
   - 所有属性和方法保持一致

### Payload 结构

与 `PDFVectorizer` 完全一致:

```python
{
    "owner": str,
    "filename": str,
    "page_number": int,  # PDF 页码
    "summary": str,
    "content": str
}
```

## 测试

运行兼容性测试:

```bash
python3 document_vectorizer/test/test_compatibility.py
```

## 迁移指南

### 无需修改代码

只需将导入语句从:
```python
from pdf_vectorizer import PDFVectorizer
```

改为:
```python
from document_vectorizer import PDFVectorizer
```

所有其他代码保持不变。

### 引用位置

当前项目中使用 `PDFVectorizer` 的位置:
- `km_agent/agent.py` (第154行)
- `app_api/services/agent_service.py` (第47, 55行)
- `app_api/routes/documents.py` (第122行 - 仅 VectorizationProgress)

## 架构

```
document_vectorizer/
├── __init__.py              # 导出 PDFVectorizer 别名
├── vectorizer.py            # 核心引擎
├── domain.py                # 数据模型
├── processors/              # 文件处理器
│   ├── base.py              # 基类
│   ├── pdf_processor.py     # PDF 处理
│   └── excel_processor.py   # Excel 处理
└── test/                    # 测试文件
    ├── test_compatibility.py
    ├── test_final.py
    └── test_universal.py
```

## 扩展性

添加新文件类型支持只需:
1. 在 `processors/` 下创建新的 processor
2. 在 `DocumentVectorizer.__init__` 中注册
3. 无需修改核心逻辑
