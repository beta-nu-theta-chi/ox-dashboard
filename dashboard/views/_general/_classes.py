from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.views.generic.edit import DeleteView

from dashboard.models import (
    Position,
    Classes,
    Brother,
    Grade
)
from dashboard.forms import ClassTakenForm
from dashboard.utils import verify_position

def classes(request, department=None, number=None, brother=None):
    if request.user.brother in Position.objects.get(title='Scholarship Chair').brothers.all():
        view = "scholarship"
    else:
        view = ""
    classes_taken = Classes.objects.all().order_by('department', 'number')
    if department is not None:
        classes_taken = classes_taken.filter(department=department)
    if brother is not None:
        classes_taken = classes_taken.filter(brothers=brother)
        if isinstance(brother, str):
            brother = int(brother)
        if request.user.brother.pk == brother:
            view = "brother"
    if number is not None:
        classes_taken = classes_taken.filter(number=number)

    if request.method == 'POST':
        if 'filter' in request.POST:
            form = request.POST
            department = ('department', form.get('department'))
            brother = ('brother', form.get('brother'))
            number = ('number', form.get('class_number'))
            kwargs = dict((arg for arg in [department, number, brother] if arg[1] != ""))

            return HttpResponseRedirect(reverse('dashboard:classes', kwargs=kwargs))
        elif 'unadd_self' in request.POST:
            form = request.POST
            class_taken = Classes.objects.get(pk=form.get('class'))
            class_taken.brothers.remove(request.user.brother)
            if not class_taken.brothers.exists():
                class_taken.delete()


    context = {
        'classes_taken': classes_taken,
        'departments': Classes.objects.all().values_list('department', flat=True).distinct,
        'brothers': Brother.objects.all(),
        'filter_department': department,
        'filter_number': number,
        'filter_brother': brother,
        'view': view,
    }

    return render(request, "classes.html", context)


def classes_add(request):
    form = ClassTakenForm(request.POST or None)

    brother = request.user.brother

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.department = instance.department.upper()
            class_taken, created = Classes.objects.get_or_create(department=instance.department, number=instance.number)
            class_taken.brothers.add(brother)
            brother_grades = Grade(grade=form.cleaned_data['grade'], class_taken=class_taken, brother=brother)
            brother_grades.save()
            class_taken.save()
            return HttpResponseRedirect(reverse('dashboard:classes'), brother.pk)

    context = {
        'form': form,
        'brother': brother,
        'title': 'Add a Class',
    }

    return render(request, "model-add.html", context)


class ClassesDelete(DeleteView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ClassesDelete, self).get(request, *args, **kwargs)

    model = Classes
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:classes')
