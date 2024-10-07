from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from item.models import Item, Category
from core.forms import SignupForm, LogginForm

class CoreViewsTest(TestCase):

    def setUp(self):
        # Criar categorias e itens para a página inicial
        self.category1 = Category.objects.create(name="Eletrônicos")
        self.category2 = Category.objects.create(name="Livros")
        
        self.item1 = Item.objects.create(
            name="Item 1",
            category=self.category1,
            price=100.0,
            is_sold=False,
            created_by=User.objects.create_user(username="user1")
        )
        self.item2 = Item.objects.create(
            name="Item 2",
            category=self.category1,
            price=150.0,
            is_sold=False,
            created_by=User.objects.create_user(username="user2")
        )
        self.item3 = Item.objects.create(
            name="Item 3",
            category=self.category2,
            price=200.0,
            is_sold=True,  # Este item não deve ser listado na página inicial
            created_by=User.objects.create_user(username="user3")
        )

    def test_index_view(self):
        # Testa se a view `index` carrega os itens e categorias corretamente
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertContains(response, 'Item 1')
        self.assertContains(response, 'Item 2')
        self.assertNotContains(response, 'Item 3')  # Item vendido não deve aparecer
        self.assertContains(response, 'Eletrônicos')
        self.assertContains(response, 'Livros')

    def test_contact_view(self):
        # Testa se a view `contact` carrega corretamente
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')

    def test_signup_view_get(self):
        # Testa se a view de signup carrega corretamente o formulário
        response = self.client.get(reverse('core:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/signup.html')
        self.assertIsInstance(response.context['form'], SignupForm)

    def test_signup_view_post_valid_data(self):
        # Testa o formulário de signup com dados válidos
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        }
        response = self.client.post(reverse('core:signup'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Deve redirecionar após sucesso
        self.assertRedirects(response, '/login/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_view_post_invalid_data(self):
        # Testa o formulário de signup com dados inválidos (senhas que não coincidem)
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'differentpassword'  # As senhas não combinam
        }
        response = self.client.post(reverse('core:signup'), data=form_data)
        
        # Verifica se o formulário foi re-renderizado com erros
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/signup.html')
        
        # Acessa o formulário da resposta
        form = response.context.get('form')
        self.assertIsNotNone(form)  # Verifica se o formulário está no contexto

        # Verifica se o erro de validação ocorreu no campo 'password2'
        self.assertTrue(form.errors)
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'], ["The two password fields didn’t match."])

        # Verifica se o usuário não foi criado no banco de dados
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        # Testa se a view de login carrega corretamente o formulário
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertIsInstance(response.context['form'], LogginForm)