from flask import Flask, request, render_template, redirect,url_for,session,flash
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
app=Flask(__name__)
app.secret_key="rjdk8741tao"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Deva'
app.config['MYSQL_PASSWORD'] = 'rjdk8741tao'
app.config['MYSQL_DB'] = 'flasktask'
mysql = MySQL(app)

def isloggedin():
    return "username" in session
@app.route('/')
def home():
    return render_template("form.html")

class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class SignUp(FlaskForm):
    username = StringField("username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("password", validators=[InputRequired(), Length(min=4, max=15)])
    submit = SubmitField("Signup")

class LoginForm(FlaskForm):
    username = StringField("username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("password", validators=[InputRequired(), Length(min=4, max=15)])
    submit = SubmitField("Signup")

class AddStudent(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=2, max=50)])
    age = StringField("Age", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Length(max=50)])
    submit = SubmitField("Add Student")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignUp()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT name FROM signup WHERE name=%s", (username,))
        old_user = cur.fetchone()
        if old_user:
            cur.close()
            flash("Username already taken, Please try a different one.", "danger")
            return render_template("signup.html", form=form)
        cur.execute("INSERT INTO signup(name, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        flash("Signup Successful", "success")
        return redirect(url_for("signin"))
    return render_template("signup.html", form=form)

@app.route("/signin/", methods=["GET", "POST"])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT name, password FROM signup WHERE name=%s", (username,))
        userdata = cur.fetchone()
        cur.close()
        if userdata and userdata[1] == password:
            session["username"] = username
            flash("Login Successful", "success")
            return redirect(url_for("display"))
        else:
            flash("Invalid Credentials", "danger")
    return render_template("signin.html", form=form)
@app.route('/display/', methods=["GET", "POST"])
def display():
    form = AddStudent()
    if form.validate_on_submit():
        name = form.name.data
        age = form.age.data
        email = form.email.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students(name, email, age) VALUES (%s, %s, %s)", (name, email, age))
        mysql.connection.commit()
        cur.close()

        flash('Student added successfully', 'success')
        return redirect(url_for('display'))

    if isloggedin():
        username = session["username"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE name = %s", (username,))
        data = cur.fetchall()
        cur.close()
        return render_template("display.html", display=data, form=form)

    return redirect(url_for('signin'))

@app.route('/edit/<string:name>', methods=['GET', 'POST'])
def edit(name):
    if request.method == "POST":
        new_name = request.form.get("name")
        new_age = request.form.get("age")
        new_email = request.form.get("email")
        print(new_age,new_name,new_email)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET  age = %s, email = %s WHERE name = %s", (new_age, new_email, name))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('display'))
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE name = %s", (name,))
        data = cur.fetchone()
        cur.close()
        return render_template('edit.html', data=data)

@app.route('/delete/<string:name>', methods=['POST'])
def delete(name):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE name = %s", (name,))
    mysql.connection.commit()
    cur.close()
    flash('Record deleted successfully', 'success')
    return redirect(url_for('display'))

@app.route("/logout")
def logout():
    session.pop("user_id",None)
    flash("Logged Out","success")
    return redirect(url_for("home"))

if __name__=="__main__":
    app.run(debug=True)