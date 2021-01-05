from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создание двух пользователей
        cls.user_author_1 = get_user_model().objects.create(username='testuser1')
        cls.user_author_2 = get_user_model().objects.create(username='testuser2')

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='test-group-description')

        cls.post = Post.objects.create(text='Тестовая запись',
                                       author=cls.user_author_1,
                                       group=cls.group)

    def setUp(self):
        # Неавторизованный клиент
        self.guest_client = Client()
        # Создаем двух авторизованных клиентов
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_author_1)

        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_author_2)        

    def test_index_url_for_guest_users(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_for_guest_users(self):
        """Страница /group/<slug>/ доступна авторизованному пользователю."""
        response = self.guest_client.get('/group/test-group/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_for_guest_users(self):
        """Тестирование URL для неавторизованных пользователей."""
    # Удостоверися, что редирект на sign up работает корректно
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(
                    response, '/auth/login/?next=/new/')

    def test_new_post_url_for_authorized_users(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client_1.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url(self):
        response = self.authorized_client_1.get('/testuser1/')
        self.assertEqual(response.status_code, 200)

    def test_user_post_url(self):
        response = self.authorized_client_1.get('/testuser1/1/')
        self.assertEqual(response.status_code, 200)

    def test_user_post_edit_url(self):
        response = self.authorized_client_1.get('/testuser1/1/edit/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_post_edit_other_url(self):
        response = self.authorized_client_1.get('/testuser2/1/edit/')
        self.assertEqual(response.status_code, 404)

    def test_user_post_edit_url_for_guest_client(self):
        response = self.guest_client.get('/testuser2/1/edit/')
        self.assertEqual(response.status_code, 404)

    def test_about_author_url_for_guest_client(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_for_guest_client(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-group/',
            'posts/new.html': '/new/',
            'posts/profile.html': '/testuser1/',
            'posts/post.html': '/testuser1/1/',
            'posts/new.html': '/testuser1/1/edit/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)
