from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.generic.fields import CommentsField, RatingField
from mezzanine.utils.models import AdminThumbMixin
from mezzanine.utils.urls import admin_url


class Blog(Ownable, Slugged):
    """
    A blog, managed by the user that owns it.
    """

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")

    @models.permalink
    def get_absolute_url(self):
        return ("blog_post_list", (), {"blog_slug": self.slug})

    def published_posts(self):
        return BlogPost.objects.published().filter(blog=self).count()

    def manage_posts(self):
        url = admin_url(BlogPost, "changelist")
        url += "?blog__id__exact=%s" % self.id
        return "<a href='%s'>Manage posts</a>" % url
    manage_posts.allow_tags = True
    manage_posts.short_description = ""


class BlogPost(Displayable, Ownable, RichText, AdminThumbMixin):
    """
    A blog post.
    """
    blog = models.ForeignKey("Blog", verbose_name=_("Blog"))
    categories = models.ManyToManyField("BlogCategory",
                                        verbose_name=_("Categories"),
                                        blank=True, related_name="blogposts")
    allow_comments = models.BooleanField(verbose_name=_("Allow comments"),
                                         default=True)
    comments = CommentsField(verbose_name=_("Comments"))
    rating = RatingField(verbose_name=_("Rating"))
    featured_image = FileField(verbose_name=_("Featured Image"),
                               upload_to="blog", format="Image",
                               max_length=255, null=True, blank=True)
    related_posts = models.ManyToManyField("self",
                                 verbose_name=_("Related posts"), blank=True)

    admin_thumb_field = "featured_image"

    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        ordering = ("-publish_date",)

    @models.permalink
    def get_absolute_url(self):
        url_name = "blog_post_detail"
        kwargs = {"blog_slug": self.blog.slug, "slug": self.slug}
        if settings.BLOG_URLS_USE_DATE:
            url_name = "blog_post_detail_date"
            month = str(self.publish_date.month)
            if len(month) == 1:
                month = "0" + month
            day = str(self.publish_date.day)
            if len(day) == 1:
                day = "0" + day
            kwargs.update({
                "day": day,
                "month": month,
                "year": self.publish_date.year,
            })
        return (url_name, (), kwargs)

    # These methods are wrappers for keyword and category access.
    # For Django 1.3, we manually assign keywords and categories
    # in the blog_post_list view, since we can't use Django 1.4's
    # prefetch_related method. Once we drop support for Django 1.3,
    # these can probably be removed.

    def category_list(self):
        return getattr(self, "_categories", self.categories.all())

    def keyword_list(self):
        try:
            return self._keywords
        except AttributeError:
            keywords = [k.keyword for k in self.keywords.all()]
            setattr(self, "_keywords", keywords)
            return self._keywords


class BlogCategory(Slugged):
    """
    A category for grouping blog posts into a series.
    """

    blog = models.ForeignKey("Blog")

    class Meta:
        verbose_name = _("Blog Category")
        verbose_name_plural = _("Blog Categories")

    @models.permalink
    def get_absolute_url(self):
        return ("blog_post_list_category", (), {"blog_slug": self.blog.slug, "category": self.slug})
