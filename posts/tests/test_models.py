from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(
            username='testuser',
            first_name='FirstNameUser',
            last_name='LastNameUser'
            )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='test-group-description'
            )

        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name(self):
        """Тестуруем verbose_name в модели Post"""
        print(PostModelTest.test_verbose_name.__doc__)

        post = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст записи',
            'group': 'Название группы',
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected,
                    (f'Ошибка в {PostModelTest.test_verbose_name.__name__},'
                     ' проверьте verbose_name в Post'))

    def test_helps_text(self):
        """Тестируем helps_text в модели Post"""
        print(PostModelTest.test_helps_text.__doc__)

        post = PostModelTest.post
        field_help_text = {
            'text': 'Укажите текст Вашей записи.',
            'group': ('Выберете группу, в которой хотите '
                      'опубликовать Вашу запись.')
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected,
                    (f'Ошибка в {PostModelTest.test_helps_text.__name__},'
                     ' проверьте help_text в Post'))

    def test_group_str_value(self):
        """Тестируем значение __str__  в модели Group
            он должен возвращать название группы"""
        print(PostModelTest.test_group_str_value.__doc__)
        group = PostModelTest.group
        str_value = self.group.title
        self.assertEqual(str_value, group.__str__())

    def test_post_str_value(self):
        """Тестируем длину __str__ значения в модели Post
            он должен возвращать строку в 15 символов"""
        print(PostModelTest.test_post_str_value.__doc__)
        max_length = 15
        len_post_str_value = len(self.post.__str__())
        self.assertEqual(max_length, len_post_str_value)
