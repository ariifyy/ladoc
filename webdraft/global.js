// ------ STYLING ------
// Dark/light mode toggle logic
const toggleBtn = document.getElementById("themeToggle");
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

if (toggleBtn) {
  toggleBtn.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    setTheme(newTheme);
  });
}

window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "dark";
  setTheme(savedTheme);
});

// Typewriter effect for landing page
const typewriterEl = document.getElementById("typewriter");
const phrases = [
  "Protect your data...",
  "Use our OSINT tools...",
  "Spot the scams...",
  "Guard your digital footprint...",
  "Download our desktop application..."
];

let currentPhraseIndex = 0;
let currentCharIndex = 0;
let isDeleting = false;

const typingSpeed = 60;      
const deletingSpeed = 30;    
const pauseAfterTyping = 1900; 
const pauseAfterDeleting = 300;

function typewriterCycle() {
  const currentPhrase = phrases[currentPhraseIndex];
  
  if (!isDeleting) {
    // Typing phase
    typewriterEl.textContent = currentPhrase.substring(0, currentCharIndex + 1);
    currentCharIndex++;
    
    if (currentCharIndex === currentPhrase.length) {
      // Finished typing, pause then delete
      setTimeout(() => {
        isDeleting = true;
        typewriterCycle();
      }, pauseAfterTyping);
    } else {
      setTimeout(typewriterCycle, typingSpeed);
    }
  } else {
    // Deleting phase
    typewriterEl.textContent = currentPhrase.substring(0, currentCharIndex - 1);
    currentCharIndex--;
    
    if (currentCharIndex === 0) {
      // Finished deleting, move to next phrase
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


// ------ FUNCTIONALITY ------
// Copy to clipboard

