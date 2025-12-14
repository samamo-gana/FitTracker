from flask import Flask, render_template, url_for, redirect, request, flash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from flask_bcrypt import Bcrypt

from datetime import datetime

import random



app = Flask(__name__)

app.config['SECRET_KEY'] = 'fit-tracker-secret-key-insane-project'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fittracker.db'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = 'login'



# --- Database Models  ---

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), unique=True, nullable=False)

    password = db.Column(db.String(60), nullable=False)

    weights = db.relationship('WeightLog', backref='author', lazy=True)

    workouts = db.relationship('Workout', backref='author', lazy=True)

    meals = db.relationship('Meal', backref='author', lazy=True)



class WeightLog(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    weight = db.Column(db.Float, nullable=False)

    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



class Workout(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    exercise_name = db.Column(db.String(100), nullable=False)

    sets = db.Column(db.Integer, nullable=False)

    reps = db.Column(db.Integer, nullable=False)

    duration_min = db.Column(db.Integer, nullable=True)

    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



class Meal(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    calories = db.Column(db.Integer, nullable=False)

    protein = db.Column(db.Integer, nullable=False)

    carbs = db.Column(db.Integer, nullable=False)

    fats = db.Column(db.Integer, nullable=False)

    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



@login_manager.user_loader

def load_user(user_id):

    return User.query.get(int(user_id))



# --- AI Tips ---

def get_ai_tip():

    tips = [

        "Focus on progressive overload to build muscle effectively.",

        "Ensure you're hitting your protein intake (1.6g - 2.2g per kg).",

        "Sleep is when your muscles grow. Aim for 7-9 hours.",

        "Stay hydrated! Water is crucial for metabolic function.",

        "Don't skip leg day! It boosts overall testosterone."

    ]

    return random.choice(tips)



# ---------------- ROUTES  ----------------



@app.route('/')

def home():

    if current_user.is_authenticated:

        logout_user()

        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])

def register():

    if current_user.is_authenticated:

        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        try:

            hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

            user = User(username=request.form['username'], password=hashed_password)

            db.session.add(user)

            db.session.commit()

            flash('Account created! You can now login', 'success')

            return redirect(url_for('login'))

        except:

            flash('Username already exists or invalid data.', 'danger')

            return render_template('register.html')

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])

def login():

    if current_user.is_authenticated:

        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        user = User.query.filter_by(username=request.form['username']).first()

        if user and bcrypt.check_password_hash(user.password, request.form['password']):

            login_user(user)

            return redirect(url_for('dashboard'))

        else:

            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html')



@app.route('/dashboard', methods=['GET', 'POST'])

@login_required

def dashboard():

    # ---------- HANDLE NEW DATA ----------

    if request.method == 'POST':

        type_ = request.form.get('type')

        try:

            if type_ == 'weight':

                new_weight = WeightLog(weight=float(request.form['weight']), author=current_user)

                db.session.add(new_weight)

                flash('Weight logged successfully!', 'success')

            elif type_ == 'workout':

                new_workout = Workout(

                    exercise_name=request.form['exercise'],

                    sets=int(request.form['sets']),

                    reps=int(request.form['reps']),

                    duration_min=int(request.form['time']),

                    author=current_user

                )

                db.session.add(new_workout)

                flash('Workout logged successfully!', 'success')

            elif type_ == 'meal':

                new_meal = Meal(

                    name=request.form['meal_name'],

                    calories=int(request.form['calories']),

                    protein=int(request.form['protein']),

                    carbs=int(request.form['carbs']),

                    fats=int(request.form['fats']),

                    author=current_user

                )

                db.session.add(new_meal)

                flash('Meal logged successfully!', 'success')

           

            db.session.commit()

        except ValueError:

            flash('Invalid input data. Please ensure all fields are correct.', 'danger')

        except Exception as e:

            flash(f'An error occurred: {e}', 'danger')

            db.session.rollback()

           

        return redirect(url_for('dashboard'))



    # ---------- FETCH DATA ----------

    today = datetime.utcnow().date()

   

    # 1. Today's Logs (Ordered by date/time ascending)

    todays_meals = Meal.query.filter(

        Meal.user_id == current_user.id,

        Meal.date >= datetime(today.year, today.month, today.day)

    ).order_by(Meal.date.asc()).all()

   

    todays_workouts = Workout.query.filter(

        Workout.user_id == current_user.id,

        Workout.date >= datetime(today.year, today.month, today.day)

    ).order_by(Workout.date.asc()).all()

   

    # 2. Current Weight (GET LATEST LOG)

    latest_weight_log = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.date.desc()).first()

    current_weight = latest_weight_log.weight if latest_weight_log else "N/A"

   

    # 3. Weight History for Chart (Last 10 points)

    weight_history_logs = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.date.desc()).limit(10).all()

    weight_history_logs.reverse()

    weight_data = [log.weight for log in weight_history_logs]

    weight_dates = [log.date.strftime('%b %d') for log in weight_history_logs]



    # ---------- NUTRITION TOTALS ----------

    today_calories = sum(m.calories for m in todays_meals)

    today_protein = sum(m.protein for m in todays_meals)

    today_carbs = sum(m.carbs for m in todays_meals)

    today_fats = sum(m.fats for m in todays_meals)



    # ---------- RENDER ----------

    return render_template(

        'dashboard.html',

        ai_tip=get_ai_tip(),

        todays_meals=todays_meals,

        todays_workouts=todays_workouts,

        today_calories=today_calories,

        today_protein=today_protein,

        today_carbs=today_carbs,

        today_fats=today_fats,

        current_weight=current_weight,

        weight_data=weight_data,

        weight_dates=weight_dates,

        user=current_user

    )





@app.route('/reset_today_data', methods=['POST'])

@login_required

def reset_today_data():

    today = datetime.utcnow().date()

   

    start_of_day = datetime(today.year, today.month, today.day)

   



    Meal.query.filter(

        Meal.user_id == current_user.id,

        Meal.date >= start_of_day

    ).delete()

   

    

    Workout.query.filter(

        Workout.user_id == current_user.id,

        Workout.date >= start_of_day

    ).delete()

   

    db.session.commit()

    flash('All meals and workouts for today have been reset!', 'warning')

    return redirect(url_for('dashboard'))



@app.route('/logout')

def logout():

    logout_user()

    return redirect(url_for('home'))



if __name__ == '__main__':

    with app.app_context():

    
        db.create_all()

    app.run(debug=True)