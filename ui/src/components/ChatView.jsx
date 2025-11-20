import React, { useRef, useEffect, useState } from 'react'
import useStore from '../store/useStore'
import { sendChatMessage } from '../services/api'
import ChatMessage from './ChatMessage'

function ChatView() {
  const messages = useStore(state => state.messages)
  const chatHistory = useStore(state => state.chatHistory)
  const isLoading = useStore(state => state.isLoading)
  const addMessage = useStore(state => state.addMessage)
  const updateLastMessage = useStore(state => state.updateLastMessage)
  const setMessages = useStore(state => state.setMessages)
  const setChatHistory = useStore(state => state.setChatHistory)
  const setIsLoading = useStore(state => state.setIsLoading)
  const toggleKnowledgeSidebar = useStore(state => state.toggleKnowledgeSidebar)

  const [inputValue, setInputValue] = useState('')
  const [greetingVisible, setGreetingVisible] = useState(true)
  const messageContainerRef = useRef(null)
  const inputRef = useRef(null)

  const hasMessages = messages.length > 0

  // 自动滚动到底部
  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight
    }
  }, [messages])

  // 处理发送消息
  const handleSendMessage = async () => {
    const text = inputValue.trim()
    if (!text || isLoading) return

    // 添加用户消息
    addMessage({ role: 'user', content: text })
    setInputValue('')

    // 隐藏问候语
    if (greetingVisible) {
      setTimeout(() => setGreetingVisible(false), 800)
    }

    // 发送到后端（流式）
    setIsLoading(true)

    // 创建一个空的assistant消息用于流式更新
    addMessage({ role: 'assistant', content: '' })

    let streamingContent = ''

    try {
      const response = await sendChatMessage(text, chatHistory, (chunk) => {
        if (chunk.type === 'content') {
          // 流式更新内容
          streamingContent += chunk.content
          updateLastMessage(streamingContent)
        } else if (chunk.type === 'tool_call') {
          console.log('Tool call:', chunk.data)
        }
      })

      // 更新历史
      if (response.history) {
        setChatHistory(response.history)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      // 更新最后一条消息为错误信息
      updateLastMessage('抱歉，发送消息失败，请稍后重试。')
    } finally {
      setIsLoading(false)
    }
  }

  // 处理键盘事件
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // 自动调整输入框高度
  const adjustInputHeight = (e) => {
    const target = e.target
    target.style.height = 'auto'
    target.style.height = Math.min(target.scrollHeight, 100) + 'px'
  }

  return (
    <div className="w-[800px] h-[calc(100vh-200px)] my-[100px] flex flex-col bg-white relative">
      {/* 消息容器 */}
      <div
        ref={messageContainerRef}
        className={`${hasMessages ? 'flex-1' : 'hidden'} overflow-y-auto scrollbar-thin bg-white w-full transition-all duration-1200 ease-out`}
      >
        <div className="w-full max-w-[760px] mx-auto p-4">
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg} />
          ))}
          {isLoading && (
            <div className="mb-4 max-w-[80%] bg-white p-3 rounded-lg rounded-tr-none border border-gray-100">
              <div className="flex items-center gap-2 text-gray-500">
                <i className="fa fa-circle-o-notch fa-spin" aria-hidden="true"></i>
                <span>思考中...</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 输入容器 */}
      <div
        className={`${
          hasMessages
            ? 'h-[100px] justify-center'
            : 'flex-1 items-center justify-center'
        } flex flex-col bg-white w-full transition-all duration-1200 ease-out`}
      >
        {/* 问候语 */}
        {!hasMessages && (
          <div
            className={`text-2xl text-gray-800 font-medium mb-8 transition-opacity duration-800 ${
              greetingVisible ? 'opacity-100' : 'opacity-0'
            }`}
          >
            创造知识   共享知识
          </div>
        )}

        {/* 输入区 */}
        <div className="w-full max-w-[760px] p-4 mx-auto">
          <div className="relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value)
                adjustInputHeight(e)
              }}
              onKeyDown={handleKeyDown}
              className="w-full p-4 pr-16 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none resize-none transition-all shadow-md"
              placeholder="发消息或输入/选择技能"
              rows="2"
              disabled={isLoading}
            />

            {/* 工具按钮组 */}
            <div className="absolute right-3 bottom-3 flex space-x-2">
              <button
                onClick={toggleKnowledgeSidebar}
                className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-primary hover:bg-gray-100 rounded-full transition-colors"
              >
                <i className="fa fa-book" aria-hidden="true"></i>
              </button>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="w-8 h-8 flex items-center justify-center text-white bg-primary hover:bg-primary/90 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <i className="fa fa-paper-plane-o" aria-hidden="true"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatView
