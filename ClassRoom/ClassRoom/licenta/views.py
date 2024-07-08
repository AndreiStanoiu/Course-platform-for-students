from django.shortcuts import render,redirect,get_object_or_404
from .models import Note, Homework, Feedback, Course, SolvedHomeWork, Profile
from .forms import CreateUserForm, ProfileForm, NoteForm, HomeWorkForm, SolvedHomeWorkForm, GiveFeedback
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError

@unauthenticated_user
def loginPage(request):
    
    if request.method =='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.info(request,"Username or password are incorrect")
            return redirect('login')
    context={}
    return render(request,'login.html',context)

@unauthenticated_user
def registerPage(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if profile.is_bachelor and profile.is_masters:
                messages.error(request,'A student cannot be both a bachelor and a master.')
                return redirect('register')
            if (not profile.is_bachelor or not profile.is_masters) and profile.user_type in  ['student', 'Student']:
                messages.error(request,'A student must be bachelors or masters')
                return redirect('register')
            if profile.user_type in  ['Teacher', 'teacher'] and profile.year:
                messages.error(request,'A teacher cannot have a study year.')
                return redirect('register')
            if profile.is_bachelor and (profile.year not in [1, 2, 3, 4]):
                messages.error(request,'Year should be betwwen 1 and 4')
                return redirect('register')
            if profile.is_masters and (profile.year not in [1, 2]):
                messages.error(request,'Year should be betwwen 1 and 2')
                return redirect('register')

            if profile_form.is_valid():
                user.save()
                profile.save()
                messages.success(request, 'Account was created for ' + user.username)
                print('Account created succesfully')
                return redirect('login')
            else:
                user.delete()
                profile.delete()
                print("Profile Form Errors:", profile_form.errors)
                return redirect('register')

        else:
            messages.error(request, 'Account creation failed')
            messages.error(request, 'Account creation failed')

    else:
        user_form = CreateUserForm()
        profile_form = ProfileForm()
        

    context = {
        'form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')


def index(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        
        courses = profile.courses.all()
        if courses is None:
            courses = []
        return render(request, 'courses.html', {'courses': courses})
    else:
        return render(request, 'courses.html', {'courses': []})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    students = Profile.objects.filter(user_type='student')
    course_students = course.profiles.filter(user_type='student')
    if request.user.profile.courses.filter(pk=pk).exists():
        notes = Note.objects.filter(course=course)
        homeworks = Homework.objects.filter(course=course)
        if request.user.profile.user_type == 'teacher':
            feedbacks = Feedback.objects.filter(teacher=request.user)

            
            if request.method == 'POST':
                student_id = request.POST.get('student_id')
                if student_id:
                    student_profile = Profile.objects.get(pk=student_id)
                    course.profiles.add(student_profile)  # Add student to the course
                    return redirect('course_detail', pk=pk)  # Redirect to the same page

        if request.user.profile.user_type == 'student':
            profiles = course.profiles.filter()
            for profile in profiles:
                if profile.user_type == 'teacher':
                    teacher = profile.user
                    break
            feedbacks = Feedback.objects.filter(student=request.user, teacher=teacher)
            if request.method == 'POST':
                feedback_content = request.POST.get('feedback_content')
                if feedback_content:  # Check if feedback content is not empty
                    new_Feedback = Feedback(student=request.user, teacher=teacher, content=feedback_content)
                    new_Feedback.save()
                    return redirect('course_detail', pk=pk)  # Redirect to the same page
        return render(request, 'course_detail.html', {
            'course': course,
            'notes': notes,
            'homeworks': homeworks,
            'feedbacks': feedbacks,
            'students': students,
            'course_students': course_students,
        })
    else:
        raise PermissionDenied

@login_required(login_url='login')
def upload_note(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.profile.courses.filter(pk=course_id).exists():
        if request.method == 'POST':
            form = NoteForm(request.POST, request.FILES)
            if form.is_valid():
                note = form.save(commit=False)
                note.teacher = request.user
                note.course = course
                note.save()
                # Process form data and save note
                # Redirect to main page after successful submission
                return redirect('course_detail', pk=course_id)  # Adjust the name of the main page URL if necessary
        else:
            form = NoteForm()
        return render(request, 'upload_note.html', {'form': form, "course": course})
    else:
        raise PermissionDenied

@login_required
def note_detail(request, pk):

    note = get_object_or_404(Note, pk=pk)
    if request.user.profile.courses.filter(pk=note.course.pk).exists():
        return render(request, 'note_detail.html', {'note': note})
    else:
        raise PermissionDenied

@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if request.user.profile.courses.filter(pk=note.course.pk).exists():
        if request.user.profile.user_type == 'teacher':
            note.delete()
            return redirect('course_detail', pk=note.course.pk)
        else:
            return redirect('note_detail', pk=pk)
    else:
        raise PermissionDenied



@login_required(login_url='login')
def upload_homework(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.profile.courses.filter(pk=course.pk).exists():
        if request.method == 'POST':
            form = HomeWorkForm(request.POST, request.FILES)
            if form.is_valid():
                homework = form.save(commit=False)
                homework.course = course
                homework.save()
                
                # Process form data and save note
                # Redirect to main page after successful submission
                return redirect('course_detail', pk=course_id)  # Adjust the name of the main page URL if necessary
        else:
            form = HomeWorkForm()
        return render(request, 'upload_homework.html', {'form': form, "course": course})
    else:
        raise PermissionDenied
    

@login_required
def homework_detail(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    if request.user.profile.courses.filter(pk=homework.course.pk).exists():
        user_type = request.user.profile.user_type
        if user_type == 'teacher':
            solved_homeworks = SolvedHomeWork.objects.filter(homework=homework)
            if request.method == 'POST':
                solved_homework_id = request.POST.get('solved_homework_id')
                grade = request.POST.get('grade')
                solved_homework = SolvedHomeWork.objects.get(pk=solved_homework_id)
                solved_homework.grade = grade
                solved_homework.save()

                # Redirect to avoid re-submitting the form on refresh
                return redirect('homework_detail', pk=pk)

        else:
            solved_homeworks = SolvedHomeWork.objects.filter(homework=homework, student=request.user) 

        
        context = {
            'homework': homework,
            'solved_homeworks': solved_homeworks,
        }
        return render(request, 'homework_detail.html', context)
    else:
        raise PermissionDenied


@login_required
def upload_solved_homework(request, homework_id):
    
    homework = get_object_or_404(Homework, id=homework_id)
    if request.user.profile.courses.filter(pk=homework.course.pk).exists():
        if timezone.now() > homework.due_date:
            return render(request, 'upload_solved_homework.html', {'error': 'Submission closed. Due date has passed.'})
        
        if request.method == 'POST':
            form = SolvedHomeWorkForm(request.POST, request.FILES)
            if form.is_valid():
                solved_homework = form.save(commit=False)
                solved_homework.homework = homework
                solved_homework.student = request.user
                solved_homework.save()
                
                return redirect('homework_detail', pk=homework_id)
        else:
            form = SolvedHomeWorkForm()
        
        return render(request, 'upload_solved_homework.html', {'form': form, 'homework': homework})
    else:
        raise PermissionDenied

@login_required
def delete_solved_homework(request, homework_id, solved_homework_id):
    solved_homework = get_object_or_404(SolvedHomeWork, id=solved_homework_id, homework_id=homework_id, student=request.user)
    if request.user.profile.courses.filter(pk=solved_homework.homework.course.id).exists():
        solved_homework.delete()
        return redirect('homework_detail', pk=homework_id)
    else:
        raise PermissionDenied

@login_required
def teacher_grades(request, course_id):
    if request.user.profile.user_type == 'teacher' and request.user.profile.courses.filter(pk=course_id).exists():
        course_homeworks = Homework.objects.filter(course_id=course_id)
        solved_hws = SolvedHomeWork.objects.filter(homework__in = course_homeworks)
        context = {
        'course_id': course_id,
        'solved_homeworks': solved_hws
        }
        return render(request, 'teacher_grades.html', context)
    else:
        return redirect('index')


@login_required
def student_grades(request, course_id):
    if request.user.profile.courses.filter(pk=course_id).exists():
        student = request.user
        course_homeworks = Homework.objects.filter(course_id=course_id)
        solved_homeworks = SolvedHomeWork.objects.filter(student=student, homework__in=course_homeworks)
        print(student_grades)
        context = {
            'course_id': course_id,
            'solved_homeworks': solved_homeworks,
        }
        return render(request, 'student_grades.html', context)
    else:
        return redirect('index')