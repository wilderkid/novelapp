import axios from 'axios'

const API_URL = '/api'

// 获取所有章节
const getChapters = async (volumeId) => {
  try {
    const response = await axios.get(`${API_URL}/volumes/${volumeId}/chapters`)
    return response.data
  } catch (error) {
    console.error('获取章节数据失败:', error)
    throw error
  }
}

// 获取单个章节
const getChapter = async (id) => {
  try {
    if (!id) {
      return null
    }
    const response = await axios.get(`${API_URL}/chapters/${id}`)
    return response.data
  } catch (error) {
    console.error('获取章节数据失败:', error)
    throw error
  }
}

// 保存章节
const saveChapter = async (chapterData) => {
  try {
    console.log('发送的章节数据:', chapterData)
    if (chapterData.id) {
      // 更新现有章节
      // 只发送后端需要的字段，避免发送多余数据
      const payload = {
        title: chapterData.title,
        content: chapterData.content,
        word_count: chapterData.wordCount || chapterData.word_count || 0,
        order: chapterData.order,
        volume_id: chapterData.volume_id || chapterData.volumeId
      };
      console.log('清理后的更新 payload:', payload);
      const response = await axios.put(`${API_URL}/chapters/${chapterData.id}`, payload)
      return response.data
    } else {
      // 创建新章节 - 注意：后端路由是 /api/volumes/{volume_id}/chapters
      const response = await axios.post(`${API_URL}/volumes/${chapterData.volume_id}/chapters`, chapterData)
      return response.data
    }
  } catch (error) {
    console.error('保存章节失败:', error)
    console.error('错误详情:', error.response?.data)
    throw error
  }
}

// 删除章节
const deleteChapter = async (id) => {
  try {
    await axios.delete(`${API_URL}/chapters/${id}`)
  } catch (error) {
    console.error('删除章节失败:', error)
    throw error
  }
}

export default {
  getChapters,
  getChapter,
  saveChapter,
  deleteChapter
}
