from flask import Flask, request, jsonify # pip install json

from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine # pip install sqlalchemy
from sqlalchemy.orm import relationship, sessionmaker 
from sqlalchemy.ext.declarative import declarative_base
from flasgger import Swagger, LazyString, LazyJSONEncoder # pip install flasgger


Base = declarative_base()
API_PORT = 8000

#region DB Table creations
# Association tables for many to many relationship
treatments_table = Table(
    'treatments', Base.metadata,
    Column('doctor_id', Integer, ForeignKey('Doctors.id'), primary_key=True),
    Column('patient_id', Integer, ForeignKey('Patients.id'), primary_key=True)
)

# Doctor table
class Doctor(Base):
    __tablename__ = 'Doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    patients = relationship('Patient', secondary=treatments_table, back_populates='doctors')

    def _repr_(self):
        return f"DoctorId: [{self.id}], DoctorName: [{self.name}], Patients:{[p.name for p in self.patients]}"

    def __str__(self):
        return f"DoctorId: [{self.id}], DoctorName: [{self.name}], Patients:{[p.name for p in self.patients]}"


# Patient table
class Patient(Base):
    __tablename__ = 'Patients'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    doctors = relationship('Doctor', secondary=treatments_table, back_populates='patients')

    def _repr_(self):
        return f"PatientId: [{self.id}], PatientName: [{self.name}], Doctors:{[d.name for d in self.doctors]}"

    def __str__(self):
        return f"PatientId: [{self.id}], PatientName: [{self.name}], Doctors:{[d.name for d in self.doctors]}"
#endregion

app = Flask(__name__)

DB_URL = 'mssql+pyodbc://(localdb)\MSSQLLocalDB/testdb?driver=ODBC+Driver+18+for+SQL+Server'
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
#region API endpoints

#region Swagger UI

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Doctor and Patient Many-to-Many Relationship API",
        "description": "API to manage doctors and patients with many-to-many relationships.",
        "version": "1.0.0"
    },
    "host": "127.0.0.1:5000",
    "basePath": "/",
    "schemes": ["http"],
    "paths": {
        "/api/Create": {
        "post": {
            "summary": "Create relationships between doctors and patients",
            "description": "Add initial data of doctors and patients and establish relationships.",
            "responses": {
            "200": {
                "description": "Successfully created"
            },
            "500": {
                "description": "Server error"
            }
            }
        }
        },
        "/api/Read": {
        "get": {
            "summary": "Read relationships",
            "description": "Retrieve all doctors with their associated patients and vice versa.",
            "responses": {
            "200": {
                "description": "Successfully retrieved",
                "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                    "id": { "type": "integer" },
                    "name": { "type": "string" },
                    "associations": {
                        "type": "array",
                        "items": { "type": "string" }
                    }
                    }
                }
                }
            },
            "500": {
                "description": "Server error"
            }
            }
        }
        },
        "/api/Update": {
        "post": {
            "summary": "Update relationships",
            "description": "Update the relationship between a doctor and a patient.",
            "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                "type": "object",
                "properties": {
                    "doctor_id": { "type": "integer" },
                    "patient_id": { "type": "integer" }
                }
                }
            }
            ],
            "responses": {
            "200": {
                "description": "Successfully updated"
            },
            "400": {
                "description": "Bad request"
            },
            "500": {
                "description": "Server error"
            }
            }
        }
        },
        "/api/Delete": {
        "post": {
            "summary": "Delete relationships",
            "description": "Delete a relationship between a doctor and a patient.",
            "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                "type": "object",
                "properties": {
                    "doctor_id": { "type": "integer" },
                    "patient_id": { "type": "integer" }
                }
                }
            }
            ],
            "responses": {
            "200": {
                "description": "Successfully deleted"
            },
            "400": {
                "description": "Bad request"
            },
            "500": {
                "description": "Server error"
            }
            }
        }
        }
    },
    "definitions": {}
}

swagger_config = {
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST"),
    ],
    "specs": [
        {
            "endpoint": 'Doctor_Patient_ManyToManyRelationship',
            "route": '/Doctor_Patient_ManyToManyRelationship.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/",
    
}

app.json_encoder = LazyJSONEncoder
swagger = Swagger(app, template=swagger_template,config=swagger_config)
#endregion

# Create
@app.route('/api/Create', methods=["POST"])
def api_create():
    try:
        d1 = Doctor(name='Doctor1')
        d2 = Doctor(name='Doctor2')
        p1 = Patient(name='Patient1')
        p2 = Patient(name='Patient2')
        p3 = Patient(name='Patient3')

        p1.doctors.extend([d1, d2])
        p2.doctors.append(d2)
        p3.doctors.append(d1)
        session.add(d1)
        session.add(d2)
        session.add(p1)
        session.add(p2)
        session.add(p3)
        session.commit()

        response = {"responseCode": "0", "responseDesc": "SUCCESS"}
        return jsonify(response), 200
    except Exception as e:
        print(e)
        response = {"responseCode" : "1", "responseDesc": "ERROR"}
        return jsonify(response), 500
#endregion

#region Read
@app.route('/api/Read', methods=["GET"])
def api_read():
    try:
        doctors = session.query(Doctor).all()
        print("\nDoctors and their Patients: ")
        for d in doctors:
            print(d)

        patients = session.query(Patient).all()
        print("\nPatients and their Doctors: ")
        for p in patients:
            print(p)
        response = {"responseCode" : "0", "responseDesc" : "SUCCESS"}
        return jsonify(response), 200
    
    except Exception as e:
        print("Error: " + e)
        response = {"responseCode" : "1", "responseDesc": "ERROR"}
        return jsonify(response), 500
#endregion

#region Update
@app.route('/api/Update', methods=["POST"])
def api_update():
    try:
        patient = session.query(Patient).filter_by(name='Patient2').first()
        doctor = session.query(Doctor).filter_by(name='Doctor1').first()

        if patient and doctor:
            patient.doctors.append(doctor)
            session.commit()
            print(f"Updated ")
        response = {"responseCode" : "0", "responseDesc" : "SUCCESS"}
        return jsonify(response), 200

    except Exception as e:
        print("Error: " + e)
        response = {"responseCode" : "1", "responseDesc": "ERROR"}
        return jsonify(response), 500
#endregion

#region Delete
@app.route('/api/Delete', methods=["POST"])
def api_delete():
    try:
        patient = session.query(Patient).filter_by(name='Patient3').first()
        doctor = session.query(Doctor).filter_by(name='Doctor2').first()

        if patient and doctor:
            patient.doctors.remove(doctor)
            session.commit()
        response = {"responseCode" : "0", "responseDesc" : "SUCCESS"}
        return jsonify(response), 200
        
    except Exception as e:
        print("Error: " + e)
        response = {"responseCode" : "1", "responseDesc": "ERROR"}
        return jsonify(response), 500
#endregion

#region VerifyFinalEnrolments
@app.route('/api/VerifyFinalTreatments', methods=["GET"])
def api_verifyFinalTreatments():
    try:
        patients = session.query(Patient).all()
        print('Final patients and their doctors:')
        for p in patients:
            print(p)
        response = {"responseCode" : "0", "responseDesc" : "SUCCESS"}
        return jsonify(response), 200
    except Exception as e:
        print("Error: " + e)
        response = {"responseCode" : "1", "responseDesc": "ERROR"}
        return jsonify(response), 500
#endregion


if __name__ == '__main__':
    app.run(debug=True)