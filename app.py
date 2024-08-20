import functools
import yaml
import os
from flask import Flask, render_template, flash, session, request, redirect, url_for, g
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_fontawesome import FontAwesome
from YeniTestSonucu import oku as ogrenci_path
from cevap import cevapoku as cevap_path
from sonuc import degerlendir

app = Flask(__name__, static_folder='static')
bootstrap = Bootstrap(app)
fa = FontAwesome(app)

with open('db.yaml', 'r') as file:
    db = yaml.load(file, Loader=yaml.FullLoader)

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = db['DictCursor']

mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24)


def get_db():
    if 'db' not in g:
        g.db = mysql.connection.cursor()
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('login'):
            flash("You need to log in to access this page", "warning")
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users(firstname, lastname, username, email, password) VALUES(%s, %s, %s, %s, %s)",
                        (firstname, lastname, username, email, generate_password_hash(password)))
            mysql.connection.commit()
            cur.close()
            flash('Kayıt başarılı! Lütfen giriş yapın', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            cur.close()
            flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'danger')
            print("Kayıt sırasında bir hata oluştu:", str(e))
            return render_template('register.html')
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        userForm = request.form
        username = userForm['username']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password'], userForm['password']):
            session.clear()
            session['login'] = True
            session['firstname'] = user['firstname']
            session['lastname'] = user['lastname']
            return redirect(url_for('panel'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre.', 'danger')
            return render_template('login.html')
    elif request.method == 'GET' and 'login' in session and session['login'] == True:
        print("giriş oldu")
        return redirect(url_for('panel'))

    return render_template('login.html')


@app.route('/panel/', methods=['GET'])
def panel():
    if 'login' in session and session['login'] == True:
        return redirect(url_for('omr'))
    else:
        return redirect(url_for('login'))


@app.route('/omr', methods=['GET'])
def omr():
    if 'login' in session and session['login'] == True:
        return render_template('omr.html')
    else:
        return redirect(url_for('login'))


@app.route('/analyze/', methods=['POST'])
def analyze():
    try:
        ogr_cevap = request.files['image']
        cevap_anahtari = request.files['cevap_anahtari']
        

        # Save the image file to a temporary location
        filename = ogr_cevap.filename
        ogr_path = os.path.join(app.root_path, 'static', filename)
        ogr_cevap.save(ogr_path)

        filename = cevap_anahtari.filename
        cvp_path = os.path.join(app.root_path, 'static', filename)
        cevap_anahtari.save(cvp_path)

        # Read the answer key and student's answers
        cevaplar = cevap_path(cvp_path)
        yanitlar = ogrenci_path(ogr_path)

        # Perform evaluation
        dogrular, yanlislar,ogr_no, kurum_no, sinav_no = degerlendir(ogr_path, cvp_path)

        # Remove the temporary image file
        os.remove(cvp_path)
        os.remove(ogr_path)

        # Save the evaluation results to the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student_note (studentNo, dogrular, yanlislar, kurumNo, sinavNo) VALUES (%s, %s, %s,%s, %s)",
                   (ogr_no, dogrular, yanlislar, kurum_no, sinav_no))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("get_list"))
    except Exception as e:
        return 'Bir hata oluştu: ' + str(e)


@app.route('/list/', methods=['GET'])
def get_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student_note")
    student_notes = cur.fetchall()
    print("not: ", student_notes)
    cur.close()

    if len(student_notes) > 0:
        show_button = True
    else:
        show_button = False
    return render_template('list.html', note_list=student_notes,  show_button=show_button)


@app.route('/delete-note/', methods=['POST'])
def deleteNote():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM student_note")
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("get_list"))


@app.route('/logout/', methods=['POST'])
def logout():
    session['login'] = False
    session['firstname'] = None
    session['lastname'] = None

    flash('Başarılı bir şekilde çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
