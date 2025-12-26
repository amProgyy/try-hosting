

let stepCount = 0;

function addStep(ingredients) {
    const container = document.getElementById('steps-container');

    const stepDiv = document.createElement('div');
    stepDiv.className = 'step-box';

    let ingredientHTML = '';
    ingredients.forEach(ing => {
        ingredientHTML += `
            <label>
                <input type="checkbox"
                       name="ingredients_${stepCount}"
                       value="${ing.id}">
                ${ing.name}
            </label><br>
        `;
    });

    stepDiv.innerHTML = `
        <h4>Step ${stepCount + 1}</h4>
        <input type="hidden" name="step_no" value="${stepCount + 1}">
        <textarea name="instruction" placeholder="Describe this step" required></textarea>
        <p><strong>Ingredients used:</strong></p>
        ${ingredientHTML}
        <hr>
    `;

    container.appendChild(stepDiv);
    stepCount++;
}
