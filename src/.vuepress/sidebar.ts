import { sidebar } from "vuepress-theme-hope";

export default sidebar({
  "/": [
    "",
    {
      text: "如何使用",
      icon: "laptop-code",
      prefix: "demo/",
      link: "demo/",
      children: "structure",
    },
    {
      text: "红队",
      icon: "user-secret",
      prefix: "redteam/",
      children: "structure",
    },
    {
      text: "蓝队",
      icon: "file-contract",
      prefix: "blueteam/",
      children: "structure",
    },
    {
      text: "Python",
      icon: "laptop-code",
      prefix: "Python/",
      children: "structure",
    },
    {
      text: "随笔",
      icon: "book-open",
      prefix: "light-mind/",
      children: "structure",
    },
    {
      text: "渗透靶场",
      icon: "crosshairs",
      prefix: "渗透靶场/",
      children: "structure",
    },
    "intro",
  ],
});
