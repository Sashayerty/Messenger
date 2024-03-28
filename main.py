from flask import Flask, redirect, render_template
from data.users import User
from forms.login_form import LoginForm
from forms.reg_form import RegisterForm
from forms.add_friends import FriendsForm
from forms.chat import ChatForm
from data import db_session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from data.AI import AI
from firebase_admin import db
from data.firebase_admin import *

"""Константы"""

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'Sdslg35KO236SafA49F21'
GPT = AI()  # Создание ИИ
db_fire = FirebaseAdmin()


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
    if not db.reference(f'/Chat with GPT/{current_user.id}').get():
        db_fire.add_data(f'/Chat with GPT/',
                         {
                             current_user.id: [
                                 {
                                     "role": "system",
                                     "text": "Ты ии-программист."
                                 }
                             ]
                         })
        GPT.set_messages(
            {
                    "role": "system",
                    "text": "Ты ии-программист."
                }
        )
    if form.validate_on_submit():
        GPT.set_messages(db.reference(f'/Chat with GPT/{current_user.id}').get())     
        GPT.message(form.message.data)
        db_fire.add_data(f'/Chat with GPT/', {
            current_user.id: GPT.get_messages()
        })
        return render_template('chatgpt.html', title='Чат с ChatGpt', form=form, messages=db.reference(f'/Chat with GPT/{current_user.id}').get())
    return render_template('chatgpt.html', title='Чат с ChatGpt', form=form, messages=db.reference(f'/Chat with GPT/{current_user.id}').get())

# Очистка чата с GPT

@app.route('/delete-chatgpt')
@login_required
def delete_chatGPT():
    db.reference(f'/Chat with GPT/').update({
        current_user.id: ''
    })
    return redirect('/chatgpt')

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


@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    form = FriendsForm()
    db_sess = db_session.create_session()
    users = []
    if db.reference(f'/Friends/{current_user.id}').get():
        for i in (db.reference(f'/Friends/{current_user.id}').get().split(', ')):
            users.append(db_sess.query(User).get(i))
    if db.reference(f'/Friends/{current_user.id}').get():
        friends_ids = [int(i) for i in db.reference(f'/Friends/{current_user.id}').get().split(', ')]
    else:
        friends_ids = []
    if form.validate_on_submit():
        users = db_sess.query(User).filter(User.name == form.name_of_user.data, User.id not in friends_ids, User.id != current_user.id)
        return render_template('friends.html', title='Друзья', users=users, form=form, search=True, friends_ids=friends_ids)
    return render_template('friends.html', title='Друзья', users=users, form=form, friends_ids=friends_ids)

# Добавление в друзья

@app.route('/add-to-friends/<int:id_of_user>')
@login_required
def add_to_friends(id_of_user):
    if db.reference(f'/Friends/{current_user.id}').get():
        friends = db.reference(f'/Friends/{current_user.id}').get().split(', ')
        friends.append(str(id_of_user))
    else:
        friends = str(id_of_user)
    db.reference(f'/Friends/').update({
        current_user.id: ', '.join(friends)
    })
    if db.reference(f'/Friends/{id_of_user}').get():
        friends = db.reference(f'/Friends/{id_of_user}').get().split(', ')
        friends.append(str(current_user.id))
    else:
        friends = str(current_user.id)
    db.reference(f'/Friends/').update({
        id_of_user: ', '.join(friends)
    })
    return redirect('/friends')

# Удаление из друзей

@app.route('/delete-from-friends/<int:id_of_user>')
@login_required
def delete_from_friends(id_of_user):
    if db.reference(f'/Friends/{current_user.id}').get():
        friends = db.reference(f'/Friends/{current_user.id}').get().split(', ')
        friends.remove(str(id_of_user))
    else:
        friends = ''
    db.reference(f'/Friends/').update({
        current_user.id: ', '.join(friends) if friends else friends
    })
    if db.reference(f'/Friends/{id_of_user}').get():
        friends = db.reference(f'/Friends/{id_of_user}').get().split(', ')
        friends.remove(str(current_user.id))
    else:
        friends = str(current_user.id)
    db.reference(f'/Friends/').update({
        id_of_user: ', '.join(friends) if friends else friends
    })
    return redirect('/friends')



# Профиль

@app.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=current_user.id).first()
    return render_template('profile.html', title='Профиль', user=user)


def main():
    db_session.global_init("db/users.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
