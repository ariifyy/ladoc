// Theme toggle logic
const toggleBtn = document.getElementById("themeToggle");
const icon = document.getElementById("themeIcon");

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  icon.src = theme === "dark" ? "moon.png" : "sun.png";
  icon.alt = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
}

toggleBtn.addEventListener("click", () => {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  setTheme(newTheme);
});

// Load saved theme
window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "dark";
  setTheme(savedTheme);
});
