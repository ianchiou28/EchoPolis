/**
 * API 工具函数
 * 自动处理生产环境的 baseURL
 */

// 获取 API 基础路径
export const getApiBaseUrl = () => {
  return import.meta.env.PROD ? '/echopolis' : ''
}

// 构建完整的 API URL
export const buildApiUrl = (path) => {
  const base = getApiBaseUrl()
  // 确保 path 以 / 开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${base}${normalizedPath}`
}

// 封装 fetch 请求
export const apiFetch = async (path, options = {}) => {
  const url = buildApiUrl(path)
  return fetch(url, options)
}
