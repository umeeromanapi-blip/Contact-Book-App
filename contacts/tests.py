from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from .models import Contact
from .forms import ContactForm, CSVImportForm


class ContactModelTests(TestCase):
    """Unit tests for Contact model and database persistence (Epic 1, 2 & 3)."""

    def test_create_contact_model_with_epic3_fields(self):
        """Test creating a contact record with category, notes, and to_dict()."""
        contact = Contact.objects.create(
            name="Alan Turing", 
            phone="+1-555-0199",
            email="alan@enigma.org",
            category="work",
            notes="Station X lead cryptanalyst",
            is_favorite=True
        )
        self.assertIsNotNone(contact.id)
        self.assertEqual(contact.name, "Alan Turing")
        self.assertEqual(contact.category, "work")
        self.assertEqual(contact.notes, "Station X lead cryptanalyst")
        self.assertTrue(contact.is_favorite)

        # Test to_dict serialization for REST API
        d = contact.to_dict()
        self.assertEqual(d['id'], contact.id)
        self.assertEqual(d['name'], "Alan Turing")
        self.assertEqual(d['category'], "work")
        self.assertEqual(d['category_display'], "Work / Office")

    def test_default_category_is_personal(self):
        """Default category is 'personal'."""
        c = Contact.objects.create(name="Default Cat", phone="123")
        self.assertEqual(c.category, "personal")
        self.assertEqual(c.notes, "")

    def test_default_ordering_newest_first(self):
        """Contacts order by -id."""
        c1 = Contact.objects.create(name="First Contact", phone="111")
        c2 = Contact.objects.create(name="Second Contact", phone="222")
        contacts = list(Contact.objects.all())
        self.assertEqual(contacts[0].id, c2.id)
        self.assertEqual(contacts[1].id, c1.id)


class ContactFormTests(TestCase):
    """Unit tests for ContactForm and CSVImportForm validation rules."""

    def test_valid_form_with_all_epic3_fields(self):
        """Valid form with category and notes passes."""
        form = ContactForm(data={
            'name': 'Grace Hopper',
            'phone': '+1-800-555-0123',
            'email': 'grace.hopper@navy.mil',
            'category': 'work',
            'notes': 'Compiler pioneer and admiral',
            'is_favorite': True
        })
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.category, 'work')
        self.assertEqual(contact.notes, 'Compiler pioneer and admiral')

    def test_notes_whitespace_is_trimmed(self):
        """Whitespace in notes is stripped."""
        form = ContactForm(data={
            'name': 'Margaret Hamilton',
            'phone': '+1-555-1212',
            'notes': '   Apollo 11 Lead   '
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['notes'], 'Apollo 11 Lead')

    def test_csv_import_form_valid(self):
        """CSV file with .csv extension passes form validation."""
        csv_content = b"Name,Phone,Email\nTest User,123456,test@example.com"
        uploaded_file = SimpleUploadedFile("contacts.csv", csv_content, content_type="text/csv")
        form = CSVImportForm(files={'csv_file': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_csv_import_form_invalid_extension(self):
        """Non-CSV file is rejected."""
        txt_content = b"Some random text"
        uploaded_file = SimpleUploadedFile("contacts.txt", txt_content, content_type="text/plain")
        form = CSVImportForm(files={'csv_file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertIn('csv_file', form.errors)


class ContactViewIntegrationTests(TestCase):
    """Integration tests for web views, pagination, bulk operations, and import."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('contact_list')

    def test_get_home_page_and_empty_state(self):
        """GET / renders empty state."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts/index.html')
        self.assertContains(response, 'Contact Book')
        self.assertContains(response, 'No contacts saved yet')

    def test_category_filtering(self):
        """Filter contacts by category parameter."""
        Contact.objects.create(name="Work Colleague", phone="111", category="work")
        Contact.objects.create(name="Family Member", phone="222", category="family")

        res_work = self.client.get(self.url + '?category=work')
        self.assertContains(res_work, 'Work Colleague')
        self.assertNotContains(res_work, 'Family Member')

        res_family = self.client.get(self.url + '?category=family')
        self.assertContains(res_family, 'Family Member')
        self.assertNotContains(res_family, 'Work Colleague')

    def test_pagination(self):
        """Pagination breaks contacts into pages of 8."""
        for i in range(12):
            Contact.objects.create(name=f"Contact {i:02d}", phone=f"555-{i:04d}")

        res_page1 = self.client.get(self.url + '?page=1')
        self.assertEqual(len(res_page1.context['contacts']), 8)
        self.assertEqual(res_page1.context['page_obj'].paginator.num_pages, 2)

        res_page2 = self.client.get(self.url + '?page=2')
        self.assertEqual(len(res_page2.context['contacts']), 4)

    def test_bulk_delete(self):
        """Bulk action deletes multiple selected contacts."""
        c1 = Contact.objects.create(name="Delete Me 1", phone="111")
        c2 = Contact.objects.create(name="Delete Me 2", phone="222")
        c3 = Contact.objects.create(name="Keep Me", phone="333")

        res = self.client.post(reverse('contact_bulk_action'), {
            'bulk_action': 'delete',
            'selected_contacts': [c1.id, c2.id]
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.first().id, c3.id)

    def test_bulk_favorite(self):
        """Bulk action marks contacts as favorites."""
        c1 = Contact.objects.create(name="Star 1", phone="111", is_favorite=False)
        c2 = Contact.objects.create(name="Star 2", phone="222", is_favorite=False)

        res = self.client.post(reverse('contact_bulk_action'), {
            'bulk_action': 'favorite',
            'selected_contacts': [c1.id, c2.id]
        })
        self.assertEqual(res.status_code, 302)
        c1.refresh_from_db()
        c2.refresh_from_db()
        self.assertTrue(c1.is_favorite)
        self.assertTrue(c2.is_favorite)

    def test_csv_import_valid_data(self):
        """Importing valid CSV creates contacts."""
        csv_data = (
            "Name,Phone,Email,Category,Notes,Favorite\n"
            "Ada Lovelace,+44 12345,ada@comp.org,vip,First programmer,Yes\n"
            "Charles Babbage,+44 67890,charles@engine.org,work,Difference Engine,No\n"
        ).encode('utf-8')

        uploaded = SimpleUploadedFile("batch.csv", csv_data, content_type="text/csv")
        res = self.client.post(reverse('contact_import_csv'), {'csv_file': uploaded})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Contact.objects.count(), 2)

        ada = Contact.objects.get(name="Ada Lovelace")
        self.assertEqual(ada.category, "vip")
        self.assertTrue(ada.is_favorite)
        self.assertEqual(ada.notes, "First programmer")

    def test_download_sample_csv(self):
        """Downloading sample CSV returns valid attachment."""
        res = self.client.get(reverse('contact_download_sample_csv'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/csv')
        self.assertIn('sample_contacts_import.csv', res['Content-Disposition'])

    def test_edit_contact_view(self):
        """Update existing contact via contact_update view."""
        contact = Contact.objects.create(name="Original", phone="123", category="personal")
        edit_url = reverse('contact_update', kwargs={'pk': contact.id})

        res = self.client.post(edit_url, {
            'name': 'Updated',
            'phone': '456',
            'category': 'work',
            'notes': 'Promoted',
            'is_favorite': True
        })
        self.assertEqual(res.status_code, 302)
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'Updated')
        self.assertEqual(contact.category, 'work')
        self.assertEqual(contact.notes, 'Promoted')
        self.assertTrue(contact.is_favorite)

    def test_delete_contact_view(self):
        """Delete contact via contact_delete view."""
        contact = Contact.objects.create(name="To Delete", phone="999")
        delete_url = reverse('contact_delete', kwargs={'pk': contact.id})

        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Contact.objects.count(), 0)

    def test_toggle_favorite_view(self):
        """Toggle favorite status."""
        contact = Contact.objects.create(name="Star Me", phone="555", is_favorite=False)
        fav_url = reverse('contact_toggle_favorite', kwargs={'pk': contact.id})

        res = self.client.post(fav_url)
        self.assertEqual(res.status_code, 302)
        contact.refresh_from_db()
        self.assertTrue(contact.is_favorite)

    def test_export_csv_view(self):
        """Export all contacts as CSV."""
        Contact.objects.create(name="Export Person", phone="777", email="exp@test.com")
        res = self.client.get(reverse('contact_export_csv'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('contact_book_export.csv', res['Content-Disposition'])
        self.assertIn('Export Person', res.content.decode('utf-8'))


class ContactRESTAPITests(TestCase):
    """Integration tests for Epic 3 REST API endpoints (JSON)."""

    def setUp(self):
        self.client = Client()

    def test_api_list_and_create(self):
        """GET /api/contacts/ and POST /api/contacts/."""
        # Test empty list
        res = self.client.get(reverse('api_contact_list_create'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 0)

        # Test POST create
        payload = {
            'name': 'API Contact',
            'phone': '+1 555-9999',
            'email': 'api@test.com',
            'category': 'work',
            'notes': 'Created via REST API',
            'is_favorite': True
        }
        post_res = self.client.post(
            reverse('api_contact_list_create'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(post_res.status_code, 201)
        created_data = post_res.json()
        self.assertTrue(created_data['success'])
        self.assertEqual(created_data['contact']['name'], 'API Contact')
        self.assertEqual(created_data['contact']['category'], 'work')

        # Test list with query
        list_res = self.client.get(reverse('api_contact_list_create') + '?q=API')
        self.assertEqual(list_res.json()['count'], 1)

    def test_api_detail_update_delete(self):
        """GET, PUT, DELETE /api/contacts/<id>/."""
        contact = Contact.objects.create(name="Original", phone="111", category="friends")
        detail_url = reverse('api_contact_detail', kwargs={'pk': contact.id})

        # GET detail
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()['contact']['name'], 'Original')

        # PUT update
        put_payload = {'name': 'Updated via API', 'category': 'vip', 'notes': 'New notes'}
        put_res = self.client.put(
            detail_url,
            data=json.dumps(put_payload),
            content_type='application/json'
        )
        self.assertEqual(put_res.status_code, 200)
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'Updated via API')
        self.assertEqual(contact.category, 'vip')

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)

    def test_api_stats(self):
        """GET /api/contacts/stats/ returns summary counts."""
        Contact.objects.create(name="C1", phone="1", category="work", is_favorite=True)
        Contact.objects.create(name="C2", phone="2", category="work", is_favorite=False)
        Contact.objects.create(name="C3", phone="3", category="family", is_favorite=True)

        res = self.client.get(reverse('api_contact_stats'))
        self.assertEqual(res.status_code, 200)
        stats = res.json()['stats']
        self.assertEqual(stats['total_contacts'], 3)
        self.assertEqual(stats['favorite_contacts'], 2)
        self.assertEqual(stats['category_breakdown']['work'], 2)
        self.assertEqual(stats['category_breakdown']['family'], 1)

    def test_api_errors(self):
        """API handles bad JSON and missing entity 404."""
        # 404 for missing contact
        res_404 = self.client.get('/api/contacts/99999/')
        self.assertEqual(res_404.status_code, 404)

        # 400 for empty name in create
        res_bad = self.client.post(
            reverse('api_contact_list_create'),
            data=json.dumps({'name': '', 'phone': '123'}),
            content_type='application/json'
        )
        self.assertEqual(res_bad.status_code, 400)


from django.contrib.auth.models import User
from .models import ActivityLog


class ContactEpic4Tests(TestCase):
    """Integration and Unit tests for Epic 4: Auth, Multi-user Isolation, Dashboard & vCard."""

    def setUp(self):
        self.client = Client()

    def test_user_registration(self):
        """User registration creates account and auto-authenticates."""
        reg_url = reverse('user_register')
        res = self.client.post(reg_url, {
            'username': 'alice',
            'email': 'alice@wonderland.org',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='alice').exists())
        user = User.objects.get(username='alice')
        self.assertTrue(user.check_password('SecurePassword123!'))

    def test_user_login_and_logout(self):
        """Login authenticates user, logout terminates session."""
        user = User.objects.create_user(username='bob', password='BobPassword123!')
        login_url = reverse('user_login')

        # Invalid password
        bad_res = self.client.post(login_url, {'username': 'bob', 'password': 'WrongPassword'})
        self.assertEqual(bad_res.status_code, 200)

        # Valid password
        good_res = self.client.post(login_url, {'username': 'bob', 'password': 'BobPassword123!'})
        self.assertEqual(good_res.status_code, 302)

        # Logout
        logout_res = self.client.get(reverse('user_logout'))
        self.assertEqual(logout_res.status_code, 302)

    def test_demo_login(self):
        """1-Click demo login creates/retrieves demo_user and authenticates."""
        res = self.client.get(reverse('user_demo_login'))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='demo_user').exists())

    def test_multi_user_isolation(self):
        """User A contacts are isolated from User B."""
        user_a = User.objects.create_user(username='user_a', password='PassA123!')
        user_b = User.objects.create_user(username='user_b', password='PassB123!')

        Contact.objects.create(user=user_a, name="Secret Contact of A", phone="111")
        Contact.objects.create(user=user_b, name="Secret Contact of B", phone="222")

        # Login as User A
        self.client.login(username='user_a', password='PassA123!')
        res_a = self.client.get(reverse('contact_list'))
        self.assertContains(res_a, "Secret Contact of A")
        self.assertNotContains(res_a, "Secret Contact of B")

        # Login as User B
        self.client.login(username='user_b', password='PassB123!')
        res_b = self.client.get(reverse('contact_list'))
        self.assertContains(res_b, "Secret Contact of B")
        self.assertNotContains(res_b, "Secret Contact of A")

    def test_vcard_export(self):
        """Exporting contact as vCard generates valid RFC vCard (.vcf) format."""
        contact = Contact.objects.create(
            name="Grace Hopper",
            phone="+1 800-555-0123",
            email="grace@navy.mil",
            category="work",
            notes="Compiler Pioneer"
        )
        vcard_url = reverse('contact_export_vcard', kwargs={'pk': contact.id})
        res = self.client.get(vcard_url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/vcard; charset=utf-8')
        self.assertIn('.vcf', res['Content-Disposition'])

        content = res.content.decode('utf-8')
        self.assertIn("BEGIN:VCARD", content)
        self.assertIn("VERSION:3.0", content)
        self.assertIn("FN:Grace Hopper", content)
        self.assertIn("TEL;TYPE=CELL:+1 800-555-0123", content)
        self.assertIn("EMAIL;TYPE=INTERNET:grace@navy.mil", content)
        self.assertIn("END:VCARD", content)

    def test_analytics_dashboard(self):
        """Analytics dashboard renders metrics and distribution."""
        Contact.objects.create(name="C1", phone="111", email="c1@test.com", category="work", is_favorite=True)
        Contact.objects.create(name="C2", phone="222", category="family")

        dash_res = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(dash_res.status_code, 200)
        self.assertTemplateUsed(dash_res, 'contacts/dashboard.html')
        self.assertEqual(dash_res.context['total_contacts'], 2)
        self.assertEqual(dash_res.context['favorite_contacts'], 1)
        self.assertEqual(dash_res.context['with_email'], 1)

    def test_activity_logging(self):
        """Operations write to ActivityLog."""
        user = User.objects.create_user(username='logger_user', password='LogPass123!')
        self.client.login(username='logger_user', password='LogPass123!')

        self.client.post(reverse('contact_list'), {
            'name': 'Logged Person',
            'phone': '555-1234'
        })
        self.assertTrue(ActivityLog.objects.filter(action='create').exists())

