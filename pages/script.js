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
  "Protect your data",
  "Use our OSINT tools",
  "Spot the scams",
  "Guard your digital footprint"
];

let currentPhraseIndex = 0;
let currentCharIndex = 0;
let isDeleting = false;

const typingSpeed = 80;      // ms per character typing speed (slow)
const deletingSpeed = 30;    // ms per character deleting speed (fast)
const pauseAfterTyping = 1800;  // ms pause after full phrase typed
const pauseAfterDeleting = 300; // ms pause after deletion before next phrase

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
// Password breach checker using HIBP API
const form = document.getElementById("hibpForm");
const input = document.getElementById("passwordInput");
const resultDiv = document.getElementById("result");

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const password = input.value;
    resultDiv.textContent = "Checking...";

    const hash = await sha1(password);
    const prefix = hash.slice(0, 5);
    const suffix = hash.slice(5).toUpperCase();

    try {
      const res = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
      const text = await res.text();
      const lines = text.split("\n");
      const found = lines.find((line) => line.startsWith(suffix));
      if (found) {
        const count = found.split(":")[1].trim();
        resultDiv.innerHTML = `<span style="color: red;">⚠️ This password has been found ${count} times in data breaches.</span>`;
      } else {
        resultDiv.innerHTML = `<span style="color: green;">✅ This password was not found in known breaches.</span>`;
      }
    } catch (err) {
      resultDiv.textContent = "Error checking password.";
    }
  });
}

// SHA-1 hashing function for HIBP API
async function sha1(str) {
  const buffer = new TextEncoder().encode(str);
  const digest = await crypto.subtle.digest("SHA-1", buffer);
  return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, "0")).join("").toUpperCase();
}


// Show/hide password logic
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("passwordInput");

if (togglePassword && passwordInput) {
  togglePassword.addEventListener("click", () => {
    const isHidden = passwordInput.type === "password";
    passwordInput.type = isHidden ? "text" : "password";
    togglePassword.textContent = isHidden ? "Show" : "Hide"; 
  });
}
