from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/project'  # Update with your database credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# HCP User Model
class HCP(UserMixin, db.Model):
    _tablename__ = 'hcp'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return HCP.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/hcp/register', methods=['POST'])
def register_hcp():
    try:
        data = request.get_json()

        # Check if email already exists
        if HCP.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already registered"}), 400

        # Check if license number already exists
        if HCP.query.filter_by(license_number=data['licenseNumber']).first():
            return jsonify({"error": "License number already registered"}), 400

        # Create new HCP user
        new_hcp = HCP(
            name=data['name'],
            email=data['email'],
            license_number=data['licenseNumber']
        )
        new_hcp.set_password(data['password'])

        # Add to database
        db.session.add(new_hcp)
        db.session.commit()

        return jsonify({
            "message": "Registration successful",
            "user_id": new_hcp.id
        })

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500

@app.route('/api/hcp/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = HCP.query.filter_by(email=data['email']).first()

        if user and user.check_password(data['password']):
            login_user(user)
            return jsonify({
                "success": True,
                "name": user.name,
                "message": "Login successful"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Invalid email or password"
            }), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api/hcp/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)