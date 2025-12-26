
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, Ingredient, Step
from .forms import RecipeForm
import random
from django.http import JsonResponse
from django.db.models import Count, Q


@login_required
def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            return redirect('add_ingredients', recipe.id)
    else:
        form = RecipeForm()

    return render(request, 'create_recipe.html', {'form': form})

@login_required
def add_ingredients(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        names = request.POST.getlist('name')
        quantities = request.POST.getlist('quantity')
        units = request.POST.getlist('unit')

        for n, q, u in zip(names, quantities, units):
            Ingredient.objects.create(
                recipe=recipe,
                name=n,
                quantity=q,
                unit=u
            )

        return redirect('add_steps', recipe_id)

    return render(request, 'add_ingredients.html', {'recipe': recipe})

@login_required
def add_steps(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    ingredients = list(
        Ingredient.objects.filter(recipe=recipe)
        .values('id', 'name')
    )

    if request.method == 'POST':
        step_nos = request.POST.getlist('step_no')
        instructions = request.POST.getlist('instruction')

        for i in range(len(step_nos)):
            step = Step.objects.create(
                recipe=recipe,
                step_no=step_nos[i],
                instruction=instructions[i]
            )

            selected_ingredients = request.POST.getlist(f'ingredients_{i}')
            step.ingredients.set(selected_ingredients)

        return redirect('recipe_detail', recipe.id)

    return render(request, 'add_steps.html', {
        'recipe': recipe,
        'ingredients': ingredients
    })


from django.http import JsonResponse
import random

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    ingredients = Ingredient.objects.filter(recipe=recipe)
    steps = Step.objects.filter(recipe=recipe).order_by('step_no')

    target_serves = int(request.GET.get("serves", recipe.serves))

    scaled_ingredients = scale_ingredients_by_people(
        ingredients,
        recipe.serves,
        target_serves
    )

    # AJAX request → return only ingredients
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "serves": target_serves,
            "ingredients": scaled_ingredients
        })

    # Normal page load → get random recipes
    all_recipe_ids = list(
        Recipe.objects.exclude(id=recipe.id).values_list('id', flat=True)
    )
    random_ids = random.sample(all_recipe_ids, min(4, len(all_recipe_ids)))
    random_recipes = Recipe.objects.filter(id__in=random_ids)

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'ingredients': scaled_ingredients,  # initial scaled ingredients
        'steps': steps,
        'random_recipes': random_recipes
    })


def home(request):
    recipes = Recipe.objects.all().order_by('-id')[:5]  # latest 6 recipes

    return render(request, 'home.html', {
        'recipes': recipes
    })



def ajax_live_search(request):
    query = request.GET.get("q", "")

    recipes = []

    if query:
        recipes_qs = Recipe.objects.filter(
            Q(title__icontains=query) 
        ).distinct()[:10]  # limit results

        recipes = [
            {
                "id": recipe.id,
                "title": recipe.title
            }
            for recipe in recipes_qs
        ]

    return JsonResponse({"results": recipes})





from decimal import Decimal, ROUND_HALF_UP

def scale_ingredients_by_people(ingredients, base_serves, target_serves):
    if base_serves <= 0:
        raise ValueError("Recipe serves must be greater than zero")

    factor = Decimal(target_serves) / Decimal(base_serves)

    scaled = []
    for ing in ingredients:
        qty = Decimal(str(ing.quantity)) * factor

        scaled.append({
            "name": ing.name,
            "unit": ing.unit,
            "quantity": qty.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        })

    return scaled






def suggest_recipes(request):
    # User submits a comma-separated list of available ingredients
    available = request.GET.get("ingredients", "")
    available_list = [i.strip().lower() for i in available.split(",") if i.strip()]

    recipes = Recipe.objects.all()
    suggested = []

    for recipe in recipes:
        recipe_ingredients = recipe.ingredient_set.values_list("name", flat=True)
        recipe_ingredients_lower = [i.lower() for i in recipe_ingredients]

        # Count matches
        matches = sum(1 for i in recipe_ingredients_lower if i in available_list)
        match_percentage = matches / max(len(recipe_ingredients_lower), 1) * 100

        if match_percentage > 0:  # show recipes with at least 1 matching ingredient
            suggested.append({
                "recipe": recipe,
                "match_percentage": int(match_percentage),
                "missing_ingredients": [i for i in recipe_ingredients_lower if i not in available_list]
            })

    # Sort by match percentage descending
    suggested = sorted(suggested, key=lambda x: x["match_percentage"], reverse=True)

    return render(request, "suggest_recipes.html", {
        "available": available,
        "suggested": suggested
    })

