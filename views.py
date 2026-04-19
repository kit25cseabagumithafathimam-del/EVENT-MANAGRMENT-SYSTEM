from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Registration
from .forms import CustomUserCreationForm, EventForm
from django.db import IntegrityError

def home(request):
    events = Event.objects.all().order_by('date', 'time')
    return render(request, 'events/home.html', {'events': events})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'events/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'events/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

@login_required
def dashboard(request):
    user = request.user
    if user.role in ['admin', 'organizer']:
        created_events = Event.objects.filter(created_by=user)
        return render(request, 'events/dashboard_org.html', {'events': created_events})
    else:
        registrations = Registration.objects.filter(user=user, status='active')
        return render(request, 'events/dashboard_student.html', {'registrations': registrations})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(user=request.user, event=event, status='active').exists()
    
    return render(request, 'events/event_detail.html', {
        'event': event, 
        'is_registered': is_registered
    })

@login_required
def register_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        if event.is_full:
            messages.error(request, 'This event is already full.')
            return redirect('event_detail', event_id=event.id)
            
        try:
            Registration.objects.create(user=request.user, event=event)
            messages.success(request, f'Successfully registered for {event.title}!')
        except IntegrityError:
            messages.warning(request, 'You are already registered for this event.')
            
    return redirect('event_detail', event_id=event_id)

@login_required
def create_event(request):
    if request.user.role not in ['admin', 'organizer']:
        messages.error(request, 'You do not have permission to create events.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('dashboard')
    else:
        form = EventForm()
        
    return render(request, 'events/create_event.html', {'form': form})
