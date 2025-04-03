from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .forms import CourseForm, ScheduleForm, EnrollmentForm, EnrollmentUpdateForm
from .models import Course, Schedule, Enrollment
from students.models import Student
from students.views import AdminRequiredMixin

class CourseListView(LoginRequiredMixin, ListView):
    """View to list all courses."""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10

class CourseDetailView(LoginRequiredMixin, DetailView):
    """View to display course details."""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedules'] = self.object.schedules.all()
        context['enrollments'] = self.object.enrollments.all()
        return context

class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """View to create a new course."""
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['schedule_formset'] = inlineformset_factory(
                Course, Schedule, form=ScheduleForm, extra=1
            )(self.request.POST)
        else:
            context['schedule_formset'] = inlineformset_factory(
                Course, Schedule, form=ScheduleForm, extra=1
            )()
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        schedule_formset = context['schedule_formset']

        if form.is_valid() and schedule_formset.is_valid():
            self.object = form.save()
            schedule_formset.instance = self.object
            schedule_formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class CourseUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """View to update course information."""
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['schedule_formset'] = inlineformset_factory(
                Course, Schedule, form=ScheduleForm, extra=1
            )(self.request.POST, instance=self.object)
        else:
            context['schedule_formset'] = inlineformset_factory(
                Course, Schedule, form=ScheduleForm, extra=1
            )(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        schedule_formset = context['schedule_formset']

        if form.is_valid() and schedule_formset.is_valid():
            self.object = form.save()
            schedule_formset.instance = self.object
            schedule_formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class CourseDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """View to delete a course."""
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

class EnrollmentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """View to list all enrollments."""
    model = Enrollment
    template_name = 'courses/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 10

class EnrollmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """View to create a new enrollment."""
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'courses/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')

class EnrollmentUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """View to update enrollment information."""
    model = Enrollment
    form_class = EnrollmentUpdateForm
    template_name = 'courses/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')

class EnrollmentDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """View to delete an enrollment."""
    model = Enrollment
    template_name = 'courses/enrollment_confirm_delete.html'
    success_url = reverse_lazy('enrollment_list')

class StudentEnrollmentListView(LoginRequiredMixin, ListView):
    """View for students to see their enrollments."""
    model = Enrollment
    template_name = 'courses/student_enrollment_list.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        if self.request.user.is_student:
            student = get_object_or_404(Student, user=self.request.user)
            return Enrollment.objects.filter(student=student)
        return Enrollment.objects.none()