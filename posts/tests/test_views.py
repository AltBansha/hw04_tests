from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = get_user_model().objects.create(
            username='testuser'
        )

        Group.objects.bulk_create([
            Group(
                title=f'Тестовая группа {number}',
                slug=f'test-group{number}',
                description=f'Описание группы {number}',
            ) for number in range(1, 3)
        ])

        Post.objects.bulk_create([
            Post(
                text=f'Тестовая запись {number}',
                author=cls.user_author,
                group=Group.objects.get(pk=number),
            ) for number in range(1, 3)
        ])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test-group1'}),
            'posts/new.html': reverse('new_post'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_contains_ten_records(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.context.get('page').object_list,
                         list(Post.objects.all()[:10]))

    def test_context_in_group_page(self):
        """ Тестирование содержания context в group"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group1'})
        )

        self.assertEqual(response.context.get('page').object_list,
                         list(Post.objects.all()[:1]))

    def test_context_in_new_post_page(self):
        """ Тестирование содержания context при создании поста"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get('form').fields.get(value)
            self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'profile',
            kwargs={'username': 'testuser'})
        )
        context_page = {
            'Тестовая запись 1': response.context.get('page')[0].text,
            'testuser': response.context.get('page')[0].author.username,
            'Тестовая группа 1': response.context.get('page')[0].group.title,
        }

        for value, expected in context_page.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_context_in_edit_post_page(self):
        """Тестирование содержания context при редактировании поста"""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': 'testuser',
                            'post_id': 1}))

        context_edit_page = {
            'Тестовая запись 1': response.context.get('post').text,
            'Тестовая группа 1': response.context.get('post').group.title,
        }

        for value, expected in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_post_is_in_correct_group(self):
        """Тестирование на правильность назначения групп для постов."""
        # Проверим, что test-group1 сожержит только назначеный пост

        group = Group.objects.first()
        posts_out_of_group = Post.objects.exclude(group=group)
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group1'})
        )
        posts_collection = set(posts_out_of_group)
        response_paginator = response.context.get('paginator').object_list
        self.assertTrue(posts_collection.isdisjoint(response_paginator))


class StaticViewsTests(TestCase):

    def setUp(self):
        self.guest_user = Client()

    def test_templates_static_pages(self):
        """Тестирование шаблонов для статических страниц """
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = get_user_model().objects.create(username='testuser')

        Post.objects.bulk_create([
            Post(
                text='Тестовая запись',
                author=cls.user_author,
            ) for number in range(13)
        ])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_first_page_contains_ten_records(self):
        """Проверяем, что первая страница содержит 10 постов."""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        """Проверяем, что на второй странице только 3 поста."""
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
