from flask import Flask, g, request, redirect, render_template, session, url_for
#import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)

#session and database details
app.secret_key = 'qwertyuiop123'

#probably not needed anymore if I changed SQLite into PostGreSQL Render.com database (today 20250328)
#db_location = 'var/QuizAppDatabase.db'
#I take it form dotenv library  <---   DATABASE_URL = "postgresql://quizapp_database_20250326_user:LG8hXL1GFY3xv4k9Dc87L6rxiB5YRtRO@dpg-cvi3685ds78s73ej15i0-a.oregon-postgres.render.com/quizapp_database_20250326"

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

#python root
@app.route("/")
def intro():
        return render_template('index.html')

@app.route("/about")
def about():
        return render_template('about.html')

@app.route("/contact")
def contact():
        return render_template('contact.html')

#connection to database <- OLD VERSION !!!!!! (today 20250328)
#def get_db():
    #db = getattr(g, 'db', None)
    #if db is None:
        #db = sqlite3.connect(db_location)
        #g.db = db
    #return db

#connection to database
#db_url = os.getenv("DATABASE_URL") <--alternative code to os.environ.get
def get_db():
    try:
        #db_url = os.environ.get("DATABASE_URL")
        #if not db_url:
            #raise ValueError("not set or empty")
    
        #db = psycopg2.connect(db_url)
        db = psycopg2.connect(DATABASE_URL)
        
        return db
    except Exception as e:
        print(f"Error connecting to db: {e}")
        return None

#database closure <- OLD VERSION !!!!!! (today 20250328)
#@app.teardown_appcontext
#def close_db_connection(exception):
#    db = getattr(g, 'db', None)
#    if db is not None:
#        db.close()

#login route
@app.route("/login", methods=['GET', 'POST'])
def login():

    usernameFromDB=""
    passwordFromDB=""

    if request.method == 'GET':
        return render_template('login.html')
    else:

        db = get_db()
        #db.commit()
        cursor=db.cursor()

        user = request.form['username']
        pw = request.form['password']

        #default:
        #sql = "SELECT * FROM Users WHERE Username = ? AND Password = ?"
        #cursor.execute(sql, (user,pw))
        #altered:
        #sql = 'SELECT * FROM Users WHERE Username = '+user+' AND Password = '+pw+''
        #cursor.execute(sql)
        #sql = "SELECT * FROM Users WHERE username = %s AND password = %s"
        #cursor.execute(sql, (user,pw))
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (user,pw))

        rows = cursor.fetchall()
        for row in rows:
            usernameFromDB = row[1]
            passwordFromDB = row[2]

        if (user == "")or(pw == ""):
            #session['emptyInput']
            return render_template('login.html', message='Sorry No Input, Type Again: ')
        elif (usernameFromDB == user)or(passwordFromDB == pw):
            session['logged']=True
            #previously in route /quiz which was redirected elsewhere so the sessions did not exist
            # ... which caused an error KeyError "negative" or "score"
            session['score']=0
            session['negative']=0
            session['q1']=0
            session['q2']=0
            session['q3']=0
            return render_template('quiz.html', message='Correct You are logged in! ')
            #later redirect to quiz
            
        else:
            return render_template('login.html', message='Sorry wrong credentials')


#redirect register to login 
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        db = get_db()
        cursor=db.cursor()

        userReg = request.form['usernameReg']
        pw1 = request.form['passwordReg']
        pw2 = request.form['passwordReg2']


        if(userReg=="")or(pw1=="")or(pw2==""):
            return render_template('register.html', messageReg='You have left empty fields')

        if(pw1==pw2):
            #db.cursor().execute('INSERT INTO Users (Username, Password) VALUES (?, ?)',(userReg,pw2))
            #db.cursor().execute('INSERT INTO users (Username, Password) VALUES (?, ?)',(userReg,pw2))
            #db.cursor().execute('INSERT INTO users (username, password) VALUES ('+userReg+', '+pw2+')')
            db.cursor().execute('INSERT INTO users (username, password) VALUES (%s, %s)',(userReg, pw2))
            db.commit()
            #no need for session? 
            return render_template('login.html', message='New account has been registerd')
        else:
            return render_template('register.html', messageReg='passwords do not match')

        
#-------------------Second Part: The QuizApp--------------------------------


#all the subsequent routes to handle each quiz URL 
@app.route("/quiz")
def hello():
    #session.clear()
    session['score']=0
    session['negative']=0
    session['q1']=0
    session['q2']=0
    session['q3']=0
    print(session['negative'])
    #return render_template('quiz.html')

@app.route("/q1/")
def q1():
    return render_template('q1.html')

@app.route("/q1w/")
def q1w():
    session['negative']+=1
    session['q1']=0
    return render_template('q1w.html')

@app.route("/q1a/")
def q1a():
    session['score'] += 1
    session['q1']=1
    return render_template('q1a.html')

@app.route("/q2/")
def q2():
    return render_template('q2.html')

@app.route("/q2w/")
def q2w():
    session['negative']+=1
    session['q2']=0
    return render_template('q2w.html')

@app.route("/q2a/")
def q2a():
    session['score'] += 1
    session['q2']=1
    return render_template('q2a.html')

@app.route("/q3/")
def q3():
    return render_template('q3.html')

@app.route("/q3w/")
def q3w():
    session['negative']+=1
    session['q3']=0
    return render_template('q3w.html')

@app.route("/q3a/")
def q3a():
    session['score'] +=1
    session['q3']=1
    return render_template('q3a.html')

#passing the session variables to qsuccess.html canvas
@app.route("/qsuccess/")
def qsuccess():
    return render_template('qsuccess.html', score=session['score'], negative=session['negative'],q1=session['q1'],q2=session['q2'],q3=session['q3'])

#-------------------Second Part: The QuizApp--------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)