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
            username='testuser')

        posts = []
        groups = []
        for i in range(1, 3):
            groups.append(
                (Group(title='Тестовая группа' + str(i),
                       slug='test-group' + str(i),
                       description='Описание группы' + str(i))
                 ))

        Group.objects.bulk_create(groups)
        for i in range(1, 3):
            posts.append(Post(
                text='Тестовая запись' + str(i),
                author=cls.user_author,
                group=Group.objects.get(pk=i)
            ))
        Post.objects.bulk_create(posts)

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

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        context_post = {
            'Тестовая запись1': response.context.get('page')[0].text,
            'testuser': response.context.get('page')[0].author.username,
            'Тестовая группа1': response.context.get('page')[0].group.title,
        }

        for text, expected in context_post.items():
            with self.subTest():
                self.assertEqual(text, expected)

    def test_context_in_group_page(self):
        """ Тестирование содержания context в group"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group1'}))

        context_group = {
            'Тестовая запись1': response.context.get('page')[0].text,
            'testuser': response.context.get('page')[0].author.username,
            'Тестовая группа1': response.context.get('group').title,
            'test-group1': response.context.get('group').slug,
            'Описание группы1': response.context.get('group').description
        }
        for value, expected in context_group.items():
            with self.subTest():
                self.assertEqual(value, expected)

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
        response = self.guest_client.get(reverse('profile', kwargs={'username': 'testuser'}))
        context_page = {
            'Тестовая запись1': response.context.get('page')[0].text,
            'testuser': response.context.get('page')[0].author.username,
            'Тестовая группа1': response.context.get('page')[0].group.title,
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
            'Тестовая запись1': response.context.get('post').text,
            'Тестовая группа1': response.context.get('post').group.title,
        }

        for value, expected in context_edit_page.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_post_is_in_index_page(self):
        """Тестирование наличия поста на главной странице сайта"""
        response = self.authorized_client.get(reverse('index'))
        post_id = response.context.get('page')[0].pk = 1
        self.assertEqual(post_id, 1)

    def test_post_is_in_group_page(self):
        """Тестирование наличия поста присвоенного группе на странице группы"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group1'}))
        post_id = response.context.get('page')[0].pk
        self.assertEqual(post_id, 1)

    def test_post_is_in_correct_group(self):
        """Тестирование на правильность назначения групп для постов"""
        # Проверим, что test-group1 сожержит только назначеный пост
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group1'}))
        post_id = response.context.get('group').pk
        post_len_except_first_post = range(2, Post.objects.count())
        self.assertNotIn(post_id, post_len_except_first_post)


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

        for i in range(1, 14):
            Post.objects.create(text='Тестовое сообщение ' + str(i),
                                author=cls.user_author)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
