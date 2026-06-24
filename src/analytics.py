"""
analytics.py - Аналитика успеваемости
"""

from typing import List, Dict, Optional
from src.storage import SchoolStorage
from src.models import Course


class Analytics:
    """Класс для аналитики успеваемости"""
    
    def __init__(self, storage: SchoolStorage):
        self.storage = storage
    
    def get_course_statistics(self, course_id: str) -> Optional[Dict]:
        course = self.storage.get_course(course_id)
        if not course:
            return None
        grades = []
        homework_scores = []
        for student_id in course.students:
            student = self.storage.get_student(student_id)
            if student:
                grades.extend(student.grades.get(course_id, []))
                homework_scores.extend(course.get_student_homework_scores(student_id))
        return {
            'course_name': course.name,
            'topic': course.topic,
            'status': course.status,
            'teacher': self.storage.get_teacher(course.teacher_id),
            'students_count': len(course.students),
            'modules_count': len(course.modules),
            'lessons_count': course.get_total_lessons(),
            'grades_count': len(grades),
            'average_grade': sum(grades) / len(grades) if grades else 0,
            'max_grade': max(grades) if grades else 0,
            'min_grade': min(grades) if grades else 0,
            'homework_scores_count': len(homework_scores),
            'homework_avg': sum(homework_scores) / len(homework_scores) if homework_scores else 0
        }
    
    def get_top_students(self, n: int = 5) -> List[Dict]:
        results = []
        for student in self.storage.get_all_students():
            avg = student.get_average_grade()
            if avg > 0:
                results.append({
                    'name': student.name,
                    'email': student.email,
                    'average_grade': round(avg, 2),
                    'courses_completed': len(student.completed_courses),
                    'active_courses': len(student.courses)
                })
        results.sort(key=lambda x: x['average_grade'], reverse=True)
        return results[:n]
    
    def get_teacher_statistics(self, teacher_id: str) -> Optional[Dict]:
        teacher = self.storage.get_teacher(teacher_id)
        if not teacher:
            return None
        courses = []
        active_courses = []
        completed_courses = []
        all_grades = []
        for course_id in teacher.courses:
            course = self.storage.get_course(course_id)
            if course:
                courses.append(course)
                if course.status == Course.STATUS_ACTIVE:
                    active_courses.append(course)
                elif course.status == Course.STATUS_COMPLETED:
                    completed_courses.append({
                        'name': course.name,
                        'completed_at': course.completed_at,
                        'students_count': len(course.students),
                        'average_grade': course.get_average_grade()
                    })
                for grades in course.grades.values():
                    all_grades.extend(grades)
        return {
            'teacher_name': teacher.name,
            'specialization': teacher.specialization,
            'total_courses': len(courses),
            'active_courses_count': len(active_courses),
            'completed_courses_count': len(completed_courses),
            'active_courses': [{'name': c.name, 'students': len(c.students)} for c in active_courses],
            'completed_courses': completed_courses,
            'total_students': sum(len(c.students) for c in courses),
            'average_student_grade': round(sum(all_grades) / len(all_grades) if all_grades else 0, 2),
            'total_grades': len(all_grades)
        }
