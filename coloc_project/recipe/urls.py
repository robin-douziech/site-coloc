from django.urls import path
from . import views

app_name = "recipe"
urlpatterns = [
    path('', views.list, name="list"),
    path('details', views.details, name="details"),
    path('edit', views.edit, name="edit"),

    path('create-recipe', views.create_recipe, name="create-recipe"),
    path('create-ingredient', views.create_ingredient, name="create-ingredient"),
    path('create-utensil', views.create_utensil, name="create-utensil"),
    path('create-tag', views.create_tag, name="create-tag"),

    path('delete-ingredient-recipe-relationship', views.delete_ingredient_recipe_relationship, name="delete-ingredient-recipe-relationship"),
    path('delete-utensil-recipe-relationship', views.delete_utensil_recipe_relationship, name="delete-utensil-recipe-relationship"),
    path('delete-step', views.delete_step, name="delete-step"),
    path('delete-comment', views.delete_comment, name="delete-comment"),
    path('delete-ingredient', views.delete_ingredient, name="delete-ingredient"),
    path('delete-utensil', views.delete_utensil, name="delete-utensil"),
    path('delete-recipe', views.delete_recipe, name="delete-recipe"),
    path('delete-ingredient-from-search', views.delete_ingredient_from_search, name="delete-ingredient-from-search"),
    path('delete-tag-from-search', views.delete_tag_from_search, name="delete-tag-from-search"),
]