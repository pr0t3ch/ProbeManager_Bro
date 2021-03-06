""" venv/bin/python probemanager/manage.py test bro.tests.test_views_admin_bro --settings=probemanager.settings.dev """
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from bro.models import Bro, SignatureBro, RuleSetBro


class ViewsBroAdminTest(TestCase):
    fixtures = ['init', 'crontab', 'test-core-secrets', 'test-bro-signature',
                'test-bro-script', 'test-bro-ruleset', 'test-bro-conf',
                'test-bro-bro']

    def setUp(self):
        self.client = Client()
        User.objects.create_superuser(username='testuser', password='12345', email='testuser@test.com')
        if not self.client.login(username='testuser', password='12345'):
            self.assertRaises(Exception("Not logged"))
        self.date_now = timezone.now()

    def tearDown(self):
        self.client.logout()

    def test_bro(self):
        response = self.client.get('/admin/bro/bro/add/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Bro.get_all()), 1)
        response = self.client.post('/admin/bro/bro/add/', {'name': 'test',
                                                            'secure_deployment': True,
                                                            'scheduled_rules_deployment_enabled': True,
                                                            'scheduled_rules_deployment_crontab': 4,
                                                            'scheduled_check_enabled': True,
                                                            'scheduled_check_crontab': 3,
                                                            'server': 1,
                                                            'rulesets': 101,
                                                            'configuration': 101,
                                                            'installed': True}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(' was added successfully', str(response.content))
        self.assertEqual(len(Bro.get_all()), 2)
        response = self.client.post('/admin/bro/bro/', {'action': 'test_rules',
                                                        '_selected_action': Bro.get_by_name('test').id},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test rules OK', str(response.content))

        response = self.client.post('/admin/bro/scriptbro/add/', {'rev': '0',
                                                                  'rule_full': 'erererooepeoerrrr',
                                                                  'name': 'fail script test',
                                                                  },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('was added successfully', str(response.content))
        self.assertIn('Test script failed', str(response.content))

        response = self.client.post('/admin/bro/signaturebro/add/', {'rev': '0',
                                                                     'rule_full': '1',
                                                                     'sid': '666',
                                                                     'msg': 'fail test',
                                                                     },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('was added successfully', str(response.content))
        self.assertIn('Test signature failed', str(response.content))
        sig = SignatureBro.get_by_msg('fail test')
        ruleset = RuleSetBro.get_by_id(101)
        ruleset.signatures.add(sig)
        ruleset.save()
        response = self.client.post('/admin/bro/bro/', {'action': 'test_rules',
                                                        '_selected_action': Bro.get_by_name('test').id},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test rules failed', str(response.content))

        self.assertTrue(Bro.get_by_name('test').installed)
        response = self.client.post('/admin/bro/bro/' + str(Bro.get_by_name('test').id) + '/change/',
                                    {'name': 'test',
                                     'secure_deployment': True,
                                     'scheduled_rules_deployment_enabled': True,
                                     'scheduled_rules_deployment_crontab': 4,
                                     'scheduled_check_enabled': True,
                                     'scheduled_check_crontab': 3,
                                     'server': 1,
                                     'rulesets': 101,
                                     'configuration': 101,
                                     'installed': False}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(' was changed successfully', str(response.content))
        self.assertFalse(Bro.get_by_name('test').installed)
        response = self.client.post('/admin/bro/bro/',
                                    {'action': 'delete_selected',
                                     '_selected_action': Bro.get_by_name('test').id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Are you sure you want to delete the selected ', str(response.content))
        response = self.client.post('/admin/bro/bro/',
                                    {'action': 'delete_selected',
                                     '_selected_action': Bro.get_by_name('test').id,
                                     'post': 'yes'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully deleted 1 ', str(response.content))

        self.assertEqual(len(Bro.get_all()), 1)

        response = self.client.post('/admin/bro/bro/add/', {'name': 'test',
                                                            'secure_deployment': True,
                                                            'scheduled_rules_deployment_enabled': True,
                                                            'scheduled_rules_deployment_crontab': 4,
                                                            'scheduled_check_enabled': True,
                                                            'scheduled_check_crontab': 3,
                                                            'server': 1,
                                                            'rulesets': 101,
                                                            'configuration': 101,
                                                            'installed': True}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(' was added successfully', str(response.content))
        response = self.client.get('/admin/bro/bro/' + str(Bro.get_by_name('test').id) + '/delete/',
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Are you sure ', str(response.content))
        response = self.client.post('/admin/bro/bro/' + str(Bro.get_by_name('test').id) + '/delete/',
                                    {'post': 'yes'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('was deleted successfully', str(response.content))
        self.assertEqual(len(Bro.get_all()), 1)
