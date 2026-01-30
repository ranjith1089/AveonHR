const form = document.getElementById("payslip-form");
const fileMeta = document.getElementById("file-meta");

if (form) {
  const fileInput = form.querySelector('input[type="file"]');

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      fileMeta.textContent = file
        ? `${file.name} (${Math.round(file.size / 1024)} KB)`
        : "No file selected";
    });
  }

  form.addEventListener("submit", () => {
    const button = form.querySelector("button.primary");
    if (button) {
      button.disabled = true;
      button.textContent = "Generating...";
      const enableButton = () => {
        button.disabled = false;
        button.textContent = "Generate Payslips";
      };
      window.addEventListener("focus", enableButton, { once: true });
      setTimeout(enableButton, 8000);
    }
  });
}

