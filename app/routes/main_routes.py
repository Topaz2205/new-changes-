from flask import Blueprint, render_template
from app.utils.decorators import login_required


main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
@login_required
def home():
    return render_template('home.html')  # תוודא שקיים קובץ כזה
