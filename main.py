from flask import Flask, redirect, render_template
from data.users import User
from forms.login_form import LoginForm
from forms.reg_form import RegisterForm
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Sdslg35KO236SafA49F21'

def main():
    db_session.global_init("db/blogs.db")
    app.run()

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='SimpleChat')


@app.route('/chat')
def chat():
  return render_template('chat.html', title='Чат с User')


@app.route('/chatgpt')
def chatGPT():
  return render_template('chatgpt.html', title='Чат с ChatGpt')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/index')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
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
  return render_template('friends.html', title='Друзья')


if __name__ == '__main__':
  main()