from rest_framework import serializers
from .models import Snippet, CustomUser, BookMark
from tagging.models import Tag as TagModel


class TagListField(serializers.Field):
    """Handle django-tagging TagField: represent as list and accept list or comma string."""
    def to_representation(self, value):
        # When serializing a single model instance DRF passes the model field
        # value (often a comma-separated string) as `value`. For list views
        # the parent.instance can be a queryset, so we can't rely on it.
        # Handle common cases:
        # 1) If value is a string (stored TagField), split and return list.
        # 2) If we have the parent instance (single model), use tagging API.
        # 3) Fallback to empty list.
        try:
            if isinstance(value, str):
                cleaned = [t.strip() for t in value.split(',') if t.strip()]
                return cleaned

            obj = getattr(self.parent, 'instance', None)
            if obj is None:
                return []

            # If parent.instance is a queryset, try to find the specific
            # object by matching primary key if available
            if not hasattr(obj, '__class__') or isinstance(obj, (list, tuple)):
                # Can't resolve object here; return empty list
                return []

            tags = TagModel.objects.get_for_object(obj)
            return [t.name for t in tags]
        except Exception:
            return []

    def to_internal_value(self, data):
        if isinstance(data, list):
            cleaned = [str(x).strip() for x in data if x is not None and str(x).strip() != '']
            return ','.join(cleaned)
        if isinstance(data, str):
            return data
        raise serializers.ValidationError('Tags must be a list of strings or a comma-separated string')

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']

class SnippetSerializer(serializers.ModelSerializer):
    coder = CustomUserSerializer(read_only=True)
    tags = TagListField(required=False)
    bookmarked = serializers.SerializerMethodField(read_only=True)     # <= new field
    class Meta:
        model = Snippet
        fields = ['id', 'title', 'description', 'code', 'language', 'coder', 'publication_date', 'updated_date', 'tags', 'style', 'highlighted_code','bookmarked']

    def get_bookmarked(self, obj):
        request = self.context.get('request', None)
        if not request or request.user.is_anonymous:
            return False
        return BookMark.objects.filter(snippet=obj, user=request.user).exists()
    
    def to_representation(self, instance):
        """Always populate tags from django-tagging so list/detail behave the same."""
        data = super().to_representation(instance)
        try:
            tags = TagModel.objects.get_for_object(instance)
            data['tags'] = [t.name for t in tags]
        except Exception:
            # Fallback to stored string on the model
            raw = getattr(instance, 'tags', '')
            if isinstance(raw, str) and raw:
                data['tags'] = [t.strip() for t in raw.split(',') if t.strip()]
            else:
                data['tags'] = []
        return data

class BookMarkSerializer(serializers.ModelSerializer):
    snippet = SnippetSerializer(read_only=True)
    
    class Meta:
        model = BookMark
        fields = ['id', 'snippet', 'user', 'date_bookmarked']