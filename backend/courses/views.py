from rest_framework import viewsets, generics, permissions
from django.contrib.auth import get_user_model
from .models import Course, Enrollment, Lesson, Assignment, AssignmentSubmission, Quiz, Question, QuizResult
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer, AssignmentSerializer, AssignmentSubmissionSerializer, QuizSerializer, QuizResultSerializer
from users.serializers import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsInstructorOrAdmin

User = get_user_model()

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class EnrollView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(enrollments__user=self.request.user)

class CourseEnrolledUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['pk']
        return User.objects.filter(enrollments__course_id=course_id)

class UnenrollView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        course_id = self.kwargs['pk']
        enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
        if enrollment:
            enrollment.delete()
            return Response({'detail': 'Unenrolled successfully.'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuizResultViewSet(viewsets.ModelViewSet):
    queryset = QuizResult.objects.all()
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]
