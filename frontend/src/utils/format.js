/**
 * 格式化工具函数
 */

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期对象或字符串
 * @returns {string} 格式化后的日期时间字符串
 */
export function formatDateTime(date) {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('zh-CN')
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期对象或字符串
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date) {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
}

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @returns {string} 格式化后的金额字符串
 */
export function formatCurrency(amount) {
  if (amount === null || amount === undefined) return '-'
  return `¥${Number(amount).toFixed(2)}`
}

/**
 * 格式化状态
 * @param {boolean} status - 状态值
 * @returns {string} 状态文本
 */
export function formatStatus(status) {
  return status ? '正常' : '禁用'
}

/**
 * 截断文本
 * @param {string} text - 原始文本
 * @param {number} length - 最大长度
 * @returns {string} 截断后的文本
 */
export function truncateText(text, length = 20) {
  if (!text) return '-'
  return text.length > length ? text.substring(0, length) + '...' : text
}
