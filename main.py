
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, ValidationError
import sqlite3


# ==========================================
# 1. CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(title="Student Management System")


# ==========================================
# 2. CONFIGURE TEMPLATES AND STATIC FILES
# ==========================================

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static", check_dir=False),
    name="static"
)


# ==========================================
# 3. STUDENT MODEL
# ==========================================

class Student(BaseModel):

    name: str
    age: int = Field(ge=18, le=60)
    gender: str
    marks: int = Field(ge=0, le=100)
    course: str
    image: str = ""
    status: int = Field(ge=0, le=1)


# ==========================================
# 4. DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect("students.db")

    return connection


# ==========================================
# 5. CREATE STUDENT TABLE
# ==========================================

def create_table():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        q = """
        CREATE TABLE IF NOT EXISTS students(

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            marks INTEGER,
            course TEXT,
            image TEXT,
            status INTEGER

        )
        """

        cursor.execute(q)

        connection.commit()

    finally:

        connection.close()


create_table()


# ==========================================
# 6. HOME PAGE - VIEW ALL STUDENTS
# ==========================================

@app.get("/")
def home(req: Request):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        q = "SELECT * FROM students"

        cursor.execute(q)

        students = cursor.fetchall()

    finally:

        connection.close()

    return templates.TemplateResponse(
        request=req,
        name="home.html",
        context={"stds": students}
    )


# ==========================================
# 7. DISPLAY ADD STUDENT FORM
# ==========================================

@app.get("/students/add")
def send_std_form(req: Request):

    return templates.TemplateResponse(
        request=req,
        name="add-student.html",
        context={}
    )


# ==========================================
# 8. ADD NEW STUDENT
# ==========================================

@app.post("/students/add")
def create_std(

    name: str = Form(),
    age: int = Form(),
    gender: str = Form(),
    marks: int = Form(),
    course: str = Form(),
    image: str = Form(""),
    status: int = Form()

):

    try:

        student = Student(

            name=name,
            age=age,
            gender=gender,
            marks=marks,
            course=course,
            image=image,
            status=status

        )

    except ValidationError as error:

        raise HTTPException(
            status_code=422,
            detail=error.errors()
        )

    values = (

        student.name,
        student.age,
        student.gender,
        student.marks,
        student.course,
        student.image,
        student.status

    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        q = """
        INSERT INTO students
        (name, age, gender, marks, course, image, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(q, values)

        connection.commit()

    finally:

        connection.close()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ==========================================
# 9. VIEW INDIVIDUAL STUDENT DETAILS
# ==========================================

@app.get("/students/view/{student_id}")
def view_student(student_id: int, req: Request):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        q = "SELECT * FROM students WHERE id = ?"

        cursor.execute(q, (student_id,))

        student = cursor.fetchone()

    finally:

        connection.close()

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return templates.TemplateResponse(
        request=req,
        name="view-student.html",
        context={"student": student}
    )


# ==========================================
# 10. DISPLAY UPDATE STUDENT FORM
# ==========================================

@app.get("/students/update/{student_id}")
def show_update_form(student_id: int, req: Request):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        q = "SELECT * FROM students WHERE id = ?"

        cursor.execute(q, (student_id,))

        student = cursor.fetchone()

    finally:

        connection.close()

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return templates.TemplateResponse(
        request=req,
        name="update-student.html",
        context={"student": student}
    )


# ==========================================
# 11. UPDATE STUDENT DETAILS
# ==========================================

@app.post("/students/update/{student_id}")
def update_student(

    student_id: int,
    name: str = Form(),
    age: int = Form(),
    gender: str = Form(),
    marks: int = Form(),
    course: str = Form(),
    image: str = Form(""),
    status: int = Form()

):

    try:

        student = Student(

            name=name,
            age=age,
            gender=gender,
            marks=marks,
            course=course,
            image=image,
            status=status

        )

    except ValidationError as error:

        raise HTTPException(
            status_code=422,
            detail=error.errors()
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        q = """
        UPDATE students
        SET
            name = ?,
            age = ?,
            gender = ?,
            marks = ?,
            course = ?,
            image = ?,
            status = ?
        WHERE id = ?
        """

        values = (

            student.name,
            student.age,
            student.gender,
            student.marks,
            student.course,
            student.image,
            student.status,
            student_id

        )

        cursor.execute(q, values)

        connection.commit()

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

    finally:

        connection.close()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ==========================================
# 12. DELETE STUDENT
# ==========================================

@app.post("/students/delete/{student_id}")
def delete_student(student_id: int):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        q = "DELETE FROM students WHERE id = ?"

        cursor.execute(q, (student_id,))

        connection.commit()

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

    finally:

        connection.close()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ==========================================
# END OF STUDENT MANAGEMENT SYSTEM
# ==========================================
