from django.db import models
from django.core.exceptions import ValidationError

class Company(models.Model):
    name = models.CharField(max_length=100)
    fees = models.CharField(max_length=20, blank=True, null=True)  # ✅ Corrected field name
    skill_required = models.TextField()
    location = models.CharField(max_length=100, blank=True, null=True)
    vacancy = models.PositiveIntegerField()
    
    class Meta:
        verbose_name_plural = "Companies"  # ✅ Correct plural


    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    applied_company = models.ForeignKey(Company, on_delete=models.CASCADE,blank=True, null=True)
    fee = models.CharField(max_length=20, blank=True, null=True)

    def clean(self):
        # Check if company has vacancy
        if not self.pk and self.applied_company.vacancy <= 0:
            raise ValidationError("No vacancies available for this company.")

    def save(self, *args, **kwargs):
        self.roll_number = self.roll_number.lower()  # 👈 Convert to lowercase

        self.full_clean()  # Ensures `clean()` is called
        if self.applied_company and not self.fee:
            self.fee = self.applied_company.fees

        if not self.pk:  # Only on first creation
            self.applied_company.vacancy -= 1
            self.applied_company.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.applied_company.name}"
