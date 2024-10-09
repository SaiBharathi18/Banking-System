from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction
from .forms import RegistrationForm, LoginForm, TransactionForm

def home(request):
    if request.user.is_authenticated:
        account = get_object_or_404(Account, user=request.user)
        transactions = Transaction.objects.filter(account=account).order_by('-date')
        return render(request, 'accounts/home.html', {
            'account': account,
            'transactions': transactions
        })
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user)
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            account = get_object_or_404(Account, user=request.user)
            transaction_type = form.cleaned_data['transaction_type']
            amount = form.cleaned_data['amount']

            if transaction_type == 'deposit':
                account.balance += amount
            elif transaction_type == 'withdrawal':
                if amount > account.balance:
                    # Handle insufficient funds case
                    return render(request, 'accounts/transaction.html', {
                        'form': form,
                        'error': 'Insufficient funds'
                    })
                account.balance -= amount

            account.save()
            Transaction.objects.create(
                account=account,
                transaction_type=transaction_type,
                amount=amount
            )
            return redirect('home')
    else:
        form = TransactionForm()
    return render(request, 'accounts/transaction.html', {'form': form})
