"use strict";

const themeButton = document.getElementById("theme-toggle");
themeButton.hidden = false;
function updateThemeLabel() {
  themeButton.textContent =
    document.documentElement.dataset.theme === "dark" ? "Light theme" : "Dark theme";
}
function carryThemeToLinks() {
  document.querySelectorAll('a[href]').forEach((link) => {
    const url = new URL(link.href, window.location.href);
    if (url.origin === window.location.origin && url.pathname.endsWith(".html")) {
      url.searchParams.set("scoutTheme", document.documentElement.dataset.theme);
      link.href = url.href;
    }
  });
}
themeButton.addEventListener("click", () => {
  document.documentElement.dataset.theme =
    document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  updateThemeLabel();
  carryThemeToLinks();
});
updateThemeLabel();
carryThemeToLinks();

document.querySelectorAll("pre").forEach((pre) => {
  const wrapper = document.createElement("div");
  wrapper.className = "code-block";
  pre.before(wrapper);
  wrapper.append(pre);
  const button = document.createElement("button");
  button.type = "button";
  button.className = "copy-button";
  button.textContent = "Copy";
  button.setAttribute("aria-label", "Copy this command or prompt");
  wrapper.append(button);
  button.addEventListener("click", async () => {
    const status = document.getElementById("copy-status");
    try {
      await navigator.clipboard.writeText(pre.textContent);
      button.textContent = "Copied";
      status.textContent = "Copied to clipboard.";
      window.setTimeout(() => { button.textContent = "Copy"; }, 2000);
    } catch (error) {
      button.textContent = "Select and copy manually";
      status.textContent = "Clipboard unavailable. Select the text and copy it manually.";
      console.warn("Clipboard write failed", error);
      const range = document.createRange();
      range.selectNodeContents(pre);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
  });
});
