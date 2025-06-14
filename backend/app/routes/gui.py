from flask import Blueprint, render_template

gui_bp = Blueprint('gui', __name__, template_folder='templates')

@gui_bp.route('/')
def index():
    return render_template('index.html')