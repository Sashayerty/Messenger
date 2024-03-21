from flask import Flask, redirect, render_template
from data.users import User
from forms.login_form import LoginForm
from forms.reg_form import RegisterForm
from forms.chat import ChatForm
from data import db_session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from g4f.client import Client
from g4f.Provider import RetryProvider, Phind, FreeChatgpt, Liaobots
import g4f.debug
from data.AI import AI

"""Константы"""

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'Sdslg35KO236SafA49F21'
GPT = AI() # Создание ИИ


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# Главная страница

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='SimpleChat')

# Чатик


@app.route('/chat')
def chat():
  form = ChatForm()
  return render_template('chat.html', title='Чат с User')

# Чатик GPT


@app.route('/chatgpt', methods=['GET', 'POST'])
@login_required
def chatGPT():
  form = ChatForm()
  if form.validate_on_submit():
        GPT.message(form.message.data)
        return render_template('chatgpt.html', title='Чат с ChatGpt', form=form, messages=GPT.messages())
  return render_template('chatgpt.html', title='Чат с ChatGpt', form=form, messages=GPT.messages())

# Вход


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

# Выход


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

# Регистрация


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

# Друзья


@app.route('/friends')
def friends():
    db_sess = db_session.create_session()
    users = [1, 2, 3, 4]
    print(list(users))
    return render_template('friends.html', title='Друзья', users=users)

# Профиль

@app.route('/profile')
@login_required
def profile():
   db_sess = db_session.create_session()
   user = db_sess.query(User).filter_by(name=current_user.name).first()
   return render_template('profile.html', title='Профиль', user=user)

def main():
    db_session.global_init("db/users.db")
    app.run(debug=True)

if __name__ == '__main__':
  main()