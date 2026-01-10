from rest_framework import viewsets

from .models import Project
from .serializers import ProjectPolymorphicSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectPolymorphicSerializer
