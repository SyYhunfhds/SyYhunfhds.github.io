import { navbar } from "vuepress-theme-hope";

export default navbar([
  "/",
  "/redteam/",
  "/blueteam/",
  "/Python/",
  "/light-mind/",
  "/CTF/",
  "/渗透靶场/",
  {
    text: "渗透练习",
    link: "/渗透靶场/",
    icon: "crosshairs",
    prefix: "渗透靶场/",
  },
]);
