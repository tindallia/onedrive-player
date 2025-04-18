import math
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from player.auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from player.graph_helper import *
import dateutil.parser

# Create your views here.
def isTokenExist(request):
  try:
    token = get_token(request)
    return token
  except:
    return None

def home(request):
  context = initialize_context(request)

  return render(request, 'player/home.html', context)

def initialize_context(request):
  context = {}

  # Check for any errors in the session
  error = request.session.pop('flash_error', None)

  if error != None:
    context['errors'] = []
    context['errors'].append(error)

  # Check for user in the session
  context['user'] = request.session.get('user', {'is_authenticated': False})
  return context

def callback(request):
  # Get the state saved in session
  expected_state = request.session.pop('auth_state', '')
  # Make the token request
  token = get_token_from_code(request.get_full_path(), expected_state)

  # Get the user's profile
  user = get_user(token)

  # Save token and user
  store_token(request, token)
  store_user(request, user)

  return HttpResponseRedirect(reverse('home'))

def sign_in(request):
  # Get the sign-in URL
  sign_in_url, state = get_sign_in_url()
  # Save the expected state so we can validate in the callback
  request.session['auth_state'] = state
  # Redirect to the Azure sign-in page
  return HttpResponseRedirect(sign_in_url)

def sign_out(request):
  # Clear out the user and token
  remove_user_and_token(request)

  return HttpResponseRedirect(reverse('home'))

def calendar(request):
  context = initialize_context(request)

  token = get_token(request)

  events = get_calendar_events(token)

  if events:
    # Convert the ISO 8601 date times to a datetime object
    # This allows the Django template to format the value nicely
    for event in events['value']:
      event['start']['dateTime'] = dateutil.parser.parse(event['start']['dateTime'])
      event['end']['dateTime'] = dateutil.parser.parse(event['end']['dateTime'])

    context['events'] = events['value']

  return render(request, 'player/calendar.html', context)

def convertTime(data):
  for item in data.values():
    realDuration = math.floor(int(item['metadata']['duration'])/1000)
    seconds = realDuration % 60
    minutes = int(realDuration / 60)
    if minutes > 60:
      hours = int(minutes / 60)
      minutes %= 60
      item['metadata']['duration'] = str(hours) + ":" + str(minutes) + ":" + str(seconds).zfill(2)
    
    item['metadata']['duration'] = str(minutes) + ":" + str(seconds).zfill(2)

def music(request):
  context = initialize_context(request)

  token = isTokenExist(request)
  if token == None:
    remove_user_and_token(request)
    return HttpResponseRedirect(reverse('home'))

  directories = get_music(token)

  if directories:
    directories = parse_dirs(directories['value'])
  
  # print("Traversing subdirs")
  # print(directories)
  traverseSubdirs(token, directories)
  # print(directories)

  # finalList = dict()
  # while 'metadata' not in finalList.values():
  directories = listMusic(directories, directories)

  for key, value in directories.items():
    convertTime(value)

  context['dirs'] = directories
  test = list()
  for dir in context['dirs'].values():
    print(dir)

  # allDirs = temp


  # for index in allDirs.values()['subdirectories']:
  #   print(index)
  
  # return JsonResponse((finalList), safe=False)

  # raise Exception("Context")

  return render(request, 'player/music.html', context)
  # return HttpResponse(context['tags'],content_type="application/json")