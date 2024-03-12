from flask import Flask, redirect, render_template
import sqlalchemy
from data.users import User
from forms.login_form import LoginForm
from forms.reg_form import RegisterForm
from forms.chat import ChatForm
from data import db_session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from g4f.client import Client
from g4f.Provider import RetryProvider, Phind, FreeChatgpt, Liaobots
import g4f.debug
import json

"""Константы"""

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'Sdslg35KO236SafA49F21'
client = Client(provider=RetryProvider([Phind, Liaobots, FreeChatgpt], shuffle=False)) # создание клиента для chatGPT
g4f.debug.logging = True

data = [] # список всех сообщений с chatGPT

def chat_GPT(mess):
    """Функция для обновления сообщений с chatGPT"""
    data.append({"role": "user", "content": mess})
    response = client.chat.completions.create(model="", messages=data)
    data.append({"role": "assistance", "content": response.choices[0].message.content})


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='SimpleChat')


@app.route('/chat')
def chat():
  form = ChatForm()
  return render_template('chat.html', title='Чат с User')


@app.route('/chatgpt', methods=['GET', 'POST'])
@login_required
def chatGPT():
  form = ChatForm()
  if form.validate_on_submit():
        chat_GPT(form.message.data)
        return render_template('chatgpt.html', title='Чат с ChatGpt', form=form, messages=data)
  return render_template('chatgpt.html', title='Чат с ChatGpt', form=form, messages=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if len(form.password.data) < 8:
           return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message='len(password) < 8')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/friends')
def friends():
    users = ['Sasa', 'Andrew', 'Das']
    return render_template('friends.html', title='Друзья', users=users)

@app.route('/profile')
@login_required
def profile():
   db_sess = db_session.create_session()
   user = db_sess.query(User).filter_by(name=current_user.name).first()
   return render_template('profile.html', title='Профиль', user=user)

def main():
    db_session.global_init("db/users.db")
    app.run()

if __name__ == '__main__':
  main()