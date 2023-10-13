import pandas as pd
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Datasets, Files


class TestMain(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test-user')
        self.user.set_password('password-test')
        self.user.save()
        self.dataset = Datasets.objects.create(user_id=self.user.id, path='test-dataset')
        dataset_id = self.dataset.id
        data = pd.DataFrame({'Name': ['Tom', 'Joseph', 'Krish', 'John'],
                             'Age': [20, 21, 19, 18]})
        self.file = Files.objects.create(user_id=self.user.id, dataset_id=dataset_id, name='test-file', data=data.to_json(orient='records'))

    def test_login(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_registration(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'test-user')
        self.assertTrue(self.user.check_password('password-test'))

    def test_logout(self):
        client = Client()
        client.login(username='test-user', password='password-test')
        client.logout()
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        client = Client()
        client.login(username='test-user', password='password-test')
        response = client.get(reverse('start'))
        self.assertEqual(response.status_code, 200)

    def test_download_dataset(self):
        client = Client()
        client.login(username='test-user', password='password-test')
        client.post('/download-dataset', data={'dataset-path': 'iamsouravbanerjee/airline-dataset'})
        response = client.get(reverse('start'))
        self.assertEqual(Datasets.objects.count(), 2)
        self.assertEqual(Files.objects.count(), 4)
        self.assertEqual(response.status_code, 200)

    def test_downloaded_file(self):
        client = Client()
        client.login(username='test-user', password='password-test')
        file_id = self.file.id
        url = reverse('downloaded-file', kwargs={'id': file_id})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_file(self):
        client = Client()
        client.login(username='test-user', password='password-test')
        file_id = self.file.id
        client.post('/delete/' + str(file_id))
        response = client.get(reverse('start'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Files.objects.count(), 0)

    def test_set_filter(self):
        client = Client()
        client.login(username='test-user', password='password-test')
        file_id = self.file.id
        filter1 = {'checked': "Age"}
        response1 = client.post('/downloads/' + str(file_id) + '/filter', data=filter1)
        tables1 = pd.read_html(response1.content)
        df1 = tables1[0]
        filter2 = {'checked': "Name,Age"}
        response2 = client.post('/downloads/' + str(file_id) + '/filter', data=filter2)
        tables2 = pd.read_html(response2.content)
        df2 = tables2[0]
        filter3 = {'checked': ""}
        response3 = client.post('/downloads/' + str(file_id) + '/filter', data=filter3)
        tables3 = pd.read_html(response3.content)
        df3 = tables3[0]
        self.assertEqual(len(df1.axes[1]), 2)
        self.assertEqual(len(df2.axes[1]), 3)
        self.assertEqual(len(df3.axes[1]), 3)

    def test_sorting(self):
        client = Client()
        client.login(username='test-user', password='password-test')
        file_id = self.file.id
        results = []
        for i in range(1, 3, 1):
            for j in range(1, 3, 1):
                if i == 1:
                    checked = "Age"
                else:
                    checked = "Name,Age"
                checked_columns = {'filter_checked': checked, 'sorting_checked': checked, 'order': str(j)}
                response = client.post('/downloads/' + str(file_id) + '/sorting', data=checked_columns)
                tables = pd.read_html(response.content)
                df = tables[0]
                result = []
                for ind in df.index:
                    if i == 1:
                        result.append(df['Age'][ind])
                    else:
                        result.append(str(df['Name'][ind]) + ": " + str(df['Age'][ind]))
                results.append(result)
        self.assertEqual(results[0], [18, 19, 20, 21])
        self.assertEqual(results[1], [21, 20, 19, 18])
        self.assertEqual(results[2], ['John: 18', 'Joseph: 21', 'Krish: 19', 'Tom: 20'])
        self.assertEqual(results[3], ['Tom: 20', 'Krish: 19', 'Joseph: 21', 'John: 18'])