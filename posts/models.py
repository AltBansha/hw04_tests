from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200
        )
    slug = models.SlugField(
        unique=True,
        max_length=100
        )
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст записи',
        help_text='Укажите текст Вашей записи.'
    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(
        Group,
        verbose_name='Название группы',
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        help_text=('Выберете группу, в которой хотите '
                   'опубликовать Вашу запись.')
        )

    def __str__(self):
        return self.text[:15]
