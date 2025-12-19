from django.urls import path 
from django.contrib.auth.views import LogoutView
from . import views 

urlpatterns = [
    path('',views.home, name='home'),
    path('dashboard/' , views.teacher_dashboard , name = 'dashboard') , 
    path('register/', views.teacher_register, name='teacher_register'),
    path('login/', views.teacher_login, name='teacher_login'),
    path('logout/' ,views.teacher_logout_confirm , name = 'teacher_logout_confirm'),
    path("logout/confirm/",views.logout , name="logout"),
    path('dashboard/quizcreate/' , views.create_quiz_view , name='quizcreate'),
    path("dashboard/<int:quiz_id>/quizdelete",views.delete_quiz, name="delete_quiz"),
    path('dashboard/quizcreate/<int:quiz_id>/add-questions/', views.add_questions_view, name='add_questions'),


    path("student/<str:code>/start/", views.start_quiz, name="start_quiz"),
    path("student/<int:attempt_id>/review/", views.quiz_review, name="quiz_review"),

    path('student/<int:attempt_id>/take/', views.take_quiz, name='take_quiz'),
    path('student/<int:attempt_id>/score/',views.quiz_score , name='quiz_score'),
    # path('student/<int:attempt_id>/review/',views.quiz_review , name='quiz_review'),
    path('dashboard/quiz/<int:quiz_id>/result/', views.student_result, name='student_result'),
    path('quiz/<int:quiz_id>/download-pdf/', views.download_results_pdf, name='download_results_pdf'),
    path('quiz/<int:quiz_id>/rank/', views.quiz_rank_card, name='quiz_rank'),
    path('attendance/', views.attendance_dashboard, name='attendance_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    


]
