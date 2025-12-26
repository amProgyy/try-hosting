// Debounce helper
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), delay);
  };
}

// Loading helper
function showLoading(show = true) {
  const loader = document.getElementById("loading");
  if (!loader) return;
  loader.style.display = show ? "inline-block" : "none";
}

// Update DOM
function updateIngredients(data) {
  if (!data.ingredients) return;

  data.ingredients.forEach(ing => {
    const item = document.querySelector(
      `[data-ingredient="${CSS.escape(ing.name)}"]`
    );
    if (!item) return;

    item.querySelector(".qty").textContent = ing.quantity;
    item.querySelector(".unit").textContent = ing.unit;
  });
}

// Fetch & scale
function scaleRecipe(serves) {
  if (!serves || serves < 1) return;

  showLoading(true);

  fetch(`?serves=${serves}`, { headers: { "X-Requested-With": "XMLHttpRequest" }})
    .then(res => res.json())
    .then(data => {
      updateIngredients(data);
      showLoading(false);
    })
    .catch(err => {
      console.error("Scaling failed:", err);
      showLoading(false);
    });
}

// Attach input listener
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("serves-input");
  if (!input) return;
  input.addEventListener("input", debounce(() => scaleRecipe(input.value), 300));
});
