from pygments import lexers,formatters,highlight
from pygments.styles import get_all_styles
from pygments.lexers import get_all_lexers,get_lexer_by_name
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import PermissionDenied
from .models import Snippet, BookMark, CustomUser
from .serializers import SnippetSerializer, BookMarkSerializer, CustomUserSerializer
from tagging.models import Tag, TaggedItem
from pygments.lexers import get_all_lexers
from django.db.models import Count
from django.core.paginator import Paginator
from rest_framework.decorators import api_view

# class LargeResultsSetPagination(PageNumberPagination):
#     page_size = 1000
#     page_size_query_param = 'page_size'
#     max_page_size = 10000

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 4

class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['title', 'description', 'code', 'language']
    ordering_fields = ['publication_date', 'updated_date', 'title']
    ordering = ['-publication_date']  # Default ordering
    pagination_class=StandardResultsSetPagination

    def perform_create(self, serializer):
        # Extract tags (if provided) and save instance
        tags = serializer.validated_data.pop('tags', None) if hasattr(serializer, 'validated_data') else None
        instance = serializer.save(coder=self.request.user)
        if tags is not None:
            # Ensure the model field stores the comma-separated string
            try:
                instance.tags = tags
                instance.save()
            except Exception:
                # If TagField assignment fails for any reason, continue and
                # still update the tagging tables
                pass
            # Update django-tagging tables to reflect tag objects
            Tag.objects.update_tags(instance, tags)
    

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get('user', None)
        language = self.request.query_params.get('language', None)
        tag = self.request.query_params.get('tag', None)

        if user:
            queryset = queryset.filter(coder__username=user)
        if language:
            queryset = queryset.filter(language=language)
        if tag:
            tag_obj = Tag.objects.get(name=tag)
            queryset = Tag.objects.get_by_model(queryset, tag_obj)
            
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, pk=None):
        snippet = self.get_object()
        bookmark, created = BookMark.objects.get_or_create(
            snippet=snippet,
            user=request.user
        )
        if not created:
            bookmark.delete()
            return Response({'status': 'bookmark removed'})
        return Response({'status': 'bookmark added'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tags = serializer.validated_data.pop('tags', None) if 'tags' in serializer.validated_data else None
        self.perform_update(serializer)
        if tags is not None:
            # Update model field and tagging tables
            try:
                instance.tags = tags
                instance.save()
            except Exception:
                pass
            Tag.objects.update_tags(instance, tags)
        return Response(self.get_serializer(instance).data)

class BookMarkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BookMarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['user', 'snippet']
    queryset=BookMark.objects.all()

    # def get_queryset(self):
    #     return BookMark.objects.filter(user=self.request.user)


class TopContributorsView(APIView):
    def get(self, request):
        # annote total snippets by user
        users = (CustomUser.objects
                .annotate(total_snippets=Count('snippet'))
                .order_by('-total_snippets'))
        result = []
        # get top languages used by the author
        for user in users:
            # Aggregate language counts manually
            lang_counts = (
                Snippet.objects
                .filter(coder=user)
                .values('language')
                .annotate(count=Count('language'))
                .order_by('-count')
            )
            top_langs = [l['language'] for l in lang_counts[:3]]
            result.append({
                'id': user.id,
                'username': user.username,
                'last_login':user.last_login,
                'date_joined':user.date_joined,
                'total_snippets': user.total_snippets,
                'top_languages': top_langs
            })

        data =list(result)
        return Response(data)

class LanguageStatsView(APIView):
    def get(self, request):
        # 1️⃣ Group snippets by language
        language_groups = (
            Snippet.objects
            .values('language')
            .annotate(total_snippets=Count('id'))
            .order_by('-total_snippets')
        )

        # Get the highest snippet count for popularity %
        max_snippets = language_groups[0]['total_snippets'] if language_groups else 1

        data = []

        for lang_group in language_groups:
            lang = lang_group['language']
            total_snippets = lang_group['total_snippets']

            # Distinct contributors count
            total_contributors = (
                Snippet.objects
                .filter(language=lang)
                .values('coder')
                .distinct()
                .count()
            )

            # Top 3 contributors for this language
            top_contributors = (
                Snippet.objects
                .filter(language=lang)
                .values('coder__id', 'coder__username')
                .annotate(snippet_count=Count('id'))
                .order_by('-snippet_count')[:3]
            )

            # Recent 3 snippets
            recent_snippets = (
                Snippet.objects
                .filter(language=lang)
                .order_by('-updated_date')
                .values('id', 'title', 'coder__username', 'updated_date')[:3]
            )

            # Popularity (percentage)
            percentage = round((total_snippets / max_snippets) * 100, 2)
            data.append({
                "language": lang,
                "total_snippets": total_snippets,
                "total_contributors": total_contributors,
                "percentage": percentage,
                "recent_snippets": list(recent_snippets),
                "top_contributors": list(top_contributors)
            })

        return Response(data)

class TopLanguagesView(APIView):
    def get(self, request):
        LEXERS = [item for item in get_all_lexers() if item[1]]
        LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
        
        languages_and_counts = {}
        language_counts_qs = (
            Snippet.objects.values('language')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        lang_count_dict = {item['language']: item['count'] for item in language_counts_qs}
        max_total = max(lang_count_dict.values())

        result = []
        for lang, lang_name in LANGUAGE_CHOICES:
            count = lang_count_dict.get(lang, 0)
            result.append({
                'language': lang,
                'display_name': lang_name,
                'count': count,
                "percentage":round((count / max_total) * 100, 2)
            })
        
        result.sort(key=lambda x: x['count'], reverse=True)
        return Response(result)

class LanguageDetailView(APIView):
    def get(self, request, lang):
        query = Snippet.objects.select_related('coder').filter(language=lang)
        total = query.count()
        
        page = request.query_params.get('page', 1)
        paginator = Paginator(query, 6)
        
        try:
            snippets = paginator.page(page)
        except:
            snippets = paginator.page(1)

        serializer = SnippetSerializer(snippets, many=True)
        return Response({
            'snippets': serializer.data,
            'total_snippets': total,
            'current_page': page,
            'total_pages': paginator.num_pages
        })

class UserDetailView(APIView):
    def get(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        snippets = Snippet.objects.filter(coder=user).order_by('-updated_date')
        page = request.query_params.get('page', 1)
        paginator = Paginator(snippets, 5)
        
        try:
            user_snippets = paginator.page(page)
        except:
            user_snippets = paginator.page(1)

        return Response({
            'user': CustomUserSerializer(user).data,
            'snippets': SnippetSerializer(user_snippets, many=True).data,
            'total_snippets': snippets.count(),
            'current_page': page,
            'total_pages': paginator.num_pages
        })

@api_view(['GET'])
def LanguageOptions(request):
    # Get all lexers (languages) from pygments
    LEXERS = [item for item in get_all_lexers() if item[1]]

    # Convert to list of {key, value}
    # LANGUAGE_CHOICES = sorted(
    #     [{"key": item[1][0], "value": item[0]} for item in LEXERS],
    #     key=lambda x: x["value"].lower()
    # )
    LANGUAGE_CHOICES=[
        {
            "key": "python",
            "value": "Python"
        },
         {
            "key": "javascript",
            "value": "JavaScript"
        },
         {
            "key": "typescript",
            "value": "TypeScript"
        },
         {
            "key": "cpp",
            "value": "C++"
        }, {
            "key": "c",
            "value": "C"
        },
        {
            "key": "csharp",
            "value": "C#"
        }, {
            "key": "css",
            "value": "CSS"
        },{
            "key": "html",
            "value": "HTML"
        },  {
            "key": "vue",
            "value": "Vue"
        }, {
            "key": "java",
            "value": "Java"
        },        {
            "key": "bash",
            "value": "Bash"
        },{
            "key": "graphql",
            "value": "GraphQL"
        },

    ]
    # Styles (themes) for syntax highlighting
    STYLE_CHOICES = sorted(
        [{"key": item, "value": item} for item in get_all_styles()],
        key=lambda x: x["value"].lower()
    )

    # Combine into response
    data = {
        "languages": LANGUAGE_CHOICES,
        "style_choices": STYLE_CHOICES
    }
    return Response(data=data, status=200)
