from flask import *
from datetime import *
import time 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "ThisIsSupposedToBeSecured"
app.permanent_session_lifetime = timedelta(minutes=25)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
db = SQLAlchemy(app)



class users(db.Model):
  _id = db.Column("id", db.Integer, primary_key = True)
  username = db.Column("username", db.String(100))
  password = db.Column("password", db.String(30))
  friends = db.Column("friends", db.PickleType)
  bio = db.Column("bio", db.String(255))
  status = db.Column("status", db.String(30))
  
  def __init__(self, username, password, friends, bio, status):
    self.username = username
    self.password = password
    self.friends = friends
    self.bio = bio
    self.status = status 
class messages(db.Model):
  _id = db.Column("id", db.Integer, primary_key = True)
  name = db.Column(db.String)
  date = db.Column(db.String)
  message = db.Column(db.String)
  def __init__(self, name, date, message):
    self.name = name
    self.date = date
    self.message = message
  

  

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)



@app.route("/")
def index():
  #db.session.query(messages).delete()
  #db.session.commit()
  
  return render_template("index.html")

@app.route("/register", methods = ["POST", "GET"])
def register():
	if request.method == "GET":
	  session["messages"] = []
	  return render_template("register.html", messages = session["messages"])
	
	elif request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		isExist = users.query.filter_by(username = username).first()
		if isExist:
		  flash("Username exists.")
		  return render_template("register.html")
		else:
		  add_user = users(username, password,[], "", "")
		  db.session.add(add_user)
		  db.session.commit()
		  return redirect(url_for("index"))
		  
		  
		  
@app.route("/communicate", methods = ["POST"])
def communicate():
  session["data"] = request.get_json()
  for i in session["data"]:
  	flash(i)
  	
  print(data)
  return "Hello"
  

  
 
@app.route("/login", methods = ["POST", "GET"])
def login():
  if request.method == "GET":
    if "isLogged" in session:
      return redirect(url_for("profile"))
    else:
      return render_template("login.html")
  if request.method == "POST":
    session["username"] = request.form["username"]
    password = request.form["password"]
    login.isExist = users.query.filter_by(username = session["username"], password = password).first()
    if login.isExist:
      session["isLogged"] = True
      return redirect(url_for("profile"))
    else:
      flash("Invalid Username or Password")
      return redirect(redirect_url())



@app.route("/profile")
def profile():
  if "isLogged" in session:
    return render_template("profile.html", username = session["username"], message = messages.query.all())
    
    
  else:
    flash("Not yet logged in.")
    return redirect(url_for("login"))
  
  
@app.route("/add_friend", methods = ["POST"])
def add_friend():
  if request.method == "POST":
    x = users.query.filter_by(username = session["username"]).first()
   
 

@app.route("/post_status", methods = ["POST"])
def post_status():
  if request.method == "POST":
    message = request.form["status"]
    print(message)
    date = time.localtime(time.time())
    add_messages = messages(session["username"], f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}", message)
    db.session.add(add_messages)
    db.session.commit()
    return redirect(redirect_url())
    
  else:
    return redirect(url_for("index"))


@app.route('/user/<username>')
def user_profile(username):
  if "isLogged" in session:
    z = users.query.filter_by(username = username).first()
    return render_template("user.html", user = z, message = messages.query.filter_by(name = username).all() )
    
  else:
    flash("Not yet logged in.")
    return redirect (url_for("login"))


@app.route('/delete', methods = ["POST"])
def delete():
  if request.method == "POST":
    data = request.get_json()
    delete_message = messages.query.filter_by(name = data["name"], date = data["date"], message = data["id"]).first()
    db.session.delete(delete_message)
    db.session.commit()
    return redirect(redirect_url())
  
  else:
    return redirect(redirect_url())


@app.route('/edit_bio', methods = ["POST"])
def edit_bio():
  if request.method == "POST":
    u = request.form["bio"]
    y = users.query.filter_by(username = session["username"]).first()
    y.bio = u
    db.session.commit()
    return redirect (redirect_url())
  
  else:
    flash("Access Denied")
    return redirect (url_for("index"))

if __name__ == "__main__":
  db.create_all()
  app.run(debug = True)
