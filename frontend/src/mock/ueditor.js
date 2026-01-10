// UEditor 后端接口模拟
export default {
  // 获取配置
  "GET /api/ueditor": (req, res) => {
    res.json({
      imageActionName: "uploadimage" /* 执行上传图片的action名称 */,
      imageFieldName: "upfile" /* 提交的图片表单名称 */,
      imageMaxSize: 2048000 /* 上传大小限制，单位B */,
      imageAllowFiles: [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
      ] /* 上传图片格式显示 */,
      imageCompressEnable: true /* 是否压缩图片,默认是true */,
      imageCompressBorder: 1600 /* 图片压缩最长边限制 */,
      imageInsertAlign: "none" /* 插入的图片浮动方式 */,
      imageUrlPrefix: "" /* 图片访问路径前缀 */,
      imagePathFormat:
        "/upload/image/{yyyy}{mm}{dd}/{time}{rand:6}" /* 上传保存路径,可以自定义保存路径和文件名格式 */,
      /* 填充其他配置项 */
    });
  },

  // 上传图片
  "POST /api/ueditor": (req, res) => {
    // 模拟上传成功
    res.json({
      state: "SUCCESS",
      url: "https://picsum.photos/seed/editor/800/400.jpg",
      title: "图片标题",
      original: "原始文件名.jpg",
      type: ".jpg",
      size: 123456,
    });
  },
};
