from typing_extensions import assert_type
from django.test import TestCase
from .models import (
    Article,
    BlogPost,
    NewsArticle,
    Topic,
    LocationTopic,
    EditorialTopic,
    MediaOutlet,
    Newspaper,
    OnlineBlog,
)


class TypeHintsTest(TestCase):
    def test_type_hints_example_models(self):
        # Just a placeholder test to ensure the example models file is included in test
        # runs
        daily = Newspaper.objects.create(
            name="The Daily Times", service_area="New York"
        )
        rg = OnlineBlog.objects.create(name="ReplyGuy")

        article = Article.objects.create(title="Test Article", outlet=daily)
        bp = BlogPost.objects.create(
            title="Test Blog Post", author="Author A", outlet=rg
        )
        na = NewsArticle.objects.create(
            title="Test News Article", source="Source A", outlet=daily
        )

        general_int = Topic.objects.create(name="General Interest")
        location_topic = LocationTopic.objects.create(
            name="Food", location="Los Angeles"
        )
        editorial_topic = EditorialTopic.objects.create(
            name="Politics", editor="BCK"
        )

        general_int.articles.add(article, bp, na)
        location_topic.articles.add(na)
        editorial_topic.articles.add(bp)

        objs: list[Article | BlogPost | NewsArticle] = list(
            Article.objects.all()
        )
        objs0: list[Article | BlogPost | NewsArticle] = list(
            Article.objects.all().all()
        )
        objs01: list[Article | BlogPost | NewsArticle] = list(
            Article.objects.filter()
        )

        objs2: list[BlogPost] = list(
            Article.objects.instance_of(BlogPost).all()
        )
        objs3: list[BlogPost | NewsArticle] = list(
            Article.objects.instance_of(NewsArticle, BlogPost).all()
        )

        for art in Article.objects.instance_of(NewsArticle, BlogPost):
            assert_type(art, NewsArticle | BlogPost)

        objs4: list[BlogPost] = list(
            Article.objects.all().instance_of(BlogPost).all()
        )
        objs5: list[BlogPost | NewsArticle] = list(
            Article.objects.all().instance_of(NewsArticle, BlogPost).all()
        )

        assert len(objs) == len(objs0) == len(objs01) == 3
        assert len(objs2) == 1
        assert len(objs3) == 2
        assert len(objs4) == 1
        assert len(objs5) == 2

        topics: list[Topic | LocationTopic | EditorialTopic] = list(
            article.topics.all()
        )
        topics2: list[Topic | LocationTopic | EditorialTopic] = list(
            article.topics.all().all()
        )

        non_poly_topics: list[Topic] = list(article.topics.non_polymorphic())

        for tpc1 in article.topics.all():
            assert_type(tpc1, Topic | LocationTopic | EditorialTopic)

        for tpc2 in article.topics.all().all():
            assert_type(tpc2, Topic | LocationTopic | EditorialTopic)
        for tpc3 in article.topics.filter():
            assert_type(tpc3, Topic | LocationTopic | EditorialTopic)

        for tpc4 in article.topics.non_polymorphic():
            assert_type(tpc4, Topic)

        for tpc5 in article.topics.all().non_polymorphic():
            assert_type(tpc5, Topic)

        for tpc6 in article.topics.all().instance_of(BlogPost):
            assert_type(tpc6, BlogPost)

        assert len(topics) == 1
        assert len(topics2) == 1
        assert len(non_poly_topics) == 1

        assert bp.topics.count() == 2

        for art2 in general_int.articles.all():
            assert_type(art2, Article | BlogPost | NewsArticle)

        assert_type(article.outlet, Newspaper | OnlineBlog | MediaOutlet)
        assert_type(bp.outlet, Newspaper | OnlineBlog | MediaOutlet)
        assert_type(na.outlet, Newspaper | OnlineBlog | MediaOutlet)

        for art3 in daily.articles.all():
            assert_type(art3, Article | BlogPost | NewsArticle)

        for art4 in daily.articles.filter().all():
            assert_type(art4, Article | BlogPost | NewsArticle)

        # reveal_type(Topic.articles)
        # reveal_type(Topic.articles2)

        # reveal_type(Topic.objects.first().articles2)
