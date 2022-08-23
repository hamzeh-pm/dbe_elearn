from readline import get_completer_delims

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms.models import modelform_factory
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import TemplateResponseMixin, View

from .forms import ModuleFormset
from .models import Content, Course, Module


# Create your views here.
class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ["subject", "title", "slug", "overview"]
    success_url = reverse_lazy("courses:manage_course_list")


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = "courses/course_form.html"


class CourseManageListView(OwnerCourseMixin, ListView):
    template_name = "courses/course_list.html"
    context_object_name = "course_list"
    permission_required = "courses.view_course"


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = "courses.add_course"


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = "courses.change_course"


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = "courses/course_delete.html"
    permission_required = "courses.delete_course"


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = "courses/module_form.html"
    course = None

    def get_formset(self, data=None):
        return ModuleFormset(instance=self.course, data=data)

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.course = get_object_or_404(Course, id=kwargs["pk"], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({"course": self.course, "formset": formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("courses:manage_course_list")

        return self.render_to_response({"course": self.course, "formset": formset})


class ModuleListView(ListView):
    model = Module
    template_name: str = "courses/module_list.html"
    context_object_name = "module_list"

    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        return super().get_queryset().filter(course=course)


class ContentListView(ListView):
    model = Content
    template_name: str = "courses/content_list.html"
    context_object_name = "content_list"

    def get_queryset(self):
        module = get_object_or_404(Module, pk=self.kwargs["module_id"])
        return super().get_queryset().filter(module=module)


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = "courses/content_form.html"

    def get_model(self, model_name):
        if model_name in ["text", "video", "image", "file"]:
            return apps.get_model("courses", model_name)

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=["owner", "order", "created", "updated"]
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        self.model = self.get_model(model_name)
        return super().dispatch(request, module_id, model_name)

    def get(self, request, module_id, model_name):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({"form": form, "object": self.obj})

    def post(self, request, module_id, model_name):
        form = self.get_form(
            self.model, instance=self.obj, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()

            Content.objects.create(module=self.module, item=obj)
            return redirect("courses:content_list", self.module.id)

        return self.render_to_response({"form": form, "object": self.obj})
