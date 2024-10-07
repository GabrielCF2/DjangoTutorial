from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from item.models import Item, Category
from conversation.models import Conversation, ConversationMessage
from conversation.forms import ConversationMessageForm
from django.core.files.uploadedfile import SimpleUploadedFile

class ConversationTest(TestCase):

    def setUp(self):
        # Criando dois usuários de teste
        self.user1 = User.objects.create_user(username='user1', password='pass12345')
        self.user2 = User.objects.create_user(username='user2', password='pass54321')
        self.category = Category.objects.create(name='Eletrônicos')
        
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )

        # Criando um item para o user1
        self.item = Item.objects.create(
            name="Item 1",
            category_id=self.category.id,  # Suponha que a categoria com ID 1 já exista
            price=100.0,
            created_by=self.user1,
            is_sold=False,
            image=image
        )

    def test_new_conversation_view(self):
        # Loga o user2
        self.client.login(username='user2', password='pass54321')

        # Verifica se a view carrega corretamente
        response = self.client.get(reverse('conversation:new', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'conversation/new.html')

        # Testa criação de uma nova conversa via POST
        form_data = {
            'content': 'Olá, estou interessado no seu item.'
        }
        response = self.client.post(reverse('conversation:new', args=[self.item.pk]), data=form_data)
        
        # Verifica se o redirecionamento ocorreu
        self.assertEqual(response.status_code, 302)
        conversation = Conversation.objects.filter(item=self.item, members=self.user2).first()
        self.assertIsNotNone(conversation)
        self.assertEqual(conversation.members.count(), 2)  # user1 e user2

        # Verifica se a mensagem foi criada
        self.assertTrue(ConversationMessage.objects.filter(conversation=conversation, content='Olá, estou interessado no seu item.').exists())

    def test_inbox_view(self):
        # Loga o user1
        self.client.login(username='user1', password='pass12345')

        # Cria uma conversa entre user1 e user2
        conversation = Conversation.objects.create(item=self.item)
        conversation.members.add(self.user1, self.user2)
        
        # Acessa a view inbox
        response = self.client.get(reverse('conversation:inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'conversation/inbox.html')
        
        # Verifica se o nome do item relacionado à conversa está sendo exibido
        self.assertContains(response, self.item.name)  # Verifica o nome do item no template

    def test_detail_view(self):
        # Loga o user1
        self.client.login(username='user1', password='pass12345')

        # Cria uma conversa entre user1 e user2
        conversation = Conversation.objects.create(item=self.item)
        conversation.members.add(self.user1, self.user2)

        # Acessa a view de detalhes da conversa
        response = self.client.get(reverse('conversation:detail', args=[conversation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'conversation/detail.html')

        # Verifica se o formulário de mensagem está no contexto
        self.assertIsInstance(response.context['form'], ConversationMessageForm)

    def test_detail_view_post_message(self):
        # Loga o user1
        self.client.login(username='user1', password='pass12345')

        # Cria uma conversa entre user1 e user2
        conversation = Conversation.objects.create(item=self.item)
        conversation.members.add(self.user1, self.user2)

        # Envia uma mensagem via POST
        form_data = {
            'content': 'Esta é uma nova mensagem.'
        }
        response = self.client.post(reverse('conversation:detail', args=[conversation.pk]), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redireciona após sucesso

        # Verifica se a mensagem foi criada na conversa
        self.assertTrue(ConversationMessage.objects.filter(conversation=conversation, content='Esta é uma nova mensagem.').exists())

    def test_conversation_message_form_valid(self):
        # Testa se o formulário de mensagem é válido com dados válidos
        form_data = {
            'content': 'Esta é uma mensagem válida.'
        }
        form = ConversationMessageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_conversation_message_form_invalid(self):
        # Testa se o formulário de mensagem é inválido com dados vazios
        form_data = {
            'content': ''  # Campo vazio
        }
        form = ConversationMessageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
