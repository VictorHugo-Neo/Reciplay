from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from account.models import Profile
from .models import Quiz, Category
from django.db.models import Q
from quiz.models import QuizSubmission
from django.contrib import messages

# Create your views here.

@login_required(login_url='login')
def all_quiz_view(request):
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    quizzes = Quiz.objects.order_by('-created_at')
    categories = Category.objects.all()

    # Verifica se o usuário já respondeu a cada quiz
    user_submissions = QuizSubmission.objects.filter(user=user_object).values_list('quiz_id', flat=True)
    quizzes_with_status = [
        {'quiz': quiz, 'already_submitted': quiz.id in user_submissions} 
        for quiz in quizzes
    ]

    context = {
        "user_profile": user_profile, 
        "quizzes_with_status": quizzes_with_status, 
        "categories": categories
    }
    return render(request, 'all-quiz.html', context)
@login_required(login_url='login')
def search_view(request, category):
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    if request.GET.get('q'):
        q = request.GET.get('q')
        query = Q(title__icontains=q) | Q(description__icontains=q)
        quizzes = Quiz.objects.filter(query).order_by('-created_at')
    elif category != " ":
        quizzes = Quiz.objects.filter(category__name=category).order_by('-created_at')
    else:
        quizzes = Quiz.objects.order_by('-created_at')

    user_submissions = QuizSubmission.objects.filter(user=user_object).values_list('quiz_id', flat=True)
    quizzes_with_status = [
        {'quiz': quiz, 'already_submitted': quiz.id in user_submissions}
        for quiz in quizzes
    ]

    categories = Category.objects.all()

    context = {
        "user_profile": user_profile, 
        "quizzes_with_status": quizzes_with_status, 
        "categories": categories
    }
    return render(request, 'all-quiz.html', context)

@login_required(login_url='login')
def quiz_view(request, quiz_id):

    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    quiz = Quiz.objects.filter(id=quiz_id).first()

    total_questions = quiz.question_set.all().count()

    if request.method == "POST":
        
        # Get the score
        score = int(request.POST.get('score', 0))

        # Check if the user has already submiited the quiz
        if QuizSubmission.objects.filter(user=request.user, quiz=quiz).exists():
            messages.success(request, f"Você acertou {score} de {total_questions} questões ")
            return redirect('quiz', quiz_id)
        
        # save the new quiz submission
        submission = QuizSubmission(user=request.user, quiz=quiz, score=score)
        submission.save()

        # show the result in message
        messages.success(request,f"Questionário enviado com sucesso. Você tem {score} de {total_questions}")
        return redirect('quiz', quiz_id)

    if quiz != None:
        context = {"user_profile": user_profile, "quiz": quiz}
    else:
        return redirect('all_quiz')
    return render(request, 'quiz.html', context)