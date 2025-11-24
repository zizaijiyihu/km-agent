# Image Analyzer 模块

图片存储和解析服务，将图片存储到临时桶（tmp bucket）并使用视觉识别服务解析图片内容。

## 功能特性

- 上传图片到 MinIO 的 `tmp` 桶（临时存储）
- 自动设置图片为公开访问
- 使用视觉识别服务（Qwen Vision）解析图片内容
- 支持自定义提示词进行定向分析
- 支持批量图片分析
- 返回图片的网络访问地址和解析结果
- 解析结果自动添加【以下内容为图片理解结果】前缀

## 接口说明

### analyze_temp_image

分析单张图片

```python
from tmp_image_repository import analyze_temp_image

result = analyze_temp_image(
    image_path='/path/to/image.png',
    username='user123',  # 可选，默认 'system'
    prompt='请详细描述这张图片',  # 可选，使用默认提示词
    custom_filename='my_image.png'  # 可选，自定义文件名
)

if result['success']:
    print(f"图片URL: {result['image_url']}")
    print(f"分析结果: {result['analysis']}")
else:
    print(f"错误: {result['error']}")
```

**参数：**
- `image_path` (str): 本地图片文件路径（必需）
- `username` (str): 用户名，默认为 'system'
- `prompt` (str): 图片分析提示词，默认为通用描述提示
- `custom_filename` (str): 自定义文件名，如果不提供则使用原文件名

**返回值：** dict，包含以下字段：
- `success` (bool): 是否成功
- `image_url` (str): 图片的网络访问地址（成功时）
- `analysis` (str): 图片解析结果，带【以下内容为图片理解结果】前缀（成功时）
- `error` (str): 错误信息（失败时）

### batch_analyze_images

批量分析多张图片

```python
from tmp_image_repository import batch_analyze_images

image_paths = [
    '/path/to/image1.png',
    '/path/to/image2.jpg',
    '/path/to/image3.png'
]

results = batch_analyze_images(
    image_paths=image_paths,
    username='user123',
    prompt='请识别图片中的文字'  # 可选
)

for i, result in enumerate(results):
    if result['success']:
        print(f"图片 {i+1}: {result['image_url']}")
        print(f"分析: {result['analysis']}")
    else:
        print(f"图片 {i+1} 失败: {result['error']}")
```

**参数：**
- `image_paths` (list[str]): 图片文件路径列表
- `username` (str): 用户名，默认为 'system'
- `prompt` (str): 图片分析提示词

**返回值：** list[dict]，每个元素格式同 `analyze_temp_image` 返回值

### DEFAULT_PROMPT

默认的图片分析提示词

```python
from tmp_image_repository import DEFAULT_PROMPT

print(DEFAULT_PROMPT)
# 输出: "请详细描述这张图片的内容，包括图片中的物体、场景、文字、颜色等信息。"
```

## 使用示例

### 示例 1: 基本使用

```python
from image_analyzer import analyze_temp_image

# 分析图片
result = analyze_temp_image(
    image_path='/Users/me/photo.jpg',
    username='alice'
)

if result['success']:
    print(result['analysis'])
    # 输出:
    # 【以下内容为图片理解结果】
    # 这是一张风景照片，蓝天白云，绿树成荫...
```

### 示例 2: 自定义提示词

```python
from image_analyzer import analyze_temp_image

# 识别图片中的文字
result = analyze_temp_image(
    image_path='/Users/me/document.png',
    username='bob',
    prompt='请提取这张图片中的所有文字内容'
)

if result['success']:
    print(f"访问链接: {result['image_url']}")
    print(result['analysis'])
```

### 示例 3: 批量处理

```python
from image_analyzer import batch_analyze_images
import glob

# 获取目录下所有 PNG 图片
image_files = glob.glob('/Users/me/images/*.png')

# 批量分析
results = batch_analyze_images(
    image_paths=image_files,
    username='charlie'
)

# 统计结果
success_count = sum(1 for r in results if r['success'])
print(f"成功: {success_count}/{len(results)}")
```

## 图片存储

- 图片存储在 MinIO 的 **tmp** 桶中
- 存储路径格式：`username/filename`
- 自动设置为公开访问（`is_public=1`）
- 图片 URL 格式：`http://{minio_endpoint}/tmp/{username}/{filename}`

## 支持的图片格式

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

## 依赖服务

- **file_repository**: 文件存储服务
- **ks_infrastructure.services.vision_service**: 视觉识别服务

## 测试

运行测试脚本：

```bash
python tmp_image_repository/test/test_analyzer.py
```

测试内容包括：
1. 单张图片分析（默认提示词）
2. 单张图片分析（自定义提示词）
3. 批量图片分析
4. 错误处理（文件不存在）

## 注意事项

1. **临时存储**: 图片存储在 `tmp` 桶中，适用于临时文件，不建议长期保存
2. **公开访问**: 上传的图片自动设为公开，任何人都可以通过 URL 访问
3. **文件覆盖**: 相同用户上传相同文件名会自动覆盖
4. **API 密钥**: 需要配置 Vision 服务的 API 密钥（DASHSCOPE_API_KEY）

## 错误处理

所有接口在失败时会在返回值中包含 `success: False` 和 `error` 字段：

```python
result = analyze_temp_image(image_path='/nonexistent.png')
if not result['success']:
    print(f"错误: {result['error']}")
    # 输出: 错误: 图片文件不存在: /nonexistent.png
```

## 配置

Vision 服务配置在 `ks_infrastructure/configs/default.py` 中：

```python
VISION_CONFIG = {
    "api_key": "your-api-key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-vl-max"
}
```

MinIO 配置在 `ks_infrastructure/configs/default.py` 中：

```python
MINIO_CONFIG = {
    "endpoint": "http://120.92.109.164:9000",
    "access_key": "admin",
    "secret_key": "rsdyxjh110!",
    "region": "us-east-1"
}
```
