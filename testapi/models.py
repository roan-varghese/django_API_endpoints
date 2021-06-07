from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=30)
    age = models.IntegerField()
    gender = models.CharField(max_length=6, choices=[('male', 'male'), ('female', 'female')])
    nationality = models.CharField(max_length=20)

    def __str__(self):
        return self.name

