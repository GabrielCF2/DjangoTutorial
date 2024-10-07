from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from item.models import Item, Category
from django.test import Client

class DashboardViewTest(TestCase):
    
    def setUp(self):
        # Criando dois usuários de teste
        self.user1 = User.objects.create_user(username='user1', password='pass12345')
        self.user2 = User.objects.create_user(username='user2', password='pass54321')
        self.category = Category.objects.create(name='Eletrônicos')

        # Criando itens para o user1 e user2
        self.item1_user1 = Item.objects.create(
            name="Item 1 User 1",
            category_id=self.category.id,  # Suponha que a categoria com ID 1 já exista
            price=100.0,
            created_by=self.user1
        )
        
        self.item2_user1 = Item.objects.create(
            name="Item 2 User 1",
            category_id=self.category.id,
            price=200.0,
            created_by=self.user1
        )
        
        self.item1_user2 = Item.objects.create(
            name="Item 1 User 2",
            category_id=self.category.id,
            price=150.0,
            created_by=self.user2
        )
    
    def test_redirect_if_not_logged_in(self):
        # Testa se o usuário não autenticado é redirecionado para a página de login
        response = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(response, '/login/?next=/dashboard')

    def test_logged_in_uses_correct_template(self):
        # Loga o usuário 1
        self.client.login(username='user1', password='pass12345')

        # Verifica se a view carrega o template correto
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')

    def test_only_user_items_displayed(self):
        # Loga o usuário 1
        self.client.login(username='user1', password='pass12345')

        # Faz a requisição para a página de dashboard
        response = self.client.get(reverse('dashboard:index'))
        
        # Verifica se a resposta está OK
        self.assertEqual(response.status_code, 200)

        # Verifica se os itens mostrados são apenas os do usuário 1
        items = response.context['items']
        self.assertEqual(len(items), 2)
        self.assertIn(self.item1_user1, items)
        self.assertIn(self.item2_user1, items)

        # Verifica se o item do user2 não está sendo exibido
        self.assertNotIn(self.item1_user2, items)
