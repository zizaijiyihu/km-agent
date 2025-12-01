import React, { useState, useEffect, useRef } from 'react'
import { sendChatMessage } from '../services/api'

function ReminderAnalysisCard({ reminder, onClose }) {
    const [status, setStatus] = useState('loading') // loading, done, error
    const [content, setContent] = useState('')
    const [isExpanded, setIsExpanded] = useState(true)
    const abortControllerRef = useRef(null)

    useEffect(() => {
        analyzeReminder()

        // 清理函数：组件卸载时中止请求
        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort()
            }
        }
    }, [reminder.id])

    const analyzeReminder = async () => {
        setStatus('loading')
        setContent('')

        abortControllerRef.current = new AbortController()
        let streamingContent = ''

        try {
            await sendChatMessage(
                reminder.content,
                null, // 不传历史
                (chunk) => {
                    if (chunk.type === 'content') {
                        streamingContent += chunk.content
                        setContent(streamingContent)
                    }
                },
                abortControllerRef.current.signal,
                null, // 不传 conversation_id
                false // 禁用历史记录
            )

            setStatus('done')
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Analysis aborted for reminder:', reminder.id)
            } else {
                console.error('Failed to analyze reminder:', error)
                setStatus('error')
                // 错误时自动关闭
                setTimeout(() => {
                    onClose(reminder.id)
                }, 1000)
            }
        } finally {
            abortControllerRef.current = null
        }
    }

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden transition-all">
            {/* 头部 - 标题和操作 */}
            <div
                className="p-3 bg-gray-50/50 border-b border-gray-100 flex items-start justify-between cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex-1 pr-2">
                    <div className="text-sm font-medium text-gray-800 line-clamp-2">
                        {reminder.content}
                    </div>
                    {status === 'loading' && (
                        <div className="flex items-center gap-1.5 mt-1.5 text-xs text-gray-400">
                            <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse"></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                            <span className="ml-1">分析中</span>
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-1">
                    {/* 展开/收起图标 */}
                    {status === 'done' && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation()
                                setIsExpanded(!isExpanded)
                            }}
                            className="w-6 h-6 flex items-center justify-center text-gray-400 hover:text-gray-600 rounded transition-colors"
                        >
                            <i className={`fa fa-chevron-${isExpanded ? 'up' : 'down'} text-xs`}></i>
                        </button>
                    )}

                    {/* 关闭按钮 */}
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            onClose(reminder.id)
                        }}
                        className="w-6 h-6 flex items-center justify-center text-gray-400 hover:text-red-500 rounded transition-colors"
                        title="关闭"
                    >
                        <i className="fa fa-times text-xs"></i>
                    </button>
                </div>
            </div>

            {/* 内容区域 */}
            {isExpanded && status === 'done' && content && (
                <div className="p-3 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap max-h-60 overflow-y-auto scrollbar-thin">
                    {content}
                </div>
            )}

            {/* 错误状态 */}
            {status === 'error' && (
                <div className="p-3 text-xs text-red-500 flex items-center gap-2">
                    <i className="fa fa-exclamation-circle"></i>
                    <span>分析失败，即将关闭...</span>
                </div>
            )}
        </div>
    )
}

export default ReminderAnalysisCard
