from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')


@app.route('/chat')
def chat():
  return render_template('chat.html')


@app.route('/chatgpt')
def chatGPT():
  return render_template('chatgpt.html')


@app.route('/login')
def login():
  return render_template('login.html')


@app.route('/reg')
def reg():
  return render_template('reg.html')


if __name__ == '__main__':
  app.run()