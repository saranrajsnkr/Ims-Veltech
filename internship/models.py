from django.db import models
from django.core.exceptions import ValidationError


class Company(models.Model):
    name = models.CharField(max_length=100)
    cgpa = models.CharField(max_length=100, blank=True, null=True)
    fees = models.CharField(max_length=20, blank=False, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    domain = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    skill_required = models.TextField(max_length=1000, blank=True, null=True)
    location = models.CharField(max_length=100, blank=False, null=True)
    vacancy = models.PositiveIntegerField()
    active = models.BooleanField("Active", default=False)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)  # ✅ Unique roll number
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    applied_company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    fee = models.CharField(max_length=20, blank=True, null=True)


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



MESSAGE_COLOR_CHOICES = [
    ('green', 'Success - Green'),
    ('blue', 'Info - Blue'),
    ('orange', 'Warning - Orange'),
    ('red', 'Error - Red'),
]

class SiteSetting(models.Model):
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"




class Announcement(models.Model):
    message1 = models.TextField("Message 1", max_length=500, blank=True, null=True)
    is_message1_active = models.BooleanField("Show Message 1", default=False)
    message1_color = models.CharField("Message 1 Color", max_length=10, choices=MESSAGE_COLOR_CHOICES, default='green')


    message2 = models.TextField("Message 2", max_length=500, blank=True, null=True)
    is_message2_active = models.BooleanField("Show Message 2", default=False)
    message2_color = models.CharField("Message 2 Color", max_length=10, choices=MESSAGE_COLOR_CHOICES, default='orange')


    def __str__(self):
        return "Announcements"

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"

