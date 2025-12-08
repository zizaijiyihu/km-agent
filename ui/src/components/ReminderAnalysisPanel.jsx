import React, { useState, useEffect } from 'react'
import useStore from '../store/useStore'
import ReminderAnalysisCard from './ReminderAnalysisCard'

function ReminderAnalysisPanel() {
    const [isCollapsed, setIsCollapsed] = useState(false)
    // 从 store 获取数据
    const reminders = useStore(state => state.reminders)
    const isLoading = useStore(state => state.isRemindersLoading)
    const closedReminders = useStore(state => state.closedReminders)
    const closeReminder = useStore(state => state.closeReminder)

    // 监听三个侧边栏的打开状态
    const isKnowledgeSidebarOpen = useStore(state => state.isKnowledgeSidebarOpen)
    const isInstructionSidebarOpen = useStore(state => state.isInstructionSidebarOpen)
    const isReminderSidebarOpen = useStore(state => state.isReminderSidebarOpen)

    // 当任意侧边栏打开时，自动收起智能提醒面板
    useEffect(() => {
        if (isKnowledgeSidebarOpen || isInstructionSidebarOpen || isReminderSidebarOpen) {
            setIsCollapsed(true)
        }
    }, [isKnowledgeSidebarOpen, isInstructionSidebarOpen, isReminderSidebarOpen])

    // 过滤掉已关闭的提醒(检查过期时间)
    const now = Date.now()
    const visibleReminders = reminders.filter(r => {
        const closedRecord = closedReminders[r.id]
        // 如果没有关闭记录,或者已过期,则显示
        return !closedRecord || closedRecord.expiresAt <= now
    })

    // 如果没有可见的提醒，不渲染面板
    if (!isLoading && visibleReminders.length === 0) {
        return null
    }

    return (
        <div className="fixed right-0 top-1/2 -translate-y-1/2 transform z-20">
            <div
                className="relative transition-all duration-300"
                style={{
                    transform: isCollapsed
                        ? 'translateX(calc(100% - 24px))'
                        : 'translateX(0)'
                }}
            >
                {/* 抽屉把手 */}
                <button
                    type="button"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="absolute -left-12 top-1/2 -translate-y-1/2 text-gray-600 group"
                    aria-label={isCollapsed ? '展开提醒面板' : '收起提醒面板'}
                    aria-expanded={!isCollapsed}
                >
                    <div className="flex flex-col items-center gap-1.5 px-2 py-2 bg-white/90 border border-gray-200 rounded-l-2xl shadow-md hover:text-gray-800 hover:bg-white transition-all">
                        <span className="w-8 h-8 flex items-center justify-center text-gray-500">
                            <i className="fa fa-bell-o text-lg"></i>
                        </span>
                        <span className="text-[11px] font-medium text-gray-600">提醒</span>
                        <span className="w-6 h-6 flex items-center justify-center border border-gray-200 rounded-full bg-white shadow-sm">
                            <i className={`fa fa-chevron-${isCollapsed ? 'left' : 'right'} text-[9px]`}></i>
                        </span>
                    </div>
                </button>

                <div>
                    <div
                        className={`w-80 max-h-[80vh] overflow-y-auto scrollbar-thin bg-white/30 backdrop-blur-sm p-4 space-y-3 ${isCollapsed ? 'pointer-events-none' : ''}`}
                        style={{
                            borderTopLeftRadius: '16px',
                            borderBottomLeftRadius: '16px'
                        }}
                        aria-hidden={isCollapsed}
                    >

                        {/* 提醒卡片列表 */}
                        {isLoading ? (
                            <div className="flex flex-col items-center justify-center py-8 text-gray-400">
                                <i className="fa fa-circle-o-notch fa-spin text-xl mb-2"></i>
                                <span className="text-xs">加载中...</span>
                            </div>
                        ) : (
                            visibleReminders.map(reminder => (
                                <ReminderAnalysisCard
                                    key={reminder.id}
                                    reminder={reminder}
                                    onClose={closeReminder}
                                />
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ReminderAnalysisPanel
