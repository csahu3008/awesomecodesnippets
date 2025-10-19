from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Comment, Ratings
from .serializers import CommentSerializer, RatingSerializer
from tagging.models import Tag, TaggedItem
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(parent=None)  # Only get parent comments by default
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        snippet_id = self.request.query_params.get('snippet', None)
        if snippet_id:
            queryset = queryset.filter(snippet_id=snippet_id)
        return queryset

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        parent_comment = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                parent=parent_comment,
                snippet=parent_comment.snippet
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        parent_comment = self.get_object()
        children = Comment.objects.filter(parent=parent_comment)
        serializer = CommentSerializer(children, many=True)
        return Response(serializer.data)

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Ratings.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Ratings.objects.filter(user=self.request.user)

class TaggedItemsView(APIView):
    def get(self, request, tag):
        try:
            tag_obj = Tag.objects.get(name=tag)
            tagged_snippets = TaggedItem.objects.get_by_model(Snippet, tag_obj)
            serializer = SnippetSerializer(tagged_snippets, many=True)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)