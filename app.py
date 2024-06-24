from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import ObjectId
import pymongo
import logging
import django
from functools import wraps
from smtplib import SMTPException
from flask_mail import Mail, Message # type: ignore
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#import bcrypt

# Define connection logic outside the app (replace with your details)
connection_string = "mongodb://programacionprofesional-bd:4tV0kEUB8soYIMA91Gre4WTptnY7xZRm8fskR7HnUolcq1ZflgdvqdxyCW90e1MtSV7UeO97Zf8nACDbykOBLQ%3D%3D@programacionprofesional-bd.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@programacionprofesional-bd@"  # Your actual connection string
client = pymongo.MongoClient(connection_string)
db = client["Login"]
collection = db["test1"]
app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG) 
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_users(type):#CHECK
  cursor = collection.find({"RoleKeyDB": str(type)})
  users=[]
  # Iterate through the documents and print them
  for document in cursor:
    users.append(document)
  return users

def email(receiver_email,subject,body):#CHECK
    # SMTP Server Configuration
    smtp_server = "smtp.office365.com"  # Replace with your SMTP server
    smtp_port = 587  # Replace with your SMTP port, usually 587 for TLS
    sender_email = "ACCprograpro@outlook.com"  # Replace with your email address
    sender_password = "PatronCenzano"  # Replace with your email account password

    # Create the email content
    subject = "Test Email from Python"
    body = "This is a test email sent from a Python script!"

    # Create a MIMEMultipart object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the email body to the MIMEMultipart object
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)  # Log in to the server

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")

    finally:
        # Close the connection to the server
        server.quit()



@app.route("/Login", methods=["POST"])#CHECK
def login():
  try:
    # Get user credentials from request JSON
    user_data = request.json
    username = user_data["user"]
    password = user_data["password"]
    user_type = user_data["key"]

    lista=get_users(user_type)
    # Implement logic to validate credentials against your user database (e.g., MongoDB)
    for index in lista:
      if index["EmailDB"]==username and index["PasswordDB"] == password:
        app.logger.info(f"The user: {username}, has login in page {index['PageDB']}")
        return jsonify({"message": "Login successful", "PageDB": index['PageDB']}), 200  #retornar también la página
    return jsonify({"message": "Login failed"}), 401
  except Exception as e:
    app.logger.error(f"Login fail for {username}")
    return jsonify({"message": f"Error: {str(e)}"}), 500  # Internal Server Error
  
@app.route("/pages", methods=["POST"])#CHECK
def save_page(): #función utilizada para cuando el usuario cierre sesión y se reciba en qué página se encontraba
    try:
        user_data = request.json
        username = user_data["user"]
        page = user_data["page"]
        user = collection.find_one({"EmailDB": username})
        if user:
            collection.update_one({"EmailDB": username}, {"$set": {"PageDB": page}})
            return jsonify({"message": "Page updated"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500  # Internal Server Error

@app.route("/Signup", methods=["POST"])#CHECK
def create_user():
  try:
    if request.json["key"] == "1":
      user_data = {
          "FirstName": request.json["name"],
          "EmailDB": request.json["user"],
          "PasswordDB": request.json["password"],
          "RoleKeyDB": request.json["key"],
          "Generation": request.json["generation"],
          "Specialty": request.json["specialty"],
          "Evaluation1": 0,
          "Evaluation2": 0,
          "Evaluation3": 0,
          "Internship": "NA",
          "InternshipProject": "NA",
          "AssignedTeacher": "NA",
          "FinalGrade": 0,
          "PageDB": 0,
          "CompanyGrade1":0,
          "CompanyGrade2":0,
          "CompanyGrade3":0,
          "CompanyGrade": 0,
          "Meeting": "False",
          "Approval": "False",
          "AdminApproval": "False",
          "InternshipApproval": "False",
          "FinalPresentation": "NA",
          "FinalPresentationGrade": 0
      }
    elif request.json["key"] == "2":
        user_data = {
            "FirstName": request.json["name"],
            "EmailDB": request.json["user"],
            "PasswordDB": request.json["password"],
            "RoleKeyDB": request.json["key"],
            "Specialty": request.json["specialty"],
            "PageDB": "0",
            "AssignedStudents": "null"
        }
    elif request.json["key"] == "3":
        user_data = {
            "FirstName": request.json["name"],
            "EmailDB": request.json["user"],
            "PasswordDB": request.json["password"],
            "PageDB": "0",
            "RoleKeyDB": request.json["key"],
        }
    elif request.json["key"] == "4":
        user_data = {
            "FirstName": request.json["name"],
            "EmailDB": request.json["user"],
            "PasswordDB": request.json["password"],
            "RoleKeyDB": request.json["key"],
            "Specialty": request.json["specialty"],
            "PageDB": "0",
        }
    user = collection.insert_one(user_data)
    app.logger.debug(f"{user.inserted_id} has been created")
    return jsonify(id=str(user.inserted_id), message="User created successfully.")
  except Exception as e:
    return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/save_internship", methods=["POST"])#CHECK
def internship():
  try:
    data = request.json
    username = data["user"]  # User's email address
    company_name = data["company"]  # Company's name
    industry = data["industry"]  # Company's industry
    country = data["country"]  # Company's country
    city = data["city"]  # Company's city

    # Create supervisor information dictionary
    supervisor_data = {
        "SupervisorName": data["name_sup"],
        "SupervisorEmail": data["email_sup"],
        "SupervisorTitle": data["title_sup"],
        "SupervisorPhone": data["phone_sup"]
    }
    student_data = {
        "StudentName": data["name_alum"],
    }
    # Extract internship details
    internship_hours = data["hours"]  # Number of internship hours
    internship_type = data["type"]  # Internship type (e.g., full-time, part-time)
    start_date = data["start"]  # Internship start date
    end_date = data["end"]  # Internship end date

    # Create internship data dictionary
    internship_data = {
        "CompanyName": company_name,
        "CompanyIndustry": industry,
        "CompanyCountry": country,
        "CompanyCity": city,
        "SupervisorInformation": supervisor_data,
        "StudentInformation": student_data,
        "InternshipHours": internship_hours,
        "InternshipType": internship_type,
        "StartDate": start_date,
        "EndDate": end_date
    }

    # Find the user's document in the MongoDB collection
    user = collection.find_one({"EmailDB": username})

    # Update the user's document if it exists
    if user:
        collection.update_one({"EmailDB": username}, {"$set": {"Internship": internship_data}})
        subject = "Internship Confirmation"
        body = f"Hello {user['FirstName']},\n\nYour internship details have been successfully saved.\n\nCompany Name: {company_name}\nCompany Industry: {industry}\nCompany Country: {country}\nCompany City: {city}\n\nSupervisor Information:\nName: {supervisor_data['SupervisorName']}\nEmail: {supervisor_data['SupervisorEmail']}\nTitle: {supervisor_data['SupervisorTitle']}\nPhone: {supervisor_data['SupervisorPhone']}\n\nStudent Information:\nName: {student_data['StudentName']}\n\nInternship Hours: {internship_hours}\nInternship Type: {internship_type}\nStart Date: {start_date}\nEnd Date: {end_date}\n\nBest regards,\nPrograPro Team"
        email(user["EmailDB"],subject,body)
        return jsonify({"message": "Internship saved"}), 200
    else:
        return jsonify({"message": "Internship not saved"}), 401
    #guardar en la base de datos y luego mandar un mensaje al frontend con la nota final
  except Exception as e:
      return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/save_proyect_internship", methods=["POST"])#NOT CHECK
def proyect():
    try:
        dato = request.json
        # Supongamos que 'dato' es el diccionario con los datos de entrada.
        username = dato["user"]
        project_name = dato["proyect_name"]
        project_details = dato["proyect_details"]
        project_participation = dato["proyect_participation"]
        project_specialty = dato["project_specialty"]
        student_data = collection.find_one({"EmailDB": username})

        # Búsqueda del profesor con la especialidad específica, ordenado por el tamaño de 'AlumnosAsignados'
            # Fetch all professors with the specific specialty
        professors = list(collection.find({"RoleKeyDB": str(2), "Specialty": project_specialty}))

        # Sort professors by the number of assigned students
        professors_sorted = sorted(professors, key=lambda prof: len(prof.get("AssignedStudents", [])))
        # Verificar si se encontró al menos un profesor
        if professors_sorted:
            # Seleccionar el primer profesor del cursor
            first_professor = professors_sorted[0]

            # Crear el diccionario del profesor
            dict_professor = {
                "EmailDB": first_professor["EmailDB"],
                "FirstName": first_professor["FirstName"],
            }
            
            dict_student = {
                "StudentName": student_data["FirstName"],
                "StudentMail": username,
                "Pages": student_data["PageDB"],
                "Evaluation1": student_data["Evaluation1"],
                "Evaluation2": student_data["Evaluation2"],
                "Evaluation3":  student_data["Evaluation3"],
                #AGREGAR LOS DATOS DEL ALUMNO A CONSIDERAR
            }

            # Crear el diccionario del proyecto
            dict_project = {
                "ProjectName": project_name,
                "ProjectDetails": project_details,
                "ProjectParticipation": project_participation,
                "ProjectSpecialty": project_specialty
            }

            # Realizar la actualización en la colección
            result = collection.update_one(
                {"EmailDB": username},
                {"$set": {"AssignedTeacher": dict_professor, "InternshipProject": dict_project}}
            )
                    # Fetch the current AssignedStudents array
            current_students = first_professor["AssignedStudents"]
            app.logger.debug(f"Alumnos Actuales: {current_students}")
            if current_students =="null":
                current_students = []
                # Add the new student to the array
            current_students.append(dict_student)
            result2 = collection.update_one(
                {"EmailDB": dict_professor["EmailDB"]},
                {"$set": {"AssignedStudents": current_students}}
            )

            # Registrar el resultado de la actualización
            app.logger.debug(f"Documentos coincidentes: {result.matched_count}")
            app.logger.debug(f"Documentos modificados: {result.modified_count}")
            return jsonify({"message": "No se encontró ningún profesor con la especialidad especificada."}), 404

        else:
            app.logger.debug("No se encontró ningún profesor con la especialidad especificada.")
            return jsonify({"message": "Project saved"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route("/Progress1", methods=["POST"])
def progress1():
    try:
        grades = request.json
        username = grades["user"]
        grade1 = int(grades["grade1"])
        feedback1 = grades["feedback1"]
        grade2 = int(grades["grade2"])
        feedback2 = grades["feedback2"]
        grade3 = int(grades["grade3"])
        feedback3 = grades["feedback3"]
        grade4 = int(grades["grade4"])
        feedback4 = grades["feedback4"]
        grade5 = int(grades["grade5"])
        feedback5 = grades["feedback5"]

        total_grade = grade1 * 0.4 + grade2 * 0.15 + grade3 * 0.15 + grade4 * 0.15 + grade5 * 0.15
        progress1_dict = {
            "correction1": {"grade": grade1, "feedback": feedback1},
            "correction2": {"grade": grade2, "feedback": feedback2},
            "correction3": {"grade": grade3, "feedback": feedback3},
            "correction4": {"grade": grade4, "feedback": feedback4},
            "correction5": {"grade": grade5, "feedback": feedback5},
            "FinalGrade": total_grade
        }

        user = collection.find_one({"EmailDB": username})
        if user:
            collection.update_one({"EmailDB": username}, {"$set": {"Evaluation1": progress1_dict}})
            return jsonify({"message": "Grade saved", "Evaluation Grade": str(total_grade)}), 200
        else:
            return jsonify({"message": "Grade not saved"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/Progress2", methods=["POST"])
def progress2():
    try:
        grades = request.json
        username = grades["user"]
        grade1 = int(grades["grade1"])
        feedback1 = grades["feedback1"]
        grade2 = int(grades["grade2"])
        feedback2 = grades["feedback2"]
        grade3 = int(grades["grade3"])
        feedback3 = grades["feedback3"]
        grade4 = int(grades["grade4"])
        feedback4 = grades["feedback4"]
        grade5 = int(grades["grade5"])
        feedback5 = grades["feedback5"]
        grade6 = int(grades["grade6"])
        feedback6 = grades["feedback6"]
        grade7 = int(grades["grade7"])
        feedback7 = grades["feedback7"]

        total_grade = grade1 * 0.1 + grade2 * 0.1 + grade3 * 0.25 + grade4 * 0.15 + grade5 * 0.15 + grade6 * 0.1 + grade7 * 0.15
        progress2_dict = {
            "correction1": {"grade": grade1, "feedback": feedback1},
            "correction2": {"grade": grade2, "feedback": feedback2},
            "correction3": {"grade": grade3, "feedback": feedback3},
            "correction4": {"grade": grade4, "feedback": feedback4},
            "correction5": {"grade": grade5, "feedback": feedback5},
            "correction6": {"grade": grade6, "feedback": feedback6},
            "correction7": {"grade": grade7, "feedback": feedback7},
            "FinalGrade": total_grade
        }

        user = collection.find_one({"EmailDB": username})
        if user:
            collection.update_one({"EmailDB": username}, {"$set": {"Evaluation2": progress2_dict}})
            return jsonify({"message": "Grade saved", "Evaluation Grade": str(total_grade)}), 200
        else:
            return jsonify({"message": "Grade not saved"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/Progress3", methods=["POST"])
def progress3():
    try:
        grades = request.json
        username = grades["user"]
        grade1 = int(grades["grade1"])
        feedback1 = grades["feedback1"]
        grade2 = int(grades["grade2"])
        feedback2 = grades["feedback2"]
        grade3 = int(grades["grade3"])
        feedback3 = grades["feedback3"]
        grade4 = int(grades["grade4"])
        feedback4 = grades["feedback4"]
        grade5 = int(grades["grade5"])
        feedback5 = grades["feedback5"]
        grade6 = int(grades["grade6"])
        feedback6 = grades["feedback6"]
        grade7 = int(grades["grade7"])
        feedback7 = grades["feedback7"]

        total_grade = grade1 * 0.2 + grade2 * 0.1 + grade3 * 0.2 + grade4 * 0.15 + grade5 * 0.1 + grade6 * 0.15 + grade7 * 0.1
        progress3_dict = {
            "correction1": {"grade": grade1, "feedback": feedback1},
            "correction2": {"grade": grade2, "feedback": feedback2},
            "correction3": {"grade": grade3, "feedback": feedback3},
            "correction4": {"grade": grade4, "feedback": feedback4},
            "correction5": {"grade": grade5, "feedback": feedback5},
            "correction6": {"grade": grade6, "feedback": feedback6},
            "correction7": {"grade": grade7, "feedback": feedback7},
            "FinalGrade": total_grade
        }

        user = collection.find_one({"EmailDB": username})
        if user:
            collection.update_one({"EmailDB": username}, {"$set": {"Evaluation3": progress3_dict}})
            return jsonify({"message": "Grade saved", "Evaluation Grade": str(total_grade)}), 200
        else:
            return jsonify({"message": "Grade not saved"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route("/FinalGrade", methods=["POST"])
def FinalGrade():
    try:
        grades = request.json
        username = grades["user"]
        user = collection.find_one({"EmailDB": username})
        ed = float(user["CompanyGrade"])
        fp = float(user["FinalPresentationGrade"])

        if user:
            ev1 = float(user["Evaluation1"]["FinalGrade"])
            ev2 = float(user["Evaluation2"]["FinalGrade"])
            ev3 = float(user["Evaluation3"]["FinalGrade"])
            final_grade = ed*0.15 + ev1*0.2 + ev2*0.2 + ev3*0.3 + fp*0.15
            final_grade = round(final_grade, 2)
            collection.update_one({"EmailDB": username}, {"$set": {"FinalGrade": str(final_grade)}})
            if (final_grade > 3.9) and (user["Meeting"] == "True") and (ed >= 4.5):
                collection.update_one({"EmailDB": username}, {"$set": {"Approval": "True"}})
                return jsonify({"message": "Grade saved", "FinalGrade": str(final_grade), "approval": "True"}), 200
            else:
                return jsonify({"message": "Grade saved", "FinalGrade": str(final_grade), "approval": "False"}), 200
        else:
            return jsonify({"message": "Grade not saved"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/AssignedStudentsAdmin", methods=["POST"]) #Mostrar la lista de alumnos asignados a un profesor en X página
def StudentsAdmin():
    try:
        user_data = request.json
        studentList = []
        validation = user_data["confirmation"]
        users = collection.find({"RoleKeyDB": "1"})
        if users:
            if validation == "2":
                students_page2 = collection.find({"RoleKeyDB": "1", "PageDB": "2"})
                for user in students_page2:
                    send={
                        "FirstName": user["FirstName"],
                        "EmailDB": user["EmailDB"],
                    }
                    studentList.append(send)
                return jsonify(studentList), 200
            elif validation == "5":
                students_page5 = collection.find({"RoleKeyDB": "1", "PageDB": "5"})
                for user in students_page5:
                    send = {
                        "FirstName": user["FirstName"],
                        "EmailDB": user["EmailDB"],
                        "Internship": user["Internship"],
                    }
                    studentList.append(send)
                return jsonify(studentList), 200
            else:
                return jsonify({"error": "Unauthorized"}), 401
        else:
            return jsonify({"error": "No users found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/AssignedStudentsProf", methods=["POST"]) #Mostrar la lista de alumnos asignados a un profesor en X página
def StudentsProf():
    try:
        user_data = request.json
        studentList = []
        username = user_data["user"]
        validation = user_data["confirmation"]
        user = collection.find_one({"EmailDB": username})
        
        if user:
            assigned_students = user["AssignedStudents"]
            if validation == "True":
                for student in assigned_students:
                    if student["PageDB"] == "7":
                        studentList.append(student)
                return jsonify(studentList), 200
            else:
                return jsonify(assigned_students), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/CompanyEvaluation", methods=["POST"])
def company_evaluation():
    try:
        grades = request.json
        username = grades["user"]
        numberEval= grades["numberEval"]
        grade1 = int(grades["grade1"])
        grade2 = int(grades["grade2"])
        grade3 = int(grades["grade3"])
        grade4 = int(grades["grade4"])
        grade5 = int(grades["grade5"])
        grade6 = int(grades["grade6"])
        grade7 = int(grades["grade7"])
        grade8 = int(grades["grade8"])
        grade9 = int(grades["grade9"])
        grade10 = int(grades["grade10"])
        
        final_grade = grade1 * 0.1 + grade2 * 0.1 + grade3 * 0.1 + grade4 * 0.1 + grade5 * 0.1 + grade6 * 0.1 + grade7 * 0.1 + grade8 * 0.1 + grade9 * 0.1 + grade10 * 0.1
        
        user = collection.find_one({"EmailDB": username})
        if user:
            collection.update_one({"EmailDB": username}, {"$set": {f"CompanyGrade{numberEval}": str(final_grade)}})
            if numberEval == "3":
                total_grade = (float(user["CompanyGrade1"]) + float(user["CompanyGrade2"]) + float(user["CompanyGrade3"])) / 3
                collection.update_one({"EmailDB": username}, {"$set": {"CompanyGrade": str(total_grade)}})
                return jsonify({"message": "Final grade saved"}), 200
            return jsonify({"message": "Grade saved"}), 200
        else:
            return jsonify({"message": "Grade not saved"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
  #guardar en la base de datos y luego mandar un mensaje al frontend con la nota final

@app.route("/AdminConfirmation", methods=["POST"]) #función que permite al administrador aceptar los requisitos para comenzar pasantía. alumno-confirmación(bool)
def AdminConfirmation():
    try:
        user_data = request.json
        username = user_data["user"]
        validation = user_data["confirmation"]
        user = collection.find_one({"EmailDB": username})
        if user:
            if validation == "True":
                collection.update_one({"EmailDB": username}, {"$set": {"AdminApproval": str(validation)}})
                return jsonify({"message": "Student Approved"}), 200
            else:
                return jsonify({"message": "Student not Approved"}), 401
        else:
            return jsonify({"message": "Student not found"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    
@app.route("/InternshipConfirmation", methods=["POST"])
def InternshipConfirmation():
    try:
        user_data = request.json
        username = user_data["user"]
        validation = user_data["confirmation"]
        user = collection.find_one({"EmailDB": username})
        if user:
            if validation == "True":
                collection.update_one({"EmailDB": username}, {"$set": {"InternshipApproval": str(validation)}})
                return jsonify({"message": "Internship Approved"}), 200
            else:
                return jsonify({"message": "Internship not Approved"}), 401
        else:
            return jsonify({"message": "Internship not found"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/meeting", methods=["POST"])
def meeting_validation():
    try:
        user_data = request.json
        username = user_data["user"]
        validation = user_data["Meeting"]
        user = collection.find_one({"EmailDB": username})
        if user:
            collection.update_one({"EmailDB": username}, {"$set": {"Meeting": str(validation)}})
            return jsonify({"message": "Meeting registered"}), 200
        else:
            return jsonify({"message": "Meeting not registered"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/studentData", methods=["POST"])
def student_data():
    try:
        user = request.json
        username = user["user"]
        user_data = collection.find_one({"EmailDB": username})
        if user_data:
            frontend_data = {
                "FirstName": user_data["FirstName"],
                "EmailDB": user_data["EmailDB"],  # Keep for identification on frontend
                "RoleKeyDB": user_data["RoleKeyDB"],  # Include if needed on frontend
                "Generation": user_data["Generation"],  # Include if needed on frontend
                "Evaluation1": user_data["Evaluation1"],  # Include entire Avance1 structure
                "Evaluation2": user_data["Evaluation2"],
                "Evaluation3": user_data["Evaluation3"],
                "Internship": user_data["Internship"],
                "InternshipProject": user_data["InternshipProject"],
                "AssignedTeacher": user_data["AssignedTeacher"],
                "FinalGrade": user_data["FinalGrade"],  # Include final grade
                "PageDB": user_data["PageDB"],
                "CompanyGrade1": user_data["CompanyGrade1"],
                "CompanyGrade2": user_data["CompanyGrade2"],
                "CompanyGrade3": user_data["CompanyGrade3"],
                "CompanyGrade": user_data["CompanyGrade"],
                "Meeting": user_data["Meeting"],
                "Approval": user_data["Approval"],
                "AdminApproval": user_data["AdminApproval"],
                "InternshipApproval": user_data["InternshipApproval"],
                "FinalPresentation": user_data["FinalPresentation"],
                "FinalPresentationGrade": user_data["FinalPresentationGrade"]
             }
            return jsonify(frontend_data), 200
        else:
            return jsonify({"message": "Data not found"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/dashboard", methods=["POST"])
def dashboard():
    try:
        user = request.json
        username = user["user"]
        key = user["key"]
        perPage = []
        if key == "2":
            user_data = list(collection.find({"AssignedTeacher.EmailDB": username}))
            
            if user_data:
                count_total = len(user_data)
                for i in range(12):
                    count_per_page = collection.count_documents({"AssignedTeacher.EmailDB": username, "PageDB": str(i+1)})
                    perPage.append(count_per_page)
                eval3count = collection.count_documents({"AssignedTeacher.EmailDB": username, "Evaluation3": {"$ne": 0}})
                eval2count = collection.count_documents({"AssignedTeacher.EmailDB": username, "Evaluation2": {"$ne": 0}})
                eval1count = collection.count_documents({"AssignedTeacher.EmailDB": username, "Evaluation1": {"$ne": 0}})
                
                return jsonify({
                    "total": count_total,
                    "perPage": perPage,
                    "countEvaluation3": str(eval3count),
                    "countEvaluation2": str(eval2count),
                    "countEvaluation1": str(eval1count)
                }), 200
            else:
                return jsonify({"message": "No data found for the given teacher"}), 404
        if key == "4":
        # Find the director by email
            director = collection.find_one({"EmailDB": username})

            if director:
                user_data = collection.find({
                    "$and": [ 
                        {"RoleKeyDB": "1"},
                        {"Specialty": director["Specialty"]}
                    ]
                }, {"_id": 0})  # Exclude the _id field from the result

                result = []
                perPage = []
                page_percentages = []
                counter = 0
                for user in user_data:
                    result.append(user)
                    counter += 1

                for i in range(12):
                    count_per_page = collection.count_documents({
                        "$and": [
                            {"RoleKeyDB": "1"},
                            {"Specialty": director["Specialty"]},
                            {"PageDB": str(i + 1)}
                        ]
                    })
                    perPage.append(count_per_page)
                    if counter > 0:
                        percentage = (count_per_page / counter) * 100
                    else:
                        percentage = 0
                    page_percentages.append({"PageDB": str(i + 1), "Percentage": percentage})

                # Students per company
                pipeline = [
                    {
                        "$match": {
                            "$and": [
                                {"RoleKeyDB": "1"},
                                {"Specialty": director["Specialty"]}
                            ]
                        }
                    },
                    {
                        "$group": {
                            "_id": "$Internship.CompanyName",
                            "studentCount": {"$sum": 1}
                        }
                    }
                ]
                    
                # Perform the aggregation
                result_pipeline = list(collection.aggregate(pipeline))
                    
                # Format the result as a list of dictionaries
                company_counts = [{"CompanyName": doc["_id"], "StudentCount": doc["studentCount"]} for doc in result_pipeline]

                return jsonify({
                    "StudentList": result, 
                    "StudentCount": counter, 
                    "PagePercentages": page_percentages, 
                    "Studentspercompany": company_counts
                }), 200
            else:
                return jsonify({"message": "Director not found"}), 404
        else:
            return jsonify({"message": "Error"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/FinalPresentation", methods=["POST"]) #identificador de persona, número de evaluación, nota1, nota2, nota3, nota4, al momento de recibir sobre 3 notas, dar un ponderado, utilizar una biblioteca para hacerlo funcionar
def FinalPresentation():
    try:
        grades = request.json
        username = grades["user"]
        correctormail = grades["correctormail"]
        grade1 = int(grades["grade1"])
        grade2 = int(grades["grade2"])
        grade3 = int(grades["grade3"])
        grade4 = int(grades["grade4"])
        general_grade = grade1 * 0.25 + grade2 * 0.2 + grade3 * 0.3 + grade4 * 0.25
        grades_dict = {
            "grade1": grade1,
            "grade2": grade2,
            "grade3": grade3,
            "grade4": grade4,
            "PresentationGrade": general_grade
        }
        
        user = collection.find_one({"EmailDB": username})
        if user:
            gradeDictionary= user["FinalPresentation"]
            if gradeDictionary == "NA":
                gradeDictionary = {}
        # Update the grades from the corrector
            gradeDictionary[correctormail] = grades_dict
            final_grades = [grades["PresentationGrade"] for grades in gradeDictionary.values()]
            general_grade_average = np.mean(final_grades)

            collection.update_one({"EmailDB": username}, {
            "$set": {
                "FinalPresentation": gradeDictionary,
                "FinalPresentationGrade": general_grade_average
            }
            })
            return jsonify({"message": "Grade saved"}), 200
        else:
            return jsonify({"message": "Grade not saved"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
  #guardar en la base de datos y luego mandar un mensaje al frontend con la nota final

@app.route("/directorSend", methods=["POST"])
def directorSend():
    try:
        requests = request.json
        carrer = requests["Specialty"]
        generation = requests["Generation"]
        page = requests["Page"]
        pageCondition = requests["PageCondition"]
        header = requests["Header"]
        content = requests["Content"]

        
        query = {}
        if carrer is not None:
            query["Specialty"] = carrer
        if generation is not None:
            query["Generation"] = generation
        if page is not None and pageCondition is not None:
            if pageCondition == "greater":
                query["Page"] = {"$gt": page}
            elif pageCondition == "less":
                query["Page"] = {"$lt": page}
        results = list(collection.find(query))
        
        for i in results:
            email(i["EmailDB"],header,content)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)
