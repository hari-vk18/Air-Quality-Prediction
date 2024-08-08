from flask import Flask
from flask import request,render_template,url_for,redirect,session
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask_mail import Mail, Message
import os
import smtplib
from email.message import EmailMessage
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to your own secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
db = SQLAlchemy(app)

# User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your SMTP server
app.config['MAIL_PORT'] = 587  # Port for SMTP server (587 for TLS)
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'prasathh303@gmail.com'  # Your email username
app.config['MAIL_PASSWORD'] = 'ymtz aqjb vvul yvtw'  # Your email password

mail = Mail(app)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        feedback_text = request.form['message']
        feedback_email = request.form.get('email')
		
        # Send email
        msg = Message(subject='Feedback Received',
                      sender=feedback_email,
                      recipients=['prasathh303@gmail.com'])  # Email recipient
        msg.body = f"Feedback from {feedback_email}:\n\n{feedback_text}"
        print("Message Sender:", msg.sender)

        try:
           mail.send(msg)
        except Exception as e:
           print("An error occurred while sending the email:", str(e))
        return "Thank you for your feedback! We have received it."

model = pickle.load(open('tree_gridcv.pkl', 'rb'))

def generate_plot():
    # Data
    x = ['Random Forest + XGBoost', 'CNN']
    ac = [88.91, 95.72]
    y = ac
    
    # Create DataFrame
    d = {"Algorithm": x, "Accuracy": ac}
    d = pd.DataFrame(d)
    
    # Plotting
    plt.style.use('ggplot')
    plt.rcParams["figure.figsize"] = (10, 7)
    ax = sns.barplot(x='Algorithm', y='Accuracy', data=d)
    ax.set_title('Accuracy comparison')
    ax.set_ylabel('Accuracy')
    ax.set_ylim(80, 100)  # Adjust ylim if necessary

    # Save plot to a file
    plot_file = 'static/accuracy_plot.png'
    plt.savefig(plot_file)
    plt.close()  # Close the plot to free up resources

    return plot_file

@app.route('/plot')
def plot():
    
	plot_file = generate_plot()
	return render_template('plot.html', plot_file=plot_file)

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/feedback')
def feedback():
	return render_template('feedback.html')
    
# Route for the sign up page
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error='Username already exists!')

        # Hash the password before saving it to the database
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username  # Store the username in the session
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password!')
    return render_template('login.html')

@app.route('/predict',methods=['POST'])
def predict():
	AQI_predict = None
	if request.method == 'POST':
		# field1 = request.form['field1']
		AQI_predict=model.predict([[
			request.form["T"],
			request.form["TM"],
			request.form["Tm"],
			request.form["SLP"],
			request.form["H"],
			request.form["VV"],
			request.form["V"],
			request.form["VM"]
		]])    
	tt=''
	if float(AQI_predict)<=50:
		tt='GOOD'
	elif float(AQI_predict)>=51 and float(AQI_predict)<=100 :
		tt='Satisfactory'
	elif float(AQI_predict)>=101 and float(AQI_predict)<=200 :
		tt='Moderate'
	elif float(AQI_predict)>=201 and float(AQI_predict)<=300:
		tt='Poor'
	else:
		tt='very poor'
	return render_template('result.html', prediction=AQI_predict,t=tt)

if __name__=='__main__':
    db.create_all()  # Create the database tables
    app.run(debug=True)
