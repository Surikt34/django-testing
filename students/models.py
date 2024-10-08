from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


class Student(models.Model):

    name = models.TextField()

    birth_date = models.DateField(
        null=True,
    )


class Course(models.Model):

    name = models.TextField()

    students = models.ManyToManyField(
        Student,
        blank=True,
    )
    def clean(self):
        max_students = getattr(settings, 'MAX_STUDENTS_PER_COURSE', 20)
        if self.students.count() > max_students:
            raise ValidationError(f"Невозможно записать на курск больше {max_students} студентов")