"""
visualizer.py - Визуализация статистики
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

from src.storage import SchoolStorage


class Visualizer:
    """Класс для визуализации статистики"""
    
    def __init__(self, storage: SchoolStorage):
        self.storage = storage
    
    def plot_student_progress(self, student_id: str):
        report = self.storage.get_student_report(student_id)
        if not report:
            print("❌ Студент не найден")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'📊 Успеваемость студента: {report["student"]}', fontsize=16, fontweight='bold')
        
        ax1 = axes[0, 0]
        courses = list(report['grades'].keys())
        grades = []
        for course in courses:
            grades_list = report['grades'][course]
            grades.append(sum(grades_list) / len(grades_list) if grades_list else 0)
        if courses:
            colors = plt.cm.viridis(range(len(courses)))
            ax1.bar(courses, grades, color=colors)
            ax1.set_title('Средние оценки по курсам', fontsize=12)
            ax1.set_ylabel('Средняя оценка')
            ax1.set_ylim(0, 105)
            ax1.tick_params(axis='x', rotation=45)
            for i, v in enumerate(grades):
                ax1.text(i, v + 2, f'{v:.1f}', ha='center', fontsize=9)
        else:
            ax1.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Средние оценки по курсам', fontsize=12)
        
        ax2 = axes[0, 1]
        active = len(report['active_courses'])
        completed = len(report['completed_courses'])
        ax2.pie([active, completed], labels=['Активные', 'Завершённые'], 
                autopct='%1.1f%%', colors=['#66b3ff', '#99ff99'])
        ax2.set_title('Курсы: активные vs завершённые', fontsize=12)
        
        ax3 = axes[1, 0]
        data_for_box = []
        labels_for_box = []
        for course_name, grades_list in report['grades'].items():
            if grades_list:
                data_for_box.append(grades_list)
                labels_for_box.append(course_name[:15] + '...' if len(course_name) > 15 else course_name)
        if data_for_box:
            bp = ax3.boxplot(data_for_box, labels=labels_for_box, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
            ax3.set_title('Распределение оценок по курсам', fontsize=12)
            ax3.set_ylabel('Оценка')
            ax3.tick_params(axis='x', rotation=45)
        else:
            ax3.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Распределение оценок по курсам', fontsize=12)
        
        ax4 = axes[1, 1]
        homework_scores = report.get('homework_scores', [])
        if homework_scores:
            ax4.hist(homework_scores, bins=10, color='green', alpha=0.7, edgecolor='black')
            ax4.set_title('Распределение оценок за ДЗ', fontsize=12)
            ax4.set_xlabel('Оценка')
            ax4.set_ylabel('Количество')
            avg = sum(homework_scores) / len(homework_scores)
            ax4.axvline(x=avg, color='red', linestyle='--', label=f'Средняя: {avg:.1f}')
            ax4.legend()
        else:
            ax4.text(0.5, 0.5, 'Нет данных о ДЗ', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Оценки за домашние задания', fontsize=12)
        
        plt.tight_layout()
        plt.show()
