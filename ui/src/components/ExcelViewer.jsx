import React, { useEffect, useMemo, useRef, useState } from 'react'
import * as XLSX from 'xlsx'
import useStore from '../store/useStore'

const MAX_ROWS_DISPLAY = 300

function ExcelViewer() {
  const isOpen = useStore(state => state.isExcelViewerOpen)
  const currentExcel = useStore(state => state.currentExcel)
  const closeExcelViewer = useStore(state => state.closeExcelViewer)
  const setExcelRow = useStore(state => state.setExcelRow)

  const [sheetNames, setSheetNames] = useState([])
  const [activeSheet, setActiveSheet] = useState(null)
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const workbookRef = useRef(null)
  const tableRef = useRef(null)
  const programScrollingRef = useRef(false) // 标记程序是否正在自动滚动
  const loadedFilenameRef = useRef(null) // 记录已加载的文件名

  // 加载 Excel 文件（仅当文件名变化时重新加载）
  useEffect(() => {
    const fetchExcel = async () => {
      if (!currentExcel) return

      // 如果是同一个文件，不重新加载
      if (loadedFilenameRef.current === currentExcel.filename && rows.length > 0) {
        return
      }

      setLoading(true)
      setError(null)
      setRows([])
      setSheetNames([])
      workbookRef.current = null
      loadedFilenameRef.current = currentExcel.filename

      try {
        const resp = await fetch(`/api/documents/${encodeURIComponent(currentExcel.filename)}/content`)
        if (!resp.ok) {
          throw new Error('无法获取文件内容')
        }

        const buffer = await resp.arrayBuffer()
        const workbook = XLSX.read(buffer, { type: 'array', cellDates: true })
        workbookRef.current = workbook

        const sheets = workbook.SheetNames || []
        setSheetNames(sheets)

        const defaultSheet = (currentExcel.sheetName && sheets.includes(currentExcel.sheetName))
          ? currentExcel.sheetName
          : sheets[0]

        if (defaultSheet) {
          loadSheet(defaultSheet)
        } else {
          setError('文件中没有可用的工作表')
        }
      } catch (err) {
        console.error('[ExcelViewer] 加载失败:', err)
        setError(err.message || '加载失败')
      } finally {
        setLoading(false)
      }
    }

    if (isOpen && currentExcel) {
      fetchExcel()
    } else {
      setRows([])
      setSheetNames([])
      setActiveSheet(null)
      setError(null)
      loadedFilenameRef.current = null
    }
  }, [isOpen, currentExcel?.filename])

  // 切换 sheet
  const loadSheet = (sheetName) => {
    if (!workbookRef.current) return
    const sheet = workbookRef.current.Sheets[sheetName]
    if (!sheet) return

    const data = XLSX.utils.sheet_to_json(sheet, { header: 1, blankrows: false, raw: true })
    setRows(data)
    setActiveSheet(sheetName)
  }

  // 当目标行号变化时滚动到新行（无动画）
  useEffect(() => {
    if (!currentExcel?.rowNumber || !tableRef.current || rows.length === 0) return

    const targetIndex = currentExcel.rowNumber - 1
    const rowElement = tableRef.current.querySelector(`[data-row-index="${targetIndex}"]`)
    if (rowElement) {
      // 标记程序正在自动滚动
      programScrollingRef.current = true

      // 使用 auto 行为，立即跳转无动画
      rowElement.scrollIntoView({ behavior: 'auto', block: 'center' })

      // 滚动完成后，重置程序滚动标记
      setTimeout(() => {
        programScrollingRef.current = false
      }, 100)
    }
  }, [rows, currentExcel?.rowNumber])

  // 监听用户手动滚动，防止与程序滚动冲突
  useEffect(() => {
    const scrollContainer = tableRef.current
    if (!scrollContainer) return

    let scrollTimeout = null
    const handleScroll = () => {
      // 如果是程序自动滚动，忽略此次滚动事件
      if (programScrollingRef.current) return

      // 清除之前的定时器
      if (scrollTimeout) {
        clearTimeout(scrollTimeout)
      }

      // 延迟处理，避免与程序滚动冲突
      scrollTimeout = setTimeout(() => {
        // 用户滚动后的处理逻辑（如果需要的话）
      }, 150)
    }

    scrollContainer.addEventListener('scroll', handleScroll, { passive: true })
    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll)
      if (scrollTimeout) {
        clearTimeout(scrollTimeout)
      }
    }
  }, [])

  const displayedRows = useMemo(() => rows.slice(0, MAX_ROWS_DISPLAY), [rows])
  const hasMore = rows.length > MAX_ROWS_DISPLAY
  const columnCount = useMemo(
    () => displayedRows.reduce((max, row) => Math.max(max, row.length), 0),
    [displayedRows]
  )
  const headers = useMemo(
    () => Array.from({ length: columnCount }, (_, i) => `列${i + 1}`),
    [columnCount]
  )

  if (!currentExcel || !isOpen) return null

  return (
    <div className={`${isOpen ? 'w-[720px] border-l border-gray-200' : 'w-0'} overflow-hidden transition-all duration-300 bg-white h-screen`}>
      <div className="w-[720px] h-full flex flex-col bg-white">
        {/* 头部工具栏 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-medium text-gray-800 truncate" title={currentExcel.filename}>
              {currentExcel.filename}
            </h3>
            {currentExcel.rowNumber && (
              <p className="text-xs text-gray-500">
                行 {currentExcel.rowNumber}
              </p>
            )}
          </div>
          {sheetNames.length > 0 && (
            <select
              className="mr-2 border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-primary/50 focus:border-primary"
              value={activeSheet || ''}
              onChange={(e) => loadSheet(e.target.value)}
            >
              {sheetNames.map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          )}
          <button
            onClick={closeExcelViewer}
            className="ml-2 w-8 h-8 flex items-center justify-center text-gray-500 hover:text-gray-700 rounded-full transition-colors flex-shrink-0"
          >
            <i className="fa fa-times" aria-hidden="true"></i>
          </button>
        </div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-auto scrollbar-thin bg-gray-50 p-3" ref={tableRef}>
          {loading && (
            <div className="flex items-center justify-center py-20 text-gray-500">
              <i className="fa fa-circle-o-notch fa-spin text-xl mr-2" aria-hidden="true"></i>
              <span>正在加载...</span>
            </div>
          )}

          {error && !loading && (
            <div className="text-center text-red-600 py-10">
              <i className="fa fa-exclamation-triangle text-3xl mb-2" aria-hidden="true"></i>
              <p>{error}</p>
            </div>
          )}

          {!loading && !error && displayedRows.length === 0 && (
            <div className="text-center text-gray-500 py-10">
              <i className="fa fa-table text-3xl mb-2" aria-hidden="true"></i>
              <p>暂无数据</p>
            </div>
          )}

          {!loading && !error && displayedRows.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse border border-gray-200 bg-white text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="border border-gray-200 px-3 py-2 text-left text-gray-600 w-14">行号</th>
                    {headers.map((header, idx) => (
                      <th key={idx} className="border border-gray-200 px-3 py-2 text-left text-gray-600">{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {displayedRows.map((row, rowIndex) => {
                    const absoluteRow = rowIndex + 1
                    const isTargetRow = currentExcel?.rowNumber === absoluteRow
                    return (
                      <tr
                        key={rowIndex}
                        data-row-index={rowIndex}
                        className={`border-b border-gray-200 ${isTargetRow ? 'bg-yellow-50' : ''}`}
                        onClick={() => setExcelRow(absoluteRow)}
                      >
                        <td className="border border-gray-200 px-3 py-2 text-gray-500">{absoluteRow}</td>
                        {Array.from({ length: columnCount }).map((_, colIndex) => (
                          <td key={colIndex} className="border border-gray-200 px-3 py-2 align-top">
                            {row[colIndex] !== undefined && row[colIndex] !== null ? String(row[colIndex]) : ''}
                          </td>
                        ))}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
              {hasMore && (
                <p className="text-xs text-gray-400 mt-2">
                  仅展示前 {MAX_ROWS_DISPLAY} 行，如需更多可在文件中查看。
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ExcelViewer
