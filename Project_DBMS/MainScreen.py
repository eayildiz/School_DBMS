from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/loginRedirect", methods=['POST'])
def loginRedirect():
    username = request.form.get('username')
    password = request.form.get('password')

    # Veritabanına bağlan
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=LAPTOP-60KSG0K4;'  # Veritabanı sunucusunun adresini girin
        'DATABASE=School_Database;'
        'UID=emiralper;'  # Veritabanı kullanıcı adınızı girin
        'PWD=5312143589'   # Veritabanı şifrenizi girin
    )
    cursor = conn.cursor()

    # Öğrenci tablosunda kontrol et
    cursor.execute("SELECT Name FROM Student WHERE Student_ID = ? AND Password = ?", username, password)
    result = cursor.fetchone()

    if result:
        name = result[0]
        return redirect(url_for("studentInfo"), name=name)

    # Öğretmen tablosunda kontrol et
    cursor.execute("SELECT Name FROM Instructor WHERE Teaching_ID = ? AND Password = ?", username, password)
    result = cursor.fetchone()

    if result:
        name = result[0]
        return redirect(url_for("instructorInfo"),  name=name)

    # Kullanıcı bulunamadı, hata mesajı göster
    return "Kullanici adi veya şifre yanliş, lütfen tekrar deneyin."

#TODO We need to distinguish instructor and student log in. We'll check this during implementation of log in and sign up functions.
@app.route('/studentInf/<name>', methods =['GET', 'POST'])
def studentInfo(name):
    return render_template("student_general_info.html", name=name)

@app.route('/studentCourseProgram', methods =['GET', 'POST'])
def studentCourseProgram():
    return render_template("student_course_program.html")

@app.route('/studentNote', methods =['GET', 'POST'])
def studentNotes():
    return render_template("student_notes.html")

#TODO This will be use during issue #1.
@app.route('/instructorInfo/<name>', methods =['GET', 'POST'])
def instructorInfo(name):
    return render_template("instructor_general_info.html", name=name)

@app.route('/instructorCourseProgram', methods =['GET', 'POST'])
def instructorCourseProgram():
    return render_template("instructor_course_program.html")

@app.route('/instructorNote', methods =['GET', 'POST'])
def instructorNotes():
    return render_template("instructor_notes.html")

if __name__ == "__main__":
    app.run()