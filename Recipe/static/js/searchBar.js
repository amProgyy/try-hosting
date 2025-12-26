const input = document.getElementById("live-search");
const resultsBox = document.getElementById("search-results");

let timeout = null;

input.addEventListener("keyup", function () {
    clearTimeout(timeout);

    const query = this.value.trim();

    if (query.length < 2) {
        resultsBox.innerHTML = "";
        return;
    }

    timeout = setTimeout(() => {
        fetch(`/ajax/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsBox.innerHTML = "";

                if (data.results.length === 0) {
                    resultsBox.innerHTML = "<li>No results</li>";
                    return;
                }

                data.results.forEach(recipe => {
                    const li = document.createElement("li");
                    li.innerHTML = `<a href="/recipe/${recipe.id}/">${recipe.title}</a>`;
                    resultsBox.appendChild(li);
                });
            });
    }, 300); // debounce
});