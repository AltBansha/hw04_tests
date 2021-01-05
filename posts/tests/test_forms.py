from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group


class NewPost_FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='testuser')
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='Описание')
        # создадим авторизованного пользователя
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

    def test_forms_new_post(self):
        """Тестируем форму новых сообщений на странице New_Post"""
        # данные для создания нового поста
        form_data = {
            'text': 'Тестовая запись',
            'group': self.group.id
        }
        response = self.authorized_user.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # проверяем правильность redirect после создания нового поста
        self.assertRedirects(response, reverse('index'))


class PostEdit_FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='testuser')

        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-group',
                                         description='Описание')
        # создадим авторизованного пользователя
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

    def test_forms_post_edit(self):
        """Тестируем форму новых сообщений на странице New_Post"""
    
        form_data = {
            'text': 'Тестовая запись',
            'group': self.group.id
        }

        form_data_1 = {
            'text': 'Тестовая запись1',
            'group': self.group.id
        }

        form_data = form_data_1

        response = self.authorized_user.post(
            reverse('post_edit'),
            date=form_data,
            follow=True)
        # проверяем правильность redirect после создания нового поста
        self.assertRedirects(response, reverse('index'))
