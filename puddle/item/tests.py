from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Item, Category
from .forms import NewItemForm

class ItemModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Eletrônicos')
    
    def test_item_creation(self):
        item = Item.objects.create(
            category=self.category,
            name='Laptop',
            description='Um laptop novo',
            price=1500.00,
            image='laptop.jpg',
            created_by=self.user
        )
        self.assertEqual(item.name, 'Laptop')
        self.assertEqual(item.price, 1500.00)
        self.assertEqual(item.created_by, self.user)
        self.assertEqual(item.category, self.category)

    def test_price_cannot_be_negative(self):
        item = Item(
            category=self.category,
            name='Produto Inválido',
            description='Teste de preço negativo',
            price=-10.00,
            image='invalid.jpg',
            created_by=self.user
        )
        
        # Tentativa de validar o item
        with self.assertRaises(ValidationError):
            item.full_clean()  # Isso acionará a validação
            item.save()  # Isso não será chamado se a validação falhar

            
class NewItemFormTest(TestCase):
    
    def setUp(self):
        # Criação de uma categoria válida para ser usada nos testes
        self.category = Category.objects.create(name='Eletrônicos')
    
    def test_form_valid(self):
        # Mock de um arquivo de imagem para o campo 'image'
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )
        
        # Dados válidos para o formulário
        form_data = {
            'category': self.category.id,
            'name': 'Smartphone',
            'description': 'Um ótimo smartphone',
            'price': '800.00'
        }
        
        form_files = {
            'image': image
        }
        
        form = NewItemForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_form_invalid_missing_name(self):
        # Mock de um arquivo de imagem para o campo 'image'
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )
        # Dados inválidos para o formulário (faltando o nome)
        form_data = {
            'category': self.category.id,  # Categoria criada no setup
            'name': '',  # Nome está ausente
            'description': 'Um ótimo smartphone',
            'price': '800.00',
        }

        form_files = {
            'image': image
        }

        form = NewItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class ItemViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.admin = User.objects.create_user(username='admin', password='admin123')
        self.category = Category.objects.create(name='Eletrônicos')
        self.item = Item.objects.create(
            category=self.category,
            name='Smartphone',
            description='Um ótimo smartphone',
            price=800.00,
            image='smartphone.jpg',
            created_by=self.user
        )

    def test_items_view(self):
        response = self.client.get(reverse('item:items'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/items.html')
        self.assertContains(response, 'Smartphone')

    def test_detail_view(self):
        response = self.client.get(reverse('item:detail', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/detail.html')
        self.assertContains(response, 'Smartphone')

    def test_edit_view_permission_denied(self):
        # Usuário não autenticado tenta acessar a página de edição
        response = self.client.get(reverse('item:edit', args=[self.item.pk]))
        self.assertEqual(response.status_code, 302)  # Redireciona para login
        
        # Autentica como um usuário que não criou o item
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('item:edit', args=[self.item.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_edit_view_authorized(self):
        # Autentica como o criador do item
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('item:edit', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/form.html')

    def test_delete_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('item:delete', args=[self.item.pk]))
        self.assertRedirects(response, reverse('dashboard:index'))
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())