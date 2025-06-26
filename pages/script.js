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

// Unified password toggle visibility for all password-wrapper blocks
document.querySelectorAll('.toggle-password').forEach(toggleBtn => {
  toggleBtn.addEventListener('click', () => {
    const wrapper = toggleBtn.closest('.password-wrapper');
    if (!wrapper) return;

    const input = wrapper.querySelector('.password-input');
    if (!input) return;

    if (input.type === 'password') {
      input.type = 'text';
      toggleBtn.textContent = 'Hide';
      toggleBtn.setAttribute('aria-label', 'Hide password');
    } else {
      input.type = 'password';
      toggleBtn.textContent = 'Show';
      toggleBtn.setAttribute('aria-label', 'Show password');
    }
  });
});



// Password strength checking
const strengthMeter = document.getElementById("strengthMeter");
const strengthText = document.getElementById("strengthText");
const entropyText = document.getElementById("entropyValue");
const tipsList = document.getElementById("passwordTips");
const strengthPasswordInput = document.getElementById("strengthPasswordInput");

if (strengthPasswordInput) {
  strengthPasswordInput.addEventListener("input", () => {
    const password = strengthPasswordInput.value;
    const score = calculatePasswordScore(password);
    const entropy = calculateEntropy(password);

    if (strengthMeter) strengthMeter.value = score;
    if (strengthText) strengthText.textContent = getStrengthLabel(score);
    if (entropyText) entropyText.textContent = `${entropy.toFixed(2)} bits`;
    if (tipsList) tipsList.innerHTML = generateTips(password).map(tip => `<li>${tip}</li>`).join("");
  });
}

function calculatePasswordScore(password) {
  let score = 0;
  if (!password) return score;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return score;
}

function getStrengthLabel(score) {
  switch (score) {
    case 0:
    case 1:
      return "Very Weak";
    case 2:
      return "Weak";
    case 3:
      return "Moderate";
    case 4:
      return "Strong";
    case 5:
      return "Very Strong";
    default:
      return "";
  }
}

function calculateEntropy(password) {
  let charsetSize = 0;
  if (/[a-z]/.test(password)) charsetSize += 26;
  if (/[A-Z]/.test(password)) charsetSize += 26;
  if (/[0-9]/.test(password)) charsetSize += 10;
  if (/[^A-Za-z0-9]/.test(password)) charsetSize += 32; // Simplified symbols set
  return password.length * Math.log2(charsetSize || 1);
}

function generateTips(password) {
  const tips = [];
  if (password.length < 12) tips.push("Use at least 12 characters.");
  if (!/[A-Z]/.test(password)) tips.push("Include uppercase letters.");
  if (!/[a-z]/.test(password)) tips.push("Include lowercase letters.");
  if (!/[0-9]/.test(password)) tips.push("Add numbers.");
  if (!/[^A-Za-z0-9]/.test(password)) tips.push("Use special characters (e.g. !@#$%).");
  return tips;
}

// Entropy popup
const entropyInfoBtn = document.getElementById("entropyInfoBtn");
if (entropyInfoBtn) {
  entropyInfoBtn.addEventListener("click", () => {
    alert("Password entropy is a measure of how unpredictable a password is. Higher entropy means better resistance against brute-force attacks.");
  });
}

window.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generatePasswordBtn");
  const passwordOutput = document.getElementById("generatedPassword");
  const lengthInput = document.getElementById("passwordLength");
  const uppercaseCheckbox = document.getElementById("includeUppercase");
  const lowercaseCheckbox = document.getElementById("includeLowercase");
  const digitsCheckbox = document.getElementById("includeDigits");
  const symbolsCheckbox = document.getElementById("includeSymbols");
  const ambiguousCheckbox = document.getElementById("avoidAmbiguous");
  const copyBtn = document.getElementById("copyPasswordBtn");

  let lastGenerated = "";

  const CHAR_SETS = {
    upper: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    lower: "abcdefghijklmnopqrstuvwxyz",
    digits: "0123456789",
    symbols: "!@#$%^&*()_+-=[]{}|;:,.<>?/~",
    ambiguous: "Il1O0|`'\"\\"
  };

  function generatePassword() {
    const length = parseInt(lengthInput.value, 10) || 12;
    let characterPool = "";

    if (uppercaseCheckbox.checked) characterPool += CHAR_SETS.upper;
    if (lowercaseCheckbox.checked) characterPool += CHAR_SETS.lower;
    if (digitsCheckbox.checked) characterPool += CHAR_SETS.digits;
    if (symbolsCheckbox.checked) characterPool += CHAR_SETS.symbols;

    if (ambiguousCheckbox.checked) {
      const ambiguousChars = new Set(CHAR_SETS.ambiguous.split(""));
      characterPool = [...characterPool].filter(c => !ambiguousChars.has(c)).join("");
    }

    if (!characterPool) {
      passwordOutput.value = "Select at least one character set!";
      return;
    }

    let password = "";
    for (let i = 0; i < length; i++) {
      const index = Math.floor(Math.random() * characterPool.length);
      password += characterPool[index];
    }

    passwordOutput.value = password;
    lastGenerated = password;
    copyBtn.textContent = "Copy";
    copyBtn.disabled = false;
  }

  function copyPasswordToClipboard() {
    if (!lastGenerated) return;

    navigator.clipboard.writeText(lastGenerated)
      .then(() => {
        copyBtn.textContent = "Copied!";
        copyBtn.disabled = true;
      })
      .catch(() => {
        copyBtn.textContent = "Failed to copy!";
      });
  }

  if (generateBtn) generateBtn.addEventListener("click", generatePassword);
  if (copyBtn) copyBtn.addEventListener("click", copyPasswordToClipboard);
});


// Email breach checker
const emailForm = document.getElementById("emailForm");
const emailInput = document.getElementById("emailInput");
const emailResult = document.getElementById("emailResult");

if (emailForm) {
  emailForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    emailResult.innerHTML = "<p>Checking...</p>";

    try {
      const res = await fetch(`https://api.xposedornot.com/v1/check-email/${encodeURIComponent(email)}`);
      const data = await res.json();

      if (data && data.status === "success" && data.breaches.length > 0) {
        const breachesList = data.breaches.map(b => `<li>${b}</li>`).join("");
        emailResult.innerHTML = `
          <p>⚠️ This email was found in <strong>${data.breaches.length}</strong> breach(es).</p>
          <button id="toggleDetails">Show Details</button>
          <ul id="breachDetails" class="hidden">${breachesList}</ul>
        `;

        const toggleBtn = document.getElementById("toggleDetails");
        const breachDetails = document.getElementById("breachDetails");

        toggleBtn.addEventListener("click", () => {
          breachDetails.classList.toggle("hidden");
          toggleBtn.textContent = breachDetails.classList.contains("emailhidden") ? "Show Details" : "Hide Details";
        });
      } else if (data.status === "not_found") {
        emailResult.innerHTML = "<p>✅ No breaches found for this email.</p>";
      } else {
        emailResult.innerHTML = "<p>❗ Unexpected response from the API.</p>";
      }
    } catch (err) {
      emailResult.innerHTML = "<p>❌ Error checking email.</p>";
    }
  });
}

