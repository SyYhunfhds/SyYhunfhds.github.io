import { defineUserConfig } from "vuepress";
import { markdownExtPlugin } from '@vuepress/plugin-markdown-ext'; // VuePress官方拓展
import { markdownMathPlugin } from '@vuepress/plugin-markdown-math'; // VuePress数学拓展

import theme from "./theme.js";
//  
// 
export default defineUserConfig({
  base: "/",
  lang: "zh-CN",
  title: "SyYhunfhds",
  description: "SyYhunfhds Personal Blog",

  theme,

  // 和 PWA 一起启用
  // shouldPrefetch: false,
  plugins:[
    markdownExtPlugin({
      // 选项
      gfm: true,
      // 启用 GFM 表格
      // 启用 GFM 任务列表
      tasklist: true,
      component: true, // 启用 GFM 自定义容器
    }),
    markdownMathPlugin({
      // 选项
      copy: true, // 启用数学公式复制功能 // 仅限KateX引擎，MathJax引擎暂不支持此功能。
    }),
  ],
});
