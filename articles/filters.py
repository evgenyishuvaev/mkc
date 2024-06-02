from django.db.models import Count
import django_filters

from articles.models.articles import Article


class ArticleFilter(django_filters.FilterSet):
    CHOICES = (
        ("category_1", "category_1"),
        ("category_2", "category_2"),
        ("category_3", "category_3"),
        ("category_4", "category_4"),
        ("category_5", "category_5"),
    )
    category = django_filters.ChoiceFilter(
        label="Category",
        method="category_filter",
        choices=CHOICES,
    )

    class Meta:
        model = Article
        fields = ("category",)

    def category_filter(self, queryset, name, value):
        cases = {
            "category_1": self._filter_category_1,
            "category_2": self._filter_category_2,
            "category_3": self._filter_category_3,
            "category_4": self._filter_category_4,
            "category_5": self._filter_category_5,
        }
        if value not in cases:
            return queryset

        return cases[value](queryset)

    def _filter_category_1(self, queryset):
        """
        В выборку должны попасть только те статьи, у которых:
            В инфо об авторе статьи НЕ указан номер телефона
        """
        return queryset.filter(author__info__phone=None)

    def _filter_category_2(self, queryset):
        """
        В выборку должны попасть только те статьи, у которых:
            Существует хотя бы один комментарий и одна оценка
        """
        return queryset.annotate(Count("comments"), Count("ratings")).filter(
            comments__count__gt=0, ratings__count__gt=0
        )

    def _filter_category_3(self, queryset):
        """
        В выборку должны попасть только те статьи, у которых:
            В статье есть тег "Разработка" (code='dev'),
            И все комментарии с источником "Мобильное устройство" (code='mobile')
        """
        # TODO: все комментарии
        return queryset.filter(
            tags__code="dev", comments__source__code="mobile"
        ).distinct()

    def _filter_category_4(self, queryset):
        """
        В выборку должны попасть только те статьи, у которых:
            В статье есть хотя бы один комментарий и одна оценка, у которых
            указан источник "Web версия" (code='web')
        """
        return queryset.annotate(Count("comments"), Count("ratings")).filter(
            comments__count__gt=0,
            comments__source__code="web",
            ratings__count__gt=0,
            ratings__source__code="web",
        )

    def _filter_category_5(self, queryset):
        """
        В выборку должны попасть только те статьи, у которых:
            Общее число статей автора строго больше 2
        """
        articls_ids = (
            queryset.values("author")
            .annotate(author_articles=Count("*"))
            .filter(author_articles__gt=2)
            .values_list("author", flat=True)
        )
        queryset = queryset.filter(author__in=articls_ids)
        return queryset
