document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("mobile_menu");
  const menu = document.getElementById("navbar_menu");

  // Mobile hamburger toggle
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

    const dropdownArrows = document.querySelectorAll(".dropdown_arrow");
    dropdownArrows.forEach(arrow => {
      arrow.src = theme === "dark"
        ? "assets/down_arrow_dark.png"
        : "assets/down_arrow_light.png";
    });

    
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

  // Close mobile menu when clicking outside
  document.addEventListener("click", (event) => {
    if (!toggle.classList.contains("active")) return;

    const isClickInsideToggle = toggle.contains(event.target);
    const isClickInsideMenu = menu.contains(event.target);

    if (!isClickInsideToggle && !isClickInsideMenu) {
      toggle.classList.remove("active");
      menu.classList.remove("active");
    }
  });

  // Helper function to detect mobile viewport
  function isMobile() {
    return window.matchMedia("(max-width: 768px)").matches;
  }

  const dropdowns = document.querySelectorAll(".dropdown");

  dropdowns.forEach(dropdown => {
    const toggleLink = dropdown.querySelector(".dropdown_toggle");
    let timeoutId;

    // Mobile: toggle dropdown open/close on click
    toggleLink.addEventListener("click", (e) => {
      if (!isMobile()) return; // Only on mobile

      e.preventDefault();

      const isOpen = dropdown.classList.contains("open");

      // Close all dropdowns first
      dropdowns.forEach(d => d.classList.remove("open"));

      if (!isOpen) {
        dropdown.classList.add("open");
      }
    });

    // Desktop: open dropdown on hover with a small delay to prevent flicker
    dropdown.addEventListener("mouseenter", () => {
      if (isMobile()) return;

      // Clear any scheduled close
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }

      // Close other dropdowns
      dropdowns.forEach(d => {
        if (d !== dropdown) d.classList.remove("open");
      });

      dropdown.classList.add("open");
    });

    // Desktop: close dropdown on mouse leave with delay for smooth UX
    dropdown.addEventListener("mouseleave", () => {
      if (isMobile()) return;

      timeoutId = setTimeout(() => {
        dropdown.classList.remove("open");
      }, 200); // 200ms delay to avoid flicker
    });
  });

  // Click outside closes open dropdowns (both desktop and mobile)
  document.addEventListener("click", (e) => {
    if (e.target.closest(".dropdown")) return;

    dropdowns.forEach(dropdown => dropdown.classList.remove("open"));
  });

  // Optional: close dropdown and mobile menu when clicking a dropdown menu item (mobile only)
  document.querySelectorAll(".dropdown_menu a").forEach(link => {
    link.addEventListener("click", () => {
      if (!isMobile()) return;

      dropdowns.forEach(dropdown => dropdown.classList.remove("open"));

      toggle.classList.remove("active");
      menu.classList.remove("active");
    });
  });
});


// Typewriter effect
document.addEventListener("DOMContentLoaded", () => {
  const typewriterEl = document.getElementById("typewriter");
  const phrases = [
    "Protect your data",
    "Spot phishing scams",
    "Use our security tools",
    "Download our desktop app"
  ];

  let currentPhraseIndex = 0;
  let currentCharIndex = 0;
  let isDeleting = false;

  const typingSpeed = 60;
  const deletingSpeed = 20;
  const pauseAfterTyping = 2000;
  const pauseAfterDeleting = 200;

  function typewriterCycle() {
    const currentPhrase = phrases[currentPhraseIndex];

    if (!isDeleting) {
      typewriterEl.textContent = currentPhrase.substring(0, currentCharIndex + 1);
      currentCharIndex++;

      if (currentCharIndex === currentPhrase.length) {
        setTimeout(() => {
          isDeleting = true;
          typewriterCycle();
        }, pauseAfterTyping);
      } else {
        setTimeout(typewriterCycle, typingSpeed);
      }
    } else {
      typewriterEl.textContent = currentPhrase.substring(0, currentCharIndex - 1);
      currentCharIndex--;

      if (currentCharIndex === 0) {
        isDeleting = false;
        currentPhraseIndex = (currentPhraseIndex + 1) % phrases.length;
        setTimeout(typewriterCycle, pauseAfterDeleting);
      } else {
        setTimeout(typewriterCycle, deletingSpeed);
      }
    }
  }

  if (typewriterEl) {
    typewriterCycle();
  }
});


// Copy to clipboard
  // Universal copy-to-clipboard handler for all buttons with class "copy-btn"
  document.body.addEventListener("click", (e) => {
    if (!e.target.classList.contains("copyBtn")) return;

    const btn = e.target;
    let textToCopy = "";

    // Use data-copy-target selector to find element to copy text/value from
    const targetSelector = btn.getAttribute("data-copy-target");
    if (targetSelector) {
      const targetEl = document.querySelector(targetSelector);
      if (targetEl) textToCopy = targetEl.value || targetEl.textContent || "";
    } else if (btn.previousElementSibling && btn.previousElementSibling.value !== undefined) {
      // fallback: previous sibling input value
      textToCopy = btn.previousElementSibling.value;
    }

    if (!textToCopy) return;

    // Write text to clipboard and give user feedback
    navigator.clipboard.writeText(textToCopy).then(() => {
      const originalText = btn.textContent;
      btn.textContent = "Copied!";
      setTimeout(() => {
        btn.textContent = originalText;
      }, 1500);
    }).catch(() => {
      btn.textContent = "Failed to copy";
    });
  });