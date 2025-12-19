from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import uuid


# ================= USER MODEL =================
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role='teacher'):
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password, role='teacher')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.email})"


# ================= QUIZ =================
class Quiz(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quiz_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    time_limit = models.IntegerField(help_text="Time in minutes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    num_of_qus = models.IntegerField()
    review_on = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.teacher.name}"


# ================= QUESTION =================
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField(
        choices=[
            (1, 'Option1'),
            (2, 'Option2'),
            (3, 'Option3'),
            (4, 'Option4')
        ]
    )
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.text


# ================= QUIZ ATTEMPT =================
class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student_name = models.CharField(max_length=100)
    email = models.EmailField()
    roll_number = models.CharField(max_length=20)
    started_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['quiz', 'email']

    def __str__(self):
        return f"{self.student_name} - {self.score}"


# ================= ANSWER =================
class Answer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=10)
    is_correct = models.BooleanField(default=False)
