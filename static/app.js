// Handle form submission
function submitForm() {
  const query = document.getElementById("query").value;
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
    .catch((error) => console.error("Error generating palette:", error));
}

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
      navigator.clipboard.writeText(color).then(() => {
        alert(`Color ${color} copied to clipboard!`);
      });
    });

    container.appendChild(div);
  });
}
