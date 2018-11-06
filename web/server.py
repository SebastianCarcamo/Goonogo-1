import os
from os.path import join, dirname, realpath
from flask import Flask,render_template, request, session, Response ,redirect
from datetime import datetime
from database import connector
from sqlalchemy import or_
from model import entities
import json

app = Flask(__name__)

db = connector.Manager()
engine = db.createEngine()


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

#Page Loaders

@app.route('/')
def index():
    if 'logged_user_id' in session:
        return render_template('index.html', logged_in = True)
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/', code=302)

@app.route('/register')
def register():
    if 'logged_user_id' in session:
        return redirect('/', code=302)
    return render_template('register.html')

@app.route('/update_subjects')
def updatepage_subjects():
    if 'logged_user_id' in session:
        if session['logged_user_type'] == "teacher":
            return render_template("registerSubjects.html")
    return redirect('/',code=302)

@app.route('/current_user')
def current_user():
    db_session = db.getSession(engine)
    if session['logged_user_type'] == 'teacher':
        user = db_session.query(entities.Teacher).filter(entities.Teacher.id == session['logged_user_id']).first()
    else:
        user = db_session.query(entities.Student).filter(entities.Student.id == session['logged_user_id']).first()
    return Response(json.dumps(user,cls=connector.AlchemyEncoder),mimetype='application/json')


@app.route('/update')
def update():
    if 'logged_user_id' in session:
        if session['logged_user_type'] == 'teacher':
            return render_template("edit_perfil_profesor.html")
        return render_template("edit_perfil_estudiante.html")
    return redirect("/", code=302)


@app.route('/userAccount')
def userAccount():
    if session['logged_user_type'] == 'teacher':
        return redirect("/teacher_profile/"+str(session['logged_user_id']))
    return redirect("/student_profile/"+str(session['logged_user_id']))



################            Search engine        ##########################


@app.route('/search', methods=['POST'])
def search():
    data = request.form['searchbar']
    if 'logged_user_id' in session:
        return render_template("search_results.html", data = data, logged_user = True)
    return render_template("search_results.html", data = data)

@app.route('/search/teachers/<str>', methods=['GET'])
def search_teachers(str):
    db_session = db.getSession(engine);
    teachers = db_session.query(entities.Teacher).\
    filter(or_(entities.Teacher.name.like("%"+str+"%"), entities.Teacher.username.like("%"+str+"%")))

    data = teachers[:]

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/search/subjects/<str>', methods=['GET'])
def search_subjects(str):
    db_session = db.getSession(engine);
    subjects = db_session.query(entities.Subject).filter(entities.Subject.name.like("%"+str+"%"))

    data = subjects[:]

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/search/students/<str>', methods=['GET'])
def search_students(str):
    db_session = db.getSession(engine);
    students = db_session.query(entities.Student).\
    filter(or_(entities.Student.name.like("%"+str+"%"), entities.Student.username.like("%"+str+"%")))

    data = students[:]

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')


##########################################################################################





################            Load Profiles        ##########################

@app.route('/teacher_profile/<id>')
def teacher_profile(id):
    if 'logged_user_id' in session:
        logged_user = True
        if session['logged_user_type'] == "student":
             return render_template("perfil_profesor.html", teacher_id = id, student_profile = True, logged_user = logged_user)
        elif str(session['logged_user_id']) == str(id):
            return render_template("perfil_profesor.html", teacher_id = id, user_profile = True, logged_user = logged_user)
        else:
            return render_template("perfil_profesor.html", teacher_id = id,logged_user = logged_user)
    return render_template("perfil_profesor.html", teacher_id = id)

@app.route('/student_profile/<id>')
def student_profile(id):
    if 'logged_user_id' in session:
        logged_user = True
        if session['logged_user_type'] == "student" and str(session['logged_user_id']) == str(id):
             return render_template("student_profile.html", student_id = id,  logged_user = logged_user, user_profile = True,)
        else:
            return render_template("student_profile.html", student_id = id, logged_user = logged_user)
    return render_template("student_profile.html", student_id = id)

@app.route('/subject_profile/<id>')
def subject_profile(id):
    if 'logged_user_id' in session:
        return render_template("subject_profile.html", subject_id = id,  logged_user = True)
    return render_template("subject_profile.html", subject_id = id)

##########################################################################################




#Login

@app.route('/do_login', methods = ['POST'])
def do_login():

    username = request.form['username']
    password = request.form['password']

    db_session = db.getSession(engine)

    student = db_session.query(entities.Student).filter(entities.Student.username == username)
    teacher = db_session.query(entities.Teacher).filter(entities.Teacher.username == username)

    if teacher.count() != 0:
        if teacher[0].password == password:
            session['logged_user_id'] = teacher[0].id
            session['logged_user_type'] = "teacher"
            return redirect("/userAccount")
        return render_template("login.html", error = True)

    if student.count() != 0:
        if student[0].password == password:
            session['logged_user_id'] = student[0].id
            session['logged_user_type'] = "student"
            return redirect("/userAccount")

    return render_template("login.html", error = True)

#Students CRUD

@app.route('/students', methods = ['POST'])
def do_register():
    db_session = db.getSession(engine) 

    name = request.form['name']
    lastname = request.form['lastname']
    username = request.form['username']
    password = request.form['password']
    
    student = entities.Student(name = name, lastname = lastname, username = username, password = password)
    db_session.add(student)
    db_session.commit()

    return redirect('/userAccount', code=302)

@app.route('/students', methods=['GET'])
def students():
    db_session = db.getSession(engine)
    students = db_session.query(entities.Student)
    data = students[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/students/<id>', methods=['GET'])
def get_student(id):
    db_session = db.getSession(engine)
    students = db_session.query(entities.Student).filter(entities.Student.id == id)
    data = students[0]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json');

@app.route('/students/<id>', methods=['PUT'])
def update_student(id):
    db_session = db.getSession(engine)
    students = db_session.query(entities.Student).filter(entities.Student.id == id)
    for student in students:
        student.name = request.form['name']
        student.lastname = request.form['lastname']
        student.password = request.form['password']
        student.username = request.form['username']
        db_session.add(user)
    db_session.commit();
    return "user updated";

@app.route('/students/<id>', methods=['DELETE'])
def delete_student(id):
    db_session = db.getSession(engine)
    students = db_session.query(entities.Student).filter(entities.Student.id == id)
    for student in students:
        db_session.delete(student)
    db_session.commit();
    return "user deleted";

@app.route('/students/update', methods=['POST'])
def update_student_get():
    if 'logged_user_id' not in session:
        redirect('/', code=302)

    if session['logged_user_type'] != "student":
        redirect('/', code=302)

    db_session = db.getSession(engine)

    if request.json:
        content = request.get_json(silent=True)
    else:
        content = request.form

    name = content['name']
    lastname = content['lastname']
    
    students = db_session.query(entities.Student).filter(entities.Student.id == session['logged_user_id'])
    
    for student in students:
        student.name = name
        student.lastname = lastname
        db_session.add(student)
    db_session.commit()

    return redirect("/student_profile/"+ str(session['logged_user_id']))


@app.route('/clean_students')
def clean_users():
    db_session = db.getSession(engine)
    students = db_session.query(entities.Student)

    for student in students:
        db_session.delete(student)

    db_session.commit()
    return "Estudiantes Eliminados"




################            Teachers CRUD         ##########################

@app.route('/teachers', methods=['POST'])
def create_teacher(): 
    db_session = db.getSession(engine)

    if request.json:
        content = request.get_json(silent=True)
    else:
        content = request.form

    name = content['name']
    lastname = content['lastname']
    username = content['username']
    password = content['password']
    information = content['information']
    
    teacher = entities.Teacher(name = name, lastname = lastname, username = username, password = password, information=information, numRating = 0, sumRating = 0)
    
    db_session.add(teacher)
    db_session.commit()

    session['logged_user_id'] = teacher.id;
    session['logged_user_type'] = "teacher";

    return render_template("registerSubjects.html")

@app.route('/teachers', methods=['GET'])
def get_teachers(): 
    db_session = db.getSession(engine)
    teachers = db_session.query(entities.Teacher)
    data = teachers[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/teachers/<id>', methods=['GET'])
def get_teacher(id): 
    db_session = db.getSession(engine)
    data = db_session.query(entities.Teacher).filter(entities.Teacher.id == id).first();
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/teachers/update', methods=['POST'])
def update_teacher(): 
    db_session = db.getSession(engine)

    if request.json:
        content = request.get_json(silent=True)
    else:
        content = request.form

    name = content['name']
    lastname = content['lastname']
    information = content['information']
    
    teachers = db_session.query(entities.Teacher).filter(entities.Teacher.id == session['logged_user_id'])
    
    for teacher in teachers:
        teacher.name = name
        teacher.information = information
        teacher.lastname = lastname
        db_session.add(teacher)
        db_session.commit()

    return redirect("/teacher_profile/"+ str(session['logged_user_id']))

############################################################################


@app.route('/users/<str>', methods=['GET'])
def get_users_username(str):
    db_session = db.getSession(engine)
    teachers = db_session.query(entities.Teacher).filter(entities.Teacher.username == str)
    students = db_session.query(entities.Student).filter(entities.Student.username == str)
    data = {'teacher' : (teachers.count() == 0), 'student' : (students.count() == 0)}
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')





################            Subjects CRUD         ##########################

@app.route('/subjects', methods=['POST'])
def create_subject():
    content = request.get_json(silent=True)
    name = content['name']
    summary = content['summary']

    subject = entities.Subject(name = name, summary=summary)
    db_session = db.getSession(engine)
    db_session.add(subject)
    db_session.commit()
    return "TODO OK"

@app.route('/subjects', methods=['GET'])
def get_subjects():
    db_session = db.getSession(engine)
    subjects = db_session.query(entities.Subject)
    data = subjects[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/subjects/<id>', methods=['GET'])
def get_subject(id):
    db_session = db.getSession(engine)
    data = db_session.query(entities.Subject).filter(entities.Subject.id == id).first()
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/subjects/<id>', methods=['PUT'])
def update_subject(id):
    db_session = db.getSession(engine)
    subjects = db_session.query(entities.Subject).filter(entities.Subject.id == id)
    content =  json.loads(request.form['values'])
    for subject in subjects:
        subject.name = content['name']
        subject.summary = content['summary']
        db_session.add(subject)
    db_session.commit()
    return "TODO OK"

@app.route('/subjects/<id>', methods=['DELETE'])
def delete_subject(id):
    db_session = db.getSession(engine)
    subjects = db_session.query(entities.Subject).filter(entities.Subject.id == id)
    for subject in subjects:
        db_session.delete(subject)
    db_session.commit()
    return "TODO OK"

####################################################################################



################            Teacher_Subjects CRUD         ##########################

@app.route('/teacher_subject', methods=['POST'])
def create_teacher_subject():
    db_session = db.getSession(engine)
    content = request.get_json(silent=True)
    teacher = db_session.query(entities.Teacher).filter(entities.Teacher.id == content['teacher_id']).first()
    subject = db_session.query(entities.Subject).filter(entities.Subject.id == content['subject_id']).first()
    t_s = entities.Teacher_Subject(teacher=teacher, subject=subject)
    db_session.add(t_s)
    db_session.commit()
    return "todo ok"

@app.route('/teacher_subject', methods=['GET'])
def get_teacher_subjects():
    db_session = db.getSession(engine)
    teacher_subjects = db_session.query(entities.Teacher_Subject)
    data = teacher_subjects[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/teacher_subject/teacher/<id>', methods=['GET'])
def get_teacher_subject_teacher(id):
    db_session = db.getSession(engine)
    teacher_subjects = db_session.query(entities.Teacher_Subject).filter(entities.Teacher_Subject.teacher_id == id)
    subject_ids = []
    for subject in teacher_subjects:
        subject_ids.append(subject.subject_id)
    data = db_session.query(entities.Subject).filter(entities.Subject.id.in_(subject_ids)).all()
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/teacher_subject/subject/<id>', methods=['GET'])
def get_teacher_subject_subject(id):
    db_session = db.getSession(engine)
    teacher_subjects = db_session.query(entities.Teacher_Subject).filter(entities.Teacher_Subject.subject_id == id)
    teacher_ids = []
    for teacher in teacher_subjects:
        teacher_ids.append(teacher.teacher_id)
    data = db_session.query(entities.Teacher).filter(entities.Teacher.id.in_(teacher_ids)).all()
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')


@app.route('/clean_teacher_subject', methods=['DELETE'])
def clean_t_s():
    db_session = db.getSession(engine)
    teacher_subjects = db_session.query(entities.Teacher_Subject).filter(entities.Teacher_Subject.teacher_id == session['logged_user_id'])
    for ts in teacher_subjects:
        db_session.delete(ts)
    db_session.commit()
    return "Listo"

####################################################################################




################            Ratings CRUD         ##########################

@app.route('/ratings/<teacher_id>', methods=['POST'])
def create_rating(teacher_id): 
    db_session = db.getSession(engine)

    if request.json:
        c = request.get_json(silent=True)
    else:
        c = request.form

    content = c['content']
    title = c['title']
    value = int(c['value'])
    teacher = db_session.query(entities.Teacher).filter(entities.Teacher.id == teacher_id).first()
    student = db_session.query(entities.Student).filter(entities.Student.id == session["logged_user_id"]).first()

    ratings = db_session.query(entities.Rating).\
    filter(entities.Rating.student_id == session['logged_user_id']).\
    filter(entities.Rating.teacher_id == teacher_id)
    
    if ratings.count() != 0 :
        for rating in ratings:
            rating.title = title
            rating.content = content
            rating.teacher = teacher
            rating.student = student
            teacher.sumRating = teacher.sumRating - rating.value + value
            rating.value = value
            db_session.add(rating)
            db_session.add(teacher)
            db_session.commit()
        return redirect('/teacher_profile/'+teacher_id, code=302)
    
    rating = entities.Rating(title=title, content=content, teacher=teacher, student=student, value = value)
    teacher.numRating += 1;
    teacher.sumRating += value;
    db_session.add(rating)
    db_session.add(teacher)
    db_session.commit()
    return redirect('/teacher_profile/'+teacher_id, code=302)

@app.route('/ratings/teacher/<id>', methods=['GET'])
def get_ratings_teacher(id): 
    db_session = db.getSession(engine)
    data = db_session.query(entities.Rating).filter(entities.Rating.teacher_id == id).all();
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/ratings/student/<id>', methods=['GET'])
def get_ratings_student(id): 
    db_session = db.getSession(engine)
    data = db_session.query(entities.Rating).filter(entities.Rating.student_id == id).all();
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')



####################################################################################


####################            Uploads         ####################################

@app.route('/upload_profile_pic', methods=['POST'])
def upload_picture():
    if 'logged_user_id' not in session:
        return redirect('/', code=302)

    app.config['UPLOAD_FOLDER'] = '/Users/Jorgefiestas/Desktop/Proyecto DBP/web/static/images/profile_pictures/'+session['logged_user_type']
    filename = str(session['logged_user_id'])
    image = request.files['image']

    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/userAccount',code=302)



####################################################################################


@app.route('/clean_teachers')
def clean_teachers():
    db_session = db.getSession(engine)
    teachers = db_session.query(entities.Teacher)

    for teacher in teachers:
        db_session.delete(teacher)

    db_session.commit()
    return "Profesores Eliminados"




if __name__ == '__main__':
    app.secret_key = "123456789"
    app.run(port=8080, threaded=True, host=('0.0.0.0'))
