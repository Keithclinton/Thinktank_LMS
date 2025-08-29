from django.contrib import admin
from .models import Course, Note, Video, Assignment

admin.site.register(Course)
admin.site.register(Note)
admin.site.register(Video)
admin.site.register(Assignment)