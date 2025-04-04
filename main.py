import os
from io import BytesIO

import requests
from firebase_admin import db
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from PIL import Image
from werkzeug.utils import secure_filename

from data import db_session
from data.AI import AI
from data.firebase_admin import *
from data.local_url import local_url as url
from data.random_ava import generate_image
from data.users import User
from forms.add_friends import FriendsForm
from forms.change_email_form import ChangeEmail
from forms.change_name_form import ChangeName
from forms.chat import ChatForm
from forms.login_form import LoginForm
from forms.reg_form import RegisterForm

# Константы

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SECRET_KEY"] = "Sdslg35KO236SafA49F21"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
GPT = AI()  # Создание ИИ


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Добавление фото


@app.route("/add-photo", methods=["GET", "POST"])
def upload_file():
    pass


# Подключение к шрифтам


@app.route("/fonts/<path:filename>")
def custom_static(filename):
    return send_from_directory("fonts", filename)


# Главная страница


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template(
            "index.html",
            title="SimpleChat",
            url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
        )
    else:
        return render_template("index.html", title="SimpleChat")


# Чатик


@app.route("/chat")
@login_required
def chat():
    form = ChatForm()
    db_sess = db_session.create_session()
    if db.reference(f"/Friends/{current_user.id}").get():
        frnds = []
        for i in [
            int(j)
            for j in db.reference(f"/Friends/{current_user.id}")
            .get()
            .split(", ")
        ]:
            frnds.append(db_sess.query(User).filter_by(id=i).first())
    else:
        frnds = "У Вас нет друзей..."
    return render_template(
        "chat.html",
        title="Чат с User",
        friends=frnds,
        form=form,
        chat=False,
        url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
    )


# Чатик с определенным ползователем


@app.route("/chat/<int:id_of_user>", methods=["POST", "GET"])
@login_required
def chat_with_user(id_of_user):
    if id_of_user in [
        int(j)
        for j in db.reference(f"/Friends/{current_user.id}").get().split(", ")
    ]:
        form = ChatForm()
        db_sess = db_session.create_session()
        if db.reference(f"/Friends/{current_user.id}").get():
            frnds = []
            for i in [
                int(j)
                for j in db.reference(f"/Friends/{current_user.id}")
                .get()
                .split(", ")
            ]:
                frnds.append(db_sess.query(User).filter_by(id=i).first())
        else:
            frnds = "У Вас нет друзей..."
        mess = db.reference(
            f'/Chats/{" ".join(sorted([str(current_user.id), str(id_of_user)]))}'
        ).get()
        if form.validate_on_submit():
            if mess:
                mess.append(
                    {"role": current_user.id, "text": form.message.data}
                )
            else:
                mess = [{"role": current_user.id, "text": form.message.data}]
            db.reference(f"/Chats/").update(
                {
                    " ".join(
                        sorted([str(current_user.id), str(id_of_user)])
                    ): mess
                }
            )
        return render_template(
            "chat.html",
            title=f"Чат с {db_sess.query(User).filter_by(id=id_of_user).first().name}",
            friends=frnds,
            messages=mess,
            url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
            name_of_friend=db_sess.query(User)
            .filter_by(id=id_of_user)
            .first()
            .name,
            form=form,
            chat=True,
            ref=sorted([str(current_user.id), str(id_of_user)]),
        )
    else:
        return render_template(
            "error.html",
            title="Это не Ваш друг",
            error="Это не Ваш друг",
            url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
        )


# Чатик GPT


@app.route("/chatgpt", methods=["GET", "POST"])
@login_required
def chatGPT():
    form = ChatForm()
    if not db.reference(f"/Chat with GPT/{current_user.id}").get():
        db_fire.add_data(
            f"/Chat with GPT/",
            {
                current_user.id: [
                    {"role": "system", "text": "Ты ии-программист."}
                ]
            },
        )
        GPT.set_messages({"role": "system", "text": "Ты ии-программист."})
    if form.validate_on_submit():
        GPT.set_messages(
            db.reference(f"/Chat with GPT/{current_user.id}").get()
        )
        GPT.message(form.message.data)
        db_fire.add_data(
            f"/Chat with GPT/", {current_user.id: GPT.get_messages()}
        )
        return render_template(
            "chatgpt.html",
            title="Чат с ChatGpt",
            form=form,
            messages=db.reference(f"/Chat with GPT/{current_user.id}").get(),
            url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
        )
    return render_template(
        "chatgpt.html",
        title="Чат с ChatGpt",
        form=form,
        messages=db.reference(f"/Chat with GPT/{current_user.id}").get(),
        url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
    )


# Очистка чата с GPT


@app.route("/delete-chatgpt")
@login_required
def delete_chatGPT():
    db.reference(f"/Chat with GPT/").update({current_user.id: ""})
    return redirect("/chatgpt")


# Уведомления


@app.route("/notifications", methods=["GET", "POST"])
@login_required
def notifications():
    if db.reference(f"Notifications/{current_user.id}").get():
        notifications = db_fire.get_data(f"Notifications/{current_user.id}")
    else:
        notifications = {0: "У тебя нет уведомлений"}
        db_fire.add_data(f"Notifications/{current_user.id}", notifications)
    if len(notifications) > 1:
        return render_template(
            "notifications.html",
            title="Уведомления",
            notifications=notifications,
            unread_nots=True,
            url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
        )
    else:
        return render_template(
            "notifications.html",
            title="Уведомления",
            notifications=notifications,
            unread_nots=False,
            url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
        )


# Вход


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = (
            db_sess.query(User).filter(User.email == form.email.data).first()
        )
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            "login.html", message="Неправильный логин или пароль", form=form
        )
    return render_template("login.html", title="Авторизация", form=form)


# Выход


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# Регистрация


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        if len(form.password.data) < 8:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="len(password) < 8",
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        photo = requests.get(f"{url}/generate-profile-photo")
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        if photo.status_code == 200:
            img = Image.open(BytesIO(photo.content))
            # Конвертируем изображение в байты
            byte_io = BytesIO()
            img.save(
                byte_io, format="PNG"
            )  # Используем формат JPEG или другой по необходимости
            image_bytes = byte_io.getvalue()
            # Уникальное имя файла: Avs/{user_id}.jpg
            file_name = f"Avs/{user.id}.png"
            # Загрузка изображения в Firebase Storage
            temporary_url = db_fire.upload_image_to_firebase(
                image_bytes, file_name
            )
            db_fire.add_data(f"user-ava/", {user.id: temporary_url})
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


# Друзья


@app.route("/friends", methods=["GET", "POST"])
@login_required
def friends():
    form = FriendsForm()
    db_sess = db_session.create_session()
    users = []
    if db.reference(f"/Friends/{current_user.id}").get():
        for i in db.reference(f"/Friends/{current_user.id}").get().split(", "):
            users.append(db_sess.query(User).get(i))
    if db.reference(f"/Friends/{current_user.id}").get():
        friends_ids = [
            int(i)
            for i in db.reference(f"/Friends/{current_user.id}")
            .get()
            .split(", ")
        ]
    else:
        friends_ids = []
    if form.validate_on_submit():
        users = db_sess.query(User).filter(
            User.name == form.name_of_user.data,
            User.id not in friends_ids,
            User.id != current_user.id,
        )
        return render_template(
            "friends.html",
            title="Друзья",
            users=users,
            form=form,
            search=True,
            friends_ids=friends_ids,
            url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
        )
    return render_template(
        "friends.html",
        title="Друзья",
        users=users,
        form=form,
        friends_ids=friends_ids,
        url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
    )


# Добавление в друзья


@app.route("/add-to-friends/<int:id_of_user>")
@login_required
def add_to_friends(id_of_user):
    if db.reference(f"/Friends/{current_user.id}").get():
        friends = db.reference(f"/Friends/{current_user.id}").get().split(", ")
        (
            friends.append(str(id_of_user))
            if str(id_of_user) not in friends
            else None
        )
    else:
        friends = str(id_of_user)
    db.reference(f"/Friends/").update({current_user.id: ", ".join(friends)})
    if db.reference(f"/Friends/{id_of_user}").get():
        friends = db.reference(f"/Friends/{id_of_user}").get().split(", ")
        friends.append(str(current_user.id))
    else:
        friends = str(current_user.id)
    db.reference(f"/Friends/").update({id_of_user: ", ".join(friends)})
    return redirect("/friends")


# Удаление из друзей


@app.route("/delete-from-friends/<int:id_of_user>")
@login_required
def delete_from_friends(id_of_user):
    if db.reference(f"/Friends/{current_user.id}").get():
        friends = db.reference(f"/Friends/{current_user.id}").get().split(", ")
        friends.remove(str(id_of_user))
    else:
        friends = ""
    db.reference(f"/Friends/").update(
        {current_user.id: ", ".join(friends) if friends else friends}
    )
    if db.reference(f"/Friends/{id_of_user}").get():
        friends = db.reference(f"/Friends/{id_of_user}").get().split(", ")
        friends.remove(str(current_user.id))
    else:
        friends = str(current_user.id)
    db.reference(f"/Friends/").update(
        {id_of_user: ", ".join(friends) if friends else friends}
    )
    return redirect("/friends")


# Профиль


@app.route("/profile")
@login_required
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=current_user.id).first()
    url_to_users_photo = db_fire.get_data(f"user-ava/{current_user.id}")
    return render_template(
        "profile.html",
        title="Профиль",
        user=user,
        current_us=True,
        url_to_photo=url_to_users_photo,
        url_to_users_photo=url_to_users_photo,
    )


# Профиль определенного человека


@app.route("/profile/<int:id_of_user>")
@login_required
def profie_of_user(id_of_user):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=id_of_user).first()
    url_to_users_photo = db_fire.get_data(f"user-ava/{id_of_user}")
    if str(id_of_user) == str(current_user.id):
        current_us = True
    else:
        current_us = False
    return render_template(
        "profile.html",
        title="Профиль",
        user=user,
        current_us=current_us,
        url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
        url_to_users_photo=url_to_users_photo,
    )


# Имзенение имени


@app.route("/change-name", methods=["POST", "GET"])
@login_required
def change_name():
    form = ChangeName()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        user = db_sess.query(User).filter_by(id=current_user.id).first()
        user.name = form.name.data
        db_sess.commit()
        return redirect("/profile")
    return render_template(
        "change-name.html",
        title="Изменить имя",
        form=form,
        url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
    )


# Имзенение почты


@app.route("/change-email", methods=["POST", "GET"])
@login_required
def change_email():
    form = ChangeEmail()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "change-email.html",
                title="Изменить почту",
                form=form,
                message="Эта почта уже используется",
            )
        user = db_sess.query(User).filter_by(id=current_user.id).first()
        user.email = form.email.data
        db_sess.commit()
        return redirect("/profile")
    return render_template(
        "change-email.html",
        title="Изменить почту",
        form=form,
        url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
    )


# Изменение фото


@app.route("/change-photo", methods=["POST", "GET"])
@login_required
def change_photo():
    return render_template(
        "change-photo.html",
        url_to_photo=db_fire.get_data(f"user-ava/{current_user.id}"),
    )


# Рандомная ава


@app.route("/generate-profile-photo", methods=["GET"])
def random_ava():
    ava = generate_image()
    return send_file(ava, mimetype="image/png")


# Проверка валидности файла


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def main():
    db_session.global_init("users.db")
    app.run(debug=True, port="8080")


if __name__ == "__main__":
    main()
