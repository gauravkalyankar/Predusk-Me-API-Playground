import sqlite3
import json
from flask import Flask, jsonify, request, g
from flask_cors import CORS

# --- Configuration ---
DATABASE = 'profile.db'
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app) # Enable Cross-Origin Resource Sharing

# --- Database Connection ---

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        # Use a Row factory to return results as dictionaries
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Helper Functions ---
def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# --- API Endpoints ---

@app.route('/health', methods=['GET'])
def health_check():
    """Liveness probe endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/profile', methods=['GET', 'POST', 'PUT'])
def profile_handler():
    """
    Handles creating, reading, and updating the main profile.
    For this simple app, we assume a single profile entry.
    """
    db = get_db()
    cursor = db.cursor()

    if request.method == 'GET':
        profile = query_db('SELECT name, email, education FROM profile LIMIT 1', one=True)
        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        profile_data = dict(profile)
        # Fetch associated data
        profile_data['skills'] = [row['name'] for row in query_db('SELECT name FROM skills')]
        profile_data['links'] = {row['name']: row['url'] for row in query_db('SELECT name, url FROM links')}
        profile_data['projects'] = [dict(row) for row in query_db('SELECT title, description, links FROM projects')]
        profile_data['work'] = [dict(row) for row in query_db('SELECT company, role, duration, description FROM work_experience')]

        return jsonify(profile_data)

    if request.method in ['POST', 'PUT']:
        data = request.json
        # In a real app, you'd have validation here
        if request.method == 'POST':
             # Simple approach: clear existing and insert new
            cursor.execute('DELETE FROM profile')
            cursor.execute('INSERT INTO profile (name, email, education) VALUES (?, ?, ?)',
                           (data['name'], data['email'], data['education']))
        elif request.method == 'PUT':
            cursor.execute('UPDATE profile SET name=?, email=?, education=? WHERE id=1',
                           (data['name'], data['email'], data['education']))
        db.commit()
        return jsonify({"status": "success", "message": f"Profile {'created' if request.method == 'POST' else 'updated'}"}), 201

@app.route('/projects', methods=['GET'])
def get_projects():
    """Returns projects, optionally filtered by skill."""
    skill_filter = request.args.get('skill')
    if skill_filter:
        # This query joins projects and skills to filter by skill name
        query = """
            SELECT p.title, p.description, p.links
            FROM projects p
            JOIN project_skills ps ON p.id = ps.project_id
            JOIN skills s ON ps.skill_id = s.id
            WHERE s.name LIKE ?
        """
        projects = query_db(query, ('%' + skill_filter + '%',))
    else:
        projects = query_db('SELECT title, description, links FROM projects')

    return jsonify([dict(p) for p in projects])


@app.route('/skills/top', methods=['GET'])
def get_top_skills():
    """Returns the top 5 skills (by ID, for simplicity)."""
    skills = query_db('SELECT name FROM skills ORDER BY id LIMIT 5')
    return jsonify([s['name'] for s in skills])

@app.route('/search', methods=['GET'])
def search():
    """Performs a simple search across project titles/descriptions and work roles/descriptions."""
    query_term = request.args.get('q')
    if not query_term:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    search_pattern = f'%{query_term}%'
    projects = query_db('SELECT title, description, links FROM projects WHERE title LIKE ? OR description LIKE ?',
                        (search_pattern, search_pattern))
    work = query_db('SELECT company, role, description FROM work_experience WHERE role LIKE ? OR description LIKE ?',
                    (search_pattern, search_pattern))

    results = {
        "projects": [dict(p) for p in projects],
        "work_experience": [dict(w) for w in work]
    }
    return jsonify(results)

if __name__ == '__main__':
    # Initialize the database if it doesn't exist
    from database import init_db
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
# import sqlite3
# import json
# import logging
# from functools import wraps
# from base64 import b64decode
# from flask import Flask, jsonify, request, g, Response
# from flask_cors import CORS
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

# # --- Configuration ---
# DATABASE = 'profile.db'
# app = Flask(__name__)
# app.config['JSON_SORT_KEYS'] = False
# CORS(app)

# # --- Logging Setup ---
# # Configure logging to write to a file and the console
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("app.log"),
#         logging.StreamHandler()
#     ]
# )

# # --- Rate Limiting Setup ---
# # Use an in-memory store for rate limiting.
# # For production with multiple workers, you'd use Redis or a similar external store.
# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     default_limits=["200 per minute", "50 per second"],
#     storage_uri="memory://",
# )

# # --- Authentication Decorator ---
# # Simple hardcoded credentials for demonstration.
# # In a real app, use environment variables.
# USERNAME = "admin"
# PASSWORD = "password123"

# def auth_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if auth and auth.username == USERNAME and auth.password == PASSWORD:
#             return f(*args, **kwargs)
#         # Fallback for some clients that send Basic auth in a different header
#         auth_header = request.headers.get('Authorization')
#         if auth_header:
#             try:
#                 encoded_creds = auth_header.split(' ')[1]
#                 decoded_creds = b64decode(encoded_creds).decode('utf-8')
#                 username, password = decoded_creds.split(':')
#                 if username == USERNAME and password == PASSWORD:
#                     return f(*args, **kwargs)
#             except Exception as e:
#                 logging.warning(f"Failed to parse Authorization header: {e}")
#                 pass
        
#         logging.warning("Unauthorized access attempt.")
#         return Response(
#             'Could not verify your access level for that URL.\n'
#             'You have to login with proper credentials', 401,
#             {'WWW-Authenticate': 'Basic realm="Login Required"'})
#     return decorated

# # --- Database Connection ---
# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(DATABASE, check_same_thread=False)
#         g.db.row_factory = sqlite3.Row
#     return g.db

# @app.teardown_appcontext
# def close_db(exception):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()

# # --- API Endpoints ---
# @app.route('/health')
# def health():
#     """Health check endpoint."""
#     logging.info("Health check successful.")
#     return jsonify({"status": "healthy"})

# @app.route('/profile', methods=['GET'])
# def get_profile():
#     """Returns the main profile, including skills, links, work, and projects."""
#     db = get_db()
#     logging.info("Fetching full profile data.")
    
#     # Fetch main profile
#     profile_row = db.execute('SELECT name, email, education FROM profile LIMIT 1').fetchone()
#     if not profile_row:
#         logging.error("Profile data not found in database.")
#         return jsonify({"error": "Profile not found"}), 404
#     profile = dict(profile_row)
    
#     # Fetch associated data
#     profile['skills'] = [row['name'] for row in db.execute('SELECT name FROM skills').fetchall()]
#     profile['links'] = {row['name']: row['url'] for row in db.execute('SELECT name, url FROM links').fetchall()}
#     profile['work_experience'] = [dict(row) for row in db.execute('SELECT company, role, duration, description FROM work_experience').fetchall()]
    
#     # Fetch projects with their skills
#     projects_query = """
#         SELECT p.id, p.title, p.description, p.links
#         FROM projects p
#     """
#     projects_raw = db.execute(projects_query).fetchall()
#     projects_list = []
#     for proj in projects_raw:
#         proj_dict = dict(proj)
#         proj_dict['links'] = json.loads(proj_dict['links'])
#         skills_query = """
#             SELECT s.name
#             FROM skills s
#             JOIN project_skills ps ON s.id = ps.skill_id
#             WHERE ps.project_id = ?
#         """
#         proj_dict['skills'] = [row['name'] for row in db.execute(skills_query, (proj['id'],)).fetchall()]
#         projects_list.append(proj_dict)
    
#     profile['projects'] = projects_list
#     return jsonify(profile)

# @app.route('/profile', methods=['PUT'])
# @auth_required
# @limiter.limit("5 per minute") # Stricter limit for write operations
# def update_profile():
#     """Updates the profile name. Protected by basic auth."""
#     if not request.json or 'name' not in request.json:
#         return jsonify({"error": "Missing 'name' in request body"}), 400
    
#     new_name = request.json['name']
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute("UPDATE profile SET name = ? WHERE id = 1", (new_name,))
#     db.commit()
    
#     logging.info(f"Profile name updated to '{new_name}' by an authorized user.")
#     return jsonify({"success": True, "message": f"Profile name updated to {new_name}"})


# @app.route('/projects', methods=['GET'])
# def get_projects():
#     """Returns a paginated list of projects."""
#     # Pagination parameters
#     page = request.args.get('page', 1, type=int)
#     per_page = request.args.get('per_page', 5, type=int)
#     offset = (page - 1) * per_page
    
#     db = get_db()
#     logging.info(f"Fetching projects - page: {page}, per_page: {per_page}")

#     # Get total number of projects for pagination metadata
#     total_projects = db.execute('SELECT COUNT(id) FROM projects').fetchone()[0]
#     total_pages = (total_projects + per_page - 1) // per_page

#     # Fetch projects for the current page
#     projects_query = "SELECT id, title, description, links FROM projects LIMIT ? OFFSET ?"
#     projects_raw = db.execute(projects_query, (per_page, offset)).fetchall()
    
#     projects_list = []
#     for proj in projects_raw:
#         proj_dict = dict(proj)
#         proj_dict['links'] = json.loads(proj_dict['links'])
#         skills_query = "SELECT s.name FROM skills s JOIN project_skills ps ON s.id = ps.skill_id WHERE ps.project_id = ?"
#         proj_dict['skills'] = [row['name'] for row in db.execute(skills_query, (proj['id'],)).fetchall()]
#         projects_list.append(proj_dict)
        
#     response = {
#         "page": page,
#         "per_page": per_page,
#         "total_pages": total_pages,
#         "total_items": total_projects,
#         "items": projects_list
#     }
#     return jsonify(response)


# # --- Error Handling ---
# @app.errorhandler(429)
# def ratelimit_handler(e):
#     logging.warning(f"Rate limit exceeded: {e.description}")
#     return jsonify(error="ratelimit exceeded", description=e.description), 429

# @app.errorhandler(500)
# def internal_server_error(e):
#     logging.error(f"Server Error: {e}")
#     return jsonify(error="Internal server error"), 500

# if __name__ == '__main__':
#     # Note: `debug=True` is not used here because it can interfere with logging and error handlers.
#     # The `flask run` command in the Dockerfile is the preferred way to run in development.
#     app.run(host='0.0.0.0', port=5000)

