import os
#import magic
import urllib.request
#from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from flask import Flask
import sqlite3
import webbrowser


      
UPLOAD_FOLDER=r"C:\Users\sharath\Desktop\ai_proj"

app = Flask(__name__, template_folder='template')
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['xlsx', 'csv'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def index_form():
	return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			flash('File successfully uploaded')
			return redirect('/requiredinput')
		else:
			flash('Allowed file types are xlsx, csv')
			return 'file type not allowed'
		file.save(secure_filename(file.filename))

@app.route('/requiredinput')
def input_form():
	return render_template('inputs.html')


@app.route('/requiredinput',methods=['POST'])
def input_taker():
        if request.method=='POST':
                Attendance = request.form['Attendance']
                Lab=request.form['Lab']
                Quiz=request.form['Quiz']
                Compre=request.form['Compre']
                Midsem=request.form['midsem']
                print(Attendance,Lab,Quiz,Compre,Midsem)
                conn = sqlite3.connect('marks_db.sqlite')
                cursor=conn.cursor()
                cursor.execute('create table inputs_req(Attendance int,Lab int,Quiz int,Compre int,Midsem int) ')
                cursor.execute('insert into inputs_req(Attendance,Lab,Quiz,Compre,Midsem) values (?,?,?,?,?)',(Attendance,Lab,Quiz,Compre,Midsem))
                conn.commit()
                conn.close()
        return redirect('/finalgrades')
        
        
@app.route('/finalgrades')
def run_backend():
        os.system("ai_project.py")
        conn = sqlite3.connect('marks_db.sqlite')
        cursor=conn.cursor()
        cursor.execute("select * from grades_table")
        data=cursor.fetchall()
        cursor.execute("DROP TABLE grades_table")
        conn.commit()
        
        return render_template('output.html',data = data) 

if __name__ == "__main__":
    url="http://127.0.0.1:5000"
    webbrowser.open_new(url)   
    app.run()
