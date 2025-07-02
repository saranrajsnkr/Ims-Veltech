from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Student
from django.contrib import messages

def company_list(request):
    companies = Company.objects.all()
    return render(request, 'internship/company_list.html', {'companies': companies})

def apply_to_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        roll = request.POST.get('roll_number')
        email = request.POST.get('email')

        if company.vacancy <= 0:
            messages.error(request, "No vacancies left!")
            return redirect('company_list')

        Student.objects.create(
            name=name,
            roll_number=roll,
            email=email,
            applied_company=company
        )
        messages.success(request, "Applied successfully!")
        return redirect('company_list')

    return render(request, 'internship/apply_form.html', {'company': company})
