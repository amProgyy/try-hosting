from django.urls import path
from Recipe import views

urlpatterns = [
    path('create_recipe/', views.create_recipe, name='create_recipe'),
    path('recipe/<int:recipe_id>/ingredients/', views.add_ingredients, name='add_ingredients'),
    path('add_steps/<int:recipe_id>/', views.add_steps, name="add_steps"),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('', views.home, name='home'),
    path("ajax/search/", views.ajax_live_search, name="ajax_live_search"),
    path('suggest_recipes/', views.suggest_recipes, name='suggest_recipes'),

]
