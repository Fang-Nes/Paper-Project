from flask import Flask, render_template, redirect, make_response, request, session, abort
from data import db_session
from registerform import RegisterForm
from loginform import LoginForm
from data.users import User
from data.pictures import Picture
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import url_for

import os
from PIL import Image

from flask_ngrok import run_with_ngrok

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
run_with_ngrok(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    session = db_session.create_session()
    return render_template('index.html', title="Главная страница")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        errors = []
        if session.query(User).filter(User.email == form.email.data).first():
            errors.append("Такой пользователь уже есть")
        if form.password.data != form.password_again.data:
            errors.append("Пароли не совпадают")
        if errors:
            return render_template('register.html', title='Регистрация',
                                   form=form, errors=errors)
        user = User(name=form.name.data, email=form.email.data, about=form.about.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        os.mkdir(os.getcwd() + '/static/img/users_pictures/' + str(user.id))
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'GET':
        return render_template('profile.html', title='Профиль')
    elif request.method == 'POST':
        session = db_session.create_session()
        pic = Picture()
        pic.name = request.form['name']
        pic.user_id = current_user.id
        session.add(pic)
        session.commit()
        f = request.files['file']
        im = Image.open(f)
        im.save(os.getcwd() + '/static/img/users_pictures/' + str(pic.user_id) + '/' + str(pic.id) + '.png')
        return redirect('art')


@app.route('/art')
def art():
    session = db_session.create_session()
    return render_template('art.html', title="Арты", pics=session.query(Picture))


@app.route('/about')
def about():
    return render_template('about.html', title="О нас")


@app.route('/contact')
def contact():
    return render_template('contact.html', title="Обратная связь")


def main():
    db_session.global_init("db/blogs.sqlite")
    app.run()


if __name__ == '__main__':
    main()
