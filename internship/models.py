from django.db import models
from django.core.exceptions import ValidationError


class Company(models.Model):
    name = models.CharField(max_length=100)
    cgpa = models.CharField(max_length=100, blank=True, null=True)
    fees = models.CharField(max_length=20, blank=False, null=True)
    duration = models.CharField(max_length=50, blank=False, null=True)
    domain = models.CharField(max_length=100, blank=False, null=True)
    description = models.TextField(max_length=1000, blank=False, null=True)
    skill_required = models.TextField(max_length=1000, blank=False, null=True)
    location = models.CharField(max_length=100, blank=False, null=True)
    vacancy = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    applied_company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    fee = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ('roll_number', 'applied_company')  # ✅ Prevent duplicate submissions per company

    def clean(self):
        # ✅ Prevent applying to full company (only for new objects)
        if not self.pk and self.applied_company and self.applied_company.vacancy <= 0:
            raise ValidationError("No vacancies available for this company.")

    def save(self, *args, **kwargs):
        # ✅ Normalize roll number
        self.roll_number = self.roll_number.lower()

        # ✅ Run clean() logic
        self.full_clean()

        # ✅ Auto-fill fee from company if not given
        if self.applied_company and not self.fee:
            self.fee = self.applied_company.fees

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.applied_company.name if self.applied_company else 'N/A'}"
