from django import forms
from django.conf import settings
from django.core import paginator
from django.test import Client

from ..models import Post
from .fixture import Fixture


class ViewsTests(Fixture):
    """Тестирование представлений"""
    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user1)

    def paginator_test(
        self,
        reverse,
        context,
        post_on_1st_page
    ):
        response = self.client.get(reverse)
        self.assertEqual(len(response.context[context]), post_on_1st_page)

    def test_current_templates(self):
        for reverse_name, template in self.expect_templates.items():
            with self.subTest(name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка страницы index"""
        response = self.auth_client.get(self.reverse_index)
        objects = response.context['page_obj']
        self.assertIsInstance(objects, paginator.Page)
        self.assertIsInstance(objects[0], Post)
        self.paginator_test(
            self.reverse_index,
            'page_obj',
            settings.POSTS_PER_PAGE
        )

    def test_group_list_page_show_correct_context(self):
        """Проверка страницы group_list"""
        response = self.auth_client.get(self.reverse_group_list)
        objects = response.context['page_obj']
        self.assertIsInstance(objects, paginator.Page)
        for post in objects:
            with self.subTest(post=post):
                self.assertEqual(post.group, self.group)
        self.paginator_test(
            self.reverse_group_list,
            'page_obj',
            settings.POSTS_PER_PAGE
        )

    def test_profile_page_show_correct_context(self):
        """Проверка страницы profile"""
        response = self.auth_client.get(self.reverse_profile)
        objects = response.context['page_obj']
        self.assertIsInstance(objects, paginator.Page)
        for post in objects:
            with self.subTest(post=post):
                self.assertEqual(post.author, self.user1)
        self.paginator_test(
            self.reverse_profile,
            'page_obj',
            settings.POSTS_PER_PAGE
        )

    def test_post_detail_page_show_correct_context(self):
        """Проверка страницы post_detail"""
        response = self.auth_client.get(self.reverse_post_detail)
        object = response.context['post']
        self.assertEqual(object.id, self.post_with_group_1.id)
        self.assertEqual(object.text, self.post_with_group_1.text)
        self.assertEqual(object.group, self.post_with_group_1.group)
        self.assertEqual(object.author, self.post_with_group_1.author)
        self.assertEqual(object.image, self.post_with_group_1.image)

    def test_post_create_page_show_correct_context(self):
        """post_create сформирована с правильным контекстом."""
        reverse_list = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
        }
        response = self.auth_client.get(self.reverse_post_create)
        for value, expected in reverse_list.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """post_edit сформирована с правильным контекстом."""
        reverse_list = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
        }
        response = self.auth_client.get(self.reverse_post_edit)
        self.assertEqual(
            response.context['post_id'],
            self.post_with_group_1.id
        )
        for value, expected in reverse_list.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_show_in_need_pages(self):
        """Проверка новый пост попал на нужные страницы"""
        expect = [
            self.auth_client.get(self.reverse_index),
            self.auth_client.get(self.reverse_group_list),
            self.auth_client.get(self.reverse_profile),
        ]
        for response in expect:
            with self.subTest(response=response):
                self.assertIn(
                    self.post_with_group_1,
                    response.context.get('page_obj').paginator.object_list
                )

    def test_new_post_in_need_group(self):
        """Проверка новый пост попал в нужную группу"""
        self.assertEqual(
            self.post_with_group_1.group,
            self.group
        )
    def test_check_content_in_index(self):
        """Проверка переданного контента на index, profile, group"""
        check_list = [
            self.reverse_index,
            self.reverse_group_list,
            self.reverse_profile,
        ]
        post_with_image = Post.objects.filter(image__contains='posts/small')[1]
        for reverse in check_list:
            with self.subTest(page=reverse):
                response = self.auth_client.get(reverse)
                post = response.context['page_obj'].paginator.object_list.filter(id=post_with_image.id)
                self.assertEquals(post[0].image, post_with_image.image)

