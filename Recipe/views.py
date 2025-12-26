
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, Ingredient, Step
from .forms import RecipeForm
import random

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



def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    ingredients = Ingredient.objects.filter(recipe=recipe)
    steps = Step.objects.filter(recipe=recipe).order_by('step_no')

    # Get random recipes (excluding current one)
    all_recipe_ids = list(
        Recipe.objects.exclude(id=recipe.id).values_list('id', flat=True)
    )

    random_ids = random.sample(
        all_recipe_ids,
        min(4, len(all_recipe_ids))   # show max 4
    )

    random_recipes = Recipe.objects.filter(id__in=random_ids)

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,
        'steps': steps,
        'random_recipes': random_recipes
    })


def home(request):
    recipes = Recipe.objects.all().order_by('-id')[:5]  # latest 6 recipes

    return render(request, 'home.html', {
        'recipes': recipes
    })