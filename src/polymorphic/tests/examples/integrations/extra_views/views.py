from polymorphic.contrib.extra_views import PolymorphicFormSetView
from polymorphic.formsets import PolymorphicFormSetChild
from django.urls import reverse_lazy
from ..models import Article, BlogPost, NewsArticle


class ArticleFormSetView(PolymorphicFormSetView):
    model = Article
    template_name = "extra_views/article_formset.html"
    success_url = reverse_lazy("extra_views:articles")
    fields = "__all__"

    # extra will add two empty forms for models in the order of their appearance
    # in formset_children
    factory_kwargs = {"extra": 2, "can_delete": True}

    formset_children = [
        PolymorphicFormSetChild(BlogPost, fields="__all__"),
        PolymorphicFormSetChild(NewsArticle, fields="__all__"),
    ]
