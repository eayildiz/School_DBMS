from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route('/studentInfo', methods =['GET', 'POST'])
def studentInfo():
    name = request.form.get('signIn')
    return render_template("student_general_info.html", name=name)

if __name__ == "__main__":
    app.run()