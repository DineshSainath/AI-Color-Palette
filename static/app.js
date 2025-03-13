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

      // Add save button if user is logged in
      if (isUserLoggedIn()) {
        addSavePaletteButton(colors);
      }
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

// Check if user is logged in
function isUserLoggedIn() {
  return document.body.dataset.userLoggedIn === "true";
}

// Add save palette button
function addSavePaletteButton(colors) {
  // Remove existing save button if any
  const existingSaveBtn = document.getElementById("savePaletteBtn");
  if (existingSaveBtn) {
    existingSaveBtn.remove();
  }

  const container = document.getElementById("paletteContainer");
  const saveBtn = document.createElement("button");
  saveBtn.id = "savePaletteBtn";
  saveBtn.className = "btn";
  saveBtn.textContent = "Save Palette";
  saveBtn.style.marginTop = "20px";

  saveBtn.addEventListener("click", function () {
    showSavePaletteModal(colors);
  });

  // Append after the container
  container.parentNode.insertBefore(saveBtn, container.nextSibling);
}

// Show save palette modal
function showSavePaletteModal(colors) {
  // Create modal if it doesn't exist
  let modal = document.getElementById("savePaletteModal");

  if (!modal) {
    modal = document.createElement("div");
    modal.id = "savePaletteModal";
    modal.className = "save-palette-modal";

    const modalContent = `
      <div class="modal-content">
        <h3>Save Palette</h3>
        <div class="modal-preview" id="modalPreview"></div>
        <form id="savePaletteForm" method="POST" action="/save_palette">
          <div class="form-group">
            <label for="paletteName">Palette Name</label>
            <input type="text" id="paletteName" name="name" class="form-control" required>
            <input type="hidden" id="paletteColors" name="colors">
          </div>
          <div class="modal-actions">
            <button type="button" class="btn close-modal" id="cancelSave">Cancel</button>
            <button type="submit" class="btn">Save</button>
          </div>
        </form>
      </div>
    `;

    modal.innerHTML = modalContent;
    document.body.appendChild(modal);

    // Add event listeners
    document
      .getElementById("cancelSave")
      .addEventListener("click", function () {
        modal.classList.remove("show");
      });

    document
      .getElementById("savePaletteForm")
      .addEventListener("submit", function (e) {
        e.preventDefault();
        const name = document.getElementById("paletteName").value;
        const colorsValue = document.getElementById("paletteColors").value;

        fetch("/save_palette", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            name: name,
            colors: colorsValue,
          }),
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Failed to save palette");
            }
            return response.json();
          })
          .then((data) => {
            showToast("Palette saved successfully!");
            modal.classList.remove("show");
          })
          .catch((error) => {
            console.error("Error saving palette:", error);
            showToast("Error saving palette. Please try again.");
          });
      });
  }

  // Update preview and colors
  const preview = document.getElementById("modalPreview");
  preview.innerHTML = "";

  colors.forEach((color) => {
    const colorDiv = document.createElement("div");
    colorDiv.className = "modal-color";
    colorDiv.style.backgroundColor = color;
    preview.appendChild(colorDiv);
  });

  // Set colors in hidden input
  document.getElementById("paletteColors").value = JSON.stringify(colors);

  // Show modal
  modal.classList.add("show");
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
