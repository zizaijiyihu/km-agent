import React from 'react'
import ChatView from './components/ChatView'
import KnowledgeSidebar from './components/KnowledgeSidebar'
import PdfViewer from './components/PdfViewer'

function App() {
  return (
    <div className="bg-white min-h-screen flex items-center justify-center p-4">
      {/* 主容器 - 包含主视图、知识侧边栏和PDF浏览器 */}
      <div className="flex space-x-4">
        {/* 主聊天视图 */}
        <ChatView />

        {/* 知识文档侧边栏 */}
        <KnowledgeSidebar />

        {/* PDF浏览器 */}
        <PdfViewer />
      </div>
    </div>
  )
}

export default App
