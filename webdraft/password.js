//Password
//PASSWORD CHECKER
document.addEventListener("DOMContentLoaded", () => {
  // Get references to DOM elements
  const passwordInput = document.getElementById("passwordInput");
  const togglePasswordBtn = document.getElementById("togglePassword");
  const checkBreachBtn = document.getElementById("checkBreach");
  const breachResult = document.getElementById("breachResult");
  const strengthText = document.getElementById("strengthText");
  const crackTime = document.getElementById("crackTime");
  const entropyText = document.getElementById("entropy");

  //Get references to DOM elements for password generator
  const generatePasswordBtn = document.getElementById("generatePassword");
  const generatedPasswordInput = document.getElementById("generatedPassword");
  const passwordLengthInput = document.getElementById("passwordLength");
  const includeUppercaseCheckbox = document.getElementById("includeUppercase");
  const includeLowercaseCheckbox = document.getElementById("includeLowercase");
  const includeDigitsCheckbox = document.getElementById("includeDigits");
  const includeSymbolsCheckbox = document.getElementById("includeSymbols");
  const avoidAmbiguousCheckbox = document.getElementById("avoidAmbiguous");


  // Labels and colors corresponding to zxcvbn strength scores 0-4
  const strengthLabels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"];
  const strengthColors = ["#d32f2f", "#f57c00", "#fbc02d", "#388e3c", "#1976d2"];

  // Fetch Top 10k password list
  let commonPasswordsMap = new Map();
  let commonPasswordList = [];

  fetch('https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt')
    .then(res => {
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
      return res.text();
    })
    .then(text => {
      text.split('\n').forEach((pw, index) => {
        const password = pw.trim();
        if (password) {
          commonPasswordsMap.set(password.toLowerCase(), index + 1);
          commonPasswordList.push(password.toLowerCase());
        }
      });
      console.log(`Loaded ${commonPasswordList.length} common passwords.`);
    })
    .catch(err => {
      console.error("Failed to load common password list:", err);
    });




  // Calculate entropy in bits based on character sets used in the password
  function calculateEntropy(password) {
    let charsetSize = 0;
    if (/[a-z]/.test(password)) charsetSize += 26;         // lowercase letters
    if (/[A-Z]/.test(password)) charsetSize += 26;         // uppercase letters
    if (/\d/.test(password)) charsetSize += 10;            // digits 0-9
    if (/[^a-zA-Z0-9]/.test(password)) charsetSize += 32;  // symbols (approximate)
    if (charsetSize === 0) return 0;
    // Entropy formula: length * log2(charset size)
    return +(password.length * Math.log2(charsetSize)).toFixed(2);
  }

  // Format a large time value in seconds into human-readable string with units like years, trillions etc.
  function formatLargeTime(seconds) {
    if (seconds === 0) return "0 seconds";

    const units = [
      { name: "octillion years", seconds: 31536000 * 1e27 },
      { name: "septillion years", seconds: 31536000 * 1e24 },
      { name: "sextillion years", seconds: 31536000 * 1e21 },
      { name: "quintillion years", seconds: 31536000 * 1e18 },
      { name: "quadrillion years", seconds: 31536000 * 1e15 },
      { name: "trillion years", seconds: 31536000 * 1e12 },
      { name: "billion years", seconds: 31536000 * 1e9 },
      { name: "million years", seconds: 31536000 * 1e6 },
      { name: "thousand years", seconds: 31536000 * 1e3 },
      { name: "year", seconds: 31536000 },
    ];

    // Find the largest unit the time fits into and format accordingly
    for (const unit of units) {
      if (seconds >= unit.seconds) {
        const value = seconds / unit.seconds;
        return `${value.toFixed(2)} ${unit.name}`;
      }
    }

    // Fallback for smaller times: seconds, minutes, hours, days
    if (seconds < 60) return `${seconds.toFixed(0)} seconds`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(0)} minutes`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)} hours`;
    if (seconds < 31536000) return `${(seconds / 86400).toFixed(1)} days`;

    return `${seconds.toFixed(0)} seconds`; // fallback
  }

  // Update UI feedback as user types or updates password input
  function updateFeedback(password) {
    if (!password) {
    // Clear feedback if no password entered
      strengthText.textContent = "—";
      strengthText.style.color = "";
      crackTime.textContent = "—";
      entropyText.textContent = "—";
      breachResult.textContent = "";
      checkBreachBtn.disabled = true;  

      // Clear char type indicators
      document.getElementById("hasLower").classList.remove("active");
      document.getElementById("hasUpper").classList.remove("active");
      document.getElementById("hasNumber").classList.remove("active");
      document.getElementById("hasSymbol").classList.remove("active");
      return;
    }

    // Use zxcvbn library to evaluate password strength
    const result = zxcvbn(password);
    const score = result.score;

    // Update strength label and color based on score
    strengthText.textContent = strengthLabels[score];
    strengthText.style.color = strengthColors[score];

    // Display estimated crack time with friendly formatting
    const seconds = result.crack_times_seconds.offline_slow_hashing_1e4_per_second;
    crackTime.textContent = formatLargeTime(seconds);

    // Show calculated entropy
    entropyText.textContent = calculateEntropy(password);

    // Update character type indicators
    document.getElementById("hasLower").classList.toggle("active", /[a-z]/.test(password));
    document.getElementById("hasUpper").classList.toggle("active", /[A-Z]/.test(password));
    document.getElementById("hasNumber").classList.toggle("active", /[0-9]/.test(password));
    document.getElementById("hasSymbol").classList.toggle("active", /[^a-zA-Z0-9]/.test(password));

    // Clear breach result and enable breach check button
    breachResult.textContent = "";
    checkBreachBtn.disabled = false;
  }

  // Toggle password input visibility between password/text
  togglePasswordBtn.addEventListener("click", () => {
    const isHidden = passwordInput.type === "password";
    passwordInput.type = isHidden ? "text" : "password";
    togglePasswordBtn.textContent = isHidden ? "Hide" : "Show";
    togglePasswordBtn.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
  });

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

  // Update feedback live as user types password
  passwordInput.addEventListener("input", () => {
    updateFeedback(passwordInput.value);
  });

  checkBreachBtn.addEventListener("click", () => {
  const pwd = passwordInput.value;
  if (!pwd) return;

  breachResult.innerHTML = "🔍 Checking password security…";

  // SHA-1 hash helper
  async function sha1(str) {
    const buffer = new TextEncoder().encode(str);
    const hashBuffer = await crypto.subtle.digest("SHA-1", buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  }

  // HaveIBeenPwned breach checker and common password list check
  Promise.all([
    // Breach check (HIBP)
    sha1(pwd).then(fullHash => {
      const prefix = fullHash.slice(0, 5);
      const suffix = fullHash.slice(5);

      return fetch(`https://api.pwnedpasswords.com/range/${prefix}`)
        .then(res => res.text())
        .then(data => {
          const lines = data.split("\n");
          const match = lines.find(line => line.startsWith(suffix));
          if (match) {
            const count = parseInt(match.split(":")[1].trim());
            return `<div style="color:#d32f2f;">⚠️ Found in ${count.toLocaleString()} breach${count !== 1 ? "es" : ""}.</div>`;
          } else {
            return `<div style="color:#388e3c;">✅ No known breaches found.</div>`;
          }
        })
        .catch(() => `<div style="color:#d32f2f;">❌ Error checking breach status.</div>`);
    }),

    // Top 10k password list check
    new Promise(resolve => {
      const lowerPassword = pwd.toLowerCase();
      const exactRank = commonPasswordsMap.get(lowerPassword);
      let partialMatch = "";

      if (!exactRank) {
        for (const commonWord of commonPasswordList) {
          if (lowerPassword.includes(commonWord) && commonWord.length >= 4) {
            partialMatch = commonWord;
            break;
          }
        }
      }

      if (exactRank) {
        resolve(`<div style="color:#f57c00;">⚠️ This password is ranked #${exactRank} in the top 10,000 most common passwords.</div>`);
      } else if (partialMatch) {
        resolve(`<div style="color:#f57c00;">⚠️ Contains common word: <strong>${partialMatch}</strong>.</div>`);
      } else {
        resolve(`<div style="color:#388e3c;">✅ Not found in the top 10,000 common passwords.</div>`);
      }
    })
  ]).then(results => {
    breachResult.innerHTML = results.join("");
  });
});


// PASSWORD GENERATOR

  function generatePassword() {
    const generatePasswordBtn = document.getElementById("generatePassword");
    const generatedPasswordInput = document.getElementById("generatedPassword");
    const length = Number(passwordLengthInput.value);
    const includeUppercase = includeUppercaseCheckbox.checked;
    const includeLowercase = includeLowercaseCheckbox.checked;
    const includeDigits = includeDigitsCheckbox.checked;
    const includeSymbols = includeSymbolsCheckbox.checked;
    const avoidAmbiguous = avoidAmbiguousCheckbox.checked;

    const ambiguousChars = "{}[]()/\\'\"`~,;:.<>|il1Lo0O";

    let charset = "";
    if (includeLowercase) charset += "abcdefghijklmnopqrstuvwxyz";
    if (includeUppercase) charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if (includeDigits) charset += "0123456789";
    if (includeSymbols) charset += "!@#$%^&*_-+=|<>.?";

    if (avoidAmbiguous) {
      charset = charset
        .split("")
        .filter(c => !ambiguousChars.includes(c))
        .join("");
    }

    if (!charset) return "";

    let password = "";
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return password;
  }

  generatePasswordBtn.addEventListener("click", () => {
    const pwd = generatePassword();
    generatedPasswordInput.value = pwd;
  });
 

  // Initialize feedback UI with empty password on page load
  updateFeedback("");
});