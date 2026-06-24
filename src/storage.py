"""
storage.py - Централизованное хранилище
"""

import json
import os
from typing import List, Optional, Dict, Tuple
from src.models import Student, Teacher, Course, Module, Lesson
from src.logger_setup import logger


class SchoolStorage:
    """Централизованное хранилище школы"""
    
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.teachers: Dict[str, Teacher] = {}
        self.courses: Dict[str, Course] = {}
        self.data_dir = "data"
        self._ensure_data_dir()
        self.load_all()
    
    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_all(self):
        self._save_students()
        self._save_teachers()
        self._save_courses()
        logger.info("Все данные сохранены")
    
    def _save_students(self):
        with open(f"{self.data_dir}/students.json", 'w', encoding='utf-8') as f:
            json.dump({sid: s.to_dict() for sid, s in self.students.items()}, f, ensure_ascii=False, indent=2)
    
    def _save_teachers(self):
        with open(f"{self.data_dir}/teachers.json", 'w', encoding='utf-8') as f:
            json.dump({tid: t.to_dict() for tid, t in self.teachers.items()}, f, ensure_ascii=False, indent=2)
    
    def _save_courses(self):
        with open(f"{self.data_dir}/courses.json", 'w', encoding='utf-8') as f:
            json.dump({cid: c.to_dict() for cid, c in self.courses.items()}, f, ensure_ascii=False, indent=2)
    
    def load_all(self):
        self._load_students()
        self._load_teachers()
        self._load_courses()
        logger.info("Все данные загружены")
    
    def _load_students(self):
        path = f"{self.data_dir}/students.json"
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.students = {sid: Student.from_dict(sdata) for sid, sdata in data.items()}
            except (json.JSONDecodeError, FileNotFoundError):
                self.students = {}
    
    def _load_teachers(self):
        path = f"{self.data_dir}/teachers.json"
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.teachers = {tid: Teacher.from_dict(tdata) for tid, tdata in data.items()}
            except (json.JSONDecodeError, FileNotFoundError):
                self.teachers = {}
    
    def _load_courses(self):
        path = f"{self.data_dir}/courses.json"
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.courses = {cid: Course.from_dict(cdata) for cid, cdata in data.items()}
            except (json.JSONDecodeError, FileNotFoundError):
                self.courses = {}
    
    def add_course(self, name: str, topic: str, teacher_id: Optional[str] = None) -> Course:
        course = Course(name, topic, teacher_id=teacher_id)
        self.courses[course.id] = course
        if teacher_id and teacher_id in self.teachers:
            self.teachers[teacher_id].assign_course(course.id)
        self._save_courses()
        self._save_teachers()
        logger.info(f"Создан курс: {name}")
        return course
    
    def add_module_to_course(self, course_id: str, title: str, description: str = "") -> Tuple[bool, str, Optional[Module]]:
        course = self.get_course(course_id)
        if not course:
            return False, f"Курс не найден", None
        if course.status == Course.STATUS_COMPLETED:
            return False, f"Курс уже завершён", None
        module = course.add_module(title, description)
        self._save_courses()
        logger.info(f"Добавлен модуль '{title}' в курс {course.name}")
        return True, f"Модуль '{title}' добавлен", module
    
    def add_lesson_to_module(self, course_id: str, module_id: str, title: str, description: str = "") -> Tuple[bool, str, Optional[Lesson]]:
        course = self.get_course(course_id)
        if not course:
            return False, f"Курс не найден", None
        module = course.get_module(module_id)
        if not module:
            return False, f"Модуль не найден", None
        if course.status == Course.STATUS_COMPLETED:
            return False, f"Курс уже завершён", None
        lesson = module.add_lesson(title, description)
        self._save_courses()
        return True, f"Урок '{title}' добавлен", lesson
    
    def add_homework_to_lesson(self, course_id: str, lesson_id: str, title: str, description: str, max_score: int = 100) -> Tuple[bool, str]:
        course = self.get_course(course_id)
        if not course:
            return False, f"Курс не найден"
        for module in course.modules:
            lesson = module.get_lesson(lesson_id)
            if lesson:
                if course.status == Course.STATUS_COMPLETED:
                    return False, f"Курс уже завершён"
                lesson.add_homework(title, description, max_score)
                self._save_courses()
                return True, f"ДЗ '{title}' добавлено"
        return False, f"Урок не найден"
    
    def grade_homework(self, course_id: str, lesson_id: str, student_id: str, score: int) -> Tuple[bool, str]:
        course = self.get_course(course_id)
        if not course:
            return False, f"Курс не найден"
        student = self.get_student(student_id)
        if not student:
            return False, f"Студент не найден"
        if student_id not in course.students:
            return False, f"Студент не зачислен"
        for module in course.modules:
            lesson = module.get_lesson(lesson_id)
            if lesson and lesson.homework:
                if not (0 <= score <= lesson.homework.max_score):
                    return False, f"Оценка должна быть от 0 до {lesson.homework.max_score}"
                lesson.homework.submit_grade(student_id, score)
                self._save_courses()
                return True, f"Оценка {score} выставлена"
        return False, f"Урок не найден или нет ДЗ"
    
    def add_student(self, name: str, email: str) -> Student:
        student = Student(name, email)
        self.students[student.id] = student
        self._save_students()
        logger.info(f"Добавлен студент: {name}")
        return student
    
    def add_teacher(self, name: str, specialization: str) -> Teacher:
        teacher = Teacher(name, specialization)
        self.teachers[teacher.id] = teacher
        self._save_teachers()
        logger.info(f"Добавлен преподаватель: {name}")
        return teacher
    
    def enroll_student(self, student_id: str, course_id: str) -> Tuple[bool, str]:
        student = self.get_student(student_id)
        course = self.get_course(course_id)
        if not student or not course:
            return False, "Студент или курс не найден"
        if course.status == Course.STATUS_COMPLETED:
            return False, f"Курс '{course.name}' уже завершён"
        if student_id in course.students:
            return False, "Студент уже зачислен"
        student.enroll(course_id)
        course.add_student(student_id)
        self._save_students()
        self._save_courses()
        return True, f"Студент {student.name} зачислен"
    
    def assign_teacher(self, teacher_id: str, course_id: str) -> Tuple[bool, str]:
        teacher = self.get_teacher(teacher_id)
        course = self.get_course(course_id)
        if not teacher or not course:
            return False, "Преподаватель или курс не найден"
        if course.status == Course.STATUS_COMPLETED:
            return False, f"Курс '{course.name}' уже завершён"
        course.assign_teacher(teacher_id)
        teacher.assign_course(course_id)
        self._save_courses()
        self._save_teachers()
        return True, f"Преподаватель {teacher.name} назначен"
    
    def add_grade(self, student_id: str, course_id: str, grade: int) -> Tuple[bool, str]:
        student = self.get_student(student_id)
        course = self.get_course(course_id)
        if not student or not course:
            return False, "Студент или курс не найден"
        if course.status == Course.STATUS_COMPLETED:
            return False, f"Курс '{course.name}' уже завершён"
        if student_id not in course.students:
            return False, "Студент не зачислен"
        if not 0 <= grade <= 100:
            return False, "Оценка должна быть от 0 до 100"
        student.add_grade(course_id, grade)
        course.add_grade(student_id, grade)
        self._save_students()
        self._save_courses()
        return True, f"Оценка {grade} выставлена"
    
    def complete_course(self, course_id: str) -> Tuple[bool, str]:
        course = self.get_course(course_id)
        if not course:
            return False, "Курс не найден"
        if course.status == Course.STATUS_COMPLETED:
            return False, "Курс уже завершён"
        course.complete()
        for student_id in course.students:
            student = self.get_student(student_id)
            if student:
                student.complete_course(course_id)
        self._save_courses()
        self._save_students()
        return True, f"Курс '{course.name}' завершён"
    
    def get_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)
    
    def get_teacher(self, teacher_id: str) -> Optional[Teacher]:
        return self.teachers.get(teacher_id)
    
    def get_course(self, course_id: str) -> Optional[Course]:
        return self.courses.get(course_id)
    
    def get_all_students(self) -> List[Student]:
        return list(self.students.values())
    
    def get_all_teachers(self) -> List[Teacher]:
        return list(self.teachers.values())
    
    def get_all_courses(self) -> List[Course]:
        return list(self.courses.values())
    
    def get_active_courses(self) -> List[Course]:
        return [c for c in self.courses.values() if c.status == Course.STATUS_ACTIVE]
    
    def get_completed_courses(self) -> List[Course]:
        return [c for c in self.courses.values() if c.status == Course.STATUS_COMPLETED]
    
    def get_student_report(self, student_id: str) -> Optional[Dict]:
        student = self.get_student(student_id)
        if not student:
            return None
        report = {
            'student': student.name,
            'email': student.email,
            'active_courses': [],
            'completed_courses': [],
            'grades': {},
            'homework_scores': [],
            'average_grade': student.get_average_grade(),
            'total_courses': len(student.courses) + len(student.completed_courses)
        }
        for course_id in student.courses:
            course = self.get_course(course_id)
            if course:
                report['active_courses'].append({
                    'name': course.name,
                    'teacher': self.teachers.get(course.teacher_id, 'Не назначен')
                })
        for course_id in student.completed_courses:
            course = self.get_course(course_id)
            if course:
                grades = student.grades.get(course_id, [])
                homework_scores = course.get_student_homework_scores(student_id)
                report['homework_scores'].extend(homework_scores)
                report['completed_courses'].append({
                    'name': course.name,
                    'grades': grades,
                    'average': round(sum(grades) / len(grades) if grades else 0, 2),
                    'homework_scores': homework_scores
                })
                report['grades'][course.name] = grades
        return report
