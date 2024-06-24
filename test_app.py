import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, request
import json
from app import app, get_users, email 
class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.collection.find')
    def test_get_users(self, mock_find):
        # Datos simulados de la base de datos
        mock_find.return_value = [
            {"EmailDB": "jruiz@gmail.com"},
            {"EmailDB": "RodrigoSilva@gmail.com"}
        ]
        users = get_users("1")
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["EmailDB"], "jruiz@gmail.com")
    
    @patch('app.smtplib.SMTP')
    def test_email(self, mock_smtp):
        # Simula el envío de correo electrónico
        mock_server = mock_smtp.return_value
        mock_server.sendmail.return_value = {}
        
        email("jruiz@gmail.com", "Test Subject", "Test Body")
        mock_server.sendmail.assert_called_once()

    @patch('app.get_users')
    def test_login_success(self, mock_get_users):
        # Simula la respuesta de la base de datos
        mock_get_users.return_value = [
            {"EmailDB": "jruiz@gmail.com", "PasswordDB": "1234567", "PageDB": "0"}
        ]
        # Datos simulados de la petición
        data = {"user": "jruiz@gmail.com", "password": "1234567", "key": "1"}
        response = self.app.post('/Login', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Login successful", "PageDB": "0"})

    @patch('app.get_users')
    def test_login_failed(self, mock_get_users):
        # Simula la respuesta de la base de datos
        mock_get_users.return_value = [
            {"EmailDB": "jruiz@gmail.com", "PasswordDB": "wrongpassword", "PageDB": "0"}
        ]
        # Datos simulados de la petición
        data = {"user": "jruiz@gmail.com", "password": "1234567", "key": "1"}
        response = self.app.post('/Login', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"message": "Login failed"})

    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_save_page_success(self, mock_update_one, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "jruiz@gmail.com"}
        mock_update_one.return_value = None
        data = {"user": "jruiz@gmail.com", "page": "2"}
        response = self.app.post('/pages', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Page updated"})

    @patch('app.collection.find_one')
    def test_save_page_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {"user": "jruiz@gmail.com", "page": "2"}
        response = self.app.post('/pages', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "User not found"})

    @patch('app.collection.insert_one')
    def test_create_user(self, mock_insert_one):
        mock_insert_one.return_value.inserted_id = "some_id"
        data = {
            "name": "Javiera Ruiz",
            "user": "jruiz@gmail.com",
            "password": "1234567",
            "key": "1",
            "generation": "2018",
            "specialty": "Ingeniería Civil Informática"
        }
        response = self.app.post('/Signup', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("User created successfully", response.json["message"])

    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_internship_success(self, mock_update_one, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "jruiz@gmail.com", "FirstName": "Javiera"}
        data = {
            "user": "jruiz@gmail.com",
            "company": "TechCorp",
            "industry": "Software",
            "country": "Chile",
            "city": "Santiago",
            "name_sup": "John Doe",
            "email_sup": "john.doe@techcorp.com",
            "title_sup": "Manager",
            "phone_sup": "123456789",
            "name_alum": "Javiera Ruiz",
            "hours": 200,
            "type": "Full-time",
            "start": "2024-07-01",
            "end": "2024-12-31"
        }
        response = self.app.post('/save_internship', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Internship saved"})

    @patch('app.collection.find_one')
    def test_internship_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {
            "user": "jruiz@gmail.com",
            "company": "TechCorp",
            "industry": "Software",
            "country": "Chile",
            "city": "Santiago",
            "name_sup": "John Doe",
            "email_sup": "john.doe@techcorp.com",
            "title_sup": "Manager",
            "phone_sup": "123456789",
            "name_alum": "Javiera Ruiz",
            "hours": 200,
            "type": "Full-time",
            "start": "2024-07-01",
            "end": "2024-12-31"
        }
        response = self.app.post('/save_internship', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"message": "Internship not saved"})

    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_progress1_success(self, mock_update_one, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "jruiz@gmail.com"}
        data = {
            "user": "jruiz@gmail.com",
            "grade1": 85,
            "feedback1": "Good job",
            "grade2": 75,
            "feedback2": "Needs improvement",
            "grade3": 90,
            "feedback3": "Excellent",
            "grade4": 80,
            "feedback4": "Well done",
            "grade5": 70,
            "feedback5": "Satisfactory"
        }
        response = self.app.post('/Progress1', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Grade saved")

    @patch('app.collection.find_one')
    def test_progress1_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {
            "user": "jruiz@gmail.com",
            "grade1": 85,
            "feedback1": "Good job",
            "grade2": 75,
            "feedback2": "Needs improvement",
            "grade3": 90,
            "feedback3": "Excellent",
            "grade4": 80,
            "feedback4": "Well done",
            "grade5": 70,
            "feedback5": "Satisfactory"
        }
        response = self.app.post('/Progress1', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "Grade not saved")

    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_proyect_success(self, mock_update_one, mock_find_one):
        mock_find_one.side_effect = [
            {"EmailDB": "jruiz@gmail.com", "FirstName": "Javiera", "PageDB": 0, "Evaluation1": 0, "Evaluation2": 0, "Evaluation3": 0},
            {"EmailDB": "RodrigoSilva@gmail.com", "FirstName": "Rodrigo Silva", "AssignedStudents": "null"}
        ]
        data = {
            "user": "jruiz@gmail.com",
            "proyect_name": "Project Name",
            "proyect_details": "Project Details",
            "proyect_participation": "Participation Details",
            "project_specialty": "Ingeniería Civil Informática"
        }
        response = self.app.post('/save_proyect_internship', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Project saved")

    @patch('app.collection.find_one')
    @patch('app.collection.find')
    def test_proyect_no_professor_found(self, mock_find, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "jruiz@gmail.com", "FirstName": "Javiera"}
        mock_find.return_value = []
        data = {
            "user": "jruiz@gmail.com",
            "proyect_name": "Project Name",
            "proyect_details": "Project Details",
            "proyect_participation": "Participation Details",
            "project_specialty": "Ingeniería Civil Informática"
        }
        response = self.app.post('/save_proyect_internship', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "No se encontró ningún profesor con la especialidad especificada.")

    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_progress2_success(self, mock_update_one, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "jruiz@gmail.com"}
        data = {
            "user": "jruiz@gmail.com",
            "grade1": 85,
            "feedback1": "Good job",
            "grade2": 75,
            "feedback2": "Needs improvement",
            "grade3": 90,
            "feedback3": "Excellent",
            "grade4": 80,
            "feedback4": "Well done",
            "grade5": 70,
            "feedback5": "Satisfactory",
            "grade6": 95,
            "feedback6": "Outstanding",
            "grade7": 80,
            "feedback7": "Good work"
        }
        response = self.app.post('/Progress2', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Grade saved")

    @patch('app.collection.find_one')
    def test_progress2_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {
            "user": "jruiz@gmail.com",
            "grade1": 85,
            "feedback1": "Good job",
            "grade2": 75,
            "feedback2": "Needs improvement",
            "grade3": 90,
            "feedback3": "Excellent",
            "grade4": 80,
            "feedback4": "Well done",
            "grade5": 70,
            "feedback5": "Satisfactory",
            "grade6": 95,
            "feedback6": "Outstanding",
            "grade7": 80,
            "feedback7": "Good work"
        }
        response = self.app.post('/Progress2', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "Grade not saved")

    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_progress3_success(self, mock_update_one, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "jruiz@gmail.com"}
        data = {
            "user": "jruiz@gmail.com",
            "grade1": 85,
            "feedback1": "Good job",
            "grade2": 75,
            "feedback2": "Needs improvement",
            "grade3": 90,
            "feedback3": "Excellent",
            "grade4": 80,
            "feedback4": "Well done",
            "grade5": 70,
            "feedback5": "Satisfactory",
            "grade6": 95,
            "feedback6": "Outstanding",
            "grade7": 80,
            "feedback7": "Good work"
        }
        response = self.app.post('/Progress3', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Grade saved")

    @patch('app.collection.find_one')
    def test_progress3_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {
            "user": "jruiz@gmail.com",
            "grade1": 85,
            "feedback1": "Good job",
            "grade2": 75,
            "feedback2": "Needs improvement",
            "grade3": 90,
            "feedback3": "Excellent",
            "grade4": 80,
            "feedback4": "Well done",
            "grade5": 70,
            "feedback5": "Satisfactory",
            "grade6": 95,
            "feedback6": "Outstanding",
            "grade7": 80,
            "feedback7": "Good work"
        }
        response = self.app.post('/Progress3', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "Grade not saved")

    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_final_grade_success(self, mock_update_one, mock_find_one):
        mock_find_one.return_value = {
            "EmailDB": "jruiz@gmail.com",
            "CompanyGrade": 5,
            "FinalPresentationGrade": 6,
            "Evaluation1": {"FinalGrade": 4},
            "Evaluation2": {"FinalGrade": 4.5},
            "Evaluation3": {"FinalGrade": 5}
        }
        data = {"user": "jruiz@gmail.com"}
        response = self.app.post('/FinalGrade', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Grade saved")
        self.assertIn('FinalGrade', response.json)
        self.assertIn('approval', response.json)

    @patch('app.collection.find_one')
    def test_final_grade_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {"user": "jruiz@gmail.com"}
        response = self.app.post('/FinalGrade', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "Grade not saved")

    # Similar pruebas unitarias pueden ser escritas para el resto de las funciones
    
    @patch('app.collection.find_one')
    @patch('app.collection.update_one')
    def test_final_presentation_success(self, mock_update_one, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "jruiz@gmail.com", "FinalPresentation": "NA"}
        data = {
            "user": "jruiz@gmail.com",
            "correctormail": "corrector@example.com",
            "grade1": 85,
            "grade2": 75,
            "grade3": 90,
            "grade4": 80
        }
        response = self.app.post('/FinalPresentation', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Grade saved")

    @patch('app.collection.find_one')
    def test_final_presentation_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {
            "user": "jruiz@gmail.com",
            "correctormail": "corrector@example.com",
            "grade1": 85,
            "grade2": 75,
            "grade3": 90,
            "grade4": 80
        }
        response = self.app.post('/FinalPresentation', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "Grade not saved")

    @patch('app.collection.find')
    def test_students_admin_page2(self, mock_find):
        mock_find.return_value = [
            {"FirstName": "Javiera Ruiz", "EmailDB": "jruiz@gmail.com"}
        ]
        data = {"confirmation": "2"}
        response = self.app.post('/AssignedStudentsAdmin', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["FirstName"], "Javiera Ruiz")

    @patch('app.collection.find')
    def test_students_admin_no_users_found(self, mock_find):
        mock_find.return_value = []
        data = {"confirmation": "2"}
        response = self.app.post('/AssignedStudentsAdmin', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "No users found")

    @patch('app.collection.find_one')
    def test_students_prof_success(self, mock_find_one):
        mock_find_one.return_value = {"EmailDB": "RodrigoSilva@gmail.com", "AssignedStudents": [{"PageDB": "7"}]}
        data = {"user": "RodrigoSilva@gmail.com", "confirmation": "True"}
        response = self.app.post('/AssignedStudentsProf', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    @patch('app.collection.find_one')
    def test_students_prof_user_not_found(self, mock_find_one):
        mock_find_one.return_value = None
        data = {"user": "RodrigoSilva@gmail.com", "confirmation": "True"}
        response = self.app.post('/AssignedStudentsProf', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('Error', response.json['message'])
        
    @patch('app.collection.find_one')
    def test_students_prof_success_page7(self, mock_find_one):
        # Simula la respuesta de la base de datos para encontrar el usuario con estudiantes en la página 7
        mock_find_one.return_value = {
            "EmailDB": "RodrigoSilva@gmail.com",
            "AssignedStudents": [
                {"PageDB": "7", "FirstName": "Student1"},
                {"PageDB": "6", "FirstName": "Student2"}
            ]
        }

        data = {"user": "RodrigoSilva@gmail.com", "confirmation": "True"}
        response = self.app.post('/AssignedStudentsProf', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["FirstName"], "Student1")

    @patch('app.collection.find_one')
    def test_students_prof_success_other_pages(self, mock_find_one):
        # Simula la respuesta de la base de datos para encontrar el usuario con estudiantes en páginas diferentes de 7
        mock_find_one.return_value = {
            "EmailDB": "RodrigoSilva@gmail.com",
            "AssignedStudents": [
                {"PageDB": "6", "FirstName": "Student2"},
                {"PageDB": "5", "FirstName": "Student3"}
            ]
        }

        data = {"user": "RodrigoSilva@gmail.com", "confirmation": "False"}
        response = self.app.post('/AssignedStudentsProf', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @patch('app.collection.find_one')
    def test_students_prof_user_not_found(self, mock_find_one):
        # Simula la respuesta de la base de datos para el caso en que el usuario no se encuentra
        mock_find_one.return_value = None

        data = {"user": "RodrigoSilva@gmail.com", "confirmation": "True"}
        response = self.app.post('/AssignedStudentsProf', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "User not found")

if __name__ == '__main__':
    unittest.main()
