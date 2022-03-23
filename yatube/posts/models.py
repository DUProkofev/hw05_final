from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Строка идентификатор', unique=True)
    description = models.TextField('Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа поста',
        related_name='posts',
        help_text='Группа, к которой будет относиться пост',
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
