from django.db.models import F, Q, Avg, Count, Func, Sum
from django.db.models.functions import ExtractYear
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from articles.filters import ArticleFilter
from articles.models.articles import Article
from articles import serializers


class ArticleListView(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ArticleFilter


class ArticleListStatsView(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleListStatsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ArticleFilter

    def get_queryset(self):
        queryset = Article.objects.annotate(
            count_comments=Count("comments", distinct=True),
            count_ratings=Count("ratings", distinct=True),
            average_rating=Avg("ratings__rate"),
            author_age=ExtractYear(Func(F("author__dob"), function="age")),
            author_age_in_publish=ExtractYear(
                Func(F("publish_date"), F("author__dob"), function="age")
            ),
            count_activities=F("count_comments") + F("count_ratings"),
        )

        print(queryset.query)
        return queryset
