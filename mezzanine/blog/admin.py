
from copy import deepcopy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine.blog.models import Blog, BlogPost, BlogCategory
from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


blogpost_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
blogpost_fieldsets[0][1]["fields"].insert(1, "categories")
blogpost_fieldsets[0][1]["fields"].insert(1, "blog")
blogpost_fieldsets[0][1]["fields"].extend(["content", "allow_comments"])
blogpost_list_display = ["title", "blog", "user", "status", "admin_link"]
if settings.BLOG_USE_FEATURED_IMAGE:
    blogpost_fieldsets[0][1]["fields"].insert(-2, "featured_image")
    blogpost_list_display.insert(0, "admin_thumb")
blogpost_fieldsets = list(blogpost_fieldsets)
blogpost_fieldsets.insert(1, (_("Other posts"), {
    "classes": ("collapse-closed",),
    "fields": ("related_posts",)}))


class BlogAdmin(OwnableAdmin):
    """
    Admin class for blogs.
    """

    list_display = ("title", "user", "published_posts", "manage_posts", "admin_link")

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            self.exclude = ["user", "slug"]
        return super(BlogAdmin, self).get_form(request, obj, **kwargs)


class BlogPostAdmin(DisplayableAdmin, OwnableAdmin):
    """
    Admin class for blog posts.
    """

    fieldsets = blogpost_fieldsets
    list_display = blogpost_list_display
    filter_horizontal = ("categories", "related_posts",)
    list_filter = ("blog", "user", "status")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limit choices for 'blog' field to only blogs owned by this user
        if db_field.name == 'blog':
            if not request.user.is_superuser:
                kwargs["queryset"] = Blog.objects.filter(
                    user=request.user)
        return super(BlogPostAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Limit choices for 'categories' and 'related posts' to only blogs owned by this user
        if not request.user.is_superuser:
            if db_field.name == 'categories':
                kwargs["queryset"] = BlogCategory.objects.filter(
                    blog__user=request.user)
            if db_field.name == 'related_posts':
                kwargs["queryset"] = BlogPost.objects.filter(
                    blog__user=request.user)
        return super(BlogPostAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)


class BlogCategoryAdmin(admin.ModelAdmin):
    """
    Admin class for blog categories. Hides itself from the admin menu
    unless explicitly specified.
    """

    fieldsets = ((None, {"fields": ("title","blog")}),)
    def queryset(self, request):
        qs = super(BlogCategoryAdmin, self).queryset(request)
        return qs.filter(blog__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limit choices for 'blog' field to only blogs owned by this user
        if db_field.name == 'blog':
            if not request.user.is_superuser:
                kwargs["queryset"] = Blog.objects.filter(
                    user=request.user)
        return super(BlogCategoryAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "blog.BlogCategory" in items:
                return True
        return False


admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogCategory, BlogCategoryAdmin)
