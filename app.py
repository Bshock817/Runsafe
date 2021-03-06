from flask import Flask, redirect, render_template, session, request, flash, url_for
from mysqlconn import connectToMySQL
from flask_bcrypt import Bcrypt
import requests
from flask_sqlalchemy import SQLAlchemy		
from flask_migrate import Migrate	
import re   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weathers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

app.secret_key = 'runsafety'

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    r = requests.get(url).json()
    return r

@app.route("/")
def home_landing():
    return render_template("register.html")

@app.route("/on_register", methods=["POST"])
def on_register():
    is_valid = True
    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("Email is not valid")
    if len(request.form['fname']) < 1:
        is_valid = False
        flash("first name needs more than 1 character.")
    if len(request.form['lname']) < 1:
        is_valid = False
        flash("last name needs more than 1 character.")
    if request.form['pw'] != request.form['cpw']:
        is_valid = False
        flash("Passwords Must Match!")
    
    if is_valid:
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES(%(fn)s, %(ln)s, %(em)s, %(pw)s,NOW(),NOW());"
        data = {
            'fn':request.form['fname'],
            'ln':request.form['lname'],
            'em':request.form['em'],
            'pw':bcrypt.generate_password_hash(request.form['pw']),
        }
        mysql = connectToMySQL('runsafe')
        user_id = mysql.query_db(query, data)
        flash("User Added!")
        if user_id:
            session['user_id'] = user_id
            return redirect ("/main")
    return redirect("/")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/on_login", methods=['POST'])
def on_login():
    is_valid = True
    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("Email is not valid")
    if is_valid :
        query = "SELECT users.id_user, users.password FROM users WHERE users.email = %(em)s"
        data = {
            'em': request.form['em'],
        }
        mysql = connectToMySQL("runsafe")
        result = mysql.query_db(query, data)
        if result:
            if not bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
                flash("Incorrect password")
                return redirect("/login")
            else:
                print(result)
                session['user_id'] = result[0]['id_user']
                return redirect ("/main")
        else:
            flash("Email not in database")


    return redirect("/login")

@app.route("/return")
def ret_home():
    return redirect("/main")

@app.route("/main")
def main_page():
    if 'user_id' not in session:
        return redirect("/")

    query = "SELECT * FROM users where id_user = %(uid)s"
    data = {
        'uid': session['user_id']
    }
    mysql = connectToMySQL('runsafe')
    results = mysql.query_db(query,data)
    return render_template ("main.html", user_data = results[0])

@app.route('/weather')
def get_weather():

    cities = City.query.all()

    weather_data = []

    for city in cities:

        r = r = get_weather_data(city.name)
        print(r)

        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }

        weather_data.append(weather)


    return render_template('weather.html', weather_data=weather_data)

@app.route('/weather', methods=['POST'])
def weather_post():
    err_msg = ''
    new_city = request.form.get('city')
        
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exist in the world!'
        else:
            err_msg = 'City already exists in the database!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added succesfully!')

    return redirect(url_for('get_weather'))

@app.route('/deleted/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted { city.name }', 'success')
    return redirect(url_for('get_weather'))

@app.route("/host")
def host_page():
    query = "SELECT * FROM users where id_user = %(uid)s"
    data = {
        'uid': session['user_id']
    }
    mysql = connectToMySQL('runsafe')
    results = mysql.query_db(query,data)
    return render_template("host.html", user_data = results[0])

@app.route("/on_host", methods=['POST'])
def host_event():
    is_valid = True
    event_details = request.form['event_details']

    if len(event_details) < 10:
        is_valid = False
        flash("Must be at least 10 charaters long")

    if is_valid:
        query = "INSERT INTO events(host,content,created_at,updated_at) VALUES(%(user_fk)s, %(event)s, NOW(), NOW());"
        data = {
            'user_fk':session['user_id'],
            'event': request.form['event_details'],
        }
        mysql = connectToMySQL('runsafe')
        mysql.query_db(query, data)
        flash("You Created an Event!")
        return redirect("/join")
    else:
        return redirect ("/host")

@app.route("/join")
def join_home():
    query = "SELECT users.first_name, users.last_name FROM users where id_user = %(uid)s"
    data = {
        'uid': session['user_id'],
    }
    mysql = connectToMySQL("runsafe")
    results = mysql.query_db(query, data)
    if results:
        query = "SELECT events.id_event, events.host, events.content, users.first_name, users.last_name FROM users JOIN events ON users.id_user = events.host"
        mysql = connectToMySQL("runsafe")
        events = mysql.query_db(query)
        return render_template("join.html", user_data = results[0], events=events)

@app.route("/delete/<event_id>")
def on_delete(event_id):
    query = "DELETE FROM events WHERE events.id_event = %(event_id)s"
    data ={'event_id': event_id}
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query, data)
    return redirect("/join")

@app.route("/edit/<event_id>")
def edit_event(event_id):
    query = "SELECT events.id_event, events.content FROM events WHERE events.id_event = %(event_id)s"
    data = {"event_id": event_id}
    mysql = connectToMySQL("runsafe")
    event = mysql.query_db(query, data)
    if event:
        return render_template("edit.html", event_data = event[0])
    return redirect("/join")

@app.route("/on_edit/<event_id>", methods=['POST'])
def on_edit(event_id):
    query = "UPDATE events SET events.content = %(event)s WHERE events.id_event = %(event_id)s"
    data = {
        'event':request.form['event_edit'],
        'event_id': event_id
        }
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query, data)

    return redirect("/join")

@app.route("/joined/<event_id>")
def joined_event(event_id):
    query = "INSERT INTO joined_events (user_id, event_id) VALUES ( %(u_id)s, %(e_id)s)"
    data = {
        "u_id":session['user_id'] ,
        "e_id":event_id ,
    }
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query, data)
    flash("joined the group")
    return redirect("/join")

@app.route("/unjoin/<event_id>")
def unjoined_event(event_id):
    query = "DELETE FROM joined_events WHERE user_id = %(u_id)s AND event_id = %(e_id)s"
    data = {
        "u_id":session['user_id'],
        "e_id":event_id}
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query, data)
    flash("left the group")
    return redirect("/join")

@app.route("/details/<event_id>")
def details_page(event_id):
    query = " SELECT users.first_name, users.last_name, events.content,events.created_at FROM users join events on users.id_user = events.host WHERE events.id_event = %(eid)s"
    data = {
        "eid": event_id
    }
    mysql = connectToMySQL("runsafe")
    event_data = mysql.query_db(query, data)
    if event_data:
        event_data=event_data[0]
    query = "SELECT users.first_name, users.last_name FROM joined_events JOIN users ON users.id_user = joined_events.user_id WHERE joined_events.event_id = %(eid)s"
    data = {
        "eid": event_id
    }
    mysql = connectToMySQL("runsafe")
    runner_data = mysql.query_db(query, data)
    query = "SELECT users.first_name, users.last_name, messages.content FROM joined_events JOIN users ON users.id_user = joined_events.user_id join messages on joined_event_id = %(eid)s"
    data = {
        "eid": event_id
    }
    mysql = connectToMySQL("runsafe")
    messages = mysql.query_db(query,data)

    return render_template("details.html", event_data =event_data, runner_data=runner_data, messages=messages)

@app.route("/chat", methods=['POST'])
def on_chat():
    is_valid = True
    chat_content = request.form['chat_content']
    if len(chat_content) < 1:
        is_valid = False
        flash("Must be at least 1 charater long")

    if len(chat_content) > 255:
        is_valid = False
        flash("Must be less than 255 charaters")
    
    if is_valid:
        query = "INSERT INTO messages (joined_event_id, joined_user_id,content,created_at, updated_at) VALUES(%(juser_fk)s, %(chat)s, NOW(), NOW());"

        data = {
            'juser_fk':session['user_id'],
            'chat': request.form['chat_content'],
        }
        mysql = connectToMySQL('runsafe')
        mysql.query_db(query, data)

@app.route("/friend")
def friend():
    query = "SELECT users.id_user, users.first_name, users.last_name FROM users"
    mysql = connectToMySQL("runsafe")
    all_users = mysql.query_db(query)

    query = "SELECT * FROM friends WHERE friender = %(uid)s"
    data = {
        "uid": session['user_id']
    }
    mysql = connectToMySQL("runsafe")
    all_user_id_friended = [info['friended'] for info in mysql.query_db(query, data)]

    friended = []
    not_friended = []

    for user in all_users:
        if user['id_user'] == session['user_id']:
            continue

        if user['id_user'] in all_user_id_friended:
            friended.append(user)
        else:
            not_friended.append(user)
    return render_template("friends.html",friended=friended,not_friended=not_friended )

@app.route("/on_friend/<user_id>")
def on_friend(user_id):
    query = "INSERT INTO friends (friender, friended) VALUES(%(friender)s, %(friended)s)"
    data ={
        'friended':user_id, 'friender':session['user_id']
    }
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query,data)
    return redirect("/friend")

@app.route("/un_friend/<user_id>")
def un_friend(user_id):
    query = "DELETE FROM friends WHERE friender = %(friender)s AND friended = %(friended)s"
    data ={
        'friended':user_id, 'friender':session['user_id']
    }
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query,data)
    return redirect("/friend")

@app.route("/rate")
def rate():
    query = "SELECT users.id_user, users.first_name, users.last_name FROM users"
    mysql = connectToMySQL("runsafe")
    all_users = mysql.query_db(query)

    query = "SELECT * FROM rates WHERE rater = %(uid)s"
    data = {
        "uid": session['user_id']
    }
    mysql = connectToMySQL("runsafe")
    all_user_id_rated = [info['rated'] for info in mysql.query_db(query, data)]

    hasnt_rated = []
    good_rating = []
    bad_rating = []

    for user in all_users:
        if user['id_user'] == session['user_id']:
            hasnt_rated.append(user)
        elif user['id_user'] in all_user_id_rated:
            good_rating.append(user)
        else:
            bad_rating.append(user)
    return render_template("rate.html",hasnt_rated=hasnt_rated, good_rating=good_rating,bad_rating=bad_rating)

@app.route("/on_rate/<user_id>")
def on_rate(user_id):
    query = "INSERT INTO rates (rater, rated) VALUES(%(rater)s, %(rated)s)"
    data ={
        'rated':user_id, 'rater':session['user_id']
    }
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query,data)
    return redirect("/rate")

@app.route("/un_rate/<user_id>")
def un_rate(user_id):
    query = "DELETE FROM rates WHERE rater = %(rater)s AND rated = %(rated)s"
    data ={
        'rated':user_id, 'rater':session['user_id']
    }
    mysql = connectToMySQL("runsafe")
    mysql.query_db(query,data)
    return redirect("/rate")

@app.route("/logout")
def on_logout():
    session.clear()
    return redirect("/")

# working 

if __name__ == "__main__":
    app.run(debug=True)