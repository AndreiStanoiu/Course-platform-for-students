from django.contrib import admin

from .models import Homework, Feedback, Profile, Note, SolvedHomeWork, Course

class ReviewAdmin(admin.ModelAdmin):
    model = Homework
    list_display = ('title', 'due_date', 'student', 'feedback')
    list_filter = ['title', 'student']
    search_fields = ['title']

admin.site.register(Profile)
admin.site.register(Homework)
admin.site.register(Feedback)
admin.site.register(Note)
admin.site.register(SolvedHomeWork)
admin.site.register(Course)