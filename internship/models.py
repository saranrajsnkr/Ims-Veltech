from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    skill_required = models.TextField()
    vacancy = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    email = models.EmailField()
    applied_company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk and self.applied_company.vacancy > 0:
            self.applied_company.vacancy -= 1
            self.applied_company.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.applied_company.name}"
