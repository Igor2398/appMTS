from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from threading import Lock
import mysql.connector
import os 
from dotenv import load_dotenv

load_dotenv()                                                                                                                                                              

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
cnx = mysql.connector.connect(user=os.getenv('USER_NAME'), password=os.getenv('PASSWORD'),
                        host=os.getenv('HOST'),
                        database=os.getenv('DATABASE'))


@app.route('/')
def index():
    if ('loggedin' not in session):
        return redirect(url_for('userLogin'))
    
    cursor = cnx.cursor()
    sql = "SELECT * FROM `data` WHERE `test_name` = (SELECT `test_name` FROM `data` ORDER BY `id` DESC LIMIT 1);"
    cursor.execute(sql)
    data = cursor.fetchall()
    count = cursor.rowcount
    cursor.close()
    
    if (count > 0):
        return render_template('sock.html', data=data, async_mode=socketio.async_mode)
    else:
        return render_template('sock.html', async_mode=socketio.async_mode)



@app.route('/sock')
def sock():
    if ('loggedin' not in session):
        return redirect(url_for('userLogin'))

    cursor = cnx.cursor()
    sql = "SELECT * FROM `data` WHERE `test_name` = (SELECT `test_name` FROM `data` ORDER BY `id` DESC LIMIT 1);"
    cursor.execute(sql)
    data = cursor.fetchall()
    count = cursor.rowcount
    cursor.close()
    
    if (count > 0):
        return render_template('index.html', data=data, async_mode=socketio.async_mode)
    else:
        return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/setalert')
def setAlert():
    return render_template('setalert.html')


@app.route('/socket.io', methods=["POST"])
def getData():
    res = request.get_json()
    cursor = cnx.cursor(prepared=True)
    sql = "INSERT INTO `data` (`id`, `test_name`, `a_count`, `a_force`, `a_displacement`) VALUES (NULL, %s, %s, %s, %s)"
    data = (res['test_name'], res['count'], res['force'], res['displacement'])
    cursor.execute(sql, data)
    cnx.commit()
    cursor.close()
    socketio.emit('getData', res)
    return res


@app.route('/list')
def showTests():
    if ('loggedin' not in session):
        return redirect(url_for('userLogin'))

    cursor = cnx.cursor()
    sql = 'SELECT DISTINCT(test_name) FROM data'
    cursor.execute(sql)
    records = cursor.fetchall()
    cursor.close()
    return render_template('list.html', data=records, async_mode=socketio.async_mode)

@app.route('/show', methods=["POST"])
def showSingleTest():
    if ('loggedin' not in session):
        return redirect(url_for('userLogin'))

    testName = request.form["test_name"]
    cursor = cnx.cursor()
    sql = ("SELECT * FROM `data` WHERE `test_name` = %s")
    data = [testName]
    cursor.execute(sql, data)
    records = cursor.fetchall()
    cursor.close()
    return render_template('show.html', data=records)

@app.route('/del', methods=["POST"])
def delSingleTest():
    if ('loggedin' not in session):
        return redirect(url_for('userLogin'))

    testName = request.form["test_name"]
    cursor = cnx.cursor(prepared=True)
    sql = ("DELETE FROM `data` WHERE `test_name` = '%s'" % testName)
    data = (testName)
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    return redirect(url_for('showTests'))

@app.route('/login', methods=["GET", "POST"])
def userLogin():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = cnx.cursor()
        sql = ("SELECT id, username FROM `users` WHERE `username` = %s AND `password` = %s")
        data = [username, password]
        cursor.execute(sql, data)
        account = cursor.fetchone()
        cursor.close()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for('index'))
        else:
            msg = 'Wrong password! Try again or contact with administrator'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def userLogout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('userLogin'))

if __name__ == '__main__':
    socketio.run(app, host="localhost", ssl_context='adhoc')





