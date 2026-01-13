from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from reversion.admin import VersionAdmin
from ..models import Article, BlogPost, NewsArticle


class ArticleChildAdmin(PolymorphicChildModelAdmin, VersionAdmin):
    base_model = Article


@admin.register(BlogPost)
class BlogPostAdmin(ArticleChildAdmin):
    pass


@admin.register(NewsArticle)
class NewsArticleAdmin(ArticleChildAdmin):
    pass


class ArticleParentAdmin(VersionAdmin, PolymorphicParentModelAdmin):
    """
    Parent admin for Article model with reversion support.

    Note: VersionAdmin must come before PolymorphicParentModelAdmin
    in the inheritance order.
    """

    base_model = Article
    child_models = (BlogPost, NewsArticle)
    list_display = ("title", "created")


admin.site.register(Article, ArticleParentAdmin)
