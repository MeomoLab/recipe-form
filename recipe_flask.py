"""A beginner-friendly recipe submission website built with Flask."""

from flask import Flask, redirect, render_template_string, request, url_for


app = Flask(__name__)
recipes = []  # Recipes are kept in memory until the server stops.
INGREDIENT_ROWS = 8

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Recipe box</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; padding: 28px 16px; background: #f5f2eb; color: #202b25; font: 17px/1.5 system-ui, sans-serif; }
    main { width: min(100%, 720px); margin: 20px auto; }
    .card { padding: clamp(22px, 5vw, 40px); margin-bottom: 22px; background: #fffefa; border: 1px solid #d9ded8; border-radius: 20px; box-shadow: 0 16px 40px #17231f12; }
    h1 { margin: 0 0 8px; font-size: clamp(2rem, 6vw, 3rem); line-height: 1.1; }
    .intro, .hint { color: #53645c; }
    .field { margin: 19px 0; }
    label { display: block; margin-bottom: 7px; font-weight: 700; }
    input, textarea { display: block; width: 100%; min-height: 50px; padding: 11px 12px; border: 1px solid #b7c5bb; border-radius: 10px; font: inherit; }
    textarea { min-height: 110px; resize: vertical; }
    input:focus, textarea:focus { outline: 3px solid #17644735; border-color: #176447; }
    .ingredient-heading, .ingredient-row { display: grid; grid-template-columns: minmax(110px, 0.8fr) minmax(0, 2fr); gap: 12px; }
    .ingredient-heading { margin: 18px 0 6px; font-weight: 700; }
    .ingredient-row { margin: 0 0 10px; }
    .error { padding: 14px 16px; border-left: 4px solid #a32121; border-radius: 8px; background: #fff0ed; color: #821b1b; }
    button { display: inline-block; padding: 13px 22px; border: 0; border-radius: 999px; background: #176447; color: white; font: inherit; font-weight: 700; cursor: pointer; }
    .recipe { padding: 16px 0; border-top: 1px solid #d9ded8; }
    @media (max-width: 480px) { body { padding: 12px; } .ingredient-heading, .ingredient-row { grid-template-columns: minmax(90px, 0.8fr) minmax(0, 2fr); gap: 8px; } button { width: 100%; } }
  </style>
</head>
<body><main>
  <section class="card">
    <h1>Share a recipe</h1>
    <p class="intro">Enter an amount and ingredient name on the same row. Fill in both fields for every ingredient you add.</p>
    {% if error %}<p class="error" role="alert">{{ error }}</p>{% endif %}
    <form method="post" action="{{ url_for('home') }}">
      <div class="field"><label for="title">Recipe name *</label>
        <input id="title" name="title" value="{{ values.title }}"></div>
      <div class="field"><label for="author">Your name (optional)</label>
        <input id="author" name="author" value="{{ values.author }}"></div>

      <div class="ingredient-heading"><span>Amount *</span><span>Ingredient name *</span></div>
      {% for row in ingredient_rows %}
      <div class="ingredient-row">
        <input aria-label="Amount {{ loop.index }}" name="amount_{{ loop.index }}" placeholder="e.g. 2 cups" value="{{ row.amount }}">
        <input aria-label="Ingredient name {{ loop.index }}" name="ingredient_{{ loop.index }}" placeholder="e.g. flour" value="{{ row.name }}">
      </div>
      {% endfor %}
      <p class="hint">At least one row is required. Leave unused rows empty.</p>

      <div class="field"><label for="method">Method (optional)</label>
        <textarea id="method" name="method">{{ values.method }}</textarea></div>
      <button type="submit">Submit recipe</button>
    </form>
  </section>

  <section class="card">
    <h2>Submitted recipes</h2>
    {% if recipes %}
      {% for recipe in recipes %}
      <article class="recipe">
        <h3>{{ recipe.title }}</h3>
        {% if recipe.author %}<p>Shared by {{ recipe.author }}</p>{% endif %}
        <p><strong>Ingredients</strong></p>
        <ul>{% for item in recipe.ingredients %}<li>{{ item.amount }} {{ item.name }}</li>{% endfor %}</ul>
        {% if recipe.method %}<p><strong>Method</strong><br>{{ recipe.method }}</p>{% endif %}
      </article>
      {% endfor %}
    {% else %}<p>No recipes yet.</p>{% endif %}
  </section>
</main></body></html>
"""


def show_page(error="", values=None, ingredient_rows=None):
    """Show the form and recipe list, including any validation message."""
    values = values or {"title": "", "author": "", "method": ""}
    ingredient_rows = ingredient_rows or [
        {"amount": "", "name": ""} for _ in range(INGREDIENT_ROWS)
    ]
    return render_template_string(
        PAGE,
        error=error,
        values=values,
        ingredient_rows=ingredient_rows,
        recipes=recipes,
    )


@app.route("/", methods=["GET", "POST"])
def home():
    """Display the form, or validate and save a recipe submission."""
    if request.method == "GET":
        return show_page()

    values = {
        "title": request.form.get("title", "").strip(),
        "author": request.form.get("author", "").strip(),
        "method": request.form.get("method", "").strip(),
    }
    ingredient_rows = []
    complete_ingredients = []

    for number in range(1, INGREDIENT_ROWS + 1):
        amount = request.form.get(f"amount_{number}", "").strip()
        name = request.form.get(f"ingredient_{number}", "").strip()
        ingredient_rows.append({"amount": amount, "name": name})

        # A row is either fully blank or has both an amount and a name.
        if amount and name:
            complete_ingredients.append({"amount": amount, "name": name})
        elif amount or name:
            return show_page(
                "Each ingredient needs both an amount and an ingredient name. Please complete the row or clear both fields.",
                values,
                ingredient_rows,
            ), 422

    if not values["title"]:
        return show_page("Please enter a recipe name.", values, ingredient_rows), 422
    if not complete_ingredients:
        return show_page(
            "Please add at least one ingredient, including both its amount and its name.",
            values,
            ingredient_rows,
        ), 422

    recipes.append({**values, "ingredients": complete_ingredients})
    return redirect(url_for("home"))


if __name__ == "__main__":
    # Flask's built-in server is for local development and learning.
    app.run(host="127.0.0.1", port=5000, debug=False)
