from requests_oauthlib import OAuth2Session
import json, os

graph_url = 'https://graph.microsoft.com/v1.0'

def get_user(token):
  graph_client = OAuth2Session(token=token)
  # Send GET to /me
  user = graph_client.get('{0}/me'.format(graph_url))
  # Return the JSON result
  return user.json()

def get_calendar_events(token):
  graph_client = OAuth2Session(token=token)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'subject,organizer,start,end',
    '$orderby': 'createdDateTime DESC'
  }

  # Send GET to /me/events
  events = graph_client.get('{0}/me/events'.format(graph_url), params=query_params)
  # Return the JSON result
  return events.json()

def get_music(token):
  graph_client = OAuth2Session(token=token)

  music = graph_client.get('{0}/me/drive/items/9523333609373617!74178/children'.format(graph_url))

  return music.json()

def get_dirs(token, dir):
  graph_client = OAuth2Session(token=token)

  dirPath = '{0}/me/drive/items/'+dir+'/children'

  music = graph_client.get(dirPath.format(graph_url))
  temp = music.json()
  while music.json()['value']['folder']:
    music = graph_client.get(dirPath.format(graph_url))

  return music.json()

# def parseFile(token, itemId):
#   graph_client = OAuth2Session(token=token)

#   reqPath = '{0}/me/drive/items/'+ itemId + '/'

#   music = graph_client.get(reqPath.format(graph_url))
  
#   return music.json()

def appendToList(newData, filename="tempJson.json"):
  with open(filename,'w') as f:
    file_data=json.load(f)
    file_data.update(newData)
    f.seek(0)
    json.dump(filename,f,indent=4)
  
  return filename