from typing import Dict
from requests_oauthlib import OAuth2Session
import json, os

from rest_condition import C

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

  #debug
  music = graph_client.get('{0}/me/drive/items/9523333609373617!78780/children'.format(graph_url))

  return music.json()

def get_dirs(token, dir):
  graph_client = OAuth2Session(token=token)

  dirPath = '{0}/me/drive/items/'+dir+'/children'

  music = graph_client.get(dirPath.format(graph_url))
  # print(music.json())

  # while music.json()['value']['folder']:
  #   music = graph_client.get(dirPath.format(graph_url))

  return music.json()

def parse_dirs(dir):
  allDirs = dict()
  index = 0
  
  for file in dir:
    temp = dict()
    #if the file is actually a folder...
    if "folder" in file:
      #get the contents
      temp['childCount'] = file['folder']['childCount']
      temp['folderName'] = file['name']
      temp['id'] = file['id']
    #it IS a file
    elif "file" in file:
      #copy the URL and metadata if it's an audio file
      if (file['file']['mimeType'].find('audio') != -1):
        temp['metadata'] = file['audio']
        temp['url'] = file['@microsoft.graph.downloadUrl']
      else: #otherwise skip it
        continue

    allDirs[index] = temp
    index+=1

  return allDirs.copy()

#TODO: fix this function to ignore non-audio files
def traverseSubdirs(token, dir, depth = 0, deleteBuf = {}):
  toDelete = []
  for key, dirs in dir.items():
    if 'childCount' in dirs and dirs['childCount'] != 0:
      dirs['subdirectories'] = parse_dirs(get_dirs(token, dirs['id'])['value'])
      if dirs['subdirectories'] == {}:
        print("This should be dropped")
        toDelete.append(key)
      traverseSubdirs(token, dirs['subdirectories'], depth + 1)
    
  if len(toDelete) != 0:
    deleteBuf[depth] = toDelete
  if depth+1 in deleteBuf.keys():
    for i in deleteBuf[depth+1]:
      del(dirs['subdirectories'][i])
      dirs['childCount'] -= 1

def listMusic(parsedDirs, finalList, counter = 0):
  for index in parsedDirs.values():
    if 'folderName' in index:
      print(index['folderName'])
      label = index['folderName']
    # elif 'metadata' in index:
    #   print(index['metadata']['title'])
    else:
      label = counter
    # keep go deeper until end of subdirectory reached
    if 'subdirectories' in index:
      if index.get('subdirectories') != {}:
        finalList[counter] = {}
        finalList[counter].update(listMusic(index['subdirectories'], finalList, counter))
        # print(finalList)
        counter+=1
      else:
        continue
    else:
      return parsedDirs


  return finalList