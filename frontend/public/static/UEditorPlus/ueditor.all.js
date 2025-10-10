/**
 * UEditorPlus 主文件
 * 这里只是一个占位符，请替换为实际的 UEditorPlus 主文件
 */
// 创建一个简单的模拟编辑器，以便测试
window.UE = {
  getEditor: function(id, config) {
    // 创建一个简单的模拟编辑器
    const editor = {
      id: id,
      config: config || {},
      ready: function(fn) {
        // 模拟编辑器准备就绪
        setTimeout(fn, 100);
      },
      getContent: function() {
        return document.querySelector(`#${id} iframe`).contentDocument.body.innerHTML;
      },
      setContent: function(content) {
        if (document.querySelector(`#${id} iframe`)) {
          document.querySelector(`#${id} iframe`).contentDocument.body.innerHTML = content;
        }
      },
      destroy: function() {
        // 模拟销毁编辑器
      }
    };

    // 创建一个简单的编辑器界面
    setTimeout(() => {
      const container = document.getElementById(id);
      if (container) {
        container.innerHTML = `
          <div style="border: 1px solid #ccc; height: 400px;">
            <div style="background-color: #f5f5f5; padding: 5px; border-bottom: 1px solid #ccc;">
              <button>加粗</button>
              <button>斜体</button>
              <button>下划线</button>
            </div>
            <iframe style="width: 100%; height: calc(100% - 40px); border: none;" 
                    srcdoc="<html><body contenteditable='true'>请输入内容...</body></html>"></iframe>
          </div>
        `;
      }
    }, 100);

    return editor;
  }
};
