from django.shortcuts import render, redirect
from .models import Message, Room, Topic, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python',},
#     {'id': 2, 'name': 'Design with me',},
#     {'id': 3, 'name': 'Front end developers',},
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            # Exception thrown if username doesn't exist
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password doesn't exist")

    context = {'page': page}
    return render(request, "base/login-register.html", context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # We don't want to lose out on user object after save, thus calling commit=False returns the user object as well
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")
    return render(request, 'base/login-register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # rooms = Room.objects.filter(topic__name__contains=q) search is case sensitive
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        ) # search is case insensitive
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    roomMessages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'room_count':room_count, 'roomMessages': roomMessages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    # The message here represents the message model. We don't write the model name in caps or the way its defined in the models file.
    # The line below basically means, return all the messages associated with this room
    roomMessages = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        # If the user is already present in the participants list, then it doesn't add the same user
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'roomMessages': roomMessages,
        'participants': participants
    }
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    roomMessages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'roomMessages': roomMessages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        # Get or create functionality
        # If in the topics we already have Python registered, and if the user enters the name of Topic as "Python"
        # Then, it will first see if it already has a topic named Python, if yes, then created = False, and a brand new Python topic object will be returned. Note, a new topic isn't added in the database.
        # If, the user enters Java, and if we currently don't have Java registered in the topics list in the database
        # Then, created = True, and a Java topic object is returned, and a new topic is added to the database
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create (
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, "base/room-form.html", context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == "POST":
        # Here, we specify the instance as well because we want to tell of which room the values needs to be updated
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room-form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, "base/delete.html", {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, "base/delete.html", {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    form = UserForm(instance=request.user)
    context = {
        'form': form
    }
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance = request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=request.user.id)
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})