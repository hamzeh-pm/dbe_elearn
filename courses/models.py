from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    query = {
                        field: getattr(model_instance, field)
                        for field in self.for_fields
                    }
                    qs = qs.filter(**query)
                    last_item = qs.latest(self.attname)
                    value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)

            return value
        else:
            return super().pre_save(model_instance, add)


# Create your models here.
class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ("title",)

    def __str__(self) -> str:
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        User, related_name="courses_created", on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject, related_name="courses", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=["course"])

    class Meta:
        ordering = ("order",)

    def __str__(self) -> str:
        return f"{self.order}. {self.title}"


class Content(models.Model):
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("text", "video", "image", "file")},
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    order = OrderField(blank=True, for_fields=["module"])

    class Meta:
        ordering = ("order",)


class ItemBase(models.Model):
    owner = models.ForeignKey(
        User, related_name="%(class)s_related", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title

    def render(self):
        return render_to_string(
            f"courses/content/{self._meta.model_name}.html", {"item": self}
        )


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    content = models.FileField(upload_to="files")


class Image(ItemBase):
    content = models.ImageField(upload_to="images")


class Video(ItemBase):
    content = models.URLField()
