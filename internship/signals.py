# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InternshipApplication, Company, Student
from django.utils.text import slugify

@receiver(post_save, sender=InternshipApplication)
def handle_approved_application(sender, instance, created, **kwargs):
    if instance.application_approved != "APPROVED":
        return

    # Normalize company name for uniqueness handling
    base_name = instance.industry_name.strip()
    normalized_name = base_name
    counter = 1

    while Company.objects.filter(name=normalized_name).exists():
        normalized_name = f"{base_name} ({counter})"
        counter += 1

    # Try to find an exact match on location + domain, not just name
    company = Company.objects.filter(
        name__iexact=base_name,
        location__iexact=instance.industry_location,
        domain__iexact=instance.domain_of_work
    ).first()

    if company:
        # Company exists — increase vacancy
        company.vacancy += 1
        company.save()
    else:
        # Company doesn't exist — create a new one with unique name
        company = Company.objects.create(
            name=normalized_name,
            fees=instance.fees_amount or '0',
            location=instance.industry_location,
            domain=instance.domain_of_work,
            vacancy=1,
            active=False,
            description="Auto-created from external application",
        )

    # Check if student exists by roll number
    student, created = Student.objects.get_or_create(
        roll_number=instance.vtu_number.lower(),
        defaults={
            'name': instance.student_name,
            'mobile_number': instance.contact_number,
            'department': instance.department,
            'applied_company': company,
            'fee': instance.fees_amount or '0',
        }
    )

    # Optional: if student exists but applied_company is blank, update it
    if not created and not student.applied_company:
        student.applied_company = company
        student.save()
