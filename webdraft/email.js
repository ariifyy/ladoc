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