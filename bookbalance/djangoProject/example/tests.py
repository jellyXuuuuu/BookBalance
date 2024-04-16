from django.test import TestCase
from django.urls import reverse
from .models import User, Record, Catalog, Record_Type, Fund, Report
from django.contrib.messages import get_messages
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from datetime import date
import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.middleware import SessionMiddleware

class LoginViewTests(TestCase):

    def setUp(self):
        # Create test user
        self.username = 'testuser'
        self.password = 'password123'
        self.email = 'testuser@example.com'
        User.objects.create(username=self.username, password=self.password, email=self.email)

    def test_login_success(self):
        # Test successful login
        response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        self.assertTrue(response.status_code, 302)


    def test_login_failure(self):
        # Provided wrong password
        response = self.client.post(reverse('login'), {'username': self.username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == "Incorrect password or username. Please try again." for message in messages))

    def test_auto_login_with_cookies(self):
        # Test automatic login via cookies
        self.client.cookies['username'] = self.username
        self.client.cookies['password'] = self.password
        response = self.client.get(reverse('login'))
        self.assertTrue(response.status_code, 302)

    def test_render_login_form(self):
        # Test rendering login form
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'system/log_in.html')

class RegisterViewTests(TestCase):

    def test_register_success(self):
        # Test successful registration
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpassword123',
            'repassword': 'testpassword123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_password_mismatch(self):
        # Test password inconsistencies
        response = self.client.post(reverse('register'), {
            'username': 'usermismatch',
            'email': 'mismatch@example.com',
            'password': 'password',
            'repassword': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='usermismatch').exists())

    def test_username_exists(self):
        User.objects.create(username='existinguser', email='existing@example.com', password='testpassword')
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'email': 'user@example.com',
            'password': 'password123',
            'repassword': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == "Username already exists." for message in messages))

class LogoutViewTests(TestCase):
    def test_logout(self):
        session = self.client.session
        session['username'] = 'testuser'
        session.save()
        self.client.cookies['username'] = 'testuser'
        self.client.cookies['password'] = 'password123'

        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, reverse('index'))

        self.assertEqual(response.cookies['username'].value, '')
        self.assertEqual(response.cookies['password'].value, '')

        self.assertNotIn('username', self.client.session)

class RecordCreateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser', password='12345', email='testuser@example.com')
        self.username = self.user.username

    def test_record_create_success(self):
        # Test successfully created record
        url = reverse('record_create_with_username', kwargs={'username': self.username})
        response = self.client.post(url, {
            'Date': '2023-03-10',
            'Category': Catalog.Grocery.value,
            'description': 'Test grocery shopping',
            'type': Record_Type.Out.value,
            'Amount': '100.00'
        })
        self.assertRedirects(response, reverse("record_list_with_username", kwargs={'username': self.username}))
        self.assertTrue(Record.objects.filter(description='Test grocery shopping').exists())

    def test_record_create_form_invalid(self):
        # Testing for form validation failures
        url = reverse('record_create_with_username', kwargs={'username': self.username})
        response = self.client.post(url, {
            'Date': '2023-03-10',
            'Category': '',
            'description': '',
            'type': '',
            'Amount': '100.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Record.objects.filter(Amount=100.00).exists())

class RecordListViewTests(TestCase):

    def setUp(self):
        # Create test users and related records
        self.username = 'testuser'
        self.user = User.objects.create(username=self.username, email='test@example.com', password='testpassword')
        Record.objects.create(username=self.username, Date='2023-03-10', Category=0, description='Income example', type=0, Amount=Decimal('100.00'))
        Record.objects.create(username=self.username, Date='2023-03-11', Category=1, description='Expense example', type=1, Amount=Decimal('50.00'))
        Fund.objects.create(username=self.username, Budget=Decimal('1000.00'), Rest=Decimal('950.00'))

    def test_record_list(self):
        url = reverse('record_list_with_username', kwargs={'username': self.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Income example')
        self.assertContains(response, 'Expense example')
        self.assertContains(response, str(100.00))
        self.assertContains(response, str(50.00))
        self.assertContains(response, str(1000.00))
        self.assertContains(response, str(950.00))

    def test_record_list_without_fund(self):
        # Delete the Fund record to test the situation without a Fund record
        Fund.objects.get(username=self.username).delete()
        url = reverse('record_list_with_username', kwargs={'username': self.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(0.00))

class RecordDetailViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.user = User.objects.create(username=self.username, email='testuser@example.com', password='12345')
        self.record = Record.objects.create(
            username=self.username,
            Date='2023-03-10',
            Category=0,
            description='Test Description',
            type=0,
            Amount=Decimal('100.00')
        )

    def test_record_detail_success(self):
        # The test can successfully display the record details
        url = reverse('record_detail', kwargs={'pk': self.record.pk, 'username': self.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Description')
        self.assertContains(response, self.username)

    def test_record_detail_not_found(self):
        # Test what happens when the record does not exist
        non_existent_pk = self.record.pk + 1
        url = reverse('record_detail', kwargs={'pk': non_existent_pk, 'username': self.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class RecordUpdateViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.user = User.objects.create(username=self.username, email='testuser@example.com', password='12345')
        self.record = Record.objects.create(
            username=self.username,
            Date='2023-03-10',
            Category=0,
            description='Original Description',
            type=0,
            Amount=Decimal('100.00')
        )

    def test_record_update_get(self):
        # Test whether the form and initial values are displayed correctly when making a GET request
        url = reverse('record_update', kwargs={'pk': self.record.pk, 'username': self.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Original Description')

    def test_record_update_post(self):
        # Test whether records can be updated correctly during POST requests
        url = reverse('record_update', kwargs={'pk': self.record.pk, 'username': self.username})
        updated_data = {
            'Date': '2023-03-10',
            'Category': 0,
            'description': 'Updated Description',
            'type': 0,
            'Amount': '150.00'
        }
        response = self.client.post(url, updated_data)
        self.assertRedirects(response, reverse("record_detail", kwargs={'pk': self.record.pk, 'username': self.username}))

        self.record.refresh_from_db()
        self.assertEqual(self.record.description, 'Updated Description')
        self.assertEqual(self.record.Amount, Decimal('150.00'))


class RecordDeleteViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.user = User.objects.create(username=self.username, email='testuser@example.com', password='12345')
        self.record = Record.objects.create(
            username=self.username,
            Date='2023-03-10',
            Category=0,
            description='Delete Me',
            type=0,
            Amount=Decimal('100.00')
        )

    def test_record_delete(self):
        # Test whether records can be deleted correctly and redirected
        self.assertTrue(Record.objects.filter(pk=self.record.pk).exists())
        url = reverse('record_delete', kwargs={'username': self.username, 'pk': self.record.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("record_list_with_username", kwargs={'username': self.username}))

        # 确保记录被删除
        self.assertFalse(Record.objects.filter(pk=self.record.pk).exists())

class FundModelTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        User.objects.create(username=self.username, email='testuser@example.com', password='12345')

    def test_create_fund(self):
        # Test creating a new Fund record
        Fund.objects.create(username=self.username, Budget=Decimal('1000.00'), Rest=Decimal('800.00'))
        fund = Fund.objects.get(username=self.username)
        self.assertEqual(fund.Budget, Decimal('1000.00'))
        self.assertEqual(fund.Rest, Decimal('800.00'))

    def test_update_fund(self):
        Fund.objects.create(username=self.username, Budget=Decimal('1000.00'), Rest=Decimal('800.00'))
        Fund.objects.filter(username=self.username).update(Budget=Decimal('1200.00'), Rest=Decimal('1000.00'))
        fund = Fund.objects.get(username=self.username)
        self.assertEqual(fund.Budget, Decimal('1200.00'))
        self.assertEqual(fund.Rest, Decimal('1000.00'))

class ReportAddViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = '12345'
        self.email = 'testuser@example.com'
        self.user = User.objects.create(username=self.username, email=self.email, password=make_password(self.password))



    def test_report_add_success(self):
        # Test successfully added report
        session = self.client.session
        session['username'] = self.username
        session.save()

        response = self.client.post(reverse('report'), {
            'email': self.email,
            'message': 'This is a test report detail.'
        })
        self.assertTrue(Report.objects.filter(username=self.username, email=self.email,
                                              report_detail='This is a test report detail.').exists())

        # Check if the response redirects to the expected URL
        self.assertRedirects(response, reverse("record_list_with_username", kwargs={'username': self.username}))


class SearchViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.email = 'test@example.com'
        self.user = User.objects.create(username=self.username, password=self.password, email=self.email)

        session = self.client.session
        session['username'] = self.username
        session.save()

        # 创建测试记录
        Record.objects.create(username=self.username, Date='2023-01-01', Category=Catalog.Grocery.value, description='Grocery shopping', type=Record_Type.Out.value, Amount=Decimal('50.00'))
        Record.objects.create(username=self.username, Date='2023-01-01', Category=Catalog.Investment.value, description='Investment income', type=Record_Type.In.value, Amount=Decimal('200.00'))

    def test_search_post_with_results(self):
        # Test submission search form and expect results to be returned
        url = reverse('search')
        response = self.client.post(url, {'date': '2023-01-01'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Grocery shopping')
        self.assertContains(response, 'Investment income')
        self.assertContains(response, str(200.00))
        self.assertContains(response, str(50.00))
        self.assertContains(response, str(150.00))

    def test_search_post_no_results(self):
        # Test submitting search form but no results
        url = reverse('search')
        response = self.client.post(url, {'date': '2023-02-01'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Grocery shopping')
        self.assertNotContains(response, 'Investment income')

class ChatboxViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = 'password'
        self.email = 'test@example.com'
        self.user = User.objects.create(username=self.username, password=self.password, email=self.email)

        session = self.client.session
        session['username'] = self.username
        session.save()

        Record.objects.create(username=self.username, Date=date.today(), Category=0, description='Test Income', type=Record_Type.In.value, Amount=100)
        Record.objects.create(username=self.username, Date=date.today(), Category=1, description='Test Expense', type=Record_Type.Out.value, Amount=50)

    def test_chatbox_income_query(self):
        # Test query "income" keyword
        response = self.client.post(reverse('chatbox'), data={'query': 'income'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Income')

    def test_chatbox_outcome_query(self):
        # Test query "outcome" keyword
        response = self.client.post(reverse('chatbox'), data={'query': 'outcome'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Expense')

    def test_chatbox_invalid_date_format(self):
        # Test for invalid date format
        response = self.client.post(reverse('chatbox'), data={'date': 'invalid-date'})
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == "Invalid date input. Please enter a valid date (YYYY-MM-DD), year (YYYY), or month (YYYY-MM)." for message in messages))

    def test_chatbox_valid_date_query(self):
        # Test valid date query
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        response = self.client.post(reverse('chatbox'), data={'date': today_str})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Income')
        self.assertContains(response, 'Test Expense')

class AccountViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = 'old_password'
        self.email = 'test@example.com'
        User.objects.create(username=self.username, password=self.password, email=self.email)

    def test_password_change_success(self):
        # Test password changed successfully
        url = reverse('account', kwargs={'username': self.username})
        new_password = 'new_password'
        response = self.client.post(url, {'old_password': self.password, 'new_password': new_password, 'repassword': new_password})
        updated_user = User.objects.get(username=self.username)
        self.assertEqual(updated_user.password, new_password)
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Your password was successfully updated!', messages)

    def test_incorrect_old_password(self):
        # Test entering your old password incorrectly
        url = reverse('account', kwargs={'username': self.username})
        response = self.client.post(url, {'old_password': 'wrong_password', 'new_password': 'new_password', 'repassword': 'new_password'})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Incorrect old password. Please try again.', messages)

    def test_password_mismatch(self):
        # Test new password and confirm password don't match
        url = reverse('account', kwargs={'username': self.username})
        response = self.client.post(url, {'old_password': self.password, 'new_password': 'new_password1', 'repassword': 'new_password2'})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('New password not equal to repeat password.', messages)

class VisualizationTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.email = 'test@example.com'

        self.user = User.objects.create(username=self.username, password=self.password, email=self.email)

        session = self.client.session
        session['username'] = self.username
        session.save()

        Record.objects.create(username=self.username, Date='2023-01-01', Category=Catalog.Grocery.value, description='Grocery shopping', type=Record_Type.Out.value, Amount=Decimal('50.00'))
        Record.objects.create(username=self.username, Date='2023-01-01', Category=Catalog.Other.value, description='Grocery shopping', type=Record_Type.In.value, Amount=Decimal('1000.50'))
        Record.objects.create(username=self.username, Date='2023-02-01', Category=Catalog.Investment.value, description='Investment income', type=Record_Type.In.value, Amount=Decimal('200.00'))
        Record.objects.create(username=self.username, Date='2023-02-01', Category=Catalog.Investment.value, description='Investment income', type=Record_Type.In.value, Amount=Decimal('200.00'))
        Record.objects.create(username=self.username, Date='2023-03-01', Category=Catalog.Investment.value, description='d', type=Record_Type.In.value, Amount=Decimal('200.00'))
        Record.objects.create(username=self.username, Date='2023-04-01', Category=Catalog.Investment.value, description='d', type=Record_Type.In.value, Amount=Decimal('10.00'))
        Record.objects.create(username=self.username, Date='2023-05-01', Category=Catalog.Investment.value, description='d', type=Record_Type.In.value, Amount=Decimal('20.00'))
        Record.objects.create(username=self.username, Date='2023-06-01', Category=Catalog.Investment.value, description='d', type=Record_Type.In.value, Amount=Decimal('50.00'))
        Record.objects.create(username=self.username, Date='2023-07-01', Category=Catalog.Investment.value, description='d', type=Record_Type.In.value, Amount=Decimal('100.00'))
        Record.objects.create(username=self.username, Date='2023-07-01', Category=Catalog.Entertainment.value, description='d', type=Record_Type.In.value, Amount=Decimal('60.00'))
        Record.objects.create(username=self.username, Date='2023-07-02', Category=Catalog.Other.value, description='d', type=Record_Type.In.value, Amount=Decimal('160.00'))
        Record.objects.create(username=self.username, Date='2023-07-03', Category=Catalog.Grocery.value, description='d', type=Record_Type.Out.value, Amount=Decimal('170.00'))
        Record.objects.create(username=self.username, Date='2023-07-11', Category=Catalog.Housing.value, description='d', type=Record_Type.Out.value, Amount=Decimal('800.00'))
        Record.objects.create(username=self.username, Date='2023-07-12', Category=Catalog.Medical.value, description='d', type=Record_Type.Out.value, Amount=Decimal('70.00'))
        Record.objects.create(username=self.username, Date='2023-07-21', Category=Catalog.Education.value, description='d', type=Record_Type.Out.value, Amount=Decimal('32.00'))
        Record.objects.create(username=self.username, Date='2023-07-21', Category=Catalog.Entertainment.value, description='d', type=Record_Type.Out.value, Amount=Decimal('1050.00'))
        Record.objects.create(username=self.username, Date='2023-07-21', Category=Catalog.Investment.value, description='d', type=Record_Type.In.value, Amount=Decimal('1360.00'))
        Record.objects.create(username=self.username, Date='2023-07-21', Category=Catalog.Entertainment.value, description='d', type=Record_Type.Out.value, Amount=Decimal('750.00'))
        Record.objects.create(username=self.username, Date='2023-07-21', Category=Catalog.Other.value, description='d', type=Record_Type.In.value, Amount=Decimal('550.00'))
        Record.objects.create(username=self.username, Date='2023-07-21', Category=Catalog.Entertainment.value, description='d', type=Record_Type.Out.value, Amount=Decimal('50.00'))
        Record.objects.create(username=self.username, Date='2024-01-01', Category=Catalog.Grocery.value, description='d', type=Record_Type.Out.value, Amount=Decimal('80.00'))
        Record.objects.create(username=self.username, Date='2024-01-02', Category=Catalog.Grocery.value, description='d', type=Record_Type.Out.value, Amount=Decimal('60.00'))


    def test_retrieve_current_month_income_expense(self):
        # Assertions for July 2023
        response = self.client.post(reverse('retrieve_current_month_income_expense'), {'year': '2023', 'month': '7'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('month_category_income', data)
        self.assertIn('month_category_expense', data)

        # Extract actual values from the response
        investment_income = next((item for item in data['month_category_income'] if item["name"] == "Investment"), None)
        entertainment_expense = next(
            (item for item in data['month_category_expense'] if item["name"] == "Entertainment"), None)

        # Check for the exact values calculated above
        self.assertEqual(investment_income['value'], "1460.00")
        self.assertEqual(entertainment_expense['value'], "1850.00")


    def test_retrieve_current_year_income_expense(self):
        # Assertions for 2023
        response = self.client.post(reverse('retrieve_current_year_income_expense'), {'year': '2023'})
        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Checks for specific categories
        for category_data in data['year_category_income'] + data['year_category_expense']:
            if category_data['name'] == 'Investment':
                self.assertAlmostEqual(category_data['value'], "2940.50")
            elif category_data['name'] == 'Grocery':
                self.assertAlmostEqual(category_data['value'], "170")
            elif category_data['name'] == 'Housing':
                self.assertAlmostEqual(category_data['value'], "800")
            elif category_data['name'] == 'Medical':
                self.assertAlmostEqual(category_data['value'], "70")
            elif category_data['name'] == 'Education':
                self.assertAlmostEqual(category_data['value'], "32")
            elif category_data['name'] == 'Entertainment':
                self.assertAlmostEqual(category_data['value'], "1900")
            elif category_data['name'] == 'Other':
                self.assertAlmostEqual(category_data['value'], "710")

    def test_retrieve_year_has_data(self):
        response = self.client.get(reverse('retrieve_year_has_data'))
        self.assertEqual(response.status_code, 200)

        # List of expected years
        expected_years = [2023, 2024]

        # Verify that the list of years returned is correct.
        data = response.json()
        self.assertIn('years', data)
        returned_years = data['years']
        self.assertEqual(len(returned_years), len(expected_years))
        for year in expected_years:
            self.assertIn(year, returned_years)

    def test_retrieve_month_has_data(self):
        # Check the data for 2023
        response = self.client.post(reverse('retrieve_month_has_data'), {'year': '2023'})
        self.assertEqual(response.status_code, 200)

        # List of expected months
        expected_months_2023 = [1, 2, 3, 4, 5, 6, 7]

        # Verify that the returned list of months is correct.
        data = response.json()
        self.assertIn('months', data)
        returned_months = data['months']
        self.assertEqual(len(returned_months), len(expected_months_2023))
        for month in expected_months_2023:
            self.assertIn(month, returned_months)

