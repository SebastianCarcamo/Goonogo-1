from sqlalchemy import Column, Integer, String, Sequence, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from database import connector


class Student(connector.Manager.Base):
    __tablename__ = 'students'
    id = Column(Integer, Sequence('student_id_seq'), primary_key=True)
    name = Column(String(50))
    lastname = Column(String(50))
    password = Column(String(15))
    username = Column(String(15))

class Teacher(connector.Manager.Base):
    __tablename__ = 'teachers'
    id = Column(Integer, Sequence('teacher_id_seq'), primary_key=True)
    name = Column(String(50))
    lastname = Column(String(50))
    password = Column(String(15))
    username = Column(String(15))
    information = Column(String(500))
    numRating = Column(Integer)
    sumRating = Column(Integer)


class Subject(connector.Manager.Base):
    __tablename__ = 'subjects'
    id = Column(Integer, Sequence('subject_id_seq'), primary_key=True)
    name = Column(String(50))
    summary = Column(String(500))
        

class Teacher_Subject(connector.Manager.Base):
    __tablename__ = 'teacher_subject'
    id = Column(Integer, Sequence('teacher_subject_id_seq'), primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    teacher = relationship(Teacher, foreign_keys=[teacher_id])
    subject = relationship(Subject, foreign_keys=[subject_id])


class Rating(connector.Manager.Base):
    __tablename__ = 'rating'
    id = Column(Integer, Sequence('rating_id_seq'), primary_key=True)
    title = Column(String(80))
    content = Column(String(500))
    value = Column(Integer)
    student_id = Column(Integer, ForeignKey('students.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    teacher = relationship(Teacher, foreign_keys=[teacher_id])
    student = relationship(Student, foreign_keys=[student_id])

