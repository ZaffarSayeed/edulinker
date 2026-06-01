from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import flash, redirect, url_for
from flask import session
from urllib.parse import quote
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
# from app import app, db





app = Flask(__name__)

# Next line is for sqlite database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'



#postgres neon database configuration and sqlite database configuration for local
app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL")

if database_url:

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

else:
    database_url = "sqlite:///database.db"

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False






#email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'abbaszaffar.insha@gmail.com'
app.config['MAIL_PASSWORD'] = 'whjb hmbb bjaj gmui'
app.config['MAIL_USE_TLS'] = True
app.secret_key = "secret123"
mail = Mail(app)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)






db = SQLAlchemy(app)

# ------------------ DATABASE MODELS ------------------

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    location = db.Column(db.String(100))
    resume = db.Column(db.String(200))   # NEW
    agreement = db.Column(db.Boolean)    # NEW
    photo = db.Column(db.String(200))
    # password = db.Column(db.String(200)) #new

    # rating = db.Column(db.Float, default=4.0)




class StudentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    location = db.Column(db.String(100))
    agreement = db.Column(db.Boolean)   # NEW


class ConnectionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    student_phone = db.Column(db.String(20))
    teacher_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)


# we run it once when we change in database field
# @app.before_request
# def create_tables():
#     db.create_all()
with app.app_context():
    db.create_all()


# SIgnup form

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():

#     if request.method == 'POST':

#         hashed_password = generate_password_hash(request.form['password'])

#         teacher = Teacher(
#             name=request.form['name'],
#             email=request.form['email'],
#             phone=request.form['phone'],
#             password=hashed_password
#         )

#         db.session.add(teacher)
#         db.session.commit()

#         flash("Account Created Successfully")

#         return redirect('/login')

#     return render_template('signup.html')







# Create Login Route

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            return "Invalid Credentials"

    return render_template('login.html')


        # if request.method == 'POST':
        #         username = request.form['username']
        #         email = request.form['email']
        #         password = request.form['password']

        #         # 🔷 ADMIN LOGIN
        #         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

        #             session['admin_logged_in'] = True
        #             return redirect('/admin')

        #         # 🔷 TEACHER LOGIN
        #         teacher = Teacher.query.filter_by(email=email).first()

        #         if teacher and check_password_hash(teacher.password, password):

        #             session['teacher_id'] = teacher.id
        #             return redirect('/teacher-dashboard')

        #         flash("Invalid Login")
        #         return redirect('/login')

        # return render_template('login.html')






# ------------------ ROUTES ------------------

@app.route('/')
def home():
    teachers = Teacher.query.all()
    return render_template('home.html', teachers=teachers)
    


@app.route('/teacher', methods=['GET', 'POST'])
def teacher():

    if request.method == 'POST':
        
        name = request.form['name']
        phone = request.form['phone']
        subject = request.form['subject']
        location = request.form['location']

        # # 🔷 MULTI SUBJECT (IMPORTANT)
        # subjects = request.form.getlist('subjects')   # list
        # subjects_str = ", ".join(subjects)            # convert to string
        # subject=subjects_str

        # 🔷 Get uploaded file
        photo = request.files['photo']

        # 🔷 Secure filename
        filename = secure_filename(photo.filename)

        # 🔷 Save file to folder
        upload_path = os.path.join('static/uploads', filename)
        photo.save(upload_path)

        # 🔷 Save to database
        new_teacher = Teacher(
            name=name,
            phone=phone,
            subject=subject,
            location=location,
            photo=filename
        )

        db.session.add(new_teacher)
        db.session.commit()

        flash("Registered Successfully!", "success")

        return redirect(url_for('home'))

    return render_template('teacher_register.html')



# Redirect to Teacher Dashboard

# @app.route('/teacher-dashboard')
# def teacher_dashboard():

#     if not session.get('teacher_id'):
#         return redirect('/login')

#     teacher = Teacher.query.get(session['teacher_id'])

#     return render_template(
#         'teacher_dashboard.html',
#         teacher=teacher
#     )


# upload video route

# @app.route('/upload_video', methods=['POST'])
# def upload_video():

#     if not session.get('teacher_id'):
#         return redirect('/login')

#     video = request.files['video']

#     filename = secure_filename(video.filename)

#     video.save(os.path.join('static/videos', filename))

#     flash("Video Uploaded Successfully")

#     return redirect('/teacher-dashboard')



@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        name = request.form['name']

        email = request.form['email']

        subject = request.form['subject']

        message = request.form['message']

        # Save to database
        new_contact = Contact(

            name=name,
            email=email,
            subject=subject,
            message=message
        )

        db.session.add(new_contact)

        db.session.commit()

        flash("Message sent successfully!")

        return redirect('/contact')

    return render_template('contact.html')



@app.route('/teacher/<int:id>')
def teacher_profile(id):
    teacher = Teacher.query.get(id)
    return render_template('teacher_profile.html', teacher=teacher)





# Student Request
@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':

        if 'agreement' not in request.form:
            return "You must accept rules & regulations!"

        new_request = StudentRequest(
            name=request.form['name'],
            phone=request.form['phone'],
            subject=request.form['subject'],
            location=request.form['location'],
            agreement=True
        )

        db.session.add(new_request)
        db.session.commit()

        # 📧 Send Email
        msg = Message(
            "New Student Request",
            sender=app.config['MAIL_USERNAME'],
            recipients=['abbaszaffar.insha@gmail.com']   #admin mail id
        )
        msg.body = f"Student: {new_request.name}, Subject: {new_request.subject}"
        mail.send(msg)

        return "Request Submitted Successfully!"

    return render_template('student_request.html')

# Admin Panel
@app.route('/admin')
def admin():

    if not session.get('admin_logged_in'):
        return redirect('/login')

    teachers = Teacher.query.all()
    student_requests = StudentRequest.query.all()
    connection_requests = ConnectionRequest.query.all()

    teacher_map = {t.id: t for t in teachers}

    return render_template(
        'admin.html',
        teachers=teachers,
        student_requests=student_requests,
        connection_requests=connection_requests,
        teacher_map=teacher_map
    )


@app.route('/admin/requests')
def admin_requests():

    if not session.get('admin_logged_in'):
        return redirect('/login')

    requests = ConnectionRequest.query.all()
    teachers = Teacher.query.all()   
     
    teacher_map = {
    teacher.id: teacher
    for teacher in teachers
}

    return render_template(
        'admin_requests.html',
        requests=requests,
        teacher_map=teacher_map
    )

@app.route('/admin/teachers')
def admin_teachers():
    if not session.get('admin_logged_in'):
        return redirect('/login')

    teachers = Teacher.query.all()
    return render_template('admin_teachers.html', teachers=teachers)


@app.route('/admin/students')
def admin_students():
    if not session.get('admin_logged_in'):
        return redirect('/login')

    students = StudentRequest.query.all()
    return render_template('admin_students.html', students=students)


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/')



# Search bar 

@app.route('/search')
def search():
    subject = request.args.get('subject')
    location = request.args.get('location')

    # Filter teachers
    teachers = Teacher.query.filter(
        Teacher.subject.ilike(f"%{subject}%"),
        Teacher.location.ilike(f"%{location}%")
    ).all()

    return render_template('search_results.html', teachers=teachers)















# @app.route('/accept_request/<int:id>')
# def accept_request(id):
#     req = ConnectionRequest.query.get(id)
#     teacher = Teacher.query.get(req.teacher_id)

#     # Ensure country code
#     phone = teacher.phone
#     if not phone.startswith("91"):
#         phone = "91" + phone

#     message = f"""
# Hello {teacher.name},

# You have a new student request.

# Student Name: {req.student_name}
# Phone: {req.student_phone}


# """

#     whatsapp_url = f"https://wa.me/{phone}?text={quote(message)}"

#     req.status = "accepted"
#     db.session.commit()

#     return redirect(whatsapp_url)





# @app.route('/reject_request/<int:id>')
# def reject_request(id):
#     req = ConnectionRequest.query.get(id)
#     req.status = "rejected"
#     db.session.commit()
#     return redirect('/admin')



# @app.route('/delete_request/<int:id>')
# def delete_request(id):
#     request_data = StudentRequest.query.get_or_404(id)
#     db.session.delete(request_data)
#     db.session.commit()
#     flash("Request deleted successfully")
#     return redirect('/admin')


@app.route('/delete_request/<int:id>')
def delete_request(id):

    if not session.get('admin_logged_in'):
        return redirect('/login')

    request_record = ConnectionRequest.query.get(id)

    if request_record:
        db.session.delete(request_record)
        db.session.commit()
        flash("Request deleted successfully.", "success")
    else:
        flash("Request not found.", "warning")

    return redirect('/admin/requests')



@app.route('/approve_request/<int:id>')
def approve_request(id):

    req = ConnectionRequest.query.get(id)
    teacher = Teacher.query.get(req.teacher_id)

    # Save into StudentRequest table
    new_student = StudentRequest(
        name=req.student_name,
        phone=req.student_phone,
        subject=teacher.subject,
        location=teacher.location
    )

    db.session.add(new_student)

    # Update status
    req.status = "accepted"

    db.session.commit()

    return redirect('/admin/requests')



@app.route('/reject_request/<int:id>')
def reject_request(id):
    req = ConnectionRequest.query.get(id)
    req.status = "rejected"
    db.session.commit()

    return redirect('/admin/requests')



@app.route('/request_teacher/<int:teacher_id>', methods=['GET', 'POST'])
def request_teacher(teacher_id):
    # print("Request route working", teacher_id)
    # return "Working"
    if request.method == 'POST':
        new_request = ConnectionRequest(
            student_name=request.form['name'],
            student_phone=request.form['phone'],
            teacher_id=teacher_id
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Your request has been sent! We will confirm after approval.", "success")

        return redirect(url_for('home'))

    return render_template('request_form.html', teacher_id=teacher_id)


# @app.route('/delete_teacher/<int:id>')
# def delete_teacher(id):

#     teacher = Teacher.query.get_or_404(id)

#     # Delete related requests
#     StudentRequest.query.filter_by(
#         teacher_id=id
#     ).delete()

#     db.session.delete(teacher)

#     db.session.commit()

#     flash("Teacher deleted successfully")

#     return redirect('/admin/teachers')

@app.route('/delete_teacher/<int:id>')
def delete_teacher(id):

    teacher = Teacher.query.get(id)

    if teacher:

        # Delete uploaded files if they exist
        import os

        if teacher.photo:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], teacher.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)

        if getattr(teacher, 'resume', None):
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], teacher.resume)
            if os.path.exists(resume_path):
                os.remove(resume_path)

        # Delete related requests
        StudentRequest.query.filter_by(id=id).delete()

        db.session.delete(teacher)
        db.session.commit()

        flash("Teacher deleted successfully.", "success")

    else:
        flash("Teacher already deleted or not found.", "warning")

    return redirect('/admin/teachers')



# @app.route('/delete_student/<int:id>')
# def delete_student(id):
#     student = StudentRequest.query.get_or_404(id)
#     # Delete related requests
#     StudentRequest.query.filter_by(
#         student_id=id
#     ).delete()

#     db.session.delete(student)
#     db.session.commit()
#     flash("Student deleted successfully")
#     return redirect('/admin/students')

@app.route('/delete_student/<int:id>')
def delete_student(id):

    student = StudentRequest.query.get_or_404(id)

    if student:

        StudentRequest.query.filter_by(id=id).delete()

        db.session.delete(student)
        db.session.commit()

        flash("Student deleted successfully.", "success")

    else:
        flash("Student already deleted or not found.", "warning")

    return redirect('/admin/students')

# ------------------ RUN ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)











