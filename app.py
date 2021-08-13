from decouple import config
from flask import Flask, redirect, render_template, url_for, request

app = Flask(__name__)

app.config['SECRET_KEY'] = config('SECRET_KEY')


@app.route('/')
def home():
    return render_template('register.html')