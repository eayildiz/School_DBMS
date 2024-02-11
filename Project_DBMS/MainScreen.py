from flask import Flask, render_template, request, redirect, url_for, g, session, sessions
import pyodbc
from flask import jsonify

app = Flask(__name__)
app.secret_key = "emiralialper123"
app.config["SESSION_PERMANENT"] = False


#Her istek öncesi çalışacak bir fonksiyon oluşturduk:
@app.before_request
def before_request_function():
    if 'db_conn' not in g:
        g.db_conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=lAPTOP-60KSG0K4;'
            'DATABASE=School_Database;'
            'UID=emiralper;'
            'PWD=5312143589'
        )

#İstek sonrası bağlantıyı kapatmak için:
@app.teardown_request
def teardown_request(exception):
    db_conn = g.pop('db_conn', None)

    if db_conn is not None:
        db_conn.close()



@app.route("/", methods=['GET', 'POST'])
def main():
    err_message = request.args.get('err_message', '')
    return render_template("index.html", err_message=err_message)

######################################################LOGIN DIRECT##################################################
@app.route("/loginRedirect", methods=['POST'])
def loginRedirect():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username.isdigit():
        return redirect(url_for("main", err_message="Kullanici adi sadece sayısal değer olmalıdır. Lütfen tekrar deneyin."))
    

    cursor = g.db_conn.cursor()


    # Öğrenci tablosunda kontrol et
    cursor.execute("SELECT Student_ID FROM Student WHERE Student_ID = ? AND Password = ?", (username, password))
    result = cursor.fetchone()

    print('result')
    
    if result:
        session['ID'] = result[0] 
        print(session['ID'],session.get('ID'))
        return redirect(url_for("studentInfo"))

    # Öğretmen tablosunda kontrol et
    cursor.execute("SELECT Teaching_ID FROM Instructor WHERE Teaching_ID = ? AND Password = ?", (username, password))

    result = cursor.fetchone()

    if result:
        session['ID'] = result[0]
        return redirect(url_for("instructorInfo"))

    # Kullanıcı bulunamadı, hata mesajı göster
    return redirect(url_for("main", err_message="Kullanici adi veya şifre yanliş, lütfen tekrar deneyin."))



######################################################STUDENT INFO##################################################
@app.route('/studentInfo', methods =['GET', 'POST'])
def studentInfo():

    cursor = g.db_conn.cursor()

    cursor.execute("SELECT Student_ID, E_mail, Grade, GNO, Active_Status, Register_Date FROM Student WHERE Student_ID = ?", (session['ID']))
    student_data = cursor.fetchone()

    return render_template("student_general_info.html", 
                           studentID=student_data[0], 
                           email=student_data[1], 
                           grade=student_data[2],
                           GNO=student_data[3],
                           activeStat=student_data[4],
                           regYear=student_data[5])    


###################################################### STUDENT COURSE PROGRAM ##################################################
@app.route('/studentCourseProgram', methods=['GET'])
def studentCourseProgram():
    cursor = g.db_conn.cursor()
    
    # Öğrencinin aldığı derslerin ID'lerini al
    cursor.execute("SELECT C_ID FROM Students_Enrolls_Course WHERE S_ID = ?", (session['ID']))
    enrolled_courses_ids = [row[0] for row in cursor.fetchall()]

    # Öğrencinin aldığı derslerin adları ve bu derslere karşılık gelen gün ve saat bilgilerini al
    query = """
    SELECT days_of_course.Hour, days_of_course.Day, Course.Course_Name
    FROM Course
    JOIN days_of_course ON Course.Course_ID = days_of_course.Course_ID
    WHERE Course.Course_ID IN ({})
    """.format(', '.join('?' for _ in enrolled_courses_ids))

    cursor.execute(query, enrolled_courses_ids)
    course_details = cursor.fetchall()

    course_details_oneD = []
    course_names = []
    for detail in course_details:
        hour, day, course_name = detail
        course_details_oneD.extend([hour, day])
        course_names.append(course_name)

    return render_template("student_course_program.html", course_details_oneD=course_details_oneD, course_names=course_names)




######################################################STUDENT NOTES##################################################
@app.route('/studentNote', methods=['GET', 'POST'])
def studentNotes():
    cursor = g.db_conn.cursor()

    student_id = session.get('ID')  # This part seems to retrieve the student ID correctly.

    query = """
    SELECT Course.Course_Name, Students_Grade.Grade
    FROM Course
    JOIN Students_Grade ON Course.Course_ID = Students_Grade.Course_ID
    WHERE Students_Grade.Students_ID = ?
    """

    cursor.execute(query, (student_id,))
    courses_and_notes = cursor.fetchall()

    return render_template("student_notes.html", courses_and_notes=courses_and_notes)


######################################################STUDENT COURSE SELECTION##################################################


@app.route('/sCourseSelection', methods=['GET', 'POST'])
def studentCourseSelection():
    cursor = g.db_conn.cursor()

    student_id = session.get('ID')  # Öğrenci ID'sini oturumdan al.

    # Öğrencinin seçebileceği dersleri sorgula.
    # Öğrencinin şu an kayıtlı olmadığı dersleri listeleyelim.
    query = """
    SELECT Course_ID, Course_Name 
    FROM Course 
    WHERE Course_ID NOT IN (
        SELECT C_ID FROM Students_Enrolls_Course WHERE S_ID = ?
    )
    """
    cursor.execute(query, (student_id))
    available_courses = cursor.fetchall()


    print(available_courses)
    return render_template("student_course_selection.html", available_courses=available_courses)

######################################################ADDING COURSE##################################################
@app.route('/add_courses', methods=['POST'])
def add_courses():
    try:
        courses = request.json.get('courses', [])
        student_id = session.get('ID')
        
        if not student_id:
            return jsonify({"message": "Öğrenci ID'si bulunamadı!"}), 400

        cursor = g.db_conn.cursor()
        for course_id in courses:
            query = "INSERT INTO Students_Enrolls_Course (S_ID, C_ID) VALUES (?, ?)"
            cursor.execute(query, (student_id, course_id))

        g.db_conn.commit()

        return jsonify({"message": "Dersler başarıyla eklendi!"})

    except Exception as e:
        print(e)
        return jsonify({"message": "Bir hata oluştu!"}), 500



######################################################STUDENT EXAMS##################################################
@app.route('/studentExams', methods=['GET', 'POST'])
def studentExams():
    cursor = g.db_conn.cursor()

    student_id = session.get('ID')  # Öğrenci ID'sini oturumdan al.

    # Öğrencinin aldığı derslerin sınav tarihlerini sorgula.
    query = """
        SELECT
            c.Course_Name,
            ed.Date_and_Hour
        FROM
            Students_Enrolls_Course as sec
        JOIN
            Course c ON c.Course_ID = sec.C_ID
        JOIN
            Exam_Dates ed ON ed.Course_ID = sec.C_ID
        WHERE
            sec.S_ID = ?
        ORDER BY
            ed.Date_and_Hour;

    """
    cursor.execute(query, (student_id,))
    exams_and_dates = cursor.fetchall()

    return render_template("student_exams.html", exams_and_dates=exams_and_dates)


######################################################INSTRUCTOR INFO##################################################
#TODO This will be use during issue #1.
@app.route('/instructorInfo', methods =['GET', 'POST'])
def instructorInfo():
    try:

        # Veritabanı bağlantısını kurma
        cursor = g.db_conn.cursor()

        # İlgili öğretmenin bilgilerini sorgulama
        query = "SELECT Name,Teaching_ID, E_Mail, Office_Number FROM Instructor WHERE Teaching_ID = ?"
        cursor.execute(query, (session['ID']))
        result = cursor.fetchone()

        if result:
            name=result[0]
            instructor_id = result[1]
            email = result[2]
            office_no = result[3]
        else:
            result="NULL"
            instructor_id = "NULL"
            email = "NULL"
            office_no = "NULL"

    except pyodbc.Error as e:
        print("Veritabanı hatası:", e)
        return "Veritabanı hatası, lütfen daha sonra tekrar deneyin."

    finally:
        cursor.close()
        

    # Bu bilgileri template'e gönderme
    return render_template("instructor_general_info.html", name=name, instructor_id=instructor_id, email=email, office_no=office_no)




@app.route('/instructorCourseProgram', methods =['GET', 'POST'])
def instructorCourseProgram():
    cursor = g.db_conn.cursor()
    
    # Öğrencinin aldığı derslerin ID'lerini al
    cursor.execute("SELECT C_ID FROM Instructor_Gives_Courses WHERE I_ID = ?", (session['ID']))
    given_courses_ids = [row[0] for row in cursor.fetchall()]

    # Öğrencinin aldığı derslerin adları ve bu derslere karşılık gelen gün ve saat bilgilerini al
    query = """
    SELECT days_of_course.Hour, days_of_course.Day, Course.Course_Name
    FROM Course
    JOIN days_of_course ON Course.Course_ID = days_of_course.Course_ID
    WHERE Course.Course_ID IN ({})
    """.format(', '.join('?' for _ in given_courses_ids))

    cursor.execute(query, given_courses_ids)
    course_details = cursor.fetchall()

    course_details_oneD = []
    course_names = []
    for detail in course_details:
        hour, day, course_name = detail
        course_details_oneD.append(hour)
        course_details_oneD.append(day)
        course_names.append(course_name)

    print(course_details_oneD)
    print(course_names)
    return render_template("instructor_course_program.html", course_details_oneD=course_details_oneD, course_names=course_names)


######################################################INSTRUCTOR NOTEE##################################################
@app.route('/instructorNote', methods=['GET', 'POST'])
def instructorNotes():
    instructor_id = session.get('ID')
    cursor = g.db_conn.cursor()

    # Öğretmenin verdiği dersleri sorgulayan SQL ifadesi
    cursor.execute("""
        SELECT Course.Course_ID, Course.Course_Name 
        FROM Course 
        JOIN Instructor_Gives_Courses ON Course.Course_ID = Instructor_Gives_Courses.C_ID
        WHERE Instructor_Gives_Courses.I_ID = ?
    """, (instructor_id,))
    
    courses = cursor.fetchall()

    return render_template('instructor_notes.html', instructor_courses=courses)

######################################################GET STUDENTS FOR COURSE ##################################################
@app.route('/get_students/<course_id>')
def get_students_for_course(course_id):
    cursor = g.db_conn.cursor()
    cursor.execute("""
    SELECT s.Student_ID, s.Name, sg.Grade 
    FROM Student s
    JOIN Students_Enrolls_Course sec ON s.Student_ID = sec.S_ID
    LEFT JOIN Students_Grade sg ON s.Student_ID = sg.Students_ID AND sg.Course_ID = ?
    WHERE sec.C_ID = ?
    """, (course_id, course_id))

    # Decimal tipindeki veriyi float tipine dönüştürüyoruz.
    students = [{"id": row[0], "name": row[1], "grade": float(row[2]) if row[2] else None} for row in cursor.fetchall()]

    return jsonify({"students": students})

######################################################INSTRUCTOR EXAMS##################################################
@app.route('/Instructor_Courses', methods=['GET', 'POST'])
def instructorExams():
    cursor = g.db_conn.cursor()

    instructor_id = session.get('ID')  # Instructor ID'sini oturumdan al.

    query = """
        SELECT
            c.Course_Name,
            ed.Date_and_Hour
        FROM
            Instructor_Gives_Courses as igc
        JOIN
            Course c ON c.Course_ID = igc.C_ID
        JOIN
            Exam_Dates ed ON ed.Course_ID = igc.C_ID
        WHERE
            igc.I_ID = ?
        ORDER BY
            ed.Date_and_Hour;
    """
    cursor.execute(query, (instructor_id,))
    exams_and_dates = cursor.fetchall()

    return render_template("instructor_courses.html", exams_and_dates=exams_and_dates)





@app.route('/logout')
def logout():
    #session.pop('ID', None)  # Oturumdan öğrenci ID'sini kaldırın
    session.clear()
    return redirect(url_for('main'))

if __name__== "__main__":
    app.run() 