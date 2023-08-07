import random
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

#TODO We need to distinguish instructor and student log in. We'll check this during implementation of log in and sign up functions.
@app.route('/studentInfo', methods =['GET', 'POST'])
def studentInfo():
    name = request.form.get('signIn')
    rand = random.choice([True, False])
    print(rand)
    if(rand):
        return render_template("student_general_info.html", name=name)
    else:
        return render_template("instructor_general_info.html", name=name)

@app.route('/studentCourseProgram', methods =['GET', 'POST'])
def studentCourseProgram():
    return render_template("student_course_program.html")

@app.route('/studentNote', methods =['GET', 'POST'])
def studentNotes():
    return render_template("student_notes.html")

#TODO This will be use during issue #1.
@app.route('/instructorInfo', methods =['GET', 'POST'])
def instructorInfo():
    name = request.form.get('signIn')
    return render_template("instructor_general_info.html", name=name)

@app.route('/instructorCourseProgram', methods =['GET', 'POST'])
def instructorCourseProgram():
    return render_template("instructor_course_program.html")

if __name__ == "__main__":
    app.run()