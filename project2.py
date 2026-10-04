from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy import create_engine,Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional,List

app=FastAPI(title="Students Data")
#Setting up the Database

engine=create_engine("sqlite:///students.db",connect_args={"check_same_thread":False})
SessionLocal= sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base= declarative_base()

#Database Model
class StudentDB(Base):
    __tablename__="user"
    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    dept=Column(String, nullable=False)
    reg_no=Column(String, unique=True, nullable=False)

Base.metadata.create_all(engine)

#Pydantic Models
class Student(BaseModel):
    name:str
    dept:str
    reg_no: str
class UserResponse(BaseModel):
    id:int
    name:str
    dept:str
    reg_no: str

    class Config:
        from_attributes=True

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
      
#Search student by ID
@app.get("/student/{student_id}", response_model=UserResponse)
def get_student(student_id:int, db:Session= Depends(get_db)):
    student= db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found!")
    return student
  
#Add new student
@app.post("/student/")
def add_student(student: Student, db:Session= Depends(get_db)):
    if db.query(StudentDB).filter(StudentDB.reg_no == student.reg_no).first():
        raise HTTPException(status_code=404, detail="Student already exists!")
    new_st=StudentDB(**student.dict())
    db.add(new_st)
    db.commit()
    db.refresh(new_st)
    return new_st

#Update existing student
@app.put("/student/{student_id}")
def update_student(student_id: int, student:Student, db:Session = Depends(get_db)):
    db_st= db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not db_st:
        raise HTTPException(status_code=404, detail="Student doesn't exist!")
    for field, value in student.dict().items():
        setattr(db_st, field, value)
    db.commit()
    db.refresh(db_st)
    return db_st

#Delete student
@app.delete("/student/{student_id}")
def delete_student(student_id: int, student:Student, db:Session = Depends(get_db)):
    db_st= db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not db_st:
        raise HTTPException(status_code=404, detail="Student doesn't exist!")
    db.delete(db_st)
    db.commit()
    return {"Message":"Student Deleted!"}

#Get all students
@app.get("/students/", response_model=List[UserResponse])
def get_all_students(db:Session = Depends(get_db)):
    return db.query(StudentDB).all()

