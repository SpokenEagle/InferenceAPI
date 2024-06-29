import asyncio
from datetime import datetime
import socket

from django.contrib.auth import alogin, alogout, aauthenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_protect

from .Preprocessor import Preprocessor
from .inference.summary import Summarizer
from .models import Chat_Session, Chat_Messages
from hashlib import sha256
from asgiref.sync import sync_to_async, async_to_sync

hostname = socket.gethostname()
print("Running '{}' server at: {}".format(hostname, socket.gethostbyname(hostname)))

summarizer = Summarizer()


async def home(request):
    return await arender(request, 'home.html')


@csrf_protect
async def direct_summary(request):
    try:
        processor = Preprocessor()
        content = await sync_to_async(processor.clean)(request.POST['content'])
    except MultiValueDictKeyError:
        return await arender(request, 'summary.html')
    if len(content) <= 10 or len(content) >= 20000:
        return await arender(request, 'summary.html',
                             {'userInput': content, 'summary': "Can't summarize this!"})

    text = await sync_to_async(summarizer.summarize)(content)
    return await arender(request, 'summary.html', {'userInput': content, 'summary': processor.formater(text)})


async def session_title(sessions):
    titles = []
    for session in sessions[::-1]:
        title = {'title': '',
                 'session_id': ''}
        messages = await sync_to_async(list)(Chat_Messages.objects.filter(session=session.session_id))
        if len(messages) > 0:
            title['title'] = messages[0].user[:35] + '...'
            title['session_id'] = session.session_id
            titles.append(title)
    return titles


async def change_session(request, session_id):
    await sync_to_async(request.session.__setitem__)('session_id', session_id)
    return await aredirect(chat)


@sync_to_async
@login_required(login_url='login_view')
@async_to_sync
async def chat(request):
    name = request.user.first_name
    try:
        session_id = request.session['session_id']
    except Exception:
        return await aredirect(new_chat)
    if session_id is None:
        return await aredirect(new_chat)
    data = await sync_to_async(list)(Chat_Messages.objects.filter(username=request.user, session=session_id))
    sessions = await sync_to_async(list)(Chat_Session.objects.filter(username=request.user))
    titles = await session_title(sessions)
    # print(sessions)
    processor = Preprocessor()

    async def format_message(message):
        message.model = await sync_to_async(processor.formater)(message.model)
        return message

    data = await asyncio.gather(*(format_message(i) for i in data))
    if len(data)==0:
        prompts=True
    else:prompts=False
    return await arender(request, 'chat.html', {'username': name, 'data': data, 'titles': titles, 'prompts': prompts})


@sync_to_async
@login_required(login_url='login_view')
@async_to_sync
@csrf_protect
async def user_query(request):
    username = request.user.username
    session_id = request.session['session_id']
    query = request.POST.get('query')
    if len(query) < 10:
        return await aredirect(chat)
    message_db = await sync_to_async(Chat_Messages.objects.filter)(
        username=username, session=session_id
    )
    message_db = await sync_to_async(message_db.order_by)('-timestamp')
    previous = await sync_to_async(list)(message_db[:8])
    # text = "response from the model!"
    text = await sync_to_async(summarizer.reply)(query, previous)
    conversation = Chat_Messages()
    conversation.session = session_id
    conversation.message_id = sha256((str(session_id) + str(datetime.now())).encode()).hexdigest()[:32]
    conversation.username = username
    conversation.user = query
    conversation.model = text
    await conversation.asave()
    return await aredirect(chat)


@sync_to_async
@login_required(login_url='login_view')
@async_to_sync
async def new_chat(request):
    session = Chat_Session()
    session.username = request.user.username
    session.session_id = sha256(str(session.username + str(datetime.now())).encode()).hexdigest()[:32]
    await session.asave()
    request.session['session_id'] = session.session_id
    return await aredirect(chat)


@csrf_protect
async def signup(request):
    user = User()
    try:
        user.first_name = request.POST['name']
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.set_password(request.POST['password'])
        await user.asave()
        return await arender(request, 'login.html', {'message': 'Account created!', 'user': user})
    except IntegrityError:
        return await arender(request, 'signup.html', {'error': 'User already existed!', 'user': user})
    except MultiValueDictKeyError:
        return await arender(request, 'signup.html')
    except Exception as e:
        return await arender(request, 'signup.html', {'error': e})


@csrf_protect
async def login_view(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except MultiValueDictKeyError:
        return await arender(request, 'login.html')
    except Exception as e:
        return await arender(request, 'login.html', {'error': e})
    user = await aauthenticate(request, username=username, password=password)
    if user is not None:
        await alogin(request, user)
        return await aredirect(chat)
    else:
        return await arender(request, 'login.html',
                             {'error': 'Invalid username or password!', 'details': user})


async def logout_view(request):
    await alogout(request)
    return await arender(request, 'login.html', {'message': 'You have been logged out!'})


@csrf_protect
async def index(request):
    processor = Preprocessor()
    content = processor.clean(request.POST['content'])
    print(content)
    if len(content) <= 10 or len(content) >= 20000:
        return JsonResponse({"summary": "Can't summarize this!"})
    text = summarizer.summarize(content)
    return JsonResponse({"summary": processor.formater(text)})


async def test(request):
    text = await sync_to_async(summarizer.summarize)(summarizer.text)
    return await sync_to_async(HttpResponse)(Preprocessor().formater(text))


async def arender(request, template, context=None):
    return await sync_to_async(render)(request, template, context)


async def aredirect(func):
    return await sync_to_async(redirect)(func)


async def test_html(request):
    return await arender(request, 'test.html')
