from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import certifi
import os
from pymongo import MongoClient

# Load env vars
load_dotenv()

app = Flask(__name__)

if os.environ.get("FLASK_ENV") == "testing":
    mongo_uri = "mongodb://localhost:27017/test_student_db"
else:
    mongo_uri = os.environ.get("MONGO_URI")

app.config["MONGO_URI"] = mongo_uri
#app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/student_db")
app.secret_key = os.getenv("SECRET_KEY")

# Use certifi CA bundle explicitly for cross-platform TLS reliability
# (notably fixes common macOS certificate verification failures).
#mongo = PyMongo(app, tlsCAFile=certifi.where())
mongo = PyMongo(app)
#db = mongo.db  # This represents your database connection engine

client = MongoClient(mongo_uri)
db = client["student_db"] 

# Home page -> list students
@app.route('/')
def index():
    students = db.students.find()
    return render_template('index.html', students=students)

# Add student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        db.students.insert_one({
            "name": name,
            "email": email,
            "course": course
        })
        return redirect(url_for('index'))
    return render_template('add_student.html')

# Update student
@app.route('/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        new_course = request.form['course']
        mongo.db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"name": new_name, "email": new_email, "course": new_course}}
        )
        return redirect(url_for('index'))
    return render_template('update_student.html', student=student)


# Delete student
@app.route('/delete/<student_id>')
def delete_student(student_id):
    mongo.db.students.delete_one({"_id": ObjectId(student_id)})
    return redirect(url_for('index'))

# health check endpoint for deployment verification
@app.route('/health')
def health():
    try:
        # This checks if the MongoDB client can successfully ping/connect to the database
        # It serves as your deployment verification gate
        from pymongo import MongoClient
        import os
        
        # Pulls URI from environment variables securely
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/student_db")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping') 
        
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)


