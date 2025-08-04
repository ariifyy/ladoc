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

      if (data && data.status === "success") {
        let breachesArray = [];

        if (Array.isArray(data.breaches)) {
          if (Array.isArray(data.breaches[0])) {
            breachesArray = data.breaches.flat();
          } else {
            breachesArray = data.breaches;
          }
        } else if (typeof data.breaches === "string") {
          breachesArray = data.breaches.split(",").map(s => s.trim()).filter(Boolean);
        }

        if (breachesArray.length > 0) {
          const breachesList = breachesArray.map(b => `<li>${b}</li>`).join("");
          emailResult.innerHTML = `
            <p>⚠️ This email was found in <strong>${breachesArray.length}</strong> breach(es).</p>
            <p>We recommend changing your password for this account immediately and enabling two-factor authentication.</p>
            <br>
            <button id="toggleDetails" class="btn">Show Breach Details</button>
            <ul id="breachDetails" class="hide">${breachesList}</ul>
          `;

          const toggleBtn = document.getElementById("toggleDetails");
          const breachDetails = document.getElementById("breachDetails");

          toggleBtn.addEventListener("click", () => {
            breachDetails.classList.toggle("hide");
            toggleBtn.textContent = breachDetails.classList.contains("hide")
              ? "Show Details"
              : "Hide Details";
          });
        } else {
          emailResult.innerHTML = "<p>✅ No breaches found for this email.</p>";
        }
      } else if (data.status === "not_found") {
        emailResult.innerHTML = "<p>✅ No breaches found for this email.</p>";
      } else {
        emailResult.innerHTML = "<p>❗ No breaches found or unexpected response.</p>";
      }
    } catch (err) {
      emailResult.innerHTML = "<p>❌ Error checking email.</p>";
      console.error(err);
    }
  });
}
