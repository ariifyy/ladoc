//URL and QR code logic
//URL expander via unshorten.me ***(limited to 10/ip/hour)***
async function expandURL() {
  const input = document.getElementById('shortUrlInput').value.trim();
  const resultDiv = document.getElementById('expandURLresult');

  if (!input) {
    resultDiv.textContent = "Please enter a URL.";
    return;
  }

  try {
    const apiUrl = `https://unshorten.me/json/${encodeURIComponent(input)}`;
    const response = await fetch(apiUrl);
    const data = await response.json();

    if (data.success && data.resolved_url) {
      resultDiv.innerHTML = `
        <strong>Expanded URL:</strong><br>
        <a href="${data.resolved_url}" target="_blank">${data.resolved_url}</a>
      `;
    } else {
      resultDiv.textContent = "Could not resolve the URL.";
    }
  } catch (error) {
    resultDiv.textContent = `Error: ${error.message}`;
  }
}

// QRCode decoder
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("qrInput");
  const canvas = document.getElementById("qrCanvas");
  const resultDiv = document.getElementById("qrResult"); // outside dropZone now
  const dropZone = document.getElementById("dropZone");
  const ctx = canvas.getContext("2d");

  showUpload();

  // Drag-and-drop upload
  dropZone.addEventListener("click", () => input.click());

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
    const file = e.dataTransfer.files[0];
    if (file) handleImageFile(file);
  });

  input.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) handleImageFile(file);
  });

  function handleImageFile(file) {
    const img = new Image();
    const reader = new FileReader();

    reader.onload = (e) => {
      img.src = e.target.result;
    };

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code) {
        resultDiv.innerHTML = `
          <strong>QR Code Content:</strong><br>
          <a href="${code.data}" target="_blank" rel="noopener noreferrer">${code.data}</a>
        `;
      } else {
        resultDiv.textContent = "Invalid / No QR code found in the image.";
      }
    };

    reader.readAsDataURL(file);
  }

  // Expose toggles globally
  window.showUpload = showUpload;
  window.showScanner = showScanner;
  window.rescan = rescan;
});

let html5QrcodeScanner = null;
let scanningPaused = false;

function startScanner() {
  const qrResult = document.getElementById("qrScanResult");
  const scanAgainBtn = document.getElementById("scanAgainBtn");
  qrResult.innerHTML = "Initializing camera...";
  scanAgainBtn.style.display = "none";
  scanningPaused = false;

  if (!html5QrcodeScanner) {
    html5QrcodeScanner = new Html5Qrcode("reader");
  }

  const config = { fps: 10, qrbox: 250 };

  html5QrcodeScanner.start(
    { facingMode: "environment" },
    config,
    (decodedText) => {
      if (scanningPaused) return;

      scanningPaused = true;
      qrResult.innerHTML = `
        <strong>QR Code Content:</strong><br>
        <a href="${decodedText}" target="_blank" rel="noopener noreferrer">${decodedText}</a>
      `;
      scanAgainBtn.style.display = "inline-block";
    },
    (errorMessage) => {
      // optional: log error
    }
  ).catch(err => {
    const qrResult = document.getElementById("qrScanResult");
    qrResult.textContent = `Camera start failed: ${err}`;
    
    // attempt cleanup
    stopScanner().then(() => {
      showUpload();  // Fallback to upload mode if camera fails
    });
  });
}

function stopScanner() {
  if (html5QrcodeScanner) {
    return html5QrcodeScanner.stop().then(() => {
      return html5QrcodeScanner.clear();
    }).then(() => {
      html5QrcodeScanner = null;
    }).catch((err) => {
      console.error("Failed to stop scanner: ", err);
    });
  }
  return Promise.resolve();
}

function rescan() {
  const scanAgainBtn = document.getElementById("scanAgainBtn");
  const qrResult = document.getElementById("qrScanResult");
  qrResult.innerHTML = "";
  scanAgainBtn.style.display = "none";
  scanningPaused = false;
}

function showUpload() {
  stopScanner();

  document.getElementById("scannerSection").style.display = "none";
  document.getElementById("uploadSection").style.display = "block";

  document.getElementById("qrScanResult").innerHTML = "";
  document.getElementById("qrResult").innerHTML = "";

  const scanAgainBtn = document.getElementById("scanAgainBtn");
  if (scanAgainBtn) scanAgainBtn.style.display = "none";
}

function showScanner() {
  document.getElementById("uploadSection").style.display = "none";
  document.getElementById("scannerSection").style.display = "block";

  document.getElementById("qrScanResult").innerHTML = "";
  document.getElementById("qrResult").innerHTML = "";

  const scanAgainBtn = document.getElementById("scanAgainBtn");
  if (scanAgainBtn) scanAgainBtn.style.display = "none";

  startScanner();
}




//URL risk identifier logic
document.getElementById("urlForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const url = document.getElementById("urlInput").value.trim();
  const resultDiv = document.getElementById("result");

  if (!url) return;

  const risks = analyzeURL(url);
  const riskLevel = risks.length === 0 ? "Low Risk ✅" :
                    risks.length <= 2 ? "Moderate Risk ⚠️" :
                    "High Risk 🚨";

  resultDiv.innerHTML = `
    <h3>Analysis Result: ${riskLevel}</h3>
    <ul>
      ${risks.length ? risks.map(risk => `<li>${risk}</li>`).join('') : "<li>No major issues detected.</li>"}
    </ul>
  `;
});

function analyzeURL(inputUrl) {
  const warnings = [];

  try {
    const parsed = new URL(inputUrl);

    // No HTTPS
    if (parsed.protocol !== "https:") {
      warnings.push("❌ Uses HTTP instead of HTTPS.");
    }

    // IP address instead of domain
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(parsed.hostname)) {
      warnings.push("❌ Domain is an IP address, which is unusual.");
    }

    // Typosquatting / brand misuse
    const knownBrands = ["google", "paypal", "apple", "amazon", "facebook"];
    knownBrands.forEach(brand => {
      if (parsed.hostname.includes(brand) && !parsed.hostname.endsWith(`${brand}.com`)) {
        warnings.push(`⚠️ Suspicious use of brand name "${brand}" in domain.`);
      }
    });

    // Suspicious TLD
    const riskyTLDs = [".tk", ".ml", ".gq", ".cf", ".ga"];
    riskyTLDs.forEach(tld => {
      if (parsed.hostname.endsWith(tld)) {
        warnings.push(`⚠️ Suspicious top-level domain (${tld}).`);
      }
    });

    // Long URL
    if (inputUrl.length > 100) {
      warnings.push("⚠️ Very long URL. Could be trying to obfuscate true destination.");
    }

    // Nested subdomains
    const subdomainParts = parsed.hostname.split(".");
    if (subdomainParts.length > 3) {
      warnings.push("⚠️ Deeply nested subdomain structure.");
    }

    // Encoded characters
    if (decodeURIComponent(parsed.href) !== parsed.href) {
      warnings.push("⚠️ Encoded characters found in URL.");
    }

    // Suspicious keywords
    const riskyWords = ["login", "verify", "secure", "update", "account", "free", "win"];
    riskyWords.forEach(word => {
      if (parsed.hostname.includes(word) || parsed.pathname.includes(word)) {
        warnings.push(`⚠️ Contains suspicious keyword: "${word}".`);
      }
    });

    // "@" symbol trick
    if (parsed.href.includes("@")) {
      warnings.push("⚠️ URL contains '@' symbol, may redirect to a different site.");
    }

    // Non-standard port
    if (parsed.port && parsed.port !== "80" && parsed.port !== "443") {
      warnings.push(`⚠️ Non-standard port used: ${parsed.port}.`);
    }

  } catch (error) {
    warnings.push("❌ Invalid URL format.");
  }

  return warnings;
}



