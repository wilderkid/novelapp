// 前端配置文件
const config = {
  // API基础URL
  apiBaseUrl: 'http://localhost:9009',

  // 编辑器配置
  editor: {
    serverUrl: 'http://localhost:9009/api/ueditor',
    UEDITOR_HOME_URL: '/static/UEditorPlus/',
    UEDITOR_CORS_URL: '/static/UEditorPlus/',
    toolbars: [
      [
        "fullscreen", "source", "|",
        "undo", "redo", "|",
        "bold", "italic", "underline", "fontborder", "strikethrough", "superscript", "subscript", "removeformat", "formatmatch", "autotypeset", "blockquote", "pasteplain", "|",
        "forecolor", "backcolor", "insertorderedlist", "insertunorderedlist", "selectall", "cleardoc", "|",
        "rowspacingtop", "rowspacingbottom", "lineheight", "|",
        "customstyle", "paragraph", "fontfamily", "fontsize", "|",
        "directionalityltr", "directionalityrtl", "indent", "|",
        "justifyleft", "justifycenter", "justifyright", "justifyjustify", "|",
        "touppercase", "tolowercase", "|",
        "link", "unlink", "anchor", "|",
        "imagenone", "imageleft", "imageright", "imagecenter", "|",
        "simpleupload", "insertimage", "emotion", "scrawl", "insertvideo", "attachment", "insertframe", "insertcode", "pagebreak", "template", "background", "formula", "|",
        "horizontal", "date", "time", "spechars", "wordimage", "|",
        "inserttable", "deletetable", "insertparagraphbeforetable", "insertrow", "deleterow", "insertcol", "deletecol", "mergecells", "mergeright", "mergedown", "splittocells", "splittorows", "splittocols", "contentimport", "|",
        "print", "preview", "searchreplace", "help"
      ]
    ],
    autoSaveEnable: true,
    uploadServiceEnable: true,
    uploadServiceUpload: function(type, file, callback, option) {
      // 在实际应用中，这里会上传到后端服务器
      setTimeout(() => {
        callback.success({
          "state": "SUCCESS",
          "url": "https://ms-assets.modstart.com/demo/modstart.jpg",
        })
      }, 1000)
    }
  }
}

export default config
