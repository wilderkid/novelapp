import axios from 'axios'

const API_URL = '/api'

// 获取所有分卷
const getVolumes = async (projectId) => {
  try {
    const response = await axios.get(`${API_URL}/projects/${projectId}/volumes`)
    return response.data
  } catch (error) {
    console.error('获取分卷数据失败:', error)
    throw error
  }
}

// 获取单个分卷
const getVolume = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/volumes/${id}`)
    return response.data
  } catch (error) {
    console.error('获取分卷数据失败:', error)
    throw error
  }
}

// 保存分卷
const saveVolume = async (volumeData) => {
  try {
    console.log('发送的分卷数据:', volumeData)
    if (volumeData.id) {
      // 更新现有分卷
      const response = await axios.put(`${API_URL}/volumes/${volumeData.id}`, volumeData)
      return response.data
    } else {
      // 创建新分卷 - 需要project_id
      const response = await axios.post(`${API_URL}/projects/${volumeData.project_id}/volumes`, volumeData)
      return response.data
    }
  } catch (error) {
    console.error('保存分卷失败:', error)
    console.error('错误详情:', error.response?.data)
    throw error
  }
}

// 删除分卷
const deleteVolume = async (id) => {
  try {
    await axios.delete(`${API_URL}/volumes/${id}`)
  } catch (error) {
    console.error('删除分卷失败:', error)
    throw error
  }
}

export default {
  getVolumes,
  getVolume,
  saveVolume,
  deleteVolume
}
