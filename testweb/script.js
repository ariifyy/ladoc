document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("mobile_menu");
  const menu = document.getElementById("navbar_menu");

  toggle.addEventListener("click", () => {
    toggle.classList.toggle("active");
    menu.classList.toggle("active");
  });

  const themeBtn = document.getElementById("themeToggleBtn");
  const icon = document.getElementById("themeIcon");

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);

    if (icon) {
      icon.src = theme === "dark" ? "assets/sun.png" : "assets/moon.png";
      icon.alt = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
    }

    const logo = document.getElementById("logo");
    if (logo) {
      logo.src = theme === "dark" ? "assets/logodark.png" : "assets/logolight.png";
    }
  }

  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme");
      const newTheme = currentTheme === "dark" ? "light" : "dark";
      setTheme(newTheme);
    });
  }

  const savedTheme = localStorage.getItem("theme") || "dark";
  setTheme(savedTheme);

  // Close menu when clicking outside of toggle or menu
  document.addEventListener("click", (event) => {
    if (!toggle.classList.contains("active")) return;

    const isClickInsideToggle = toggle.contains(event.target);
    const isClickInsideMenu = menu.contains(event.target);

    if (!isClickInsideToggle && !isClickInsideMenu) {
      toggle.classList.remove("active");
      menu.classList.remove("active");
    }
  });
});
