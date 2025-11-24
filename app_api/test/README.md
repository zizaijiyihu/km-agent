# API 测试脚本

这个目录包含用于测试 Knowledge Management Agent API 的测试脚本和测试数据。

## 文件说明

- `test_api.py` - API 接口测试脚本
- `居住证办理.pdf` - 测试用的 PDF 文件

## 测试内容

测试脚本会按顺序测试以下 API 接口：

1. **Health Check** - 检查服务健康状态
2. **Get Documents** - 获取文档列表
3. **Upload PDF** - 上传 PDF 并向量化（使用 SSE）
4. **Chat** - 与智能体对话（使用 SSE）
5. **Update Visibility** - 更新文档可见性
6. **Get Document Content** - 获取文档内容
7. **Delete Document** - 删除文档

## 使用方法

### 前置条件

1. 确保 API 服务正在运行（默认: `http://localhost:5001`）
2. 确保测试 PDF 文件存在：`居住证办理.pdf`
3. 安装依赖：`pip install requests`

### 运行测试

```bash
# 基本用法（使用默认配置）
python test_api.py

# 或者使其可执行
chmod +x test_api.py
./test_api.py
```

### 环境变量配置

可以通过环境变量自定义测试配置：

```bash
# 设置 API 地址
export API_BASE_URL=http://localhost:5001

# 设置默认用户
export DEFAULT_OWNER=hu

# 运行测试
python test_api.py
```

### 一次性配置

```bash
API_BASE_URL=http://localhost:8080 DEFAULT_OWNER=testuser python test_api.py
```

## 测试输出

测试脚本会输出彩色的结果，包括：

- ✓ 成功的测试（绿色）
- ✗ 失败的测试（红色）
- ℹ 信息提示（青色）
- ⚠ 警告信息（黄色）

示例输出：

```
======================================================================
Test 1: Health Check
======================================================================

✓ Status: 200
ℹ Response: {
  "status": "healthy",
  "services": {
    "km_agent": true,
    "vectorizer": true
  }
}
✓ Health check passed!

...

======================================================================
Test Summary
======================================================================

Health Check.......................................... PASSED
Get Documents......................................... PASSED
Upload PDF............................................ PASSED
Chat.................................................. PASSED
Update Visibility..................................... PASSED
Get Document Content.................................. PASSED
Delete Document....................................... PASSED

Total: 7/7 tests passed

🎉 All tests passed!
```

## 注意事项

1. **测试顺序** - 测试按顺序执行，某些测试依赖前面测试的结果（例如，删除文档测试需要先上传文档）

2. **数据清理** - 测试脚本会在最后删除上传的测试文档，确保环境清洁

3. **超时设置** - 各个接口有不同的超时设置：
   - 健康检查：5秒
   - 获取文档列表：10秒
   - 上传 PDF：300秒（5分钟）
   - 聊天：60秒
   - 其他操作：10-30秒

4. **SSE 流式测试** - 上传和聊天接口使用 SSE（Server-Sent Events）流式响应，测试脚本会实时显示进度

5. **中断恢复** - 可以使用 Ctrl+C 中断测试，脚本会优雅退出

## 故障排查

### API 连接失败

```
✗ Health check failed: HTTPConnectionPool...
```

**解决方案**：
- 检查 API 服务是否正在运行
- 确认 `API_BASE_URL` 设置正确
- 检查防火墙设置

### 测试文件未找到

```
✗ Test PDF not found: /path/to/居住证办理.pdf
```

**解决方案**：
- 确保 `居住证办理.pdf` 在 `app_api/test/` 目录下
- 或者修改 `test_api.py` 中的 `TEST_PDF_PATH` 变量

### 上传超时

```
✗ Upload test failed: Read timed out
```

**解决方案**：
- 检查文件大小是否过大
- 确认向量化服务（Qdrant）正常运行
- 检查 PDF 解析服务是否可用

## 自定义测试

如果需要测试特定接口或使用不同的测试数据，可以修改 `test_api.py`：

```python
# 修改测试用户
DEFAULT_OWNER = 'your_username'

# 修改测试文件
TEST_PDF_PATH = '/path/to/your/test.pdf'

# 修改 API 地址
API_BASE_URL = 'http://your-api-server:port'
```

## 集成到 CI/CD

测试脚本返回标准退出码：
- `0` - 所有测试通过
- `1` - 至少有一个测试失败
- `130` - 用户中断（Ctrl+C）

可以在 CI/CD 流程中使用：

```bash
# 在 CI/CD 脚本中
python test_api.py
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Tests failed"
    exit 1
fi
```
