from django.shortcuts import render
from django.views.generic import ListView

from .models import Course

# Create your views here.


class CourseManageListView(ListView):
    queryset = Course.objects.all()
    template_name = "courses/course_list.html"
    context_object_name = "course_list"
