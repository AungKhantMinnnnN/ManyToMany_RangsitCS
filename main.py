from flask import Flask, request, jsonify

from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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
        return "Success"
    except Exception as e:
        return "Error"
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
        return "Success"
    
    except Exception as e:
        print("Error: " + e)
        return "Error"
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

    except Exception as e:
        print("Error: " + e)
        return "Error"
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
        
    except Exception as e:
        print("Error: " + e)
        return "Error"
#endregio

#region VerifyFinalEnrolments
@app.route('/api/VerifyFinalTreatments', methods=["GET"])
def api_verifyFinalTreatments():
    try:
        patients = session.query(Patient).all()
        print('Final patients and their doctors:')
        for p in patients:
            print(p)
    except Exception as e:
        print("Error: " + e)
        return "Error"

if __name__ == '__main__':
    app.run()