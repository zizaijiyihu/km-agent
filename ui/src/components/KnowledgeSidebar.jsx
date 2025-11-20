import React, { useEffect, useRef } from 'react'
import useStore from '../store/useStore'
import { getDocuments, uploadPDF } from '../services/api'
import DocumentItem from './DocumentItem'

function KnowledgeSidebar() {
  const isOpen = useStore(state => state.isKnowledgeSidebarOpen)
  const setKnowledgeSidebarOpen = useStore(state => state.setKnowledgeSidebarOpen)
  const owner = useStore(state => state.owner)
  const documents = useStore(state => state.documents)
  const setDocuments = useStore(state => state.setDocuments)
  const addDocument = useStore(state => state.addDocument)
  const uploadProgress = useStore(state => state.uploadProgress)
  const setUploadProgress = useStore(state => state.setUploadProgress)
  const resetUploadProgress = useStore(state => state.resetUploadProgress)

  const fileInputRef = useRef(null)

  // 加载文档列表
  useEffect(() => {
    if (isOpen && documents.length === 0) {
      loadDocuments()
    }
  }, [isOpen])

  const loadDocuments = async () => {
    try {
      const response = await getDocuments(owner)
      setDocuments(response.documents || [])
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }

  // 处理文件上传
  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // 重置文件输入,允许重复上传同一文件
    e.target.value = ''

    setUploadProgress({
      isUploading: true,
      filename: file.name,
      progress: 0,
      stage: 'init',
      message: '开始处理...'
    })

    try {
      const result = await uploadPDF(file, owner, 0, (progressData) => {
        setUploadProgress({
          progress: progressData.progress_percent || 0,
          stage: progressData.stage || '',
          message: progressData.message || '',
          currentPage: progressData.current_page || 0,
          totalPages: progressData.total_pages || 0
        })
      })

      // 上传完成,添加到文档列表
      if (result && result.data) {
        addDocument({
          filename: file.name,
          owner: owner,
          is_public: 0,
          page_count: result.data.total_pages || 0
        })
      }

      // 1秒后隐藏进度条
      setTimeout(() => {
        resetUploadProgress()
      }, 1000)
    } catch (error) {
      console.error('Upload failed:', error)
      alert('上传失败: ' + error.message)
      resetUploadProgress()
    }
  }

  return (
    <div
      className={`${
        isOpen ? 'w-80 border-l border-gray-200' : 'w-0'
      } overflow-hidden transition-all duration-300 bg-white`}
    >
      <div className="w-80 h-[calc(100vh-200px)] my-[100px] p-6 overflow-y-auto scrollbar-thin">
        {/* 头部 */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">知识文档</h2>
          <button
            onClick={() => setKnowledgeSidebarOpen(false)}
            className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-gray-700 rounded-full transition-colors"
          >
            <i className="fa fa-times" aria-hidden="true"></i>
          </button>
        </div>

        {/* 文件上传组件 */}
        <div className="mb-6">
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer bg-gray-50"
          >
            <i className="fa fa-cloud-upload text-3xl text-gray-400 mb-2" aria-hidden="true"></i>
            <p className="text-gray-600 text-sm mb-1">点击或拖拽文件上传</p>
            <p className="text-xs text-gray-500">目前仅支持 PDF 格式</p>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf"
              onChange={handleFileSelect}
            />
          </div>

          {/* 上传进度显示 */}
          {uploadProgress.isUploading && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">{uploadProgress.filename}</span>
                <span className="text-xs text-gray-500">{uploadProgress.stage}</span>
              </div>
              <div className="text-sm text-primary mb-2">
                {uploadProgress.totalPages > 0
                  ? `共${uploadProgress.totalPages}页，第${uploadProgress.currentPage}页解析中`
                  : uploadProgress.message}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress.progress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* 文档列表 */}
        <div className="space-y-4">
          {documents.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <i className="fa fa-folder-open-o text-4xl mb-2" aria-hidden="true"></i>
              <p className="text-sm">暂无文档</p>
            </div>
          ) : (
            documents.map((doc, index) => (
              <DocumentItem key={`${doc.filename}-${doc.owner}-${index}`} document={doc} />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default KnowledgeSidebar
