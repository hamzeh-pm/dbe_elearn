from django.urls import path

from . import views

app_name = "courses"


urlpatterns = [
    path("manage/", views.CourseManageListView.as_view(), name="manage_course_list")
]
