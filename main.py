from flask import Flask, redirect, render_template, flash, request, send_from_directory, url_for, send_file
from data.users import User
from forms.login_form import LoginForm
from forms.change_name_form import ChangeName
from forms.change_email_form import ChangeEmail
from forms.reg_form import RegisterForm
from forms.add_friends import FriendsForm
from forms.chat import ChatForm
from data import db_session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from data.AI import AI
from firebase_admin import db
from data.firebase_admin import *
from werkzeug.utils import secure_filename
import os
from data.random_ava import generate_image

# Константы

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'Sdslg35KO236SafA49F21'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
GPT = AI()  # Создание ИИ
db_fire = FirebaseAdmin()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/add-photo', methods=['GET', 'POST'])
def upload_file():
    pass


@app.route('/fonts/<path:filename>')
def custom_static(filename):
    return send_from_directory('fonts', filename)

# Главная страница

@app.route('/')
def index():
    return render_template('index.html', title='SimpleChat')


# Чатик


@app.route('/chat')
@login_required
def chat():
    form = ChatForm()
    db_sess = db_session.create_session()
    if db.reference(f'/Friends/{current_user.id}').get():
        frnds = []
        for i in [int(j) for j in db.reference(f'/Friends/{current_user.id}').get().split(', ')]:
            frnds.append(db_sess.query(User).filter_by(id=i).first())
    else:
        frnds = 'У Вас нет друзей...'
    return render_template('chat.html', title='Чат с User', friends=frnds, form=form, chat=False)


# Чатик с определенным ползователем

@app.route('/chat/<int:id_of_user>', methods=["POST", "GET"])
@login_required
def chat_with_user(id_of_user):
    if id_of_user in [int(j) for j in db.reference(f'/Friends/{current_user.id}').get().split(', ')]:
        form = ChatForm()
        db_sess = db_session.create_session()
        if db.reference(f'/Friends/{current_user.id}').get():
            frnds = []
            for i in [int(j) for j in db.reference(f'/Friends/{current_user.id}').get().split(', ')]:
                frnds.append(db_sess.query(User).filter_by(id=i).first())
        else:
            frnds = 'У Вас нет друзей...'
        mess = db.reference(f'/Chats/{" ".join(sorted([str(current_user.id), str(id_of_user)]))}').get()
        if form.validate_on_submit():
            if mess:
                mess.append({
                    "role": current_user.id,
                    "text": form.message.data
                })
            else:
                mess = [{
                    "role": current_user.id,
                    "text": form.message.data
                }]
            db.reference(f'/Chats/').update({
                ' '.join(sorted([str(current_user.id), str(id_of_user)])): mess
            })
        return render_template('chat.html', 
                                title=f'Чат с {db_sess.query(User).filter_by(id=id_of_user).first().name}',
                                friends=frnds,
                                messages=mess,
                                name_of_friend=db_sess.query(User).filter_by(id=id_of_user).first().name,
                                form=form, 
                                chat=True, 
                                ref=sorted([str(current_user.id), str(id_of_user)]))
    else:
        return render_template('error.html', title='Это не Ваш друг', error='Это не Ваш друг')


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
        return render_template('chatgpt.html', title='Чат с ChatGpt', form=form,
                               messages=db.reference(f'/Chat with GPT/{current_user.id}').get())
    return render_template('chatgpt.html', title='Чат с ChatGpt', form=form,
                           messages=db.reference(f'/Chat with GPT/{current_user.id}').get())


# Очистка чата с GPT

@app.route('/delete-chatgpt')
@login_required
def delete_chatGPT():
    db.reference(f'/Chat with GPT/').update({
        current_user.id: ''
    })
    return redirect('/chatgpt')

# Уведомления

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    if db.reference(f'Notifications/{current_user.id}').get():
        notifications = db_fire.get_data(f'Notifications/{current_user.id}')
    else:
        notifications = {0: 'У тебя нет уведомлений'}
        db_fire.add_data(f'Notifications/{current_user.id}', notifications)
    if len(notifications) > 1:
        return render_template('notifications.html', title='Уведомления', notifications=notifications, unread_nots=True)
    else:
        return render_template('notifications.html', title='Уведомления', notifications=notifications, unread_nots=False)

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
        users = db_sess.query(User).filter(User.name == form.name_of_user.data, User.id not in friends_ids,
                                           User.id != current_user.id)
        return render_template('friends.html', title='Друзья', users=users, form=form, search=True,
                               friends_ids=friends_ids)
    return render_template('friends.html', title='Друзья', users=users, form=form, friends_ids=friends_ids)


# Добавление в друзья

@app.route('/add-to-friends/<int:id_of_user>')
@login_required
def add_to_friends(id_of_user):
    if db.reference(f'/Friends/{current_user.id}').get():
        friends = db.reference(f'/Friends/{current_user.id}').get().split(', ')
        friends.append(str(id_of_user)) if str(id_of_user) not in friends else None
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
    return render_template('profile.html', title='Профиль', user=user, current_us=True)


# Профиль определенного человека

@app.route('/profile/<int:id_of_user>')
@login_required
def profie_of_user(id_of_user):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=id_of_user).first()
    return render_template('profile.html', title='Профиль', user=user, current_us=False)


# Имзенение имени

@app.route('/change-name', methods=['POST', 'GET'])
@login_required
def change_name():
    form = ChangeName()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        user = db_sess.query(User).filter_by(id=current_user.id).first()
        user.name = form.name.data
        db_sess.commit()
        return redirect('/profile')
    return render_template('change-name.html', title='Изменить имя', form=form)


# Имзенение почты

@app.route('/change-email', methods=['POST', 'GET'])
@login_required
def change_email():
    form = ChangeEmail()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('change-email.html', title='Изменить почту',
                                   form=form,
                                   message="Эта почта уже используется")
        user = db_sess.query(User).filter_by(id=current_user.id).first()
        user.email = form.email.data
        db_sess.commit()
        return redirect('/profile')
    return render_template('change-email.html', title='Изменить почту', form=form)

# Изменение фото

@app.route('/change-photo', methods=['POST', 'GET'])
@login_required
def change_photo():
    return render_template('change-photo.html')

# Рандомная ава

@app.route('/generate-profile-photo', methods=['GET'])
def random_ava():
    ava = generate_image()
    return send_file(ava, mimetype='image/png')

# Проверка валидности файла


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def main():
    db_session.global_init("db/users.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
