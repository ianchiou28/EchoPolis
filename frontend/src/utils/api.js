/**
 * API 工具函数
 * 自动处理生产环境的 baseURL
 */

// 获取 API 基础路径
export const getApiBaseUrl = () => {
  return import.meta.env.PROD ? '/echopolis' : ''
}

// 获取静态资源基础路径
export const getAssetBaseUrl = () => {
  return import.meta.env.BASE_URL || '/'
}

// 构建完整的 API URL
export const buildApiUrl = (path) => {
  const base = getApiBaseUrl()
  // 确保 path 以 / 开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${base}${normalizedPath}`
}

// 构建静态资源 URL
export const buildAssetUrl = (path) => {
  const base = getAssetBaseUrl()
  // 移除 path 开头的 /，因为 base 已经包含了
  const normalizedPath = path.startsWith('/') ? path.slice(1) : path
  return `${base}${normalizedPath}`
}

// 封装 fetch 请求
export const apiFetch = async (path, options = {}) => {
  const url = buildApiUrl(path)
  return fetch(url, options)
}

// ============ 管理员 API 工具函数 ============

// 获取管理员密钥
export const getAdminKey = () => {
  return localStorage.getItem('admin_key') || ''
}

// 设置管理员密钥
export const setAdminKey = (key) => {
  localStorage.setItem('admin_key', key)
}

// 清除管理员密钥
export const clearAdminKey = () => {
  localStorage.removeItem('admin_key')
}

// 管理员 API 请求
export const adminApiFetch = async (path, options = {}) => {
  const adminKey = getAdminKey()
  const separator = path.includes('?') ? '&' : '?'
  const url = buildApiUrl(`${path}${separator}admin_key=${adminKey}`)
  return fetch(url, options)
}

// 管理员 POST 请求
export const adminApiPost = async (path, data = {}) => {
  const adminKey = getAdminKey()
  const url = buildApiUrl(`${path}?admin_key=${adminKey}`)
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
}
