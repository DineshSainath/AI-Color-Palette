import openai
import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import dotenv_values
from livereload import Server
from models import db, User, Palette
from forms import RegistrationForm, LoginForm, PaletteForm
from sqlalchemy.exc import OperationalError

# Load API key from .env file
dot_env = dotenv_values(".env")
# openai.api_key = dot_env["OPENAI_API_KEY"]
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='')

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_for_development_only')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///palette.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add connection pooling and timeout settings for better reliability in serverless environment
if os.getenv('DATABASE_URL') and 'postgresql' in os.getenv('DATABASE_URL'):
    # Check if we're using Supavisor (connection pooler)
    is_supavisor = 'pooler.supabase.com' in os.getenv('DATABASE_URL', '')
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_timeout': 10,
        'pool_size': 1 if is_supavisor else 5,  # Smaller pool for Supavisor
        'max_overflow': 0,  # No overflow connections
        'connect_args': {
            'connect_timeout': 15,  # Increased timeout
            'application_name': 'palette_ai_vercel',
            'sslmode': 'require',
            # Only use keepalives for direct connections, not for Supavisor
            **({"keepalives": 1, 
                "keepalives_idle": 30,
                "keepalives_interval": 10, 
                "keepalives_count": 5} if not is_supavisor else {}),
            'options': '-c statement_timeout=30000'  # 30 second statement timeout
        }
    }

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def getPalette(msg):
    response = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "You are a color palette generating assistant. You should generate color palettes that fit the theme, mood, or instructions in the prompt. The palettes should be between 3 and 5 colors."},
            {"role": "user", "content": f"""Input:{msg}. The output should be in a JSON array format. Don't say it's JSON, just give the array in a single line."""}
        ],
        max_tokens=100
    )

    colors = json.loads(response.choices[0].message.content)
    return colors

@app.route("/palette", methods=['POST'])
def promptForPalette():
    app.logger.info("HIT THE POST REQUEST ROUTE!")
    query = request.form.get("query")
    colors = getPalette(query)  # Generate color palette
    app.logger.info(f"Generated colors: {colors}")
    
    return {"colors": colors}

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error with the OpenAI API request."

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    try:
        if form.validate_on_submit():
            # Add retry logic for database operations
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    user = User.query.filter_by(email=form.email.data).first()
                    if user and user.check_password(form.password.data):
                        login_user(user)
                        flash('Logged in successfully!', 'success')
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('index'))
                    else:
                        flash('Invalid email or password', 'danger')
                    break  # Exit the retry loop if query succeeds
                except OperationalError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        app.logger.error(f"Database connection failed after {max_retries} retries: {str(e)}")
                        flash('Database connection error. Please try again later.', 'danger')
                        raise
                    app.logger.warning(f"Database connection attempt {retry_count} failed, retrying: {str(e)}")
                    time.sleep(1)  # Wait before retrying
                except Exception as e:
                    app.logger.error(f"Database error during login: {str(e)}")
                    flash('An error occurred while trying to log in. Please try again later.', 'danger')
                    raise
    except Exception as e:
        app.logger.error(f"Form validation error: {str(e)}")
        flash('An error occurred while processing your request. Please try again later.', 'danger')
    
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route("/save_palette", methods=['POST'])
@login_required
def save_palette():
    name = request.form.get('name')
    colors_json = request.form.get('colors')
    
    if not name or not colors_json:
        return jsonify({'error': 'Missing required fields'}), 400
    
    palette = Palette(name=name, colors=colors_json, user_id=current_user.id)
    db.session.add(palette)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Palette saved successfully'})

@app.route("/my_palettes")
@login_required
def my_palettes():
    palettes = Palette.query.filter_by(user_id=current_user.id).order_by(Palette.created_at.desc()).all()
    
    # Add colors_list attribute to each palette
    for palette in palettes:
        palette.colors_list = json.loads(palette.colors)
    
    return render_template('my_palettes.html', palettes=palettes)

@app.route("/palette/<int:palette_id>")
@login_required
def view_palette(palette_id):
    palette = Palette.query.get_or_404(palette_id)
    
    # Check if the palette belongs to the current user
    if palette.user_id != current_user.id:
        flash('You do not have permission to view this palette', 'danger')
        return redirect(url_for('my_palettes'))
    
    palette.colors_list = json.loads(palette.colors)
    return render_template('view_palette.html', palette=palette)

@app.route("/delete_palette/<int:palette_id>", methods=['POST'])
@login_required
def delete_palette(palette_id):
    palette = Palette.query.get_or_404(palette_id)
    
    # Check if the palette belongs to the current user
    if palette.user_id != current_user.id:
        flash('You do not have permission to delete this palette', 'danger')
        return redirect(url_for('my_palettes'))
    
    db.session.delete(palette)
    db.session.commit()
    flash('Palette deleted successfully', 'success')
    return redirect(url_for('my_palettes'))

@app.route("/debug")
def debug():
    """Debug route to check database connection and configuration."""
    try:
        # Check database connection
        with db.engine.connect() as conn:
            result = conn.execute("SELECT 1").fetchone()
            db_connected = result is not None
        
        # Get environment info
        env_info = {
            "VERCEL_ENV": os.environ.get("VERCEL_ENV", "Not set"),
            "DATABASE_URL": os.environ.get("DATABASE_URL", "Not set")[:20] + "..." if os.environ.get("DATABASE_URL") else "Not set",
            "FLASK_ENV": os.environ.get("FLASK_ENV", "Not set"),
            "DB Connected": db_connected,
            "SQLAlchemy Version": db.engine.dialect.driver,
        }
        
        return jsonify({
            "status": "ok",
            "environment": env_info,
            "tables": [table for table in db.metadata.tables.keys()]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "type": str(type(e))
        }), 500

@app.route("/test_db_connection")
def test_db_connection():
    """Test database connection directly using psycopg2."""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Get database URL
        database_url = os.getenv('DATABASE_URL', '')
        
        if not database_url:
            return jsonify({"status": "error", "message": "No DATABASE_URL environment variable set"}), 500
        
        # Parse the URL
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        # Check if using Supavisor
        is_supavisor = 'pooler.supabase.com' in hostname if hostname else False
        
        # Connect directly with additional parameters
        connection_params = {
            "database": database,
            "user": username,
            "password": password,
            "host": hostname,
            "port": port,
            "connect_timeout": 15,
            "sslmode": 'require',
            "options": "-c statement_timeout=30000"
        }
        
        # Only add keepalives for direct connections, not for Supavisor
        if not is_supavisor:
            connection_params.update({
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5
            })
        
        app.logger.info(f"Connecting to database at {hostname} (Supavisor: {is_supavisor})")
        connection = psycopg2.connect(**connection_params)
        
        # Test the connection
        cursor = connection.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success", 
            "message": "Database connection successful",
            "version": version[0] if version else "Unknown",
            "using_supavisor": is_supavisor,
            "host": hostname
        })
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "error_type": str(type(e)),
            "host": result.hostname if 'result' in locals() else "Unknown",
            "using_supavisor": 'pooler.supabase.com' in result.hostname if 'result' in locals() and result.hostname else False
        }), 500

@app.route("/health")
def health_check():
    """Simple health check that doesn't require database access."""
    return jsonify({
        "status": "ok",
        "message": "Application is running",
        "timestamp": time.time(),
        "environment": os.environ.get("VERCEL_ENV", "development")
    })

@app.route("/test_sqlalchemy")
def test_sqlalchemy_connection():
    """Test database connection using SQLAlchemy."""
    try:
        # Get database URL for diagnostics
        database_url = os.getenv('DATABASE_URL', '')
        is_supavisor = 'pooler.supabase.com' in database_url
        
        # Test with a simple query
        result = db.session.execute(db.text("SELECT 1")).fetchone()
        
        # Get database version
        version_result = db.session.execute(db.text("SELECT version()")).fetchone()
        version = version_result[0] if version_result else "Unknown"
        
        # Parse connection info for diagnostics
        from urllib.parse import urlparse
        parsed_url = urlparse(database_url)
        hostname = parsed_url.hostname
        
        return jsonify({
            "status": "success",
            "message": "SQLAlchemy connection successful",
            "result": result[0] if result else None,
            "version": version,
            "using_supavisor": is_supavisor,
            "host": hostname or "Unknown",
            "engine_options": {
                k: str(v) for k, v in app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).items() 
                if k != 'connect_args'  # Don't expose credentials
            }
        })
    except Exception as e:
        app.logger.error(f"SQLAlchemy connection error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"SQLAlchemy connection failed: {str(e)}",
            "error_type": str(type(e)),
            "using_supavisor": 'pooler.supabase.com' in os.getenv('DATABASE_URL', '')
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions."""
    app.logger.error(f"Unhandled exception: {str(e)}")
    return render_template('error.html', error=str(e)), 500

@app.context_processor
def inject_user_logged_in():
    return dict(user_logged_in=current_user.is_authenticated)

# Create database tables
# Only create tables when running locally, not on Vercel
if not os.environ.get('VERCEL_ENV'):
    with app.app_context():
        db.create_all()
else:
    # For Vercel, we'll just ensure the app context is set up properly
    # Tables should be created using the setup_db.py script
    with app.app_context():
        pass  # Just initialize the app context

if __name__ == "__main__":
    # Only run the development server when running locally
    if not os.environ.get('VERCEL_ENV'):
        server = Server(app.wsgi_app)  # Create a livereload server
        server.watch('templates/*.html')  #  Watch HTML changes
        server.watch('static/*.css')  #  Watch CSS changes
        server.serve(port=5000, debug=True)
    else:
        app.run()  
