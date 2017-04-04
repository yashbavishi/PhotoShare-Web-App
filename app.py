######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from flask.ext.login import current_user
from collections import Counter
import operator
#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'Yash1234'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Namrata2002'
app.config['MYSQL_DATABASE_DB'] = 'PA1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


Globalvariableforphotos = ()
Globalvariableforphotos1 = ()
aid = 0

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from User") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from User") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register", methods=['POST'])
def register_user():
	try:
                F_ame=request.form.get('F_ame')
                L_ame=request.form.get('L_ame')
		email=request.form.get('email')
		password=request.form.get('password')
		DOB=request.form.get('DOB')
		Home_town=request.form.get('Home_town')
		Gender=request.form.get('Gender')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print cursor.execute("INSERT INTO User (F_ame, L_ame, email, password, DOB, Home_town, Gender, Activity_count) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', 0)".format(F_ame, L_ame, email, password, DOB, Home_town, Gender))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(aid): #Returns Photos in a particular album of the user
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption, likes_count FROM Photos WHERE Album_id = '{0}'".format(aid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUsersAlbums(uid): #Returns all the Album ids and names of all the albums of the user
        cursor = conn.cursor()
        cursor.execute("Select album_id, a_name From Albums WHERE Owner_id = '{0}'".format(uid))
        return cursor.fetchall()
                       

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM User WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

# def getPhotoCaptionFromPhotos(pid):
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT caption  FROM Photos WHERE photo_id = '{0}'".format(pid))
# 	return cursor.fetchone()[0]

# def getAlbumID(a_name):
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT album_id FROM Albums Where a_name = '{0}'".format(a_name))	
# 	return cursor.fetchone()[0]

def getUserFriends(uid): # Return the names of the friends of the user
	cursor = conn.cursor()
	cursor.execute("Select f.f_ame, f.l_ame From Friends fr, User f Where fr.user_id1 = '{0}' and fr.user_id2 = f.user_id".format(uid))
	return cursor.fetchall()

def getTop10Users(): # Returns top 10 users in the descending order of their activity count
	cursor = conn.cursor()
	cursor.execute("Select u.user_id, u.f_ame, u.l_ame From User u Where u.user_id <> 4 order by activity_count desc limit 10".format())
	return cursor.fetchall()

def getUsersFromDatabase(uid): # Return list of users that are not friends of the current user
	cursor = conn.cursor()
	cursor.execute("Select u.user_id, u.f_ame, u.l_ame From User u Where u.user_id <> '{0}' and u.user_id NOT IN (Select f.user_id2 From Friends f Where f.user_id1 = '{0}')".format(uid))
	return cursor.fetchall()

def getTagIDFromTagName(title): # returns the Tag Id of a particular tag
	cursor = conn.cursor()
	cursor.execute("SELECT TagID FROM Tags Where title = '{0}'".format(title))
	flag = cursor.fetchone()
	if flag == None:
		return None
	else:
		return flag

def getPidFromData(data, caption): # Returns the pid of a particular photo
	cursor = conn.cursor()
	cursor.execute("SELECT Photo_id FROM Photos Where data = '{0}' and caption = '{1}'".format(data, caption))
	return cursor.fetchone()[0]

def getPhotosWithTags(uid, tag, flag): # returns the photos that have a particular tag
	if flag == '1':
		cursor = conn.cursor()
		cursor.execute("SELECT DISTINCT p.caption, p.data, p.photo_id, p.likes_count FROM Photos p, Albums a, Tags t, Associate_with tp WHERE tp.tag_id = '{0}' and p.Photo_id = tp.photo_id".format(tag))
		return cursor.fetchall()
	elif flag == 2:
		cursor = conn.cursor()
		cursor.execute("SELECT DISTINCT p1.caption, p1.data, p1.photo_id, p1.likes_count FROM Photos p1, Associate_with tp1 WHERE tp1.tag_id = '{1}' and p1.Photo_id = tp1.photo_id and p1.photo_id NOT IN (SELECT DISTINCT p.photo_id FROM Photos p, User u, Albums a, Tags t, Associate_with tp WHERE a.Owner_ID = '{0}' and p.album_id = a.album_id  and tp.tag_id = '{1}' and p.Photo_id = tp.photo_id)".format(uid, tag))
		return cursor.fetchall()
	else:
		cursor = conn.cursor()
		cursor.execute("SELECT DISTINCT p.caption, p.data, p.photo_id, p.likes_count FROM Photos p, User u, Albums a, Tags t, Associate_with tp WHERE a.Owner_ID = '{0}' and p.album_id = a.album_id  and tp.tag_id = '{1}' and p.Photo_id = tp.photo_id".format(uid, tag))
		return cursor.fetchall()


def getTagSearchPhotos(tags): # Returns the resulting photos of the search by tags
	
	tagids = ()
	for i in tags:
		tagids = tagids +  getTagidsFromTags(i)
		
		#tagsids = cursor.fetchone()[0] + " "
	
	for i in tagids:
		print i

	s = ""
	for i in tagids:
		s = s + ", associate_with t" + str(i[0])
	print s 

	q = ""
	for i in tagids:
		q = q + "p.photo_id = t" + str(i[0]) + ".photo_id and "
	print q 

	w = ""
	ctr=len(tagids)
	c=0
	for i in tagids:
		if(c<ctr-1):
			w = w + "t" + str(i[0]) + ".tag_id = " + str(i[0]) + " and "
		else:
			w = w + "t" + str(i[0]) + ".tag_id = " + str(i[0])
		c = c + 1
	print w

	st = s + " Where p.album_id = a.Album_ID and " + q + " " + w
	print st
	 #p.album_id = a.Album_ID and
	 #

	cursor = conn.cursor()
	cursor.execute("SELECT p.caption, p.data, p.photo_id, p.likes_count, a.owner_id FROM Photos p, Albums a" + st)
	return cursor.fetchall()
	
	
def getTagidsFromTags(tag): # Returns the tag id of a particular tag
	cursor = conn.cursor()
	cursor.execute("SELECT t.tagID FROM Tags t Where t.title = '{0}'".format(tag))
	return cursor.fetchall()
def getUserTags(uid): # Returns the tags associated with a particular user
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT t.tagID, t.title FROM Photos p, Albums a, Tags t, Associate_with tp WHERE a.Owner_ID = '{0}' and p.album_id = a.album_id  and t.tagid = tp.tag_id and p.Photo_id = tp.photo_id".format(uid))
	return cursor.fetchall()

def getOtherTags(uid): #Returns the tags that are not associated with a particular user
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT t1.tagID, t1.title FROM Tags t1 WHERE t1.tagID NOT IN (SELECT DISTINCT t.tagID FROM Photos p, Albums a, Tags t, Associate_with tp WHERE a.Owner_ID = '{0}' and p.album_id = a.album_id  and t.tagid = tp.tag_id and p.Photo_id = tp.photo_id)".format(uid))
	return cursor.fetchall()

def getTop10Tags(): # return the top 10 most popular tags from the database
	cursor = conn.cursor()
	cursor.execute("SELECT  t.tagid, t.title From Associate_with tp, Tags t Where tp.tag_id = t.tagID group by tp.tag_id order by count(tp.tag_id) desc limit 10")
	return cursor.fetchall()

def insertIntoAssociateWith(tagid1, pid): # Inserts in the Associate_with table (Table of photo ids and tag ids)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Associate_with (Tag_id, Photo_id) values ('{0}', '{1}')".format(tagid1[0], pid))
	conn.commit()
def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM User WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
        uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile", albums=getUsersAlbums(uid), friends=getUserFriends(uid), tags=getUserTags(uid), othertags=getOtherTags(uid), top10tags=getTop10Tags(), top10users=getTop10Users())

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/create_album', methods=['GET', 'POST']) # Code for Creating Albums
@flask_login.login_required
def create_albums():
	
	if request.method == 'POST':
		uid=getUserIdFromEmail(flask_login.current_user.id)
		a_name=request.form.get('a_name')
		print a_name
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums (A_name, Owner_id) VALUES ('{0}', '{1}')".format(a_name, uid))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message="Album Created!", albums=getUsersAlbums(uid))
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('createalbum.html')

@app.route('/upload', methods=['GET', 'POST']) # Code for Uploading Photos and inserting tags
@flask_login.login_required
def upload_file():
	
	
	if request.method == 'POST':
		global aid
		aid=request.args.get('value2')
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = request.form.get('tags')
		tags= tags.split(' ')
		uid=getUserIdFromEmail(flask_login.current_user.id)
		print caption
		print aid
		data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Photos (caption, data, likes_count, Album_id) VALUES ('{0}', '{1}', 0, '{2}')".format(caption, data, aid))
		conn.commit()
		cursor = conn.cursor()
		cursor.execute("UPDATE USER SET Activity_count= Activity_count + 1 Where user_id = '{0}'".format(uid))
		conn.commit()
		for i in tags:
			
			tagid = getTagIDFromTagName(i)
			if tagid == None:
				cursor = conn.cursor()
				cursor.execute("INSERT INTO Tags (Title) VALUES ('{0}')".format(i))
				conn.commit()
				tagid1 = getTagIDFromTagName(i)
				pid = getPidFromData(data, caption)
				print tagid1
				insertIntoAssociateWith(tagid1, pid)
			else:
				pid = getPidFromData(data, caption)
				insertIntoAssociateWith(tagid, pid)
		
		return render_template('album.html', photos=getUsersPhotos(aid), albumid=aid)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		global aid
		aid=request.args.get('value1')
		return render_template('upload.html', albumid=aid)
#end photo uploading code 
@app.route('/friends', methods=['GET', 'POST']) # Code for adding friends
@flask_login.login_required
def add_friends():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		user_id2 = request.args.get('value')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid, user_id2))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message="Friend Added!", albums=getUsersAlbums(uid), friends=getUserFriends(uid))

@app.route('/addfriends', methods=['GET', 'POST']) #Code to display users that can be added as friends
@flask_login.login_required
def render_addfriend():	
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('addfriend.html', users= getUsersFromDatabase(uid))
		
@app.route('/likes', methods=['POST']) # Code to like a particular photo
@flask_login.login_required
def like_photo():
	pid = request.args.get('value')
	flag = request.args.get('value1')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Likes (user_id, photo_id) values ('{0}', '{1}')".format(uid, pid))
	conn.commit()
	if flag == '1':
		return render_template('album.html', message='Like Added', photos=Globalvariableforphotos, albumid=aid)
	elif flag == '2':
		return render_template('album.html', message='Like Added', tagphotos= Globalvariableforphotos)
	elif flag == '3':
		return render_template('album.html', message='Like Added', tag1photos= Globalvariableforphotos, notusertagphotos = Globalvariableforphotos1)
	elif flag == '4':
		return render_template('album.html', message='Like Added', tagsearchphotos= Globalvariableforphotos)
	elif flag == '5':
		return render_template('album.html', message='Comment Added', usermaylikePhotos=Globalvariableforphotos)
		


@app.route('/tags', methods=['GET']) # Code to return photos with a particular tag
@flask_login.login_required
def display_tag_photos():
	tag = request.args.get('value')
	flag = request.args.get('value1')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	print flag
	if flag == '1':
		global Globalvariableforphotos
		Globalvariableforphotos = getPhotosWithTags(uid, tag, flag)
		return render_template('album.html', tagphotos= Globalvariableforphotos)
	elif flag == '2':
		global Globalvariableforphotos
		Globalvariableforphotos = getPhotosWithTags(uid, tag, '1')
		return render_template('album.html', notusertagphotos= Globalvariableforphotos)	
	elif flag == '0':
		global Globalvariableforphotos
		Globalvariableforphotos = getPhotosWithTags(uid, tag, flag)
		global Globalvariableforphotos1
		Globalvariableforphotos1 = getPhotosWithTags(uid, tag, 2)
		return render_template('album.html', tag1photos= Globalvariableforphotos, notusertagphotos = Globalvariableforphotos1)

@app.route('/search', methods=['POST']) #Code to search for photos with tags
def display_tag_search_photos():
	tags = request.form.get('tags')
	tags = tags.split(" ")
	if current_user.is_authenticated:
		uid=getUserIdFromEmail(flask_login.current_user.id)
	else:
		uid=4
	global Globalvariableforphotos
	Globalvariableforphotos = getTagSearchPhotos(tags)
	return render_template('album.html', tagsearchphotos= Globalvariableforphotos, uid=uid)	

@app.route('/likeusers', methods=['POST']) #Code to display the users who have liked a particular photo
@flask_login.login_required
def display_like_users():
    
        pid=request.args.get('value')
        print(pid)
        cursor = conn.cursor()
        cursor.execute("SELECT u.user_id, u.f_ame, u.l_ame FROM User u, Likes l Where l.photo_id = '{0}' and l.user_id = u.user_id".format(pid))
        userss = cursor.fetchall()
        return render_template('likeusers.html', likeusers = userss)

@app.route('/comments', methods=['POST']) #Code to Add a comment to a photo
def add_comment(): 
    
        pid=request.args.get('value')
        flag=request.args.get('value1')
        print(pid)
        text = request.form.get('text')
        if current_user.is_authenticated:
        	uid=getUserIdFromEmail(flask_login.current_user.id)
        else:
        	uid = 4
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Comments (Comment_text, Commenter_id, Photo_id) VALUES ('{0}', '{1}', '{2}') ".format(text, uid, pid))
        conn.commit()
        if flag == '1':
        	return render_template('album.html', message='Comment Added', notusertagphotos= Globalvariableforphotos)
        elif flag == '2':
        	return render_template('album.html', message='Comment Added', tagsearchphotos= Globalvariableforphotos, uid=uid)
        elif flag == '3':
        	return render_template('album.html', message='Comment Added', photos=Globalvariableforphotos, albumid=aid, flag=flag)
        elif flag == '4':
        	return render_template('album.html', message='Comment Added', usermaylikePhotos=Globalvariableforphotos)

@app.route('/commentsdisplay', methods=['POST']) #Code to Display Comments of a particular photo
def display_comments():
    
        pid=request.args.get('value')
        print(pid)
        cursor = conn.cursor()
        cursor.execute("SELECT u.user_id, u.f_ame, u.l_ame, c.Comment_text FROM Comments c, User u Where c.photo_id = '{0}' and c.Commenter_id = u.user_id".format(pid))
        userss = cursor.fetchall()
        return render_template('displaycomments.html', usercomments = userss)

@app.route('/recommendation', methods=['POST']) #Code to give recommendation for tags to the user
@flask_login.login_required
def tag_recommendations():
	tags = request.form.get('tags')
	tags1 = []
	tags = tags.split(" ")
	for i in tags:
		print i
		tags1.append(i)
	print tags1
	cursor = conn.cursor()
	cursor.execute("SELECT aw.photo_id FROM Associate_with aw, Tags t Where t.title = '{0}' and t.tagid = aw.tag_id or t.title = '{1}' and t.tagid = aw.tag_id".format(tags1[0], tags1[1]))
	photo_ids = cursor.fetchall()
	recommendation=[]
	for photo_id in photo_ids:
		cursor = conn.cursor()
		cursor.execute("SELECT t.title FROM Associate_with aw, Tags t Where t.tagid = aw.tag_id and aw.photo_id = '{0}'".format(photo_id[0]))
		tagnames = cursor.fetchall()
		for tagname in tagnames:
			print tagname
			if tagname[0] in tags1:
				tagname
				continue
			else:
				recommendation.append(tagname[0])
	print recommendation
	counts = Counter(recommendation)
	recommendations = sorted(set(recommendation), key=counts.get, reverse=True)
	recommendations = recommendations[0:5]
	return render_template('upload.html', albumid=aid, tagrecommendations=recommendations)

@app.route('/album') #Code tp Return photos with a particular album id
def displayPhotos():
    if current_user.is_authenticated:
       	uid=getUserIdFromEmail(flask_login.current_user.id)
    else:
        uid = 4
    flag=request.args.get('value1')        
    print flag
    global aid
    aid=request.args.get('values')
    print(aid)
    global Globalvariableforphotos
    Globalvariableforphotos = getUsersPhotos(aid)
    uploadflag=request.args.get('value1')
    return render_template('album.html', photos=Globalvariableforphotos, albumid=aid, flag=flag, uploadflag=uploadflag, uid=uid)


@app.route('/delete', methods=['POST']) #Code to Delete a photo
@flask_login.login_required
def delete_photo():
	if request.method == 'POST':
		
		pid=request.args.get('value')
		print(pid)
		aid=request.args.get('value1')
		print(aid)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(pid))
		conn.commit()
		return render_template('album.html', message='Photo Deleted!', photos=getUsersPhotos(aid), albumid=aid)

@app.route('/deletealbum', methods=['POST']) #Code to delete a album
@flask_login.login_required
def delete_album():
	if request.method == 'POST':
		aid=request.args.get('value')
		print(aid)
		uid=getUserIdFromEmail(flask_login.current_user.id)
		print(uid)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM Albums WHERE Album_id = '{0}'".format(aid))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message="Album DELETED!", albums=getUsersAlbums(uid))		
#default page  
@app.route("/", methods=['GET'])
def hello():
 		return render_template('hello.html', message='Welecome to Photoshare')

@app.route('/allalbums', methods=['GET']) #Code to display list of all albums in the database
def display_all_albums():
	cursor = conn.cursor()
	cursor.execute("SELECT  a.album_id, a.a_name, u.user_id, u.f_ame, u.l_ame From Albums a, User u Where a.Owner_id = u.user_id")
	return render_template('displayallalbums.html', allalbums=cursor.fetchall())

@app.route('/youmaylike', methods=['POST','GET']) # Code that implements You may also like feature
@flask_login.login_required
def you_May_Also_Like():
	uid= getUserIdFromEmail(flask_login.current_user.id)
	return render_template('album.html', usermaylikePhotos= userwillike(uid))


def userwillike(uid):
	cursor=conn.cursor()
	cursor.execute("SELECT t.tagid from tags t , associate_with aw, photos p, albums a where a.owner_id = '{0}' and a.album_id=p.album_id and p.photo_id=aw.photo_id and aw.tag_id=t.tagid group by t.tagid order by count(t.tagid) desc limit 5".format(uid))
	got=cursor.fetchall()


	cursor=conn.cursor()
	cursor.execute("SELECT p.photo_id from photos p, albums a where p.album_id = a.album_id and a.owner_id <> '{0}'".format(uid))
	photoidlist=cursor.fetchall()

	rank = {}
	for i in photoidlist:
		for j in got:
			cursor=conn.cursor()
			cursor.execute("SELECT p.photo_id from photos p, associate_with aw where aw.tag_id= '{0}' AND aw.photo_id= '{1}' AND aw.photo_id=p.photo_id".format(j[0],i[0]))
			got1=cursor.fetchall()
			if got1:
				if i[0] not in rank:
					rank[i[0]] = 1
				else:
					rank[i[0]]+=1


	sorted_rank = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)
	print sorted_rank


	resultphotos=()
	for key,value in sorted_rank:
		cursor=conn.cursor()
		cursor.execute("SELECT p.caption, p.data, p.photo_id, p.likes_count from photos p where p.photo_id='{0}'".format(key))
		resultphotos += cursor.fetchall()
	global Globalvariableforphotos
	Globalvariableforphotos = resultphotos
	return Globalvariableforphotos




if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
