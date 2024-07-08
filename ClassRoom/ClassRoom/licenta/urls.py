from django.urls import path
from licenta import views

urlpatterns = [
    path('', views.index, name='index'),
    path('course_detail/<str:pk>', views.course_detail, name='course_detail'),
    path('course/<str:course_id>/upload_note/', views.upload_note, name='upload_note'),
    path('course/<str:course_id>/upload_homework/', views.upload_homework, name='upload_homework'),
    path('login/', views.loginPage,name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser,name="logout"),
    path('note/<str:pk>/', views.note_detail, name='note_detail'),
    path('note/<str:pk>/delete/', views.delete_note, name='delete_note'), 
    path('homework/<str:pk>/', views.homework_detail, name='homework_detail'),\
    path('homework/<str:homework_id>/upload_solved/', views.upload_solved_homework, name='upload_solved'),
    path('homework/<str:homework_id>/delete_solved/<int:solved_homework_id>/', views.delete_solved_homework, name='delete_solved_homework'),
    path('teacher/grades/<str:course_id>/', views.teacher_grades, name='teacher_grades'),
    path('student/grades/<str:course_id>/', views.student_grades, name='student_grades'),

]
