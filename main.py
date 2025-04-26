# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
from werkzeug.utils import secure_filename
from supportFile import *
import os
import cv2
import pandas as pd
import utils
import nltk
import moviepy.editor as mp
import speech_recognition as sr 
import sqlite3
from datetime import datetime
from autocorrect import Speller
import json
from suicide import *

interest=''
problem=''
count = 1
userResponse = []

video = ''
name = ''
spell = Speller(lang='en')
r = sr.Recognizer()

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
		try:
			name = cursorObj.fetchone()[0]
			return redirect(url_for('home'))
		except:
			error = "Invalid Credentials Please try again..!!!"
			return render_template('login.html',error=error)
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			name = request.form['name']
			email = request.form['email']
			password = request.form['password']
			rpassword = request.form['rpassword']
			pet = request.form['pet']
			if(password != rpassword):
				error='Password dose not match..!!!'
				return render_template('register.html',error=error)
			try:
				con = sqlite3.connect('mydatabase.db')
				cursorObj = con.cursor()
				cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
			
				if(cursorObj.fetchone()):
					error = "User already Registered...!!!"
					return render_template('register.html',error=error)
			except:
				pass
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Email text,password text,pet text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?)",(dt_string,name,email,password,pet))
			con.commit()

			return redirect(url_for('login'))

	return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		pet = request.form['pet']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT password from Users WHERE Email='{email}' AND pet = '{pet}';")
		
		try:
			password = cursorObj.fetchone()
			#print(password)
			error = "Your password : "+password[0]
		except:
			error = "Invalid information Please try again..!!!"
		return render_template('forgot-password.html',error=error)
	return render_template('forgot-password.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	global name
	return render_template('home.html',name=name)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	return render_template('dashboard.html',name=name)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method=='POST':
		if request.form['uploadbutton'] == 'Upload':
			savepath = r'upload/'
			f = request.files['doc']
			f.save(os.path.join(savepath,(secure_filename('test.mp4'))))
			return render_template('upload.html',name=name,file=f.filename,mgs='File uploaded..!!')
		elif request.form['uploadbutton'] == 'Detect Depression':
			return redirect(url_for('video'))
	return render_template('upload.html',name=name)


@app.route('/video', methods=['GET', 'POST'])
def video():
	global name
	return render_template('video.html',name=name)

@app.route('/video_stream')
def video_stream():
	global name
	return Response(video_feed(name),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/record', methods=['GET', 'POST'])
def record():
	global name
	conn = sqlite3.connect('mydatabase.db', isolation_level=None,
						detect_types=sqlite3.PARSE_COLNAMES)
	df = pd.read_sql_query(f"SELECT * from Result WHERE Name='{name}';", conn)
	
	return render_template('record.html',name=name,tables=[df.to_html(classes='table-responsive table table-bordered table-hover')], titles=df.columns.values)

@app.route('/text_record', methods=['GET', 'POST'])
def text_record():
	global name
	conn = sqlite3.connect('mydatabase.db', isolation_level=None,
						detect_types=sqlite3.PARSE_COLNAMES)
	df = pd.read_sql_query(f"SELECT * from TextResult WHERE Name='{name}';", conn)
	
	return render_template('textrecord.html',name=name,tables=[df.to_html(classes='table-responsive table table-bordered table-hover')], titles=df.columns.values)

@app.route('/bot', methods=['GET', 'POST'])
def bot():
	state = 0
	global name
	global num
	
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			state = 1
			name1 = request.form['name']
			num = request.form['num']
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS botUsers (Date text,Name text,Contact text)")
			cursorObj.execute("INSERT INTO botUsers VALUES(?,?,?)",(dt_string,name1,num))
			con.commit()

		if request.form['sub']=='Rate':
			rating = request.form['rate']
			suggestion = request.form['suggestions']
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Feedback (Date text,Name text,Contact text,Ratings text,Feedback text)")
			cursorObj.execute("INSERT INTO Feedback VALUES(?,?,?,?,?)",(dt_string,name,num,rating,suggestion))
			con.commit()
			return redirect(url_for('home'))


	#print(state)
	return render_template('bot.html',state = json.dumps(state),name=name)


@app.route("/get")
def get_bot_response():
    global count,userResponse

    user_response = spell(request.args.get('msg'))
    user_response=user_response.lower()
    userResponse.append(user_response)
    botResponse = questions[count]
    count = count + 1
    if(count > 19):
        tendency = analyze_responses(userResponse)
        video_url = '<a href="https://www.youtube.com/watch?v=5YoTP_fO4FI" target="_blank">click here to watch helpful video</a>'
        
        if(tendency != 'Low Risk'):
            botResponse = f'Stress Tendency: {tendency} - {video_url}'
        else:
            botResponse = '<div class="text-success"> No Risk </div>'
        count = 0
    return botResponse

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	global name
	conn = sqlite3.connect('mydatabase.db', isolation_level=None,
						detect_types=sqlite3.PARSE_COLNAMES)
	df = pd.read_sql_query(f"SELECT * from Feedback WHERE Name='{name}';", conn)
	
	return render_template('feedback.html',name=name,tables=[df.to_html(classes='table-responsive table table-bordered table-hover')], titles=df.columns.values)

@app.route('/help', methods=['GET', 'POST'])
def help():
    global name
    return render_template('help.html', name=name)


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__' and run:
	app.run(host='0.0.0.0', debug=False, threaded=True)
