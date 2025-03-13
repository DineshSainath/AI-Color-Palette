// Handle form submission
function submitForm() {
  const query = document.getElementById("query").value;
  if (!query.trim()) {
    showToast("Please enter a prompt first");
    return;
  }

  // Show loading state
  const button = document.querySelector("button");
  const originalText = button.textContent;
  button.textContent = "Generating...";
  button.disabled = true;

  fetch("/palette", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      query: query,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      const colors = data.colors;
      const container = document.getElementById("paletteContainer");
      createColorBoxes(colors, container);
    })
    .catch((error) => {
      console.error("Error generating palette:", error);
      showToast("Error generating palette. Please try again.");
    })
    .finally(() => {
      // Reset button state
      button.textContent = originalText;
      button.disabled = false;
    });
}

document.getElementById("query").addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    event.preventDefault(); // Prevent form submission if inside a form element
    submitForm();
  }
});

function createColorBoxes(colors, container) {
  container.innerHTML = ""; // Clear existing palette

  colors.forEach((color) => {
    const div = document.createElement("div");
    div.classList.add("color-box");
    div.style.backgroundColor = color;

    const hexCode = document.createElement("span");
    hexCode.classList.add("hex-code");
    hexCode.textContent = color;

    div.appendChild(hexCode);

    // Clipboard copy functionality
    div.addEventListener("click", function () {
      navigator.clipboard
        .writeText(color)
        .then(() => {
          showToast(`Color ${color} copied to clipboard!`);
        })
        .catch((err) => {
          showToast("Failed to copy color");
          console.error("Copy failed:", err);
        });
    });

    container.appendChild(div);
  });
}

// Toast notification function
function showToast(message) {
  // Check if a toast container already exists
  let toastContainer = document.querySelector(".toast-container");

  // If not, create one
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.className = "toast-container";
    document.body.appendChild(toastContainer);
  }

  // Create the toast element
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;

  // Add it to the container
  toastContainer.appendChild(toast);

  // Trigger animation
  setTimeout(() => {
    toast.classList.add("show");
  }, 10);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}
