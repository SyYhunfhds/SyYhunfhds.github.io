import { defineUserConfig } from "vuepress";

import theme from "./theme.js";

export default defineUserConfig({
  base: "/syy-v-hope-docs/",

  lang: "zh-CN",
  title: "SyYhunfhds",
  description: "SyYhunfhds Personal Blog",

  theme,

  // 和 PWA 一起启用
  // shouldPrefetch: false,
});
