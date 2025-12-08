import React, { useEffect, useState } from 'react'
import useStore from '../store/useStore'
import { getInstructions, createInstruction } from '../services/api'
import InstructionItem from './InstructionItem'

function InstructionSidebar() {
    const isOpen = useStore(state => state.isInstructionSidebarOpen)
    const setInstructionSidebarOpen = useStore(state => state.setInstructionSidebarOpen)
    const instructions = useStore(state => state.instructions)
    const setInstructions = useStore(state => state.setInstructions)
    const addInstruction = useStore(state => state.addInstruction)
    const clearMessages = useStore(state => state.clearMessages) // 清空对话历史
    const isAdmin = useStore(state => state.isAdmin)

    const [isCreating, setIsCreating] = useState(false)
    const [newContent, setNewContent] = useState('')
    const [newIsPublic, setNewIsPublic] = useState(false)
    const [isSaving, setIsSaving] = useState(false)

    const [isLoading, setIsLoading] = useState(false)
    const [page, setPage] = useState(1)
    const [hasMore, setHasMore] = useState(true)
    const PAGE_SIZE = 20

    // 加载指示列表
    useEffect(() => {
        if (isOpen && instructions.length === 0) {
            loadInstructions()
        }
    }, [isOpen])

    const loadInstructions = async (isLoadMore = false) => {
        if (isLoading) return

        setIsLoading(true)
        try {
            const currentPage = isLoadMore ? page : 1
            const response = await getInstructions(currentPage, PAGE_SIZE)
            const newInstructions = (response.instructions || []).map(inst => ({
                ...inst,
                is_public: inst.is_public ?? 0,
                is_editable: inst.is_editable !== undefined ? inst.is_editable : true
            }))

            if (isLoadMore) {
                setInstructions([...instructions, ...newInstructions])
            } else {
                setInstructions(newInstructions)
            }

            setPage(currentPage + 1)
            setHasMore(newInstructions.length === PAGE_SIZE)
        } catch (error) {
            console.error('Failed to load instructions:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleCreate = async () => {
        if (!newContent.trim() || isSaving) return
        if (newIsPublic && !isAdmin) {
            alert('仅管理员可创建公开指示')
            return
        }

        setIsSaving(true)
        try {
            const result = await createInstruction(newContent, 0, isAdmin && newIsPublic)
            if (result.success) {
                // 重新加载列表或者直接添加到store
                // 这里为了简单直接添加到store，实际应该用后端返回的完整对象
                // 但后端返回的 instruction_id，我们需要构造一个对象
                const newInstruction = {
                    id: result.instruction_id,
                    content: newContent,
                    is_active: 1,
                    priority: 0,
                    is_public: newIsPublic && isAdmin ? 1 : 0,
                    is_editable: true,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                }
                addInstruction(newInstruction)
                setNewContent('')
                setNewIsPublic(false)
                setIsCreating(false)

                // 清空对话历史，避免旧的上下文污染
                clearMessages()
            }
        } catch (error) {
            console.error('Failed to create instruction:', error)
            alert('创建失败: ' + error.message)
        } finally {
            setIsSaving(false)
        }
    }

    return (
        <div
            className={`${isOpen ? 'w-80 border-l border-gray-200' : 'w-0'
                } overflow-hidden transition-all duration-300 bg-white relative z-30`}
        >
            <div className="w-80 h-[calc(100vh-200px)] my-[100px] p-6 overflow-y-auto scrollbar-thin">
                {/* 头部 */}
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-800">我的指示</h2>
                    <button
                        onClick={() => setInstructionSidebarOpen(false)}
                        className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-gray-700 rounded-full transition-colors"
                    >
                        <i className="fa fa-times" aria-hidden="true"></i>
                    </button>
                </div>

                {/* 创建新指示 */}
                <div className="mb-6">
                    {isCreating ? (
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <textarea
                                value={newContent}
                                onChange={(e) => setNewContent(e.target.value)}
                                placeholder="请输入新的指示内容..."
                                className="w-full p-2 mb-3 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none resize-none bg-white"
                                rows="3"
                                autoFocus
                            />
                            <div className="flex items-center justify-between mb-3 text-xs text-gray-600">
                                <span className="flex items-center gap-2">
                                    {newIsPublic ? (
                                        <>
                                            <i className="fa fa-globe text-green-500"></i>
                                            <span>公开指示，所有人可见</span>
                                        </>
                                    ) : (
                                        <>
                                            <i className="fa fa-lock text-orange-500"></i>
                                            <span>私有指示，仅自己可见</span>
                                        </>
                                    )}
                                </span>
                                {isAdmin && (
                                    <button
                                        onClick={() => setNewIsPublic(!newIsPublic)}
                                        className="flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-100 transition-colors"
                                        type="button"
                                    >
                                        <span>{newIsPublic ? '切换为私有' : '切换为公开'}</span>
                                    </button>
                                )}
                            </div>
                            <div className="flex justify-end gap-2">
                                <button
                                    onClick={() => {
                                        setIsCreating(false)
                                        setNewContent('')
                                        setNewIsPublic(false)
                                    }}
                                    className="px-3 py-1 text-xs text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                    disabled={isSaving}
                                >
                                    取消
                                </button>
                                <button
                                    onClick={handleCreate}
                                    className="px-3 py-1 text-xs text-white bg-primary hover:bg-primary/90 rounded transition-colors flex items-center gap-1"
                                    disabled={isSaving || !newContent.trim()}
                                >
                                    {isSaving && <i className="fa fa-spinner fa-spin"></i>}
                                    创建
                                </button>
                            </div>
                        </div>
                    ) : (
                        <button
                            onClick={() => setIsCreating(true)}
                            className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-primary hover:text-primary transition-colors flex items-center justify-center gap-2"
                        >
                            <i className="fa fa-plus"></i>
                            <span>新建指示</span>
                        </button>
                    )}
                    <p className="mt-3 text-xs text-gray-500">指示支持公开/私有，默认为私有，可在列表中随时切换。</p>
                </div>

                {/* 指示列表 */}
                <div
                    className="space-y-4"
                    onScroll={(e) => {
                        const { scrollTop, clientHeight, scrollHeight } = e.target
                        if (scrollHeight - scrollTop - clientHeight < 50 && !isLoading && hasMore) {
                            loadInstructions(true)
                        }
                    }}
                >
                    {instructions.length === 0 && !isLoading ? (
                        <div className="text-center text-gray-500 py-8">
                            <i className="fa fa-lightbulb-o text-4xl mb-2" aria-hidden="true"></i>
                            <p className="text-sm">暂无指示</p>
                        </div>
                    ) : (
                        <>
                            {instructions.map((inst) => (
                                <InstructionItem key={inst.id} instruction={inst} />
                            ))}

                            {isLoading && (
                                <div className="flex flex-col items-center justify-center py-4 text-gray-400 gap-2">
                                    <i className="fa fa-circle-o-notch fa-spin text-sm"></i>
                                    <span className="text-xs">加载中...</span>
                                </div>
                            )}

                            {!hasMore && instructions.length > 0 && (
                                <div className="text-center py-4 text-xs text-gray-300">
                                    没有更多了
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

export default InstructionSidebar
