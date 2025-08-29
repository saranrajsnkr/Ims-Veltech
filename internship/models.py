import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone




import uuid
from django.db import models
from django.utils.text import slugify

class Company(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  
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

    # Login credentials
    username = models.CharField(max_length=100, blank=True, null=True, unique=True)
    password = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.username:
            # Create professional username
            base_username = slugify(self.name).replace("-", "")  # e.g. "Infosys Ltd" -> "infosysltd"
            base_username = base_username[:10].lower()  # keep short, lowercase
            count = Company.objects.filter(username__startswith=base_username).count()

            self.username = f"{base_username}{count+1}" if count else base_username

        if not self.password:
            # Minimal & professional password (company prefix + year or number)
            prefix = self.username[:4]  # first 4 letters of username
            year = "2025"  # you can make this dynamic with datetime.now().year
            count = Company.objects.filter(username__startswith=self.username[:4]).count()

            self.password = f"{prefix}{year}{count+1}"  # e.g. info20251, goog20252

        super().save(*args, **kwargs)



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
    house=models.CharField(max_length=100, blank=True, null=True)


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


class UserReport(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=50)
    email = models.EmailField()
    problem = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"
    
    
    

class InternshipApplication(models.Model):
    STIPEND_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    
    FEES_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    
    APPROVAL_CHOICES = [
    ("APPROVED", "Approved"),
    ("REJECTED", "Not Approved"),
    ("PENDING", "Pending"),
]
    DEPARTMENT_CHOICES = [
        ('Artificial Intelligence (AI) and Data Science', 'Artificial Intelligence (AI) and Data Science'),
        ('Artificial Intelligence and Machine Learning', 'Artificial Intelligence and Machine Learning'),
        ('Computer Science & Engineering', 'Computer Science & Engineering'),
        ('Computer Science and Engineering (Artificial Intelligence and Machine Learning)', 'Computer Science and Engineering (Artificial Intelligence and Machine Learning)'),
        ('Computer Science and Engineering (Cyber Security)', 'Computer Science and Engineering (Cyber Security)'),
        ('Computer Science and Engineering (Data Science)', 'Computer Science and Engineering (Data Science)'),
        ('Computer Science and Design', 'Computer Science and Design'),
        ('Information Technology', 'Information Technology'),
        # Add more departments as needed
    ]
    email = models.EmailField(verbose_name="Email")
    student_name = models.CharField(max_length=100, verbose_name="Name of the Student")
    vtu_number = models.CharField(max_length=20, verbose_name="VTU Number")
    department = models.CharField(max_length=100, verbose_name="Department of the Student")
    contact_number = models.CharField(max_length=15, verbose_name="Contact Number of the Student")
    department = models.CharField(
        max_length=150,
        choices=DEPARTMENT_CHOICES,
        verbose_name="Department of the Student",
        blank=True,
        null=True,
    )
    industry_name = models.CharField(max_length=100, verbose_name="Name of the Industry")
    industry_location = models.CharField(max_length=100, verbose_name="Location of the Industry")
    domain_of_work = models.CharField(max_length=100, verbose_name="Domain of Work")
    industry_category = models.CharField(max_length=100, verbose_name="Category the Industry")
    referal_person_name = models.CharField(
        max_length=100,
        verbose_name="Name of the Referal Person",
        blank=True,
        null=True
    )
    referal_person_designation = models.CharField(
        max_length=100,
        verbose_name="Designation of the Referal Person",
        blank=True,
        null=True
    )
    referal_person_phone_number = models.CharField(
        max_length=10,
        verbose_name="Mobile Number of the Referal Person",
        blank=True,
        null=True,
    )
    referal_person_email = models.EmailField(
        verbose_name="Email of the Referal Person",
        blank=True,
        null=True
    )
    industry_website = models.URLField(verbose_name="Website Link of the Industry", blank=True, null=True)

    industry_email = models.EmailField(verbose_name="Industry Contact Email", blank=True, null=True)
    industry_phone_number = models.CharField(max_length=15, verbose_name="Industry Contact Phone", blank=True, null=True)

    stipend_provided = models.CharField(
        max_length=3,
        verbose_name="Any Stipend Provided from the Industry?"
    )
    stipend_amount = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="If Yes, How much Stipend?"
    )

    fees_required = models.CharField(
        max_length=3,
        verbose_name="Is there any need to pay fees to acquire the Internship?"
    )
    fees_amount = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="If yes, How much fees?"
    )

    application_approved = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default="PENDING",
        verbose_name="Application Approval Status"
    )
    approval_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Message Regarding Approval Status"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"{self.student_name} ({self.vtu_number}) - {self.industry_name}"

    # def save(self, *args, **kwargs):
    #     if self.pk:  # Only on update, not on creation
    #         old = InternshipApplication.objects.get(pk=self.pk)
    #         if old.application_approved != self.application_approved:
    #             # Send approval mail
    #             subject = f"Internship Application Status - {self.application_approved}"
    #             message = self.approval_message or "Your application status has been updated."
    #             send_mail(
    #                 subject,
    #                 message,
    #                 settings.DEFAULT_FROM_EMAIL,  # From Email
    #                 [self.email],
    #                 fail_silently=False,
    #             )
    #     super().save(*args, **kwargs)
    
    
    
    


class StudentReport(models.Model):
    REPORT_STATUS_CHOICES = [
        ('REPORTED', 'Reported to the Company'),
        ('NOT_REPORTED', 'Not Reported to the Company'),
        ('PENDING', 'repoting on 21 july'),
    ]

    roll_number = models.CharField(max_length=20, unique=True)
    report_status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES)

    def __str__(self):
        return f"{self.roll_number} - {self.report_status}"
    
    
    
    
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    vtu_number = models.CharField(max_length=20, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=[("Present", "Present"), ("Absent", "Absent")],
        default="Present"
    )

    class Meta:
        unique_together = ("student", "company", "date")

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"