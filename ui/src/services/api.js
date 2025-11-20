const API_BASE_URL = '/api'

/**
 * 发送聊天消息（流式）
 * @param {string} message - 用户消息
 * @param {Array} history - 聊天历史
 * @param {Function} onChunk - 流式数据回调
 * @returns {Promise<Object>} 最终结果
 */
export async function sendChatMessage(message, history = [], onChunk) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, history })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to send message')
  }

  // 处理SSE流
  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  let fullContent = ''
  let toolCalls = []
  let finalHistory = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const text = decoder.decode(value)
    const lines = text.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.substring(6))

          if (data.type === 'content') {
            // 内容流式输出
            fullContent += data.data
            if (onChunk) {
              onChunk({ type: 'content', content: data.data })
            }
          } else if (data.type === 'tool_call') {
            // 工具调用通知
            toolCalls.push(data.data)
            if (onChunk) {
              onChunk({ type: 'tool_call', data: data.data })
            }
          } else if (data.type === 'done') {
            // 完成
            finalHistory = data.data.history
            toolCalls = data.data.tool_calls
          } else if (data.type === 'error') {
            throw new Error(data.data.error)
          }
        } catch (e) {
          console.error('Failed to parse SSE data:', e, 'Line:', line)
        }
      }
    }
  }

  return {
    response: fullContent,
    tool_calls: toolCalls,
    history: finalHistory
  }
}

/**
 * 获取文档列表
 * @param {string} owner - 用户名
 * @returns {Promise<Object>} 文档列表
 */
export async function getDocuments(owner = 'hu') {
  const response = await fetch(`${API_BASE_URL}/documents?owner=${encodeURIComponent(owner)}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to fetch documents')
  }

  return response.json()
}

/**
 * 上传并向量化PDF
 * @param {File} file - PDF文件
 * @param {string} owner - 用户名
 * @param {number} isPublic - 是否公开 (0=私有, 1=公开)
 * @param {Function} onProgress - 进度回调
 * @returns {Promise<Object>} 上传结果
 */
export async function uploadPDF(file, owner = 'hu', isPublic = 0, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('owner', owner)
  formData.append('is_public', isPublic.toString())

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error('Upload failed')
  }

  // 处理SSE流
  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  let result = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const text = decoder.decode(value)
    const lines = text.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.substring(6))

          // 调用进度回调
          if (onProgress) {
            onProgress(data)
          }

          // 检查错误状态
          if (data.stage === 'error') {
            throw new Error(data.error || '上传处理失败')
          }

          // 保存最终结果
          if (data.stage === 'completed') {
            result = data
          }
        } catch (e) {
          console.error('Failed to parse SSE data:', e)
          // 如果是Error对象，向上抛出
          if (e instanceof Error && e.message !== 'Failed to parse SSE data:') {
            throw e
          }
        }
      }
    }
  }

  return result
}

/**
 * 删除文档
 * @param {string} filename - 文件名
 * @param {string} owner - 用户名
 * @returns {Promise<Object>} 删除结果
 */
export async function deleteDocument(filename, owner = 'hu') {
  const response = await fetch(
    `${API_BASE_URL}/documents/${encodeURIComponent(filename)}?owner=${encodeURIComponent(owner)}`,
    { method: 'DELETE' }
  )

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to delete document')
  }

  return response.json()
}

/**
 * 修改文档可见性
 * @param {string} filename - 文件名
 * @param {string} owner - 用户名
 * @param {number} isPublic - 是否公开 (0=私有, 1=公开)
 * @returns {Promise<Object>} 更新结果
 */
export async function updateDocumentVisibility(filename, owner = 'hu', isPublic) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${encodeURIComponent(filename)}/visibility?owner=${encodeURIComponent(owner)}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_public: isPublic })
    }
  )

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to update document visibility')
  }

  return response.json()
}

/**
 * 检查服务健康状态
 * @returns {Promise<Object>} 健康状态
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`)
  return response.json()
}
