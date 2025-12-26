function addIngredient() {
    const container = document.getElementById('ingredient-container');

    const row = document.createElement('div');
    row.className = 'ingredient-row';

    row.innerHTML = `
        <input type="text" name="name" placeholder="Ingredient name" required>
        <input type="number" step="0.1" name="quantity" placeholder="Qty" required>
        <input type="text" name="unit" placeholder="Unit" required>
        <button type="button" onclick="this.parentElement.remove()">❌</button>
    `;

    container.appendChild(row);
}
