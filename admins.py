from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+$')

mysql = connectToMySQL('admins_flask')

app = Flask(__name__)
app.secret_key = "Secretadmins"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods = ['POST'])
def register():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    password_con = request.form['password_con']
    
    if len(firstname) < 2:
        flash(u"The first name should be two or more characters long.", 'firstname')
    elif not name_regex.match(firstname):
        flash(u"The first name should not contain any numbers"
        " or any special characters.", 'firstname')
    
    if len(lastname) < 2:
        flash(u"The last name should be two or more characters long.", 'lastname')
    elif not name_regex.match(lastname):
        flash(u"The last name should not contain any numbers"
        " or any special characters.", 'lastname')
    
    query = "SELECT EXISTS (SELECT * FROM users WHERE email = %(email)s) AS email"
    data = {
        'email': email
    }
    emailisthere = mysql.query_db(query, data)
        
    if len(email) < 1:
        flash(u"Email cannot be blank.", 'email')
    elif not EMAIL_REGEX.match(email):
        flash(u"Invalid Email Address.", 'email')
    elif emailisthere[0]['email'] != 0:
        flash("The email already exists in the system. Please type another one.")
    
    if len(password) < 1:
        flash(u"Please enter your password.", 'password')
    elif len(password) < 8:
        flash(u"Password should be more than 8 characters long.", 'password')
    elif re.search('[0-9]', password) is None:
        flash(u"Make sure that your password has a number in it", 'password')
    elif re.search('[A-Z]', password) is None: 
        flash(u"Make sure that your password has a capital letter in it", 'password')

    if len(password_con) < 1:
        flash(u"Please verify your password.", 'password_con')
    elif password != password_con:
        flash(u"Password does not match.", 'password_con')
    
    if '_flashes' in session.keys():
        return redirect("/")
    else:
        query_user_level = "select user_level from users;"
        levels = mysql.query_db(query_user_level)
        adminexists = False

        for level in levels:
            u_level = level ['user_level']
            if u_level > 1:
                adminexists = True

        if (adminexists is False):
            user_level = 9
            query = "INSERT INTO users (firstname, lastname, email, password, user_level) VALUES (%(firstname)s, %(lastname)s, %(email)s, %(password)s, %(user_level)s);"
            data = {
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'password': password,
                'user_level': user_level
            }
            mysql.query_db(query, data)

            session['firstname'] = firstname
            session['lastname'] = lastname
            session['user_level'] = user_level

            return redirect("/admin")
        else: 
            user_level = 1
            query = "INSERT INTO users (firstname, lastname, email, password, user_level) VALUES (%(firstname)s, %(lastname)s, %(email)s, %(password)s, %(user_level)s);"
            data = {
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'password': password,
                'user_level': user_level
            }
            mysql.query_db(query, data)

            session['firstname'] = firstname
            session['lastname'] = lastname
            session['user_level'] = user_level

            return redirect("/user")

@app.route('/login', methods = ['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    query = "SELECT * FROM users;"
    entries = mysql.query_db(query)

    emailexists = False

    for entry in entries:
        if entry['email'] == email:
            emailexists = True
            if entry['password'] == password:
                if entry['user_level'] > 1:
                    session['firstname'] = entry['firstname']
                    session['lastname'] = entry['lastname']
                    session['user_level'] = entry['user_level']
                    return redirect('/admin')
                else:
                    session['firstname'] = entry['firstname']
                    session['lastname'] = entry['lastname']
                    session['user_level'] = entry['user_level']
                    return redirect('/user')
            else:
                flash(u"Incorrect password. Please try again.", 'password')
            break
    if emailexists is False:
        flash("The email does not exist in the system. Please type another one.", 'email')

    if '_flashes' in session.keys():
        return redirect("/")

@app.route('/user')
def user():
    if session['firstname'] is None:
        return redirect("/")
    else:
        return render_template('user.html')

@app.route('/admin')
def admin():
    if session['user_level'] == 1:
        return redirect("/nope")
    query = f"SELECT * FROM users;"
    users = mysql.query_db(query)

    return render_template('admin.html', users = users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/clear')
def delete_all():
    query = "TRUNCATE TABLE users;"
    mysql.query_db(query)
    return redirect("/")

@app.route('/admin/<id>/delete')
def deleteuser(id):
    if session['user_level'] == 1:
        return redirect("/nope")
    else:
        query = f"delete from users where id = {id}"
        mysql.query_db(query)
        return redirect("/admin")

@app.route('/admin/<id>/removeadmin')
def removeadmin(id):
    if session['user_level'] == 1:
        return redirect("/nope")
    else:
        query = f"update users set user_level = 1 where id = {id}"
        mysql.query_db(query)
        return redirect("/admin")

@app.route('/admin/<id>/makeadmin')
def makeadmin(id):
    if session['user_level'] == 1:
        return redirect("/nope")
    else:
        query = f"update users set user_level = 2 where id = {id}"
        mysql.query_db(query)
        return redirect("/admin")

@app.route('/nope')
def nope():
    session.clear()
    return render_template('nope.html')

if __name__=="__main__":
    app.run(debug = True) 