from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Student
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError



def company_list(request):
    companies = Company.objects.all()
    return render(request, 'internship/company_list.html', {'companies': companies})

def apply_to_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        roll = request.POST.get('roll_number').lower()  # normalize case
        email = request.POST.get('email')
        mobile = request.POST.get('mobile_number')
        department = request.POST.get('department')

        if company.vacancy <= 0:
            messages.error(request, "No vacancies left!")
            return redirect('company_list')

        try:
            student = Student.objects.create(
                name=name,
                roll_number=roll,
                email=email,
                mobile_number=mobile,
                department=department,
                applied_company=company
            )

            company.vacancy -= 1
            company.save()
            messages.success(request, "Applied successfully!")
            return redirect('company_list')

        except IntegrityError:
            messages.error(request, "You have already applied with this roll number.")
            return redirect('company_list')

        except ValidationError as e:
            messages.error(request, "You have already applied with this roll number.")
            return redirect('company_list')

    return render(request, 'internship/apply_form.html', {'company': company})