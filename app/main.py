from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from bson import ObjectId
from urllib.parse import quote_plus
import os

app = Flask(__name__)

def connect_to_db():
    try:
        # Get MongoDB credentials from environment variables
        mongo_user = os.environ.get('MONGO_USER')
        mongo_password = os.environ.get('MONGO_PASSWORD')
        mongo_host = os.environ.get('MONGO_HOST', 'localhost')
        mongo_port = os.environ.get('MONGO_PORT', '27017')
        mongo_db_name = os.environ.get('MONGO_DB_NAME', 'UniversalDB')

        # Connection URI
        connection_uri = f'mongodb://{quote_plus(mongo_user)}:{quote_plus(mongo_password)}@{mongo_host}:{mongo_port}/{mongo_db_name}?authSource=admin'
        client = MongoClient(connection_uri)
        db = client[mongo_db_name]

        return db
    except Exception as e:
        print(f"Failed to connect to the database. Error: {e}")
        return None

def convert_objectid_to_str(doc):
    if '_id' in doc and isinstance(doc['_id'], ObjectId):
        doc['_id'] = str(doc['_id'])
    return doc

@app.route('/')
def home():
    html_content = '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Game Searcher</title>
      </head>
      <body>
        <h1>Welcome to the Game Searcher!</h1>
        <form action="/games/by-name" method="get">
          <label for="game_name">Search by Game Name:</label>
          <input type="text" id="game_name" name="game_name">
          <button type="submit">Search</button>
        </form>
        <form action="/games/by-studio" method="get">
          <label for="studio_name">Search by Studio Name:</label>
          <input type="text" id="studio_name" name="studio_name">
          <button type="submit">Search</button>
        </form>
        <form action="/games/by-genre" method="get">
          <label for="genre">Search by Genre:</label>
          <input type="text" id="genre" name="genre">
          <button type="submit">Search</button>
        </form>
        <form action="/games/by-year" method="get">
          <label for="year">Search by Year:</label>
          <input type="number" id="year" name="year">
          <button type="submit">Search</button>
        </form>
      </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/games/by-name')
def get_game_by_name():
    game_name = request.args.get('game_name')
    db = connect_to_db()
    if db is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    game = db.games.find_one({"normalized_name": game_name.lower().replace(" ", "")})
    if game:
        game = convert_objectid_to_str(game)
        return render_template_string(render_game(game))
    else:
        return jsonify({"error": "Game not found"}), 404

@app.route('/games/by-studio')
def get_games_by_studio():
    studio_name = request.args.get('studio_name')
    db = connect_to_db()
    if db is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    cursor = db.games.find({"normalized_studio": studio_name.lower().replace(" ", "")})
    games = list(cursor)
    if games:
        games = [convert_objectid_to_str(game) for game in games]
        return render_template_string(render_games(games))
    else:
        return jsonify({"error": "No games found"}), 404

@app.route('/games/by-genre')
def get_games_by_genre():
    genre = request.args.get('genre')
    db = connect_to_db()
    if db is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    cursor = db.games.find({"genre": genre.lower()})
    games = list(cursor)
    if games:
        games = [convert_objectid_to_str(game) for game in games]
        return render_template_string(render_games(games))
    else:
        return jsonify({"error": "No games found"}), 404

@app.route('/games/by-year')
def get_games_by_year():
    year = request.args.get('year')
    db = connect_to_db()
    if db is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    cursor = db.games.find({"release_year": int(year)})
    games = list(cursor)
    if games:
        games = [convert_objectid_to_str(game) for game in games]
        return render_template_string(render_games(games))
    else:
        return jsonify({"error": "No games found"}), 404

def render_game(game):
    return f'''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Game Details</title>
      </head>
      <body>
        <h1>{game['name']}</h1>
        <ul>
          <li><strong>Genre:</strong> {game['genre']}</li>
          <li><strong>Studio:</strong> {game['studio']}</li>
          <li><strong>Release Year:</strong> {game['release_year']}</li>
        </ul>
      </body>
    </html>
    '''

def render_games(games):
    game_entries = ''.join([f'''
        <li>
          <h2>{game['name']}</h2>
          <ul>
            <li><strong>Genre:</strong> {game['genre']}</li>
            <li><strong>Studio:</strong> {game['studio']}</li>
            <li><strong>Release Year:</strong> {game['release_year']}</li>
          </ul>
        </li>
    ''' for game in games])
    
    return f'''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Game List</title>
      </head>
      <body>
        <h1>Games</h1>
        <ul>
          {game_entries}
        </ul>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
