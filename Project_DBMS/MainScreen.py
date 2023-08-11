from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

@app.route("/")
def main(err_message=""):
    return render_template("index.html")

@app.route("/loginRedirect", methods=['POST'])
def loginRedirect():
    username = request.form.get('username')
    password = request.form.get('password')
    print('----------')
    print(username)
    print(password)
    print('----')
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=lAPTOP-60KSG0K4;'  # Veritabanı sunucusunun adresini girin
            'DATABASE=School_Database;'
            'UID=emiralper;'  # Veritabanı kullanıcı adınızı girin
            'PWD=5312143589'   # Veritabanı şifrenizi girin
        )
        cursor = conn.cursor()
        # Bağlantı başarılı, devam edebilirsiniz
        print('Bağlandi')
    except pyodbc.Error as e:
        print("Veritabanina bağlanilamadi:", e)
        return "Veritabani hatasi, lütfen daha sonra tekrar deneyin."


    # İhtiyaca göre uygun bir hata yanıtı döndürebilirsiniz


    # Öğrenci tablosunda kontrol et
    cursor.execute("SELECT Name FROM Student WHERE Student_ID = ? AND Password = ?", (username, password))
    result = cursor.fetchone()

    print('result')
    print(result)
    
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
    return redirect(url_for("/"), err_message="Kullanici adi veya şifre yanliş, lütfen tekrar deneyin.")


@app.route('/studentInfo/<name>', methods =['GET', 'POST'])
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