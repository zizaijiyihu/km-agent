/**
 * 本地提醒排序缓存（IndexedDB）
 * 仅在当前浏览器生效，不依赖后端
 */

const DB_NAME = 'km-agent-reminder-order'
const DB_VERSION = 1
const STORE_NAME = 'reminder-order'
const DEFAULT_KEY = 'default'

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onerror = () => {
      console.error('IndexedDB 打开失败:', request.error)
      reject(request.error)
    }

    request.onsuccess = () => resolve(request.result)

    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'key' })
      }
    }
  })
}

async function readOrder(key = DEFAULT_KEY) {
  try {
    const db = await openDB()
    const tx = db.transaction([STORE_NAME], 'readonly')
    const store = tx.objectStore(STORE_NAME)
    const request = store.get(key)

    return await new Promise((resolve, reject) => {
      request.onsuccess = () => {
        resolve(request.result?.ids || [])
      }
      request.onerror = () => reject(request.error)
    })
  } catch (err) {
    console.error('读取排序失败:', err)
    return []
  }
}

async function writeOrder(ids, key = DEFAULT_KEY) {
  try {
    const db = await openDB()
    const tx = db.transaction([STORE_NAME], 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    store.put({ key, ids })
    return await new Promise((resolve, reject) => {
      tx.oncomplete = () => resolve()
      tx.onerror = () => reject(tx.error)
    })
  } catch (err) {
    console.error('写入排序失败:', err)
  }
}

export async function getReminderOrder(orderKey = DEFAULT_KEY) {
  return readOrder(orderKey)
}

export async function setReminderOrder(ids, orderKey = DEFAULT_KEY) {
  return writeOrder(ids, orderKey)
}

/**
 * 根据本地排序重排提醒列表，并自动清理无效ID
 * @param {Array} reminders
 * @param {string} orderKey
 * @returns {Promise<Array>} 排好序的提醒列表
 */
export async function applyReminderOrder(reminders, orderKey = DEFAULT_KEY) {
  const orderIds = await readOrder(orderKey)
  if (!orderIds.length) {
    return reminders
  }

  const reminderMap = new Map(reminders.map(r => [r.id, r]))
  const ordered = []
  const seen = new Set()

  orderIds.forEach(id => {
    const item = reminderMap.get(id)
    if (item) {
      ordered.push(item)
      seen.add(id)
    }
  })

  reminders.forEach(r => {
    if (!seen.has(r.id)) {
      ordered.push(r)
    }
  })

  // 如果有无效ID或新增提醒，回写最新顺序
  if (ordered.length !== orderIds.length || reminders.length !== orderIds.length) {
    writeOrder(ordered.map(r => r.id), orderKey)
  }

  return ordered
}
