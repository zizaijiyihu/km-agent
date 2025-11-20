# UI - 知识管理前端界面

基于 React + Zustand + Vite 的现代化前端应用，为知识管理系统提供美观的用户界面。

## 技术栈

- **React 18**: 用户界面框架
- **Zustand**: 轻量级状态管理
- **Vite**: 快速的构建工具
- **Tailwind CSS**: 实用优先的 CSS 框架
- **React-PDF**: PDF 文档渲染
- **Font Awesome**: 图标库

## 功能特性

### ✅ 已实现功能

1. **智能对话界面**
   - 与 KM Agent 实时对话
   - 支持多轮对话历史
   - 优雅的消息显示动画
   - 自适应输入框

2. **文档管理**
   - 查看文档列表（公开 + 私有）
   - 上传 PDF 并实时显示进度
   - 删除文档（带确认弹窗）
   - 区分公开/私有文档

3. **PDF 浏览器**
   - 大窗口浏览 PDF 文档
   - 支持页码定位
   - 翻页控制（上一页/下一页）
   - 跳转到指定页
   - 右侧滑出式显示

4. **文档引用链接**
   - 在 Agent 回复中自动识别文档引用
   - 格式: `[文档名.pdf:页码]`
   - 点击链接直接跳转到对应页

5. **响应式设计**
   - 流畅的过渡动画
   - 侧边栏滑动效果
   - 优雅的加载状态

## 项目结构

```
ui/
├── src/
│   ├── components/          # React 组件
│   │   ├── ChatView.jsx     # 主聊天界面
│   │   ├── ChatMessage.jsx  # 消息组件（支持文档链接）
│   │   ├── KnowledgeSidebar.jsx  # 知识文档侧边栏
│   │   ├── DocumentItem.jsx      # 文档列表项
│   │   └── PdfViewer.jsx         # PDF浏览器
│   ├── store/
│   │   └── useStore.js      # Zustand 全局状态
│   ├── services/
│   │   └── api.js           # API 服务层
│   ├── App.jsx              # 主应用组件
│   ├── main.jsx             # 应用入口
│   └── index.css            # 全局样式
├── index.html               # HTML 模板
├── package.json             # 项目配置
├── vite.config.js           # Vite 配置
└── tailwind.config.js       # Tailwind 配置
```

## 快速开始

### 安装依赖

```bash
cd ui
npm install
```

### 启动开发服务器

```bash
npm run dev
```

服务将在 `http://localhost:8080` 启动

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录

### 预览生产构建

```bash
npm run preview
```

## API 集成

前端通过 Vite 代理与后端 API 通信：

```javascript
// vite.config.js
server: {
  port: 8080,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    }
  }
}
```

### API 端点使用

1. **聊天**: `POST /api/chat`
2. **获取文档**: `GET /api/documents`
3. **上传文档**: `POST /api/upload` (SSE)
4. **删除文档**: `DELETE /api/documents/:filename`
5. **修改可见性**: `PUT /api/documents/:filename/visibility`

## 状态管理

使用 Zustand 进行全局状态管理：

```javascript
const useStore = create((set) => ({
  // 聊天状态
  messages: [],
  chatHistory: [],
  isLoading: false,

  // 文档状态
  documents: [],

  // 上传状态
  uploadProgress: {...},

  // UI 状态
  isKnowledgeSidebarOpen: false,
  isPdfViewerOpen: false,
  currentPdf: null,

  // Actions...
}))
```

## 组件说明

### ChatView
主聊天界面组件，负责：
- 消息显示和滚动
- 用户输入处理
- 发送消息到后端
- 问候语动画

### ChatMessage
单条消息组件，支持：
- 用户/系统消息样式区分
- 解析文档引用 `[文档名.pdf:页码]`
- 点击文档链接打开 PDF 浏览器

### KnowledgeSidebar
知识文档侧边栏，提供：
- 文档列表展示
- PDF 上传功能
- 实时上传进度
- 滑动显示/隐藏

### PdfViewer
PDF 浏览器组件，功能：
- 渲染 PDF 页面
- 页码导航
- 支持跳转到指定页
- 右侧滑出式显示

### DocumentItem
文档列表项，包含：
- 公开/私有标识
- 页数信息
- 删除按钮（仅所有者）
- 点击浏览功能

## 样式定制

使用 Tailwind CSS 进行样式定制：

```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: '#4F46E5',      // 主题色
      secondary: '#F3F4F6',    // 次要色
      'light-blue': '#f0f8ff', // 用户消息背景
    },
  },
}
```

## 重要说明

### PDF 文件访问

⚠️ **注意**: 当前 `app_api` 模块缺少获取 PDF 文件内容的 API 端点。

PDF 浏览器组件使用的 URL 格式为:
```
/api/documents/<filename>/content?owner=<owner>
```

需要在后端添加此端点才能正常浏览 PDF。建议实现：

```python
@app.route('/api/documents/<filename>/content', methods=['GET'])
def get_document_content(filename):
    owner = request.args.get('owner', config.DEFAULT_USER)
    # 从 vectorizer 获取文件路径并返回
    # 或从文件系统直接读取
    return send_file(pdf_path, mimetype='application/pdf')
```

### 文档引用格式

Agent 回复中的文档引用应使用以下格式：
```
根据文档 [产品需求文档.pdf:5] 所述...
```

格式说明：
- `[` 开始标记
- `文档名.pdf` - 完整文件名
- `:` 分隔符
- `页码` - 数字
- `]` 结束标记

## 开发建议

1. **调试**: 打开浏览器开发者工具查看网络请求和状态
2. **样式**: 使用 Tailwind CSS 类名进行样式定制
3. **状态**: 通过 Zustand DevTools 监控状态变化
4. **组件**: 保持组件职责单一，便于维护

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 许可证

MIT License
