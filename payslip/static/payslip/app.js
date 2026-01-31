// Global Date Field Validation with Checkmark
document.addEventListener("DOMContentLoaded", function () {
  // Add checkmark to all date inputs when they have a value
  const dateInputs = document.querySelectorAll('input[type="date"]');
  
  dateInputs.forEach(input => {
    // Skip if already wrapped (like in travel expense table)
    if (input.parentElement.classList.contains('date-field-wrapper')) {
      // Just add event listener
      input.addEventListener('change', function() {
        const wrapper = this.parentElement;
        if (this.value) {
          wrapper.classList.add('has-value');
        } else {
          wrapper.classList.remove('has-value');
        }
      });
      
      // Check initial value
      if (input.value) {
        input.parentElement.classList.add('has-value');
      }
      return;
    }
    
    // Wrap date input
    const wrapper = document.createElement('div');
    wrapper.className = 'date-field-wrapper';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    
    // Add checkmark element
    const checkmark = document.createElement('span');
    checkmark.className = 'date-checkmark';
    checkmark.textContent = '✓';
    wrapper.appendChild(checkmark);
    
    // Show/hide checkmark on change
    input.addEventListener('change', function() {
      const wrapper = this.parentElement;
      if (this.value) {
        wrapper.classList.add('has-value');
      } else {
        wrapper.classList.remove('has-value');
      }
    });
    
    // Check initial value
    if (input.value) {
      input.parentElement.classList.add('has-value');
    }
  });
});

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

