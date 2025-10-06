from django.urls import path, include
from . import views
from .views import (
    CourseViewSet, EnrollView, MyEnrollmentsView,
    CourseEnrolledUsersView, UnenrollView, LessonViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet, QuizViewSet, QuizResultViewSet
)
from rest_framework.routers import DefaultRouter

# ViewSet-based API routes
router = DefaultRouter()
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'viewset', CourseViewSet, basename='course')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'assignment-submissions', AssignmentSubmissionViewSet, basename='assignment-submission')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-results', QuizResultViewSet, basename='quiz-result')

# URL patterns
urlpatterns = [
    # Include ViewSet routes
    path('api/', include(router.urls)),
    
    # Custom enrollment endpoints
    path('enroll/', EnrollView.as_view(), name='enroll'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my_enrollments'),
    path('<int:pk>/enrolled-users/', CourseEnrolledUsersView.as_view(), name='course_enrolled_users'),
    path('<int:pk>/unenroll/', UnenrollView.as_view(), name='unenroll'),
    
    # Frontend-compatible API endpoints
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/progress/', views.update_progress, name='update_progress'),
    
    # User courses and certificates
    path('user/courses/', views.user_courses, name='user_courses'),
    path('user/certificates/', views.user_certificates, name='user_certificates'),
    path('certificates/<int:certificate_id>/download/', views.download_certificate, name='download_certificate'),

    # Articles
    path('articles/', views.ArticleListCreateView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<slug:slug>/like/', views.like_article, name='like-article'),
    
    # Webinars
    path('webinars/', views.WebinarListCreateView.as_view(), name='webinar-list'),
    path('webinars/<slug:slug>/', views.WebinarDetailView.as_view(), name='webinar-detail'),
    path('webinars/<slug:slug>/register/', views.register_webinar, name='register-webinar'),
    path('webinars/<slug:slug>/unregister/', views.unregister_webinar, name='unregister-webinar'),
]

