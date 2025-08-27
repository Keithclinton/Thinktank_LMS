from django.urls import path
from .views import (
    CourseViewSet, EnrollView, MyEnrollmentsView,
    CourseEnrolledUsersView, UnenrollView, LessonViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet, QuizViewSet, QuizResultViewSet
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'', CourseViewSet, basename='course')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'assignment-submissions', AssignmentSubmissionViewSet, basename='assignment-submission')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-results', QuizResultViewSet, basename='quiz-result')

urlpatterns = router.urls + [
    path('enroll/', EnrollView.as_view(), name='enroll'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my_enrollments'),
    path('<int:pk>/enrolled-users/', CourseEnrolledUsersView.as_view(), name='course_enrolled_users'),
    path('<int:pk>/unenroll/', UnenrollView.as_view(), name='unenroll'),
]
