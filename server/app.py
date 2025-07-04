from flask import request, session, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from config import app, db
from models import User, Recipe

CORS(app, supports_credentials=True)
migrate = Migrate(app, db)

# --- Signup ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    user = User(
        username=data.get('username'),
        image_url=data.get('image_url'),
        bio=data.get('bio')
    )
    user.password_hash = data.get('password')

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 422

    session['user_id'] = user.id
    return jsonify(user.to_dict()), 201

# --- Check Session ---
@app.route('/check_session', methods=['GET'])
def check_session():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(uid)
    return jsonify(user.to_dict()), 200

# --- Login ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.authenticate(data.get('password')):
        session['user_id'] = user.id
        return jsonify(user.to_dict()), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# --- Logout ---
@app.route('/logout', methods=['DELETE'])
def logout():
    if 'user_id' in session:
        session.pop('user_id')
        return '', 204
    return jsonify({'error': 'Unauthorized'}), 401

# --- Get & Post Recipes ---
@app.route('/recipes', methods=['GET', 'POST'])
def recipes_index():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    if request.method == 'GET':
        recipes = Recipe.query.all()
        return jsonify([r.to_dict() for r in recipes]), 200

    data = request.get_json()
    recipe = Recipe(
        title=data.get('title'),
        instructions=data.get('instructions'),
        minutes_to_complete=data.get('minutes_to_complete'),
        user_id=uid
    )
    if not recipe.title or not recipe.instructions or len(recipe.instructions) < 50:
        return jsonify({'errors': ["Invalid recipe data"]}), 422

    db.session.add(recipe)
    db.session.commit()
    return jsonify(recipe.to_dict()), 201

if __name__ == '__main__':
    app.run(debug=True)
