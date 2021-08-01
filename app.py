from flask import *
from datetime import *
import time 
from sqlalchemy import or_, and_, desc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import Mutable
import uuid
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit, join_room, leave_room


app = Flask(__name__)
app.secret_key = "ThisIsSupposedToBeSecured"
app.permanent_session_lifetime = timedelta(minutes=60)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)


# SocketIO

@socketio.on('receive')
def handler(data):
  print(data)
  join_room(data["room_id"])
  print(f"User successfully joined room: {data['room_id']}")
  
@socketio.on('message receive')
def message_server(msg):
  print(f"Message Received! {msg}") 
  emit('add_element', msg, to = msg["room_id"], broadcast = True)


# SQLAlchemy
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
class status(db.Model):
  _id = db.Column("id", db.Integer, primary_key = True)
  name = db.Column(db.String)
  date = db.Column(db.String)
  message = db.Column(db.String)
  identifier = db.Column(db.String)
  def __init__(self, name, date, message, identifier):
    self.name = name
    self.date = date
    self.message = message
    self.identifier = identifier
class message(db.Model):
  _id = db.Column("id", db.Integer, primary_key = True)
  sender = db.Column(db.String)
  receiver = db.Column(db.String)
  content = db.Column(db.String)
  identifier = db.Column(db.String)
  date = db.Column(db.String)
  
  def __init__(self, sender, receiver, content, identifier, date):
    self.sender = sender 
    self.receiver = receiver
    self.content = content
    self.identifier = identifier 
    self.date = date
class friend_uid(db.Model):
  _id = db.Column("id", db.Integer, primary_key = True)
  initiator = db.Column("initiator", db.String)
  target = db.Column("target", db.String)
  uid = db.Column("uid", db.String)
  
  def __init__(self, initiator, target, uid):
    self.initiator = initiator 
    self.target = target 
    self.uid = uid


#/..
def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


#URL Routing
@app.route("/")
def index():
  #db.session.commit()
  return render_template("index.html")

@app.route("/register", methods = ["POST", "GET"])
def register():
	if request.method == "GET":
	  session["status"] = []
	  return render_template("register.html", messages = session["status"])
	
	elif request.method == "POST":
		username = request.form["username"]
		hash_password = bcrypt.generate_password_hash(request.form["password"])
		isExist = users.query.filter_by(username = username).first()
		if isExist:
		  flash("Username exists.")
		  return render_template("register.html")
		else:
		  add_user = users(username, hash_password,[f"{username}"], "", "")
		  db.session.add(add_user)
		  db.session.commit()
		  return redirect(url_for("index"))
		  
		  
		  
@app.route("/communicate", methods = ["POST"])
def communicate():
  session["data"] = request.get_json()
  for i in session["data"]:
  	flash(i)
  	
  print(session["data"])
  return "Hello"
  
@app.route("/logout")
def logout():
  session.pop("isLogged", None)
  session.pop("username", None)
  
  
  return redirect( url_for("index"))
  
 
@app.route("/login", methods = ["POST", "GET"])
def login():
 
  
  if request.method == "GET":
    if "isLogged" in session:
      return redirect(url_for("profile"))
    else:
      return render_template("login.html")
  if request.method == "POST":
    session["username"] = request.form["username"]
    x = users.query.filter_by(username = session["username"]).first()
    if x:
      isExist = bcrypt.check_password_hash(x.password, request.form["password"])
    else:
      isExist = False
    if isExist:
      session["isLogged"] = True
      return redirect(f"/user/{session['username']}")
    else:
      flash("Invalid Username or Password")
      return redirect(redirect_url())


@app.route("/profile")
def profile():
  if "isLogged" in session:
    return render_template("profile.html", username = session["username"], message = status.query.all())
    
    
  else:
    flash("Not yet logged in.")
    return redirect(url_for("login"))
 
 
  
@app.route("/add_friend", methods = ["POST"])
def add_friend():
  if request.method == "POST":
    uid = str(uuid.uuid4())
    name = request.get_json()
   #Initiate new queries
   #Session Username is = Current_User
    current_user = users.query.filter_by(username = session["username"]).first()
    #manipulate current_user friends
    friends =list(current_user.friends)
    friends.append(f"{name[0]}")
    current_user.friends = friends
    #add_query to friend_uid
    add_uid = friend_uid(session["username"],name[0],uid)
    #commit everything
    db.session.add(add_uid)
    db.session.commit()
    
    return redirect(redirect_url())
 

@app.route("/post_status", methods = ["POST"])
def post_status():
  if request.method == "POST":
    status_content = request.form["status"]
    print(status)
    unique_id = uuid.uuid4()
    date = time.localtime(time.time())
    add_status = status(session["username"], f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}", status_content, f"{unique_id}" )
    db.session.add(add_status)
    db.session.commit()
    return redirect(redirect_url())
    
  else:
    return redirect(url_for("index"))

# TODO
@app.route('/user/<username>')
def user_profile(username):
  if "isLogged" in session:
    # complicated isFriends query
    z = users.query.filter_by(username = username).first()
    friends = friend_uid.query.filter(or_(and_(friend_uid.initiator == username, friend_uid.target == session['username']),and_(friend_uid.initiator == session['username'], friend_uid.target == username))).first()
    print(friends)
    if username == session["username"]:
      session["isFriends"] = "Self"
    
    elif friends:
      session["isFriends"] = True
    else:
      session["isFriends"] = False
    print (session['isFriends'])
    return render_template("user.html", user = z, message = status.query.filter_by(name = username).all(), isFriends = session["isFriends"], username = session["username"], uid = friends)
    
  else:
    flash("Not yet logged in.")
    return redirect (url_for("login"))


@app.route('/delete', methods = ["POST"])
def delete():
  if request.method == "POST":
    data = request.get_json()
    print(data)
    delete_status = status.query.filter_by(name = data["name"], identifier = data["identifier"]).first()
    db.session.delete(delete_status)
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

@app.route('/newsfeed')
def newsfeed():
  if "isLogged" in session:
    x = users.query.filter_by(username = session["username"]).first()
    post =  status.query.filter(status.name.in_(x.friends))
    return render_template("newsfeed.html", user = x)
  else:
    flash('Not yet logged in.')
    return redirect(url_for("login"))



@app.route('/inbox')
def inbox():
  if "isLogged" in session:
    x = users.query.filter_by(username = session["username"]).first()
    
    messagesReceived = db.session.query(message.sender).filter(message.sender.in_(x.friends)).group_by(message.sender).order_by(db.func.max(message._id)).distinct()
    print (messagesReceived)
    return render_template("inbox.html", user = x, msg = messagesReceived)
  else:
    return redirect(url_for("login"))

@app.route('/inbox/<username>')
def inbox_user(username):
  if "isLogged" in session:
    x = users.query.filter_by(username = session['username']).first()
    username = request.args["username"]
    msg = message.query.filter(or_(and_(message.sender == username, message.receiver == x.username),and_(message.sender == x.username, message.receiver == username))).order_by(message._id).all()
    uid = request.args["uid"]
    print(uid)
    return render_template("send_message.html", username = username, user = x, msg = msg, uid = uid)
    


@app.route('/send_message', methods = ['POST'])
def send_message():
  if request.method == "POST":
    data = request.get_json()
    identifier = str(uuid.uuid4)
    date = time.localtime(time.time())
    
    add_message = message(data["sender"], data["receiver"], data["content"], identifier, f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}")
    print(f"Sender: {data['sender']}")
    print(f"Receiver: {data['receiver']}")
    db.session.add(add_message)
    db.session.commit()
    return redirect(redirect_url())


if __name__ == "__main__":
  db.create_all()
  socketio.run(app, debug = True)
  
  
  