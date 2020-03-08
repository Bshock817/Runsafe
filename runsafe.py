from flask import Flask, redirect, render_template, session, request, flash
from mysqlconn import connectToMySQL
from flask_bcrypt import Bcrypt
import re   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'runsafety'

bcrypt = Bcrypt(app)

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

@app.route("/main")
def main_page():
    query = "SELECT * FROM users where id_user = %(uid)s"
    data = {
        'uid': session['user_id']
    }
    mysql = connectToMySQL('runsafe')
    results = mysql.query_db(query,data)
    return render_template ("main.html", user_data = results[0])

@app.route("/logout")
def on_logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)