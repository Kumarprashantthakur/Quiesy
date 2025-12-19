from django.shortcuts import render , get_object_or_404
from django.db.models import Avg, Count

from django.shortcuts import render, redirect , HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as log
from .forms import TeacherRegisterForm, TeacherLoginForm
from django.shortcuts import render, redirect
from .forms import QuizForm, QuestionFormSet
from django.forms import inlineformset_factory
from .models import Quiz, Question , QuizAttempt , Answer
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from datetime import timedelta
from django.contrib.auth import login
def home(request):
    return render(request, 'app/home.html')
@login_required
def teacher_dashboard(request):
    quizzes = Quiz.objects.filter(teacher=request.user).order_by('-created_at')
    if request.method == 'POST':
        quiz_id = request.POST.get("quiz_id")
        quiz = get_object_or_404(Quiz, id=quiz_id, teacher=request.user)
        quiz.review_on = "review_on" in request.POST
        quiz.save()
    return render(request, 'app/dashboard.html', {'quizzes': quizzes})



def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = TeacherRegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = TeacherLoginForm()
    return render(request, 'auth/login.html', {'form': form})
@login_required
def teacher_logout_confirm(request):
    return render(request , 'auth/confirm_logout.html')

@login_required
def logout(request):
    if request.method == 'POST':
        log(request)
        return redirect('teacher_login') 
    return redirect('teacher_logout_confirm')  # If someone tries GET directly


@login_required
def create_quiz_view(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.teacher = request.user
            quiz.save()
            return redirect('dashboard')
    else:
        quiz_form = QuizForm()
    
    return render(request, 'app/create_quiz.html', {'quiz_form': quiz_form})


@login_required
def delete_quiz(request , quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, teacher=request.user)
    if request.method == 'POST':
         quiz.delete()
         return redirect('dashboard')
    return render(request, 'app/quiz_confirm_delete.html', {'quiz': quiz})

@login_required
def add_questions_view(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    remaining =quiz.num_of_qus -  quiz.questions.count()
    if remaining>0:
        QuestionFormSet = inlineformset_factory(
            Quiz,
            Question,
            fields=['text', 'option1', 'option2', 'option3', 'option4', 'correct_option', 'marks'],
            extra=remaining,
            can_delete=False
        )

        if request.method == 'POST':
            formset = QuestionFormSet(request.POST, instance=quiz)
            if formset.is_valid():
                formset.save()
                return redirect('dashboard') 
        else:
            formset = QuestionFormSet(instance=quiz)

        return render(request, 'app/add_questions.html', {
            'quiz': quiz,
            'formset': formset
        })
    else:
        messages.warning(request, "You have already added all questions.")
        return redirect('dashboard')
    

# def start_quiz(request , code):
#     quiz = get_object_or_404(Quiz , quiz_code = code)
#     if request.method == 'POST':
#         email = request.POST['email']
#         if QuizAttempt.objects.filter(quiz = quiz , email = email).exists():
#             return HttpResponse("you have already attempted this quiz")
#         attempt = QuizAttempt.objects.create(
#             quiz = quiz,
#             student_name = request.POST['name'],
#             email = email,
#             roll_number = request.POST['roll'],

#         )
#         return redirect('take_quiz' , attempt_id = attempt.id)
#     context = {
#         'quiz' : quiz
#     }
#     return render(request , 'app/quiz_start.html' , context)

# def take_quiz(request , attempt_id):
#     attempt = get_object_or_404(QuizAttempt , id = attempt_id)
#     questions = list(attempt.quiz.questions.all())
#     total_questions = len(questions)
#     q_index = int(request.GET.get('q' , 0))
#     if 'quiz_answers' not in request.session:
#         request.session['quiz_answers'] = {}
#     if request.method == 'POST':
#         selected_option = request.POST.get('selected_option')
#         question_id = str(questions[q_index].id)
#         request.session['quiz_answers'][question_id] = selected_option
#         request.session.modified = True
#         if q_index + 1 < total_questions:
#             return redirect(f"{request.path}?q={q_index + 1}")
#         else:
#             score = 0
#             for q in questions:
#                 selected = request.session['quiz_answers'].get(str(q.id))
#                 is_correct = (int(selected) == q.correct_option)
#                 Answer.objects.create(
#                     attempt = attempt,
#                     question = q,
#                     selected_option = selected, 
#                     is_correct = is_correct,
#                 )
#                 if is_correct:
#                     score+=1
#         attempt.score = score
#         attempt.completed_at = timezone.now()
#         attempt.save()
#         del request.session['quiz_answers']
#         request.session.flush()
#         return redirect('quiz_result', attempt_id=attempt.id)
#     context = {
#         'question':questions[q_index],
#         'q_index':q_index,
#         'total':total_questions,
#     }
#     return render(request , 'app/take_quiz.html',context)
    

def quiz_score(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    return render(request, 'app/quiz_score.html', {'attempt': attempt})

def quiz_review(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    return render(request, 'app/quiz_review.html', {'attempt': attempt})


# def start_quiz(request, code):
#     quiz = get_object_or_404(Quiz, quiz_code = code)

#     if request.method == "POST":
#         action = request.POST.get("action")

#         # -------------------
#         # START QUIZ FORM
#         # -------------------
#         if action == "start_quiz":
#             name = request.POST.get("name")
#             email = request.POST.get("email")
#             roll = request.POST.get("roll")
#             password = request.POST.get("password")

#             # Password check
#             if quiz.password and password.strip() != quiz.password.strip():
#                 messages.error(request, "Incorrect password")
#                 return redirect("start_quiz", quiz_id=quiz.id)
            
#             if QuizAttempt.objects.filter(quiz=quiz, email=email).exists():
#                 messages.error(request, "You have already attempted this quiz with this email.")
#                 return redirect("start_quiz", code=quiz.quiz_code)

#             # Attempt create
#             attempt = QuizAttempt.objects.create(
#                 quiz=quiz,
#                 student_name=name,
#                 email=email,
#                 roll_number=roll
#             )
#             request.session['quiz_attempt_id'] = attempt.id
#             request.session['quiz_answers'] = {}
#             request.session['current_q_index'] = 0
#             return redirect("take_quiz", attempt_id=attempt.id)

#         elif action == "review_quiz":
#             name = request.POST.get("name")
#             email = request.POST.get("email")
#             roll = request.POST.get("roll")

#             try:
#                 attempt = QuizAttempt.objects.get(
#                     quiz=quiz,
#                     student_name=name,
#                     email=email,
#                     roll_number=roll
#                 )
#                 return redirect("quiz_review", attempt_id=attempt.id)
#             except QuizAttempt.DoesNotExist:
#                 messages.error(request, "No attempt found with these details")
#                 return redirect("start_quiz", code=quiz.quiz_code)

#     return render(request, "app/quiz_start.html", {"quiz": quiz})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Quiz, QuizAttempt
from django.urls import reverse

def start_quiz(request, code):
    quiz = get_object_or_404(Quiz, quiz_code=code)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "start_quiz":
            name = request.POST.get("name")
            email = request.POST.get("email")
            roll = request.POST.get("roll")
            password = request.POST.get("password", "").strip()

            # -------------------------
            # AJAX password check support
            # -------------------------
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                if quiz.password and password != quiz.password:
                    return JsonResponse({'ok': False, 'message': 'Password is wrong'}, status=200)
                if QuizAttempt.objects.filter(quiz=quiz, email=email).exists():
                    return JsonResponse({'ok': False, 'message': 'You have already attempted this quiz with this email.'})
                # Create attempt
                attempt = QuizAttempt.objects.create(
                    quiz=quiz,
                    student_name=name,
                    email=email,
                    roll_number=roll
                )
                request.session['quiz_attempt_id'] = attempt.id
                request.session['quiz_answers'] = {}
                request.session['current_q_index'] = 0
                redirect_url = reverse('take_quiz', kwargs={'attempt_id': attempt.id})
                return JsonResponse({'ok': True, 'redirect_url': redirect_url})

            # -------------------------
            # Non-AJAX fallback
            # -------------------------
            if quiz.password and password != quiz.password:
                messages.error(request, "Incorrect password")
                return redirect("start_quiz", code=quiz.quiz_code)

            if QuizAttempt.objects.filter(quiz=quiz, email=email).exists():
                messages.error(request, "You have already attempted this quiz with this email.")
                return redirect("start_quiz", code=quiz.quiz_code)

            attempt = QuizAttempt.objects.create(
                quiz=quiz,
                student_name=name,
                email=email,
                roll_number=roll,
                started_at=timezone.now(),
                end_time=timezone.now() + timedelta(minutes=quiz.time_limit)
            )
            request.session['quiz_attempt_id'] = attempt.id
            request.session['quiz_answers'] = {}
            request.session['current_q_index'] = 0
            return redirect("take_quiz", attempt_id=attempt.id)

        elif action == "review_quiz":
            name = request.POST.get("name")
            email = request.POST.get("email")
            roll = request.POST.get("roll")

            try:
                attempt = QuizAttempt.objects.get(
                    quiz=quiz,
                    student_name=name,
                    email=email,
                    roll_number=roll
                )
                return redirect("quiz_review", attempt_id=attempt.id)
            except QuizAttempt.DoesNotExist:
                messages.error(request, "No attempt found with these details")
                return redirect("start_quiz", code=quiz.quiz_code)

    return render(request, "app/quiz_start.html", {"quiz": quiz})

@never_cache
def take_quiz(request, attempt_id):

    # -----------------------------
    # Session security
    # -----------------------------
    if request.session.get('quiz_attempt_id') != attempt_id:
        return HttpResponse("Session expired or invalid access")

    attempt = get_object_or_404(QuizAttempt, id=attempt_id)

    # -----------------------------
    # Set quiz END TIME only once
    # -----------------------------
    if not attempt.end_time:
        minutes = attempt.quiz.time_limit or 0
        attempt.end_time = attempt.started_at + timedelta(minutes=minutes)
        attempt.save()

    # -----------------------------
    # Auto-submit if time is over
    # -----------------------------
    now = timezone.now()
    if now >= attempt.end_time:
        attempt.completed_at = now
        attempt.save()
        return redirect('quiz_score', attempt_id=attempt.id)

    # -----------------------------
    # Remaining seconds (MAIN FIX)
    # -----------------------------
    remaining_seconds = int((attempt.end_time - now).total_seconds())
    if remaining_seconds < 0:
        remaining_seconds = 0

    # -----------------------------
    # Questions logic
    # -----------------------------
    questions = list(attempt.quiz.questions.all())
    total_questions = len(questions)
    q_index = int(request.GET.get('q', 0))

    if q_index < request.session.get('current_q_index', 0):
        return redirect(f"{request.path}?q={request.session.get('current_q_index', 0)}")

    # -----------------------------
    # Save answer
    # -----------------------------
    if request.method == 'POST':
        selected_option = request.POST.get('selected_option', "-1")
        question_id = str(questions[q_index].id)

        request.session['quiz_answers'][question_id] = selected_option
        request.session['current_q_index'] = q_index + 1
        request.session.modified = True

        # Next question
        if q_index + 1 < total_questions:
            return redirect(f"{request.path}?q={q_index + 1}")

        # -----------------------------
        # Submit quiz
        # -----------------------------
        score = 0
        for q in questions:
            selected = request.session['quiz_answers'].get(str(q.id), "-1")
            is_correct = int(selected) == q.correct_option

            Answer.objects.create(
                attempt=attempt,
                question=q,
                selected_option=selected,
                is_correct=is_correct
            )

            if is_correct:
                score += q.marks

        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()

        # Clear session
        for key in ['quiz_answers', 'current_q_index', 'quiz_attempt_id']:
            request.session.pop(key, None)

        return redirect('quiz_score', attempt_id=attempt.id)

    # -----------------------------
    # Render page with timer
    # -----------------------------
    return render(request, 'app/take_quiz.html', {
        'question': questions[q_index],
        'q_index': q_index,
        'total': total_questions,
        'remaining_seconds': remaining_seconds,  # ✅ THIS FIXES TIMER
    })

def student_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, teacher=request.user)
    attempts = QuizAttempt.objects.filter(quiz=quiz).order_by('-started_at')
    return render(request,'app/student_results.html', {
        'quiz': quiz,
        'attempts': attempts
    })

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import Quiz, QuizAttempt

def download_results_pdf(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(quiz=quiz)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{quiz.title}_results.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"Quiz Results: {quiz.title}")

    y -= 40
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Name")
    p.drawString(200, y, "Email")
    p.drawString(380, y, "Score")

    y -= 20
    p.setFont("Helvetica", 10)

    for attempt in attempts:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(50, y, attempt.student_name)
        p.drawString(200, y, attempt.email)
        p.drawString(380, y, str(attempt.score if attempt.score is not None else "Not Attempted"))
        y -= 18

    p.showPage()
    p.save()
    return response



def quiz_rank_card(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        completed_at__isnull=False
    ).order_by('-score', 'completed_at')

    ranked_students = []
    rank = 0
    last_score = None

    for index, attempt in enumerate(attempts):
        if attempt.score != last_score:
            rank = index + 1

        ranked_students.append({
            'rank': rank,
            'name': attempt.student_name,  # ✅ FIXED
            'score': attempt.score
        })

        last_score = attempt.score

    top_3 = ranked_students[:3]

    return render(request, 'app/rank_card.html', {
        'quiz': quiz,
        'top_3': top_3,
        'all_ranks': ranked_students
    })


@login_required
def attendance_dashboard(request):
    quizzes = Quiz.objects.filter(teacher=request.user)

    attendance_data = []

    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(quiz=quiz)

        students = {}
        for attempt in attempts:
            students[attempt.email] = {
                'name': attempt.student_name,
                'email': attempt.email,
                'roll': attempt.roll_number, 
                'status': 'Present',
                'attempts': QuizAttempt.objects.filter(
                    quiz=quiz, email=attempt.email
                ).count()
            }

        attendance_data.append({
            'subject': quiz.title,
            'total_students': len(students),
            'students': students.values()
        })

    return render(request, 'app/attendance_dashboard.html', {
        'attendance_data': attendance_data
    })


from django.db.models import Avg
from .models import QuizAttempt, Quiz

from django.db.models import Avg
from .models import QuizAttempt, Quiz

def student_dashboard(request):
    email = request.GET.get("email")

    # 1️⃣ Show login page if email not provided
    if not email:
        return render(request, "auth/student_login.html")

    # 2️⃣ Fetch attempts
    attempts = QuizAttempt.objects.filter(
        email=email,
        completed_at__isnull=False
    )

    # ✅ GET STUDENT NAME
    student_name = (
        attempts.first().student_name
        if attempts.exists()
        else "Student"
    )

    total_quizzes = attempts.count()
    average_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0

    # 3️⃣ Attendance %
    total_available_quizzes = Quiz.objects.count()
    attendance_percentage = 0
    if total_available_quizzes > 0:
        attendance_percentage = round(
            (total_quizzes / total_available_quizzes) * 100, 2
        )

    # 4️⃣ SHOW DASHBOARD
    return render(request, "app/student_dashboard.html", {
        'student_name': student_name,   # ✅ ADDED
        'email': email,
        'attempts': attempts,
        'total_quizzes': total_quizzes,
        'average_score': average_score,
        'attendance_percentage': attendance_percentage
    })
