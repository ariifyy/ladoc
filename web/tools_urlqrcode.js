//Qr Code decoder and URL threat indicator

//INPUT METHODS (QR AND URL) ---------
// Cache DOM elements 
const urlSection = document.getElementById("urlSection");
const uploadSection = document.getElementById("uploadSection");

const urlInput = document.getElementById("urlInput");
const pasteResult = document.getElementById("pasteResult");

const dropZone = document.getElementById("dropZone");
const qrInput = document.getElementById("qrInput");
const qrCanvas = document.getElementById("qrCanvas");
const uploadResult = document.getElementById("uploadResult");

const ctx = qrCanvas.getContext("2d");

// Utility to escape HTML to prevent injection
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Show url and hide upload image
function showUrl() {
  urlSection.style.display = "block";
  uploadSection.style.display = "none";

  pasteResult.innerHTML = "";
  urlInput.value = "";
  clearCanvas();
  uploadResult.innerHTML = "";

  setActiveToggle("urlButton"); 
}

// Show upload image and hide url
function showUpload() {
  urlSection.style.display = "none";
  uploadSection.style.display = "block";

  pasteResult.innerHTML = "";
  urlInput.value = "";
  clearCanvas();
  uploadResult.innerHTML = "";

  setActiveToggle("uploadButton");
}


// Clear canvas drawing
function clearCanvas() {
  ctx.clearRect(0, 0, qrCanvas.width, qrCanvas.height);
}

// Handle image file dropped or selected
function handleImageFile(file) {
  if (!file.type.startsWith("image/")) {
    uploadResult.textContent = "Please upload a valid image file.";
    return;
  }

  const img = new Image();
  const reader = new FileReader();

  reader.onload = (e) => {
    img.src = e.target.result;
  };

  img.onload = () => {
    qrCanvas.width = img.width;
    qrCanvas.height = img.height;
    clearCanvas();

    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, qrCanvas.width, qrCanvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height);

    if (code) {
      uploadResult.innerHTML = `
        <strong>QR Code Content:</strong><br>
        <span>${escapeHtml(code.data)}</span>
      `;
    } else {
      uploadResult.textContent = "Invalid or no QR code found in the image.";
    }
  };

  reader.readAsDataURL(file);
}

// Setup event listeners after DOM content loaded
window.addEventListener("DOMContentLoaded", () => {
  // Toggle buttons
  document.querySelector("#inputMethodButtons button:nth-child(1)").addEventListener("click", showUrl);
  document.querySelector("#inputMethodButtons button:nth-child(2)").addEventListener("click", showUpload);

  // Drag & drop and click for image upload
  dropZone.addEventListener("click", () => {
    qrInput.value = '';
    qrInput.click();
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      handleImageFile(e.dataTransfer.files[0]);
    }
  });

  // File input change event
  qrInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      handleImageFile(e.target.files[0]);
    }
  });

  // Start with URL paste mode by default
  showUrl();
});

function setActiveToggle(activeId) {
  const buttons = document.querySelectorAll("#inputMethodButtons .toggle-btn");
  buttons.forEach(btn => btn.classList.remove("active"));
  document.getElementById(activeId).classList.add("active");
}




// URL THREAT ANALYSER LOGIC --------
async function analyzeUrl(url) {
  const results = [];

  // Regex for IP matching (matches full IPv4)
  const ipLikePattern = /\b((25[0-5]|2[0-4]\d|1\d\d|\d{1,2})\.){3}(25[0-5]|2[0-4]\d|1\d\d|\d{1,2})\b/;

  // Function to validate full IPv4 address
  function isValidIPv4(hostname) {
    const parts = hostname.split(".");
    if (parts.length !== 4) return false;
    return parts.every(part => {
      const n = Number(part);
      return /^\d+$/.test(part) && n >= 0 && n <= 255;
    });
  }

  // HTTPS / HTTP check
  if (url.startsWith("https://")) {
    results.push({
      name: "Uses HTTPS",
      status: "pass",
      message: "Uses secure HTTPS protocol."
    });
  } else if (url.startsWith("http://")) {
    results.push({
      name: "Uses HTTP",
      status: "warn",
      message: "Uses insecure HTTP protocol."
    });
  }

  // Get hostname safely
  let hostname = "";
  try {
    hostname = new URL(url).hostname;
  } catch {
    hostname = "";
  }

  // Check if hostname is a full IPv4
  const isFullIpHost = isValidIPv4(hostname);

  // IP address detection anywhere in hostname parts (including subdomains)
  const hostnamePartsSplit = hostname.split(/[\.\-]/);
  const candidates = [];
  for (let i = 0; i <= hostnamePartsSplit.length - 4; i++) {
    candidates.push(hostnamePartsSplit.slice(i, i + 4).join("."));
  }
  const foundIpLike = candidates.some(part => ipLikePattern.test(part)) || ipLikePattern.test(hostname);

  if (foundIpLike) {
    results.push({
      name: "IP Address in Hostname",
      status: "warn",
      message: "IP address detected in URL hostname. IP-based URLs might be suspicious or unsafe."
    });
  } else {
    results.push({
      name: "Domain Format",
      status: "pass",
      message: "No IP-like patterns detected in hostname."
    });
  }

  // TLD checking (skip if IP)
  if (!isFullIpHost) {
    try {
      const parts = hostname.split(".");
      const tld = parts[parts.length - 1].toLowerCase();
      const commonTLDs = ["com", "org", "net", "edu", "gov", "sg", "io"];
      if (!commonTLDs.includes(tld)) {
        results.push({
          name: "Unusual Top-Level Domain",
          status: "warn",
          message: `The domain ends in .${tld}, which is less commonly used. Be cautious if unfamiliar with this TLD.`
        });
      } else {
        results.push({
          name: "Recognized Top-Level Domain",
          status: "pass",
          message: `The domain ends in .${tld}, a commonly used and trusted top-level domain.`
        });
      }
    } catch {
      results.push({
        name: "TLD Parsing Error",
        status: "warn",
        message: "Unable to extract or analyze the top-level domain from the URL."
      });
    }
  } else {
    results.push({
      name: "TLD Check Skipped",
      status: "pass",
      message: "Skipped TLD check because the hostname is a direct IP address."
    });
  }

  // Subdomain structure check
  try {
    if (isFullIpHost) {
      results.push({
        name: "Subdomain Structure",
        status: "pass",
        message: `The URL uses a direct IP address (${hostname}). Subdomain checks are not applicable.`
      });
    } else {
      const parts = hostname.split(".");
      if (parts.length < 2) {
        results.push({
          name: "Subdomain Structure",
          status: "warn",
          message: "Unable to determine domain structure from the hostname."
        });
      } else {
        const tld = parts[parts.length - 1];
        const domain = parts[parts.length - 2];
        const mainDomain = `${domain}.${tld}`;
        const subdomains = parts.slice(0, -2);

        // Clean IP-like subdomains as single tokens
        const cleanedSubdomains = [];
        let skip = 0;
        for (let i = 0; i < subdomains.length; i++) {
          if (skip > 0) {
            skip--;
            continue;
          }
          const candidate = subdomains.slice(i, i + 4).join(".");
          if (ipLikePattern.test(candidate)) {
            cleanedSubdomains.push(candidate);
            skip = 3;
          } else {
            cleanedSubdomains.push(subdomains[i]);
          }
        }

        let status = "pass";
        let note = "Subdomain structure appears normal.";

        if (cleanedSubdomains.length >= 4) {
          status = "fail";
          note = "This URL has many nested subdomains, which is unusual and sometimes used to mislead users.";
        } else if (cleanedSubdomains.length >= 2) {
          status = "warn";
          note = "This URL contains multiple subdomains. Always verify that you're on the correct domain.";
        }

        results.push({
          name: "Subdomain Structure",
          status: status,
          message: `Detected ${cleanedSubdomains.length} subdomain level${cleanedSubdomains.length !== 1 ? "s" : ""}.<br>
            Subdomain: ${cleanedSubdomains.join(".") || "(none)"}<br>
            Main domain: ${mainDomain}<br>
            ${note}`
        });
      }
    }
  } catch {
    results.push({
      name: "Subdomain Check Error",
      status: "warn",
      message: "Could not parse subdomains from hostname."
    });
  }

  // URL shortener check
  const knownShorteners = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "rebrand.ly",
    "ow.ly", "is.gd", "buff.ly", "shorte.st", "bl.ink"
  ];

  // Extract domain from url
  const domainMatch = url.match(/^https?:\/\/([^\/]+)/i);
  const domain = domainMatch ? domainMatch[1].toLowerCase() : "";

  if (knownShorteners.includes(domain)) {
    let expanded = "";
    try {
      const response = await fetch(`https://unshorten.me/json/${encodeURIComponent(url)}`);
      const data = await response.json();
      expanded = data.resolved_url || "(could not resolve)";
    } catch {
      expanded = "(error expanding URL)";
    }

    results.push({
      name: "URL Shortener detected",
      status: "warn",
      message: `URL uses a known shortening service: ${domain}<br>Expanded URL: ${escapeHtml(expanded)}`
    });
  } else {
    results.push({
      name: "No URL shortener",
      status: "pass",
      message: "URL does not use a known shortener."
    });
  }

  // Phishing keyword check
  const phishingKeywords = [
    "login", "verify", "account", "secure", "bank", "webscr", "signin", "redirect",
    "update", "confirm", "validate", "activate", "pay", "password", "wp-admin", "win", "download"
  ];
  const lowerUrl = url.toLowerCase();
  const foundKeywords = phishingKeywords.filter(k => lowerUrl.includes(k));

  if (foundKeywords.length > 0) {
    results.push({
      name: "Phishing Keywords",
      status: "warn",
      message: `URL contains suspicious keywords: ${foundKeywords.join(", ")}. Verify before proceeding.`
    });
  } else {
    results.push({
      name: "No Phishing Keywords",
      status: "pass",
      message: "No suspicious keywords found in URL."
    });
  }

  return results;
}

// Validate if a string is a valid URL
function isValidUrl(string) {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}

// MAIN THREAT ANALYSIS FUNCTION ---------
async function handleAnalysis() {
  let url = "";

  // Check QR code content first
  const qrSpan = uploadResult.querySelector("span");
  if (qrSpan && qrSpan.textContent) {
    url = qrSpan.textContent.trim();
  }

  // Fallback to URL input
  if (!url && urlInput.value.trim()) {
    url = urlInput.value.trim();
  }

  const output = document.getElementById("analysisOutput");
  output.innerHTML = ""; // Clear previous results

  if (!url) {
    output.textContent = "No URL found to analyze.";
    return;
  }

  if (!isValidUrl(url)) {
    output.textContent = "Invalid URL format. Please enter a valid URL starting with http:// or https://. If you have checked that the link you entered is correct, then it is a suspicious link - proceed with caution.";
    return;
  }

  output.innerHTML = `<em>Analyzing ${escapeHtml(url)}...</em>`;

  const results = await analyzeUrl(url);

  const resultsHTML = results.map(res => {
    const color = {
      pass: "limegreen",
      warn: "orange",
      fail: "red"
    }[res.status] || "gray";

    return `<div style="margin-bottom: 0.5em;">
      <span style="color:${color}; font-weight: 600;">${escapeHtml(res.name)}</span><br>
      <span>${res.message}</span>
    </div>`;
  }).join("");

  output.innerHTML = `
    <div style="margin-bottom: 1em;"><strong>Analyzing:</strong> ${escapeHtml(url)}</div>
    ${resultsHTML}
  `;
}


