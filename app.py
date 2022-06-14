# flask basic app
from django.shortcuts import render
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager , login_required, login_user, logout_user, current_user, UserMixin
from enum import Enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

class TodoStatus(Enum):
    CREATED = 1
    COMPLETED = 2

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)
db = SQLAlchemy(app)

# user model


# sqlite db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'

# create all tables
# db.create_all()



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))


    def __repr__(self):
        return '<User %r>' % self.username

# todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.Boolean, default=TodoStatus.CREATED.value)

    def get_status_from_enum(self):
        if self.status is not None and self.status == 1:
            return "COMPLETED"
        else:
            return "CREATED"

    def __repr__(self):
        return '<Todo %r>' % self.description
    


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/home')
# @login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user, remember=True)
            return redirect(url_for('listTodos'))
        else:
            flash('Invalid Credentials')
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username.lower()).first()
        if user:
            flash('Username already exists', 'danger')
            return render_template('register.html', error='Username already exists')
        else:
            user = User(username=username, password=password.lower())
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    else:
        return render_template('register.html')
    


@app.route('/listTodos', methods=['GET'])
@login_required
def listTodos():    
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('listTodos.html', todos=todos)


@app.route('/deleteTodo/<int:todo_id>', methods=['GET'])
@login_required
def deleteTodo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for('listTodos'))
    else:
        flash('Todo not found')
        return redirect(url_for('listTodos'))

@app.route('/mark_as_complete/<int:todo_id>', methods=['GET'])
@login_required
def mark_as_complete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo:
        todo.status = True
        todo.completed_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('listTodos'))
    else:
        flash('Todo not found')
        return redirect(url_for('listTodos'))

@app.route('/createTodo', methods=['GET', 'POST'])
@login_required
def createTodo():
    if request.method == 'POST':
        description = request.form['description']
        if current_user is None:
            flash('Invalid user_id')
            return redirect(url_for('createTodo'))
        todo = Todo(description=description, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('listTodos'))
    else:
        return render_template('createTodo.html')
    

        