from flask import Flask, redirect, render_template, request, url_for, flash, session
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'NNEYtaR'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonflask'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form :
        email = request.form['email']
        password = request.form['password']
        print(password)
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM login WHERE email = %s",(email,))
        account = cur.fetchone()
        
        if account :
            hpassword = account['password']
            print(hpassword)
            if check_password_hash(hpassword, password) :
                session['Loggedin'] = True
                session["email"] = request.form.get("email")
                return redirect(url_for('Index'))
            else :
                flash("Incorrect password")
        else :
            flash("Incorrect email")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session["email"] = None
    return redirect(url_for('Index'))


@app.route('/regis', methods = ['POST'])
def regis():
    if request.method == "POST" and 'name' in request.form and 'email' in request.form and 'password' in request.form and 'cpassword' in request.form :
        name = request.form['name']
        email= request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        
        hpassword = generate_password_hash(password)
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM login WHERE email = %s',(email,))
        account = cur.fetchone()
        
        if account :
            flash("Email already exists !")
        elif not re.match(r'[A-Za-z0-9]+', name):
            flash('Username must contain only characters and numbers!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif password != cpassword :
            flash("Passwords do not match !")
        else :
            cur.execute("INSERT INTO login (name, email, password) VALUES (%s, %s, %s);", (name, email,hpassword))
            mysql.connection.commit()
    return redirect(url_for('login'))


@app.route('/', methods = ['POST','GET'])
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student")
    data = cur.fetchall()
    cur.close()
    
    if not session.get('email') :
        return redirect(url_for('login'))
    return render_template('index.html', student=data)


@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
        mysql.connection.commit()
        return redirect(url_for('Index'))
    
    
@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM student WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index'))


@app.route('/update',methods = ['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE student SET name=%s, email=%s, phone=%s WHERE id=%s", (name, email, phone, id_data))
        flash("Data Update Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))
    

if __name__ == '__main__':
    app.run(debug=True)