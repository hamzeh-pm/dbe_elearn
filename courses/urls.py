from django.urls import path

from . import views

app_name = "courses"


urlpatterns = [
    path("manage/", views.CourseManageListView.as_view(), name="manage_course_list"),
    path("add/", views.CourseCreateView.as_view(), name="course_add"),
    path("update/<slug:slug>/", views.CourseUpdateView.as_view(), name="course_update"),
    path("delete/<slug:slug>/", views.CourseDeleteView.as_view(), name="course_delete"),
    path(
        "module_list/<int:course_id>/",
        views.ModuleListView.as_view(),
        name="module_list",
    ),
    path("module/<int:pk>/", views.CourseModuleUpdateView.as_view(), name="module_add"),
    path(
        "content_list/<int:module_id>/",
        views.ContentListView.as_view(),
        name="content_list",
    ),
    path(
        "content/<int:module_id>/<str:model_name>/",
        views.ContentCreateUpdateView.as_view(),
        name="content_add",
    ),
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/<slug:slug>", views.CourseDetailView.as_view(), name="course_detail"),
]
