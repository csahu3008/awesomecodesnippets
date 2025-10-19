from rest_framework import serializers
from .models import Comment, Ratings
from snippets.serializers import CustomUserSerializer

class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'snippet', 'user', 'detail', 'date_commented', 'parent', 'replies']

    def get_replies(self, obj):
        if not obj.parent:  # Only get replies for parent comments
            return CommentSerializer(Comment.objects.filter(parent=obj), many=True).data
        return []

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = ['id', 'snippet', 'user', 'point']