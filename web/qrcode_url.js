// Cache DOM elements once for efficiency
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
  return text.replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[m]));
}

// Show URL paste input and hide upload section
function showUrl() {
  urlSection.style.display = "block";
  uploadSection.style.display = "none";

  pasteResult.innerHTML = "";
  urlInput.value = "";
  clearCanvas();
  uploadResult.innerHTML = "";
}

// Show upload section and hide URL paste input
function showUpload() {
  urlSection.style.display = "none";
  uploadSection.style.display = "block";

  pasteResult.innerHTML = "";
  urlInput.value = "";
  clearCanvas();
  uploadResult.innerHTML = "";
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
        <a href="${escapeHtml(code.data)}" target="_blank" rel="noopener noreferrer">${escapeHtml(code.data)}</a>
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

  // Analyze URL button
  document.querySelector("#urlSection button").addEventListener("click", handleUrl);

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


//URL Threat analyser logic
function handleAnalysis() {
  let finalUrl = "";

  // Prefer QR code result if available
  const qrLink = uploadResult.querySelector("a");
  if (qrLink && qrLink.href) {
    finalUrl = qrLink.href.trim();
  }

  // Else fallback to URL input
  if (!finalUrl && urlInput.value.trim()) {
    finalUrl = urlInput.value.trim();
  }

  const output = document.getElementById("analysisOutput");

  if (!finalUrl) {
    output.textContent = "No URL found to analyze.";
    return;
  }

  // Very simple http/https check
  if (finalUrl.startsWith("https://")) {
    output.innerHTML = `<p style="color:limegreen;"><strong>Safe:</strong> Uses HTTPS</p><p>${escapeHtml(finalUrl)}</p>`;
  } else if (finalUrl.startsWith("http://")) {
    output.innerHTML = `<p style="color:orange;"><strong>Warning:</strong> Uses HTTP</p><p>${escapeHtml(finalUrl)}</p>`;
  } else {
    output.innerHTML = `<p style="color:red;"><strong>Invalid or Unrecognized URL</strong></p><p>${escapeHtml(finalUrl)}</p>`;
  }
}
