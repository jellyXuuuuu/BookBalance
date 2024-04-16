from django.contrib.auth.hashers import make_password
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User as AuthUser
from django.db.models import Sum
from decimal import Decimal
from .models import Record_Type, Report, Catalog
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from django import forms
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import logout as auth_logout

from . import models
from .models import Fund
from .models import User  # 确保从正确的地方导入你的自定义User模型
from .models import Record
from .forms import RecordForm
import datetime, calendar


from django.db.models.functions import ExtractMonth, ExtractYear

# from .utils import login_required


from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm


''' Login Page '''


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)  # Use get method instead of filter method
        except User.DoesNotExist:
            user = None
        if user and check_password(password, user.password):
            if 'remember' in request.POST:
                response = redirect('mainpage_with_username', username=username)
                response.set_cookie('username', username, max_age=30 * 24 * 60 * 60)
            else:
                request.session['username'] = username
                return redirect('mainpage_with_username', username=username)
            request.session['username'] = username
            return response
        else:
            # Login failed, error message returned
            messages.error(request, 'Incorrect password or username. Please try again.')
            return render(request, 'system/log_in.html')
    else:
        username = request.COOKIES.get('username')
        if username:
            user = User.objects.filter(username=username)
            if user:
                return redirect('mainpage_with_username', username=username)
    return render(request, 'system/log_in.html', {'username': username})


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        repassword = request.POST['repassword']
        if password == repassword:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'system/register.html')
            else:
                user_data = User()
                user_data.username = username
                user_data.email = email
                user_data.password = make_password(password)
                print(user_data.password)
                user_data.save()
                return redirect('login')
    return render(request, 'system/register.html')


def logout(request):
    auth_logout(request)
    response = redirect('index')
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response


def index(request):
    context = {
        'status': '未登录状态'
    }
    return render(request, 'system/index.html', context)


def mainpage(request, username):
    print("mainpage test username: ", username)
    return render(request, 'system/mainpage.html', {'username': username})


def visualization(request):
    username = request.session.get('username')
    print("visualization session username: ", username)
    return render(request, 'system/visualization.html', {"username": username})


def chatbox(request):
    return render(request, 'system/chatbox.html')


def support(request):
    username = request.session.get("username")
    if username is not None:
        return render(request, 'system/support.html', {'username':username, })
    else:
        return render(request, 'system/support.html')


def support0(request):
    return render(request, 'system/support0.html')



def account(request, username):
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    else:
        user = None

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        repassword = request.POST['repassword']
        if new_password == repassword:
            if check_password(old_password, user.password):
                user.password = make_password(new_password)
                user.save()
                error_message=messages.success(request, 'Your password was successfully updated!')
                return redirect(reverse('account', kwargs={'username': user.username}))
            else:
                print("error: Incorrect old password. Please try again.")
                error_message=messages.error(request, 'Incorrect old password. Please try again.')

        else:

            error_message=messages.error(request, 'New password not equal to repeat password.')
            print("error: new password not equal to repeat password.")

    else:
        form = PasswordChangeForm(user)

    return render(request, 'system/account.html', {'form': form, 'username': username, 'user': user})


''' Record CRUD '''


# Create a record
class RecordForm(forms.ModelForm):
    class Meta:
        model = models.Record
        fields = ['Date', 'Category', 'description', 'type', 'Amount']
        widgets = {
            'Date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date', 'class': 'form-control'}),
        }


def record_create(request, username):
    print("Record Create test username: ", username)
    if request.method == "POST":
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.username = username
            record.save()
            return redirect(reverse("record_list_with_username", kwargs={'username': username}))
    else:
        form = RecordForm()
    return render(request, "system/record_form.html", {"form": form, "username": username})


def record_list(request, username):
    # 从数据库获取任务清单
    print("Current User username is: ", username)
    records = models.Record.objects.filter(username=username).order_by("Date")
    total_in = models.Record.objects.filter(username=username, type=models.Record_Type.In).aggregate(Sum('Amount'))
    total_out = models.Record.objects.filter(username=username, type=models.Record_Type.Out).aggregate(Sum('Amount'))
    total_in_amount = round(total_in['Amount__sum'] or 0, 2)
    total_out_amount = round(total_out['Amount__sum'] or 0, 2)
    total = round((total_in_amount - total_out_amount), 2)
    try:
        fund = Fund.objects.get(username=username)
        budget = fund.Budget
        rest = fund.Rest
    except Fund.DoesNotExist:
        # If there is no corresponding Fund record, set the default value
        budget = 0
        rest = 0
    print("total: " ,total)
    context = {
        "records": records,
        "total_in": total_in_amount,  # If there is no In record, 0 is displayed.
        "total_out": total_out_amount,
        "total": total,
        "budget": budget,
        "rest": rest,
        "username": username,
    }
    return render(request, "system/record_list.html", context)


# Retrieve a single record
def record_detail(request, pk, username):
    # Get the pk value of a single task from the url, and then query the database to get a single object
    record = get_object_or_404(Record, pk=pk)
    print("record: ", record)
    return render(request, "system/record_detail.html", {"record": record, "username": username, })


def record_update(request, pk, username):
    # Get the pk value of a single task from the url, and then query the database to obtain a single object instance
    record_obj = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        form = RecordForm(instance=record_obj, data=request.POST)
        if form.is_valid():
            form.save()
        record_id = Record.id
        print("Record id: ", record_id)
        return redirect(reverse("record_detail", args=[ pk, username, ]))
    else:
        form = RecordForm(instance=record_obj)
    return render(request, "system/record_form.html", {"form": form, "object": record_obj, "username": username})


# Delete a single record
def record_delete(request, username, pk):
    record_obj = get_object_or_404(Record, pk=pk)
    record_obj.delete()  # 删除然后跳转
    return redirect(reverse("record_list_with_username", kwargs={'username': username}))


def set_budget(request):
    username = request.session.get('username')
    if request.method == 'POST':
        username = request.session.get('username')
        budget = Decimal(request.POST.get('Budget'))

        fund = Fund.objects.filter(username=username).first()
        total_in = Record.objects.filter(username=username, type=Record_Type.In).aggregate(Sum('Amount'))
        total_out = Record.objects.filter(username=username, type=Record_Type.Out).aggregate(Sum('Amount'))
        total_in_amount = round(total_in['Amount__sum'] or 0, 2)
        total_out_amount = round(total_out['Amount__sum'] or 0, 2)
        rest = round(budget + total_in_amount - total_out_amount, 2)

        if fund:

            # If present, only update the Budget field
            Fund.objects.filter(username=username).update(Budget=budget, Rest=rest)
        else:
            # If it does not exist, create a new Fund record
            Fund.objects.create(username=username, Budget=budget, Rest=rest)

        return redirect(reverse("record_list_with_username", kwargs={'username': username}))
    else:
        # If it is not a POST request, display the form for setting the budget.
        return render(request, 'system/set_budget.html', {'username':username,})

def report_add(request):
    if request.method == 'POST':
        username = request.session.get('username')
        email = request.POST['email']
        detail = request.POST['message']
        report_data = Report()
        report_data.username = username
        report_data.email = email
        report_data.report_detail = detail
        report_data.save()
        return redirect(reverse("record_list_with_username", kwargs={'username': username}))

def retrieve_current_month_income_expense(request):
    username = request.session.get('username')
    post_year = request.POST.get('year')
    post_month = request.POST.get('month')
    if post_year and post_month:
        year = int(post_year)
        month = int(post_month)
    else:
        today = datetime.date.today()
        year = today.year
        month = today.month
    month_has_days = calendar.monthrange(year, month)[1]
    days = [datetime.date(year, month, day).strftime("%Y-%m-%d") for day in range(1, month_has_days + 1)]
    days_income = []
    days_expense = []
    category_names = set()
    month_category_income = {}
    month_category_expense = {}
    month_total_income = 0
    month_total_expense = 0
    month_history_records = Record.objects.filter(Date__year=year, Date__month=month, username=username).order_by(
        "Date")
    for day in days:
        day_history_records = month_history_records.filter(Date__day=int(day.split("-")[-1]))

        day_income = 0
        day_expense = 0
        for hr in day_history_records:
            hr_type = hr.type
            hr_category = hr.Category
            record_category_label = Catalog(hr_category).label
            if hr_type == 1:
                day_expense += hr.Amount
                month_total_expense += hr.Amount
                if record_category_label not in month_category_expense:
                    category_names.add(record_category_label)
                    month_category_expense[record_category_label] = {"value": hr.Amount, "name": record_category_label}
                else:
                    month_category_expense[record_category_label]["value"] += hr.Amount
            elif hr_type == 0:
                day_income += hr.Amount
                month_total_income += hr.Amount
                if record_category_label not in month_category_income:
                    category_names.add(record_category_label)
                    month_category_income[record_category_label] = {"value": hr.Amount, "name": record_category_label}
                else:
                    month_category_income[record_category_label]["value"] += hr.Amount
        days_income.append(day_income)
        days_expense.append(day_expense)
    return JsonResponse({"days": days,
                         "days_income": days_income,
                         "days_expense": days_expense,
                         "month_total_income": month_total_income,
                         "month_total_expense": month_total_expense,
                         "month_category_names": list(category_names),
                         "month_category_income": list(month_category_income.values()),
                         "month_category_expense": list(month_category_expense.values())})



def retrieve_current_year_income_expense(request):
    username = request.session.get('username')
    post_year = request.POST.get('year')
    if post_year:
        year = int(post_year)
    else:
        today = datetime.date.today()
        year = today.year
    months = [i for i in range(1, 13)]
    months_income = []
    months_expense = []
    category_names = set()
    year_category_income = {}
    year_category_expense = {}
    year_total_income = 0
    year_total_expense = 0
    year_history_records = Record.objects.filter(Date__year=year, username=username).order_by("Date")

    for month in months:
        month_history_records = year_history_records.filter(Date__month=month)
        month_income = 0
        month_expense = 0
        for hr in month_history_records:
            hr_type = hr.type
            hr_category = hr.Category
            record_category_label = Catalog(hr_category).label
            if hr_type == 1:
                month_expense += hr.Amount
                year_total_expense += hr.Amount
                if record_category_label not in year_category_expense:
                    category_names.add(record_category_label)
                    year_category_expense[record_category_label] = {"value": hr.Amount, "name": record_category_label}
                else:
                    year_category_expense[hr_category.name]["value"] += hr.Amount
            elif hr_type == 0:
                month_income += hr.Amount
                year_total_income += hr.Amount
                if record_category_label not in year_category_income:
                    category_names.add(record_category_label)
                    year_category_income[record_category_label] = {"value": hr.Amount, "name": record_category_label}
                else:
                    year_category_income[record_category_label]["value"] += hr.Amount
        months_income.append(month_income)
        months_expense.append(month_expense)
    return JsonResponse({"months": months,
                         "months_income": months_income,
                         "months_expense": months_expense,
                         "year_total_income": year_total_income,
                         "year_total_expense": year_total_expense,
                         "year_category_names": list(category_names),
                         "year_category_income": list(year_category_income.values()),
                         "year_category_expense": list(year_category_expense.values())})



def retrieve_year_has_data(request):
    username = request.session.get('username')
    hr = Record.objects.filter(username=username).order_by("Date")
    hr_first = hr.first()
    hr_last = hr.last()
    year_list = [y for y in range(hr_last.Date.year, hr_first.Date.year - 1, -1)]
    return JsonResponse({"years": year_list})


def retrieve_month_has_data(request):
    username = request.session.get('username')
    year = request.POST.get('year')
    hr = Record.objects.filter(Date__year=year, username=username).order_by("Date")
    hr_first = hr.first()
    hr_last = hr.last()
    month_list = [m for m in range(hr_last.Date.month, hr_first.Date.month - 1, -1)]
    return JsonResponse({"months": month_list})

def search(request):
    username = request.session.get('username')
    print("search session username: ", username)
    if request.method == 'POST':
        username = request.session.get('username')
        date = request.POST.get('date')
        records = models.Record.objects.filter(username=username, Date=date).order_by("Date")
        total_in = models.Record.objects.filter(username=username, type=models.Record_Type.In, Date=date).aggregate(Sum('Amount'))
        total_out = models.Record.objects.filter(username=username, type=models.Record_Type.Out,Date=date).aggregate(Sum('Amount'))
        total_in_amount = round(total_in['Amount__sum'] or 0, 2)
        total_out_amount = round(total_out['Amount__sum'] or 0, 2)
        total = round((total_in_amount - total_out_amount), 2)
        context = {
            "records": records,
            "total_in": total_in_amount,
            "total_out": total_out_amount,
            "total": total,
            "username": username,
        }
        # 指定渲染模板并传递数据
        return render(request, "system/search.html", context)
    else:
        return render(request, 'system/search.html', {'username': username,})

def chatbox(request):
    content = {}
    username = request.session.get('username')
    content['username'] = username
    print("chatbox username: ", username)
    if request.method == "POST":
        user_query = request.POST.get("query", '')
        query_keywords = user_query.lower().split()
        date_str = request.POST.get("date", '')
        query_conditions = Q()
        if date_str:
            try:
            # Try converting date string to date object
                date_input = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                query_conditions = Q(Date=date_input)
            except ValueError:
                if len(date_str) == 4 and date_str.isdigit():
                    year = int(date_str)
                    query_conditions = Q(Date__year=year)
                elif len(date_str) == 7 and "-" in date_str and date_str[:4].isdigit() and date_str[
                                                                                                 5:].isdigit():
                    year, month = map(int, date_str.split('-'))
                    query_conditions = Q(Date__year=year, Date__month=month)
                else:
                    messages.error(request, 'Invalid date input. Please enter a valid date (YYYY-MM-DD), year (YYYY), or month (YYYY-MM).')
                    content['error'] = "Invalid date input. Please enter a valid date (YYYY-MM-DD), year (YYYY), or month (YYYY-MM)."
                    
                    return render(request, 'system/chatbox.html', content)
        if 'most' in query_keywords and not date_str:
            if 'outcome' in query_keywords:
                most_expensive_record = Record.objects.filter(username=username, type=1).order_by("-Amount").first()
                content['record'] = most_expensive_record
            if 'income' in query_keywords:
                most_income_record = Record.objects.filter(username=username, type=0).order_by("-Amount").first()
                content['record'] = most_income_record
        elif 'least' in query_keywords and not date_str:
            if 'outcome' in query_keywords:
                least_outcome_record = Record.objects.filter(username=username, type=1).order_by("Amount").first()
                content['record'] = least_outcome_record
            if 'income' in query_keywords and not date_str:
                least_income_record = Record.objects.filter(username=username, type=0).order_by("Amount").first()
                content['record'] = least_income_record
        elif 'income' in query_keywords and not date_str:
            In = Record.objects.filter(username=username, type=0)
            content['records'] = In
        elif 'outcome' in query_keywords and not date_str:
            Out = Record.objects.filter(username=username, type=1)
            content['records'] = Out
        if date_str and user_query:
            if 'most' in query_keywords:
                if 'outcome' in query_keywords:
                    most_expensive_record = Record.objects.filter(query_conditions, username=username, type=1).order_by("-Amount").first()
                    content['record'] = most_expensive_record
                if 'income' in query_keywords:
                    most_income_record = Record.objects.filter(query_conditions, username=username, type=0).order_by("-Amount").first()
                    content['record'] = most_income_record
            elif 'least' in query_keywords:
                if 'outcome' in query_keywords:
                    least_outcome_record = Record.objects.filter(query_conditions, username=username, type=1).order_by("Amount").first()
                    content['record'] = least_outcome_record
                if 'income' in query_keywords:
                    least_income_record = Record.objects.filter(query_conditions, username=username, type=0).order_by("Amount").first()
                    content['record'] = least_income_record
            elif 'income' in query_keywords:
                In = Record.objects.filter(query_conditions, username=username, type=0)
                content['records'] = In
            elif 'outcome' in query_keywords:
                Out = Record.objects.filter(query_conditions, username=username, type=1)
                content['records'] = Out
        if not user_query and date_str:
            records = Record.objects.filter(query_conditions)
            if records.exists():
                content['records'] = records
            else:
                messages.error(request,'No records found for the given input.')
                content['error'] = "No records found for the given input."
    return render(request, 'system/chatbox.html', content)


