from flask import  Flask,render_template,url_for,request,redirect,flash,session
import random,os
import datetime
import mysql.connector
from flask_ngrok import run_with_ngrok

cur = mysql.connector.connect(
	user=os.environ.get('MYSQL_USER'),
	password=os.environ.get('MYSQL_PASSWORD'),
	database='blog'
	)

app = Flask(__name__)
#run_with_ngrok(app)
app.config['SECRET_KEY']="adsd"
app.session_permanent_lifetime=datetime.timedelta(days=1)

con = cur.cursor()
con.execute('select max(id) from posts')
rt = 0
for i in con:
	if i:
		rt+=i[0]
con.execute('select max(id) from users')
pt = 0
for i in con:
	if i:
		pt+=i[0]


@app.route('/',methods=['POST','GET'])
def home():
	con.execute('select * from posts')
	posts = []
	authors = []
	
	for i  in con:
		posts.append(i[1])
		posts.append(i[2])
		posts.append(i[4])
		authors.append(i[3])
	t = 2
	new = []
	for i in authors:
		con.execute(f'select * from users where id={i}')
		for j in con:
			new.append(j[1])
	lists = []
	y = 0
	for i in new:
		lists.append(i)
		for j in range(y,len(posts),3):
			lists.append(posts[j])
			lists.append(posts[j+1])
			lists.append(posts[j+2])
			y+=3
			break
	lists.reverse()
	if request.method=="POST":
		session.permanent=True
		email = request.form['email']
		password = request.form['password']
		
		con.execute('select * from users')
		r = 0

		for i in con:
			if i[2]==email and i[4]==password:
				name = i[1]
				r+=1
		if r==1:
			session['user'] = name
			f = 'select count(id) from posts'
			c = 0
			for i  in con:
				c = i
			flash(f'total posts {c}')
			return render_template('home.html',posts=lists,len=len(lists))
		else:
			flash(f'you should check your mail and password')
			return redirect(url_for('login'))
	else:

		f = 'select count(id) from posts'
		con.execute(f)
		c = 0
		for i  in con:
			c = i
		flash(f'total posts {c}')
		return render_template('home.html',posts=lists,len=len(lists))



@app.route('/newuser')
def newuser():
	return render_template('signup.html')



@app.route('/login',methods=['POST','GET'])
def login():
	if request.method=="POST":
		username = request.form['username']
		mail = request.form['email']
		city = request.form['city']
		con.execute('select * from users')
		p = 0
		for i in con:
			if i[2]==mail or  i[1]==username:
				p+=1
		if p==1:
			flash('details already registered!')
			return redirect(url_for('newuser'))
		password = request.form['password']
		t = "insert into users(id,username,email,city,password) values(%s,%s,%s,%s,%s)"
		global pt
		pt+=1
		tups = (pt,username,mail,city,password)
		con.execute(t,tups)
		cur.commit()
		return render_template('login.html')
	return render_template('login.html')



@app.route('/forgetpassword')
def forgetpassword():
	return render_template('forgetpassword.html')



current = []
total = -1
@app.route('/check',methods=['POST','GET'])
def check():
	if request.method=="POST":
		name = request.form['username']
		mail = request.form['email']
		citi = request.form['city']
		con.execute('select * from users')
		r = 0
		for i in con:
			if i[1]==name and i[2]==mail and i[3]==citi:
				r+=1
		if r==1:
			global total
			total+=1
			current.append(mail)
			return redirect(url_for('good'))
		else:
			flash('check your details'.title())
			return redirect(url_for('forgetpassword'))
	else:
		return redirect(url_for("forgetpassword"))

@app.route('/good')
def good():
	return render_template('changepassword.html')



@app.route('/changepassword',methods=['POST','GET'])
def changepassword():
	if request.method=='POST':
		password = request.form['password']
		conpassword = request.form['conpassword']
		if password==conpassword:
			global total
			cv = 'update  users set password=%s where email=%s'
			tup = (password,current[total])
			con.execute(cv,tup)
			cur.commit()
			flash(f'password successfully changed!')
			return redirect(url_for('home'))
		else:
			flash('password and confirm password must be same!'.capitalize())
			return   redirect(url_for('good'))
	return redirect(url_for('forgetpassword'))



@app.route('/post')
def post():
	if "user" in session:
		return render_template('post.html',user=session["user"])
	else:
		return redirect(url_for('login'))
user_ids =[]
tot=0



@app.route('/oldpost',methods=['POST','GET'])
def oldpost():
	if request.method=="POST":
		title = request.form['title']
		text = request.form['text']
		session['title']=title
		session['text']=text
		ma = f'select * from users'
		con.execute(ma)
		d = 0
		for i in con:
			if i[1]==session["user"]:
				d+=i[0]
		global post_id,tot,rt
		rt+=1
		ins = 'insert into posts values(%s,%s,%s,%s,%s)'
		tup = (rt,title,text,d,str(datetime.datetime.today()).split()[0])
		tot+=1
		con.execute(ins,tup)
		cur.commit()
		return redirect(url_for('home'))
		return render_template('oldpost.html',title=title,text=text,user=  session['user'])
	elif 'user' in session:
		x = 0
		my= []
		con.execute('select * from users')
		for i in con:
			if i[1]==session['user']:
				x = i[0]

		f = f'select * from users where id = {x}'
		con.execute(f)
		for i in con:
			my.append(i[1])
			my.append(i[2])
			my.append(i[3])
			my.append(i[5])
		con.execute('select * from posts')
		all_posts = []
		for i in con:
			if i[3]==x:
				all_posts.append(i[1])
				all_posts.append(i[2])
				all_posts.append(str(i[4]))
		all_posts.reverse()
		#flash(my)
		return render_template('oldpost.html',pos=all_posts,user=session['user'],len=len(all_posts),personal=my,lem=len(my))
	else:
		flash('login to see your old posts')
		return render_template('oldpost.html')


@app.route('/logout')
def logout():
	session.pop('user',None)
	return redirect(url_for('login'))



@app.route('/friends',methods=['POST','GET'])
def friends():
	if request.method=="POST":
		search = request.form['good']
		q = []
		con.execute('select * from users')
		for i in con:
			if search.title() in i[1].title():
				q.append(i[1])
				q.append(i[2])
				q.append(i[3])
				q.append(i[5])
		if len(q)!=0:
			flash(f'results found by search on: "{search}"'.title())
			return render_template('friends.html',friends=q,len=len(q))
		else:
			flash(f'results not found!')
			return render_template('friends.html')
	else:
		return redirect(url_for('oldpost'))



@app.route('/personalpost/<uname>')
def personalpost(uname):
	con.execute('select * from users')
	idd = []
	name = []
	for i in con:
		if i[1]==uname:
			idd.append(i[0])
			name.append(i[1])
	
	lists = []
	y = 0
	con.execute('select * from posts')
	for j in con:
		if j[3]==idd[0]:
			lists.append(j[1])
			lists.append(j[2])
			lists.append(j[4])
	q=0
	lists.reverse()
	return render_template('personal_posts.html',q=lists,len=len(lists),name=uname)



@app.route('/area/<city>')
def area(city):
	con.execute('select * from users')
	c = []
	for i in con:
		if i[3]==city:
			c.append(i[1])
			c.append(i[2])
			c.append(i[3])
	flash(f'bloggers in {city}')
	return render_template('city.html',q=c,len=len(c))



@app.route('/dating/<dates>')
def dating(dates):
	con.execute('select * from posts')
	author_id = []
	poster = []
	for i in con:
		if str(i[4])==dates:
			author_id.append(i[3])
			poster.append(i[1])
			poster.append(i[2])
			poster.append(dates)
	z=2
	for i  in author_id:
		con.execute('select * from users')
		for j in con:
			if i==j[0]:
				poster.insert(z,j[1])
				z+=4
	
	del author_id
	poster.reverse()
	flash(f'blogs on {dates}')	
	return render_template('dating.html',posts=poster,len=len(poster))


updater = []


@app.route('/updatepost',methods=['POST','GET'])
def updatepost():
	if request.method=="POST":
		title = request.form['good']
		text = request.form['content']
		con.execute('select * from posts')
		c = 0
		for i in con:
			if i[1]==title:
				c+=1
				updater.append(i[0])
		if c==1:
			return render_template('update.html',data=title,text=text)
	return redirect(url_for('oldpost'))



@app.route('/doset',methods=['POST','GET'])
def doset():
	if request.method=="POST":
		title = request.form['title']
		text = request.form['text']
		
		t = f'update posts set title=%s,content = %s where id=%s'
		m = (title,text,updater[-1])
		con.execute(t,m)
		cur.commit()
		flash(f'post successfully updated!')
		return redirect(url_for('oldpost'))
	else:
		return redirect(url_for('oldpost'))



@app.route('/deletepost',methods=['POST'])
def deletepost():
	titl = request.form['good']
	tup =(titl,)
	f = 'delete from posts where title=%s'
	con.execute(f,tup)
	cur.commit()
	flash(f'post  successfully deleted!')
	return redirect(url_for('oldpost'))



@app.route('/new')
def new():
	img = []
	con.execute('select * from users')
	for i in con:
		img.append(i[1])
		img.append(i[2])
		img.append(i[-1])
	return render_template('new.html',data=img,len=len(img))



@app.route('/pic',methods=['post'])
def pic():
	path = 'C:/Users/RedLine Compuer/Desktop/new/static/'
	file = request.form['good']
	h = 'update users set image=%s where username=%s'
	tup = (file,session["user"])	
	con.execute(h,tup)
	cur.commit()
	return redirect('oldpost')


if __name__=='__main__':
	app.run(debug=True,port=4000)