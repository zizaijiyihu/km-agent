import React, { useEffect, useState } from 'react'
import useStore from '../store/useStore'
import { getReminders, createReminder } from '../services/api'
import { applyReminderOrder, setReminderOrder } from '../services/reminderOrderCache'
import ReminderItem from './ReminderItem'

function ReminderSidebar() {
    const isOpen = useStore(state => state.isReminderSidebarOpen)
    const setReminderSidebarOpen = useStore(state => state.setReminderSidebarOpen)
    const reminders = useStore(state => state.reminders)
    const setReminders = useStore(state => state.setReminders)
    const addReminder = useStore(state => state.addReminder)
    const reorderReminders = useStore(state => state.reorderReminders)

    const [isCreating, setIsCreating] = useState(false)
    const [newContent, setNewContent] = useState('')
    const [isSaving, setIsSaving] = useState(false)

    const [isLoading, setIsLoading] = useState(false)
    const [page, setPage] = useState(1)
    const [hasMore, setHasMore] = useState(true)
    const PAGE_SIZE = 20
    const [draggingId, setDraggingId] = useState(null)
    const [dragOverId, setDragOverId] = useState(null)
    const [isSavingOrder, setIsSavingOrder] = useState(false)

    // 加载提醒列表
    useEffect(() => {
        if (isOpen && reminders.length === 0) {
            loadReminders()
        }
    }, [isOpen])

    const loadReminders = async (isLoadMore = false) => {
        if (isLoading) return

        setIsLoading(true)
        try {
            const currentPage = isLoadMore ? page : 1
            const response = await getReminders(currentPage, PAGE_SIZE)
            let newReminders = response.data || []
            newReminders = await applyReminderOrder(newReminders)

            if (isLoadMore) {
                setReminders(newReminders)
            } else {
                setReminders(newReminders)
            }

            setPage(currentPage + 1)
            setHasMore(newReminders.length === PAGE_SIZE)
        } catch (error) {
            console.error('Failed to load reminders:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleCreate = async () => {
        if (!newContent.trim() || isSaving) return

        setIsSaving(true)
        try {
            const result = await createReminder(newContent)
            if (result.success) {
                const newReminder = {
                    id: result.reminder_id,
                    content: newContent,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    is_public: 0,
                    sort_order: result.sort_order ?? reminders.length + 1
                }
                // 新建的默认追加到末尾以保持与后端一致
                const updated = [...reminders, newReminder]
                setReminders(updated)
                setReminderOrder(updated.map(r => r.id))
                setNewContent('')
                setIsCreating(false)
            }
        } catch (error) {
            console.error('Failed to create reminder:', error)
            alert('创建失败: ' + error.message)
        } finally {
            setIsSaving(false)
        }
    }

    return (
        <div
            className={`${isOpen ? 'w-80 border-l border-gray-100' : 'w-0'
                } overflow-hidden transition-all duration-300 bg-white relative z-30`}
        >
            <div className="w-80 h-[calc(100vh-200px)] my-[100px] p-6 overflow-y-auto scrollbar-thin">
                {/* 头部 */}
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-800">我的提醒</h2>
                    <button
                        onClick={() => setReminderSidebarOpen(false)}
                        className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-gray-700 rounded-full transition-colors"
                    >
                        <i className="fa fa-times" aria-hidden="true"></i>
                    </button>
                </div>

                {/* 创建新提醒 */}
                <div className="mb-6">
                    {isCreating ? (
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <textarea
                                value={newContent}
                                onChange={(e) => setNewContent(e.target.value)}
                                placeholder="请输入提醒内容，例如：今天谁比较辛苦..."
                                className="w-full p-2 mb-3 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none resize-none bg-white"
                                rows="3"
                                autoFocus
                            />
                            <div className="flex justify-end gap-2">
                                <button
                                    onClick={() => {
                                        setIsCreating(false)
                                        setNewContent('')
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
                            className="w-full py-3 border-2 border-dashed border-gray-300/50 rounded-lg text-gray-500 hover:border-primary/50 hover:text-primary transition-colors flex items-center justify-center gap-2"
                        >
                            <i className="fa fa-plus"></i>
                            <span>新建提醒</span>
                        </button>
                    )}
                    <p className="mt-3 text-xs text-gray-500">私有提醒每个用户最多5个，默认为私有。</p>
                </div>

                {/* 提醒列表 */}
                <div
                    className="space-y-4"
                    onScroll={(e) => {
                        const { scrollTop, clientHeight, scrollHeight } = e.target
                        if (scrollHeight - scrollTop - clientHeight < 50 && !isLoading && hasMore) {
                            loadReminders(true)
                        }
                    }}
                >
                    {reminders.length === 0 && !isLoading ? (
                        <div className="text-center text-gray-500 py-8">
                            <i className="fa fa-bell-o text-4xl mb-2" aria-hidden="true"></i>
                            <p className="text-sm">暂无提醒</p>
                        </div>
                    ) : (
                        <>
                            {reminders.map((reminder) => (
                                <ReminderItem
                                    key={reminder.id}
                                    reminder={reminder}
                                    draggable
                                    isDragOver={dragOverId === reminder.id}
                                    onDragStart={(e) => {
                                        e.dataTransfer.effectAllowed = 'move'
                                        e.dataTransfer.setData('text/plain', String(reminder.id))
                                        setDraggingId(reminder.id)
                                    }}
                                    onDragOver={(e) => {
                                        e.preventDefault()
                                        e.dataTransfer.dropEffect = 'move'
                                        if (dragOverId !== reminder.id) {
                                            setDragOverId(reminder.id)
                                        }
                                    }}
                                    onDrop={(e) => {
                                        e.preventDefault()
                                        if (!draggingId || draggingId === reminder.id || isSavingOrder) {
                                            setDragOverId(null)
                                            setDraggingId(null)
                                            return
                                        }

                                        const items = [...reminders]
                                        const fromIndex = items.findIndex(r => r.id === draggingId)
                                        const toIndex = items.findIndex(r => r.id === reminder.id)
                                        if (fromIndex === -1 || toIndex === -1) {
                                            setDragOverId(null)
                                            setDraggingId(null)
                                            return
                                        }
                                        const [moved] = items.splice(fromIndex, 1)
                                        items.splice(toIndex, 0, moved)

                                        setReminders(items)
                                        setIsSavingOrder(true)
                                        setReminderOrder(items.map(r => r.id))
                                            .catch((error) => {
                                                console.error('Failed to save local order:', error)
                                                alert('保存排序失败: ' + error.message)
                                            })
                                            .finally(() => setIsSavingOrder(false))

                                        setDragOverId(null)
                                        setDraggingId(null)
                                    }}
                                    onDragEnd={() => {
                                        setDragOverId(null)
                                        setDraggingId(null)
                                    }}
                                />
                            ))}

                            {isLoading && (
                                <div className="flex flex-col items-center justify-center py-4 text-gray-400 gap-2">
                                    <i className="fa fa-circle-o-notch fa-spin text-sm"></i>
                                    <span className="text-xs">加载中...</span>
                                </div>
                            )}

                            {!hasMore && reminders.length > 0 && (
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

export default ReminderSidebar
