from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import User, Site


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin', password='testpass123', role='admin'
        )
        self.site = Site.objects.create(name='HQ', code='hq', color='#0052CC')

    def test_login_page_loads(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_login_success(self):
        resp = self.client.post(reverse('login'), {
            'username': 'admin', 'password': 'testpass123'
        })
        self.assertRedirects(resp, reverse('dashboard'))

    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertRedirects(resp, '/login/?next=/')

    def test_dashboard_accessible_after_login(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_license_list(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.get(reverse('license_list'))
        self.assertEqual(resp.status_code, 200)

    def test_isp_list(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.get(reverse('isp_list'))
        self.assertEqual(resp.status_code, 200)

    def test_dns_list(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.get(reverse('dns_list'))
        self.assertEqual(resp.status_code, 200)

    def test_cloud_list(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.get(reverse('cloud_list'))
        self.assertEqual(resp.status_code, 200)

    def test_site_switcher(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.post(reverse('switch_site'), {'site_id': self.site.id})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['name'], 'HQ')

    def test_switch_to_all(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.post(reverse('switch_site'), {'site_id': 'all'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['ok'])


class SiteModelTests(TestCase):
    def test_site_str(self):
        site = Site(name='MMG', code='mmg')
        self.assertEqual(str(site), 'MMG')

    def test_user_is_admin(self):
        user = User(username='admin', role='admin')
        self.assertTrue(user.is_admin)

    def test_user_viewer_not_admin(self):
        user = User(username='viewer', role='viewer')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_editor)
