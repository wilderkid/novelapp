## [#](#ueditorplus-软件介绍) UEditorPlus 软件介绍

基于 UEditor 二次开发的富文本编辑器，让UEditor重新焕发活力

![UEditorPlus](https://ms-assets.modstart.com/demo/UEditorPlus_v2.1.0.jpeg)

## [#](#功能亮点) 功能亮点

- 全新的UI外观，使用字体图标替换原有图片图标
- 移除过时、无用的插件支持，不断完善使用体验
- 图片、文件、视频上传配置化定制增强
- 演示界面重构，右上角可直接查看当前演示界面代码
- 兼容现有UEditor，实现无缝切换
- AI功能支持，支持续写、翻译等功能

## [#](#在线演示) 在线演示

- [https://open-demo.modstart.com/ueditor-plus/\_examples/ (opens new window)](https://open-demo.modstart.com/ueditor-plus/_examples/)

## [#](#使用教程) 使用教程

### [#](#原生使用) 原生使用

```html
<script id="editor" type="text/plain" style="height:300px;"></script>
<script
  type="text/javascript"
  src="/path/to/UEditorPlus/ueditor.config.js"
></script>
<script
  type="text/javascript"
  src="/path/to/UEditorPlus/ueditor.all.js"
></script>
<script>
  var ue = UE.getEditor("editor", {
    // ... 更多配置
  });
</script>
```

1  
2  
3  
4  
5  
6  
7  
8  
9

### [#](#vue2-使用) vue2 使用

① 安装插件支持

```bash
npm i --save vue-ueditor-wrap@2.x
# 或
yarn add --save vue-ueditor-wrap@2.x
```

1  
2  
3

② 解压 UEditorPlus 到静态资源目录

复制 `dist-min` 到项目 `public/static/UEditorPlus/` 目录

③ 引入组件并使用

```html
<template>
  <div>
    <vue-ueditor-wrap
      v-model="content"
      editor-id="editor"
      :config="editorConfig"
      :editorDependencies="['ueditor.config.js','ueditor.all.js']"
      style="height:500px;"
    />
  </div>
</template>
<script>
  import VueUeditorWrap from "vue-ueditor-wrap";

  export default {
    components: {
      VueUeditorWrap,
    },
    data() {
      return {
        content: "<p>Hello UEditorPlus</p>",
        editorConfig: {
          // 后端服务地址，后端处理参考
          // https://open-doc.modstart.com/ueditor-plus/backend.html
          serverUrl: "/api/path/to/server",
          UEDITOR_HOME_URL: "/static/UEditorPlus/",
          UEDITOR_CORS_URL: "/static/UEditorPlus/",
        },
      };
    },
  };
</script>
```

1  
2  
3  
4  
5  
6  
7  
8  
9  
10  
11  
12  
13  
14  
15  
16  
17  
18  
19  
20  
21  
22  
23  
24  
25  
26  
27  
28  
29  
30  
31

### [#](#vue3-使用) vue3 使用

① 安装插件支持

```bash
npm i --save vue-ueditor-wrap@3.x
# 或
yarn add --save vue-ueditor-wrap@3.x
```

1  
2  
3

② 解压 UEditorPlus 到静态资源目录

复制 `dist-min` 到项目 `public/static/UEditorPlus/` 目录

③ 引入组件并使用

**main.js**

```js
import { createApp } from "vue";
import App from "./App.vue";
import VueUeditorWrap from "vue-ueditor-wrap";

createApp(App).use(VueUeditorWrap).mount("#app");
```

1  
2  
3  
4  
5

**App.vue**

```html
<template>
  <div>
    <vue-ueditor-wrap
      v-model="content"
      editor-id="editor"
      :config="editorConfig"
      :editorDependencies="['ueditor.config.js','ueditor.all.js']"
      style="height:500px;"
    />
  </div>
</template>

<script setup>
  import { ref } from "vue";

  const content = ref("<p>Hello UEditorPlus</p>");
  const editorConfig = {
    // 后端服务地址，后端处理参考
    // https://open-doc.modstart.com/ueditor-plus/backend.html
    serverUrl: "/api/path/to/server",
    UEDITOR_HOME_URL: "/static/UEditorPlus/",
    UEDITOR_CORS_URL: "/static/UEditorPlus/",
  };
</script>
```

1  
2  
3  
4  
5  
6  
7  
8  
9  
10  
11  
12  
13  
14  
15  
16  
17  
18  
19  
20  
21  
22  
23

### [#](#react-使用) react 使用

① 安装插件支持

```bash
npm i --save react-ueditor-wrap
# 或
yarn add --save react-ueditor-wrap
```

1  
2  
3

② 解压 UEditorPlus 到静态资源目录

复制 `dist-min` 到项目 `public/static/UEditorPlus/` 目录

③ 引入组件并使用

```jsx
import RcUeditor from "react-ueditor-wrap";

function App() {
  const hanldeChage = (value) => {
    console.log("RcUeditor", value);
  };
  return (
    <div className="App">
      <div style={{ margin: "0 auto", maxWidth: "800px" }}>
        <RcUeditor
          value={"<p>Hello UEditorPlus</p>"}
          ueditorUrl={"/static/UEditorPlus/ueditor.all.js"}
          ueditorConfigUrl={"/static/UEditorPlus/ueditor.config.js"}
          editorConfig={{
            // 后端服务地址，后端处理参考
            // https://open-doc.modstart.com/ueditor-plus/backend.html
            initialFrameWidth: "100%",
            serverUrl: "/api/path/to/server",
            UEDITOR_HOME_URL: "/static/UEditorPlus/",
            UEDITOR_CORS_URL: "/static/UEditorPlus/",
          }}
          onChange={hanldeChage}
        />
      </div>
    </div>
  );
}

export default App;
```

1  
2  
3  
4  
5  
6  
7  
8  
9  
10  
11  
12  
13  
14  
15  
16  
17  
18  
19  
20  
21  
22  
23  
24  
25  
26  
27  
28

## [#](#二次开发) 二次开发

### [#](#第一步-clone代码到本地) 第一步，clone代码到本地

```bash
git clone https://gitee.com/modstart-lib/ueditor-plus.git
```

1

### [#](#第二步-开始功能开发) 第二步，开始功能开发

使用浏览器打开 `_examples/index.html` 页面相关内容，完成功能开发

### [#](#第三步-打包) 第三步，打包

```bash
npm install
grunt default
```

1  
2

## [#](#关于bug反馈与维护) 关于Bug反馈与维护

- 众所周知 UEditor 使用的人数多，目前已经累积了N个Bug，开源不易需要大家共同维护

对于在实际使用中遇到的问题，如果急需解决推荐使用 [悬赏Issue (opens new window)](https://gitee.com/modstart-lib/ueditor-plus/reward_issues/new) ，这样让更多有能力的开发者有共同维护的动力

## [#](#使用交流) 使用交流

- QQ群：539492162
- 使用问题或者改进建议，欢迎进群交流

## [#](#版权说明) 版权说明

本文档参考了以下原UEditor网站

- [http://fex.baidu.com/ueditor/ (opens new window)](http://fex.baidu.com/ueditor/)

Last Updated: an hour ago
