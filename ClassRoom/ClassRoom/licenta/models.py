from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Profile(models.Model):
    USER_TYPES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    fullname = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    is_bachelor = models.BooleanField(default=True, null=True, blank=True)
    is_masters = models.BooleanField(default=False, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    courses = models.ManyToManyField(Course, blank=True, related_name='profiles')


    def __str__(self):
        return f'{self.user.username} - {self.user_type}'

    '''
    def clean(self):
        if self.is_bachelor and self.is_masters:
            raise ValidationError('A student cannot be both a bachelor and a master.')
        if (not self.is_bachelor or not self.is_masters) and self.user_type in  ['student', 'Student']:
            raise ValidationError('A student must be bachelors or masters')
        if self.user_type in  ['Teacher', 'teacher'] and self.year:
            raise ValidationError('A teacher cannot have a study year.')
        if self.is_bachelor and (self.year not in [1, 2, 3, 4]):
            raise ValidationError('Year should be betwwen 1 and 4')
        if self.is_masters and (self.year not in [1, 2]):
            raise ValidationError('Year should be betwwen 1 and 2')
    '''

    
class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='notes/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)


    def __str__(self):
        return self.title

class Homework(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateTimeField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='homeworks/', blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    def __str__(self):
        return f'{self.title} - {self.course}'
    

class SolvedHomeWork(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='solved_homeworks')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_solved_homeworks')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='homeworks/', blank=True, null=True)
    grade = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.homework.title} - {self.student}'


class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedbacks')
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    #course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='course_feedback')

    def __str__(self):
        return f'Feedback from {self.student.username} to {self.teacher.username}'


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()