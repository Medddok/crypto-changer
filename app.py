import flask
import os
import sqlite3
import requests  # Библиотека для запросов к API
from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from dotenv import load_dotenv
import random

# Загрузка переменных окружения из .env файла
load_dotenv()
app = Flask(__name__)
app.secret_key = '15'  # Секретный ключ для сессий

crypto_facts = [
    "Биткойн был создан в 2008 году анонимным человеком или группой людей под псевдонимом Сатоши Накамото.",
    "Эфириум был разработан Виталиком Бутериным и был запущен в 2015 году.",
    "Майнинг — это процесс создания новых криптовалютных единиц с помощью вычислительных мощностей.",
    "В 2021 году рынок криптовалют достиг рыночной капитализации более $2 трлн.",
    "Децентрализованные финансы (DeFi) — это новое направление, которое использует криптовалюты для создания финансовых услуг без участия посредников.",
    "Биткойн не имеет центрального эмитента, и его количество ограничено 21 миллионом монет."
]

# Получение API ключа из переменной окружения
API_KEY = os.getenv('API_KEY')


def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, 
            password TEXT
        )
    ''')
    conn.close()

init_sqlite_db()

@app.route('/registraccion', methods=['POST', 'GET'])
def registraccion():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM user WHERE username = ?', (username,))
            user = cur.fetchone()

        if user:
            flash('Username already taken, choose another one')
            return render_template('registraccion.html')

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('INSERT INTO user (username, password) VALUES (?,?)', (username, password))
            con.commit()
            flash('You are successfully registered!')
            return redirect(url_for('main'))

    return render_template('registraccion.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE username = ?", (username,))
            user = cur.fetchone()

        if user and user[2] == password:
            session.clear()
            session['username'] = username
            flash('Login successfully!')
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

# Функция для получения данных из CoinMarketCap API
def get_crypto_data():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',    # Начиная с самой дорогой криптовалюты
        'limit': '30',   # Получаем топ-30 криптовалют
        'convert': 'USD' # Валюта для конвертации
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()

    # Обрабатываем данные для использования в шаблоне
    crypto_data = []
    if 'data' in data:
        for currency in data['data']:
            change_24h = currency['quote']['USD']['percent_change_24h']
            change_class = 'positive' if change_24h > 0 else 'negative'

            crypto_data.append({
                'name': currency['name'],
                'symbol': currency['symbol'],
                'price': currency['quote']['USD']['price'],
                'percent_change_24h': change_24h,
                'market_cap': currency['quote']['USD']['market_cap'],
                'change_class': change_class  # Класс для положительного/отрицательного изменения
            })
    return crypto_data

    
@app.route('/')
@app.route('/main', methods=['POST', 'GET'])
def main():
    crypto_data = get_crypto_data()  # Получаем данные из API
    return render_template('main.html', crypto_data=crypto_data)

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    random_fact = random.choice(crypto_facts)
    return render_template('profile.html', username=username, fact=random_fact)

@app.route('/info', methods=['POST', 'GET'])
def info():
    return render_template('info.html')

@app.route('/forum', methods=['POST', 'GET'])
def forum():
    return render_template('forum.html')

@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html')

@app.route('/new_fact')
def new_fact():
    random_fact = random.choice(crypto_facts)
    return jsonify({'new_fact': random_fact})


@app.route('/update_data', methods=['GET'])
def update_data():
    crypto_data = get_crypto_data()
    return jsonify(crypto_data)

if __name__ == '__main__':  
    app.run(debug=True)
