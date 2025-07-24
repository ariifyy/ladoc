// Cache DOM elements for better performance
const pasteSection = document.getElementById("pasteSection");
const uploadSection = document.getElementById("uploadSection");
const qrInput = document.getElementById("qrInput");
const qrCanvas = document.getElementById("qrCanvas");
const qrResult = document.getElementById("uploadResult");
const pastedUrlInput = document.getElementById("pastedUrl");
const pasteResult = document.getElementById("pasteResult");

// Mode toggle functions
function showPaste() {
  pasteSection.style.display = "block";
  uploadSection.style.display = "none";

  pasteResult.innerHTML = "";
  pastedUrlInput.value = "";
}

function showUpload() {
  pasteSection.style.display = "none";
  uploadSection.style.display = "block";

  qrResult.innerHTML = "";
  clearCanvas();
}

// Upload image file & drag-drop handling
function handleImageFile(file) {
  if (!file.type.startsWith("image/")) {
    qrResult.textContent = "Please upload a valid image file.";
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

    const ctx = qrCanvas.getContext("2d");
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, qrCanvas.width, qrCanvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height);

    if (code) {
      qrResult.innerHTML = `
        <strong>QR Code Content:</strong><br>
        <a href="${escapeHtml(code.data)}" target="_blank" rel="noopener noreferrer">${escapeHtml(code.data)}</a>
      `;
    } else {
      qrResult.textContent = "Invalid or no QR code found in the image.";
    }
  };

  reader.readAsDataURL(file);
}

// Clear canvas drawing
function clearCanvas() {
  const ctx = qrCanvas.getContext("2d");
  ctx.clearRect(0, 0, qrCanvas.width, qrCanvas.height);
}

// Escape HTML for safety
function escapeHtml(text) {
  return text.replace(/[&<>"']/g, function(m) {
    return ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    })[m];
  });
}

// Paste URL analyze handler
function handlePastedUrl() {
  const url = pastedUrlInput.value.trim();
  if (!url) {
    pasteResult.textContent = "Please enter a URL.";
    return;
  }
  pasteResult.innerHTML = `<strong>URL Entered:</strong> ${escapeHtml(url)}`;
  // TODO: Add your phishing and URL analysis logic here
}

// Attach event listeners once DOM is loaded
window.addEventListener("DOMContentLoaded", () => {
  window.addEventListener('dragover', e => e.preventDefault());
  window.addEventListener('drop', e => e.preventDefault());
  
  document.getElementById("btnPaste").addEventListener("click", showPaste);
  document.getElementById("btnUpload").addEventListener("click", showUpload);
  document.getElementById("btnAnalyze").addEventListener("click", handlePastedUrl);

  // Drag-drop & click for upload
  const dropZone = document.getElementById("dropZone");
  qrInput.addEventListener("click", (e) => {
    e.stopPropagation();
  });
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      handleImageFile(e.dataTransfer.files[0]);
    }
  });

  qrInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      handleImageFile(e.target.files[0]);
    }
  });

  // Show paste mode by default on load
  showPaste();
});
