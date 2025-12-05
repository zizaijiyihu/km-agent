import React, { useState, useRef, useEffect } from 'react'
import { updateInstruction, deleteInstruction } from '../services/api'
import useStore from '../store/useStore'

function InstructionItem({ instruction }) {
    const [isEditing, setIsEditing] = useState(false)
    const [editContent, setEditContent] = useState(instruction.content)
    const [isSaving, setIsSaving] = useState(false)
    const [isDeleting, setIsDeleting] = useState(false)
    const [isToggling, setIsToggling] = useState(false)
    const canEdit = instruction.is_editable !== false

    const updateInstructionInList = useStore(state => state.updateInstructionInList)
    const removeInstruction = useStore(state => state.removeInstruction)
    const isAdmin = useStore(state => state.isAdmin)

    const textareaRef = useRef(null)

    useEffect(() => {
        if (isEditing && textareaRef.current) {
            textareaRef.current.focus()
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
        }
    }, [isEditing])

    const handleSave = async () => {
        if (!editContent.trim() || isSaving || !canEdit) return

        setIsSaving(true)
        try {
            await updateInstruction(instruction.id, {
                content: editContent,
                is_active: instruction.is_active,
                priority: instruction.priority
            })

            updateInstructionInList(instruction.id, { content: editContent })
            setIsEditing(false)
        } catch (error) {
            console.error('Failed to update instruction:', error)
            alert('更新失败: ' + error.message)
        } finally {
            setIsSaving(false)
        }
    }

    const handleDelete = async () => {
        if (!canEdit) return
        if (!window.confirm('确定要删除这条指示吗？')) return

        setIsDeleting(true)
        try {
            await deleteInstruction(instruction.id)
            removeInstruction(instruction.id)
        } catch (error) {
            console.error('Failed to delete instruction:', error)
            alert('删除失败: ' + error.message)
            setIsDeleting(false)
        }
    }

    const handleTextareaInput = (e) => {
        setEditContent(e.target.value)
        e.target.style.height = 'auto'
        e.target.style.height = e.target.scrollHeight + 'px'
    }

    const handleToggleVisibility = async () => {
        if (isToggling || !canEdit) return

        const newIsPublic = !instruction.is_public
        if (newIsPublic && !isAdmin) {
            alert('仅管理员可设置公开')
            return
        }
        setIsToggling(true)
        try {
            await updateInstruction(instruction.id, { is_public: newIsPublic })
            updateInstructionInList(instruction.id, { is_public: newIsPublic ? 1 : 0 })
        } catch (error) {
            console.error('Failed to toggle instruction visibility:', error)
            alert('切换失败: ' + error.message)
        } finally {
            setIsToggling(false)
        }
    }

    return (
        <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow group">
            {isEditing ? (
                <div className="space-y-3">
                    <textarea
                        ref={textareaRef}
                        value={editContent}
                        onChange={handleTextareaInput}
                        className="w-full p-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none resize-none"
                        rows="3"
                        disabled={isSaving}
                    />
                    <div className="flex justify-end gap-2">
                        <button
                            onClick={() => {
                                setIsEditing(false)
                                setEditContent(instruction.content)
                            }}
                            className="px-3 py-1 text-xs text-gray-600 hover:bg-gray-100 rounded transition-colors"
                            disabled={isSaving}
                        >
                            取消
                        </button>
                        <button
                            onClick={handleSave}
                            className="px-3 py-1 text-xs text-white bg-primary hover:bg-primary/90 rounded transition-colors flex items-center gap-1"
                            disabled={isSaving}
                        >
                            {isSaving && <i className="fa fa-spinner fa-spin"></i>}
                            保存
                        </button>
                    </div>
                </div>
            ) : (
                <>
                    <div className="text-sm text-gray-800 whitespace-pre-wrap mb-3">
                        {instruction.content}
                    </div>
                    <div className="flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-400">
                                {new Date(instruction.created_at).toLocaleDateString()}
                            </span>
                            {isAdmin && (
                                <button
                                    onClick={handleToggleVisibility}
                                    className="flex items-center gap-1 text-xs px-2 py-1 rounded hover:bg-gray-100 transition-colors disabled:opacity-60"
                                    title={instruction.is_public ? '公开 - 点击切换为私有' : '私有 - 点击切换为公开'}
                                    disabled={isToggling || !canEdit}
                                >
                                    {isToggling ? (
                                        <i className="fa fa-spinner fa-spin text-gray-400"></i>
                                    ) : instruction.is_public ? (
                                        <>
                                            <i className="fa fa-globe text-green-500"></i>
                                            <span className="text-green-600">公开</span>
                                        </>
                                    ) : (
                                        <>
                                            <i className="fa fa-lock text-orange-500"></i>
                                            <span className="text-orange-600">私有</span>
                                        </>
                                    )}
                                </button>
                            )}
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setIsEditing(true)}
                                className="text-gray-400 hover:text-primary transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                                title={canEdit ? '编辑' : '仅创建者可编辑'}
                                disabled={!canEdit}
                            >
                                <i className="fa fa-pencil"></i>
                            </button>
                            <button
                                onClick={handleDelete}
                                className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                                title={canEdit ? '删除' : '仅创建者可删除'}
                                disabled={isDeleting || !canEdit}
                            >
                                {isDeleting ? (
                                    <i className="fa fa-spinner fa-spin"></i>
                                ) : (
                                    <i className="fa fa-trash-o"></i>
                                )}
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}

export default InstructionItem
