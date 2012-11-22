
from django.conf.urls.defaults import patterns, url

from mezzanine.conf import settings


# Leading and trailing slahes for urlpatterns based on setup.
_slashes = (
    "/" if settings.BLOG_SLUG else "",
    "/" if settings.APPEND_SLASH else "",
)

# Blog patterns.
urlpatterns = patterns("mezzanine.blog.views",
    url("^%s(?P<blog_slug>.*)/feeds/(?P<format>.*)%s$" % _slashes,
        "blog_post_feed", name="blog_post_feed"),
    url("^%s(?P<blog_slug>.*)/tag/(?P<tag>.*)/feeds/(?P<format>.*)%s$" % _slashes,
        "blog_post_feed", name="blog_post_feed_tag"),
    url("^%s(?P<blog_slug>.*)/tag/(?P<tag>.*)%s$" % _slashes, "blog_post_list",
        name="blog_post_list_tag"),
    url("^%s(?P<blog_slug>.*)/category/(?P<category>.*)/feeds/(?P<format>.*)%s$" % _slashes,
        "blog_post_feed", name="blog_post_feed_category"),
    url("^%s(?P<blog_slug>.*)/category/(?P<category>.*)%s$" % _slashes,
        "blog_post_list", name="blog_post_list_category"),
    url("^%s(?P<blog_slug>.*)/author/(?P<username>.*)/feeds/(?P<format>.*)%s$" % _slashes,
        "blog_post_feed", name="blog_post_feed_author"),
    url("^%s(?P<blog_slug>.*)/author/(?P<username>.*)%s$" % _slashes,
        "blog_post_list", name="blog_post_list_author"),
    url("^%s(?P<blog_slug>.*)/archive/(?P<year>\d{4})/(?P<month>\d{1,2})%s$" % _slashes,
        "blog_post_list", name="blog_post_list_month"),
    url("^%s(?P<blog_slug>.*)/archive/(?P<year>.*)%s$" % _slashes,
        "blog_post_list", name="blog_post_list_year"),
    url("^%s(?P<blog_slug>.*)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/"
        "(?P<slug>.*)%s$" % _slashes,
        "blog_post_detail", name="blog_post_detail_date"),
    url("^%s(?P<blog_slug>.*)/(?P<slug>.*)%s$" % _slashes, "blog_post_detail",
        name="blog_post_detail"),
    url("^%s(?P<blog_slug>.*)%s$" % _slashes, "blog_post_list", name="blog_post_list"),
)
