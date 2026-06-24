"""
test_school.py - Юнит-тесты для системы управления школой
"""

import unittest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import Student, Teacher, Course, Module, Lesson, Homework
from src.storage import SchoolStorage
from src.analytics import Analytics


class TestModels(unittest.TestCase):
    """Тесты моделей данных"""
    
    def test_student_creation(self):
        student = Student("Иван", "ivan@mail.com")
        self.assertEqual(student.name, "Иван")
        self.assertEqual(student.email, "ivan@mail.com")
        self.assertEqual(len(student.id), 8)
    
    def test_teacher_creation(self):
        teacher = Teacher("Петр", "Математика")
        self.assertEqual(teacher.name, "Петр")
        self.assertEqual(teacher.specialization, "Математика")
    
    def test_course_creation(self):
        course = Course("Python", "Программирование")
        self.assertEqual(course.name, "Python")
        self.assertEqual(course.topic, "Программирование")
        self.assertEqual(course.status, Course.STATUS_ACTIVE)
    
    def test_module_creation(self):
        module = Module("Основы", "Введение")
        self.assertEqual(module.title, "Основы")
        self.assertEqual(len(module.lessons), 0)
    
    def test_lesson_creation(self):
        lesson = Lesson("Урок 1", "Описание")
        self.assertEqual(lesson.title, "Урок 1")
        self.assertIsNone(lesson.homework)
    
    def test_homework_creation(self):
        homework = Homework("ДЗ 1", "Сделать", 100)
        self.assertEqual(homework.title, "ДЗ 1")
        self.assertEqual(homework.max_score, 100)
    
    def test_add_homework_to_lesson(self):
        lesson = Lesson("Урок 1")
        lesson.add_homework("ДЗ 1", "Сделать", 100)
        self.assertIsNotNone(lesson.homework)
        self.assertEqual(lesson.homework.title, "ДЗ 1")
    
    def test_add_lesson_to_module(self):
        module = Module("Основы")
        lesson = module.add_lesson("Урок 1")
        self.assertEqual(len(module.lessons), 1)
        self.assertEqual(module.lessons[0].title, "Урок 1")
    
    def test_add_module_to_course(self):
        course = Course("Python", "Программирование")
        module = course.add_module("Основы")
        self.assertEqual(len(course.modules), 1)
        self.assertEqual(course.modules[0].title, "Основы")
    
    def test_student_enroll(self):
        student = Student("Иван", "ivan@mail.com")
        course = Course("Python", "Программирование")
        student.enroll(course.id)
        self.assertIn(course.id, student.courses)
    
    def test_student_add_grade(self):
        student = Student("Иван", "ivan@mail.com")
        student.add_grade("course1", 85)
        self.assertIn(85, student.grades["course1"])
    
    def test_student_average_grade(self):
        student = Student("Иван", "ivan@mail.com")
        student.add_grade("course1", 80)
        student.add_grade("course1", 90)
        self.assertEqual(student.get_average_grade("course1"), 85.0)
    
    def test_course_complete(self):
        course = Course("Python", "Программирование")
        course.complete()
        self.assertEqual(course.status, Course.STATUS_COMPLETED)
        self.assertIsNotNone(course.completed_at)


class TestStorage(unittest.TestCase):
    """Тесты хранилища"""
    
    def setUp(self):
        self.storage = SchoolStorage()
        self.storage.students = {}
        self.storage.teachers = {}
        self.storage.courses = {}
    
    def test_add_student(self):
        student = self.storage.add_student("Иван", "ivan@mail.com")
        self.assertEqual(len(self.storage.students), 1)
        self.assertEqual(self.storage.students[student.id].name, "Иван")
    
    def test_add_teacher(self):
        teacher = self.storage.add_teacher("Петр", "Математика")
        self.assertEqual(len(self.storage.teachers), 1)
        self.assertEqual(self.storage.teachers[teacher.id].specialization, "Математика")
    
    def test_add_course(self):
        course = self.storage.add_course("Python", "Программирование")
        self.assertEqual(len(self.storage.courses), 1)
        self.assertEqual(self.storage.courses[course.id].name, "Python")
    
    def test_enroll_student(self):
        student = self.storage.add_student("Иван", "ivan@mail.com")
        course = self.storage.add_course("Python", "Программирование")
        success, msg = self.storage.enroll_student(student.id, course.id)
        self.assertTrue(success)
        self.assertIn(student.id, course.students)
        self.assertIn(course.id, student.courses)
    
    def test_assign_teacher(self):
        teacher = self.storage.add_teacher("Петр", "Математика")
        course = self.storage.add_course("Python", "Программирование")
        success, msg = self.storage.assign_teacher(teacher.id, course.id)
        self.assertTrue(success)
        self.assertEqual(course.teacher_id, teacher.id)
        self.assertIn(course.id, teacher.courses)
    
    def test_add_grade(self):
        student = self.storage.add_student("Иван", "ivan@mail.com")
        course = self.storage.add_course("Python", "Программирование")
        self.storage.enroll_student(student.id, course.id)
        success, msg = self.storage.add_grade(student.id, course.id, 85)
        self.assertTrue(success)
        self.assertIn(85, student.grades[course.id])
    
    def test_complete_course(self):
        student = self.storage.add_student("Иван", "ivan@mail.com")
        course = self.storage.add_course("Python", "Программирование")
        self.storage.enroll_student(student.id, course.id)
        success, msg = self.storage.complete_course(course.id)
        self.assertTrue(success)
        self.assertEqual(course.status, Course.STATUS_COMPLETED)
        self.assertIn(course.id, student.completed_courses)
    
    def test_add_module_to_course(self):
        course = self.storage.add_course("Python", "Программирование")
        success, msg, module = self.storage.add_module_to_course(course.id, "Основы")
        self.assertTrue(success)
        self.assertEqual(len(course.modules), 1)
    
    def test_add_lesson_to_module(self):
        course = self.storage.add_course("Python", "Программирование")
        _, _, module = self.storage.add_module_to_course(course.id, "Основы")
        success, msg, lesson = self.storage.add_lesson_to_module(course.id, module.id, "Урок 1")
        self.assertTrue(success)
        self.assertEqual(len(module.lessons), 1)
    
    def test_add_homework_to_lesson(self):
        course = self.storage.add_course("Python", "Программирование")
        _, _, module = self.storage.add_module_to_course(course.id, "Основы")
        _, _, lesson = self.storage.add_lesson_to_module(course.id, module.id, "Урок 1")
        success, msg = self.storage.add_homework_to_lesson(course.id, lesson.id, "ДЗ 1", "Сделать", 100)
        self.assertTrue(success)
        self.assertIsNotNone(lesson.homework)
    
    def test_grade_homework(self):
        course = self.storage.add_course("Python", "Программирование")
        student = self.storage.add_student("Иван", "ivan@mail.com")
        self.storage.enroll_student(student.id, course.id)
        _, _, module = self.storage.add_module_to_course(course.id, "Основы")
        _, _, lesson = self.storage.add_lesson_to_module(course.id, module.id, "Урок 1")
        self.storage.add_homework_to_lesson(course.id, lesson.id, "ДЗ 1", "Сделать", 100)
        success, msg = self.storage.grade_homework(course.id, lesson.id, student.id, 85)
        self.assertTrue(success)
        self.assertEqual(lesson.homework.get_student_score(student.id), 85)


class TestAnalytics(unittest.TestCase):
    """Тесты аналитики"""
    
    def setUp(self):
        self.storage = SchoolStorage()
        self.analytics = Analytics(self.storage)
        self.student = self.storage.add_student("Иван", "ivan@mail.com")
        self.course = self.storage.add_course("Python", "Программирование")
        self.storage.enroll_student(self.student.id, self.course.id)
        self.storage.add_grade(self.student.id, self.course.id, 85)
    
    def test_course_statistics(self):
        stats = self.analytics.get_course_statistics(self.course.id)
        self.assertEqual(stats['course_name'], "Python")
        self.assertEqual(stats['students_count'], 1)
        self.assertEqual(stats['average_grade'], 85.0)
    
    def test_top_students(self):
        top = self.analytics.get_top_students(1)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]['name'], "Иван")
    
    def test_teacher_statistics(self):
        teacher = self.storage.add_teacher("Петр", "Математика")
        self.storage.assign_teacher(teacher.id, self.course.id)
        stats = self.analytics.get_teacher_statistics(teacher.id)
        self.assertEqual(stats['teacher_name'], "Петр")
        self.assertEqual(stats['active_courses_count'], 1)


def run_tests():
    """Запуск всех тестов"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalytics))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 ЗАПУСК ТЕСТОВ")
    print("=" * 40)
    success = run_tests()
    print("=" * 40)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!" if success else "❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
