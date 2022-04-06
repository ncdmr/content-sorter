#!/usr/bin/env python3

import os
import re
import shutil
import sys
from pprint import pprint

location = ''

def fill_environment():
  import json
  configfile = os.path.abspath(sys.path[0]) + '/config.json'
  with open(configfile) as f:
    return json.load(f)

def check_mount():
  if not os.path.exists(env['incoming_location']):
    print('%s not found.  Please check.  ' % env['incoming_location'])
    sys.exit()

# def reportmove(result):
#   body = ''
#   for r in result:
#     body = body + r + '\n'
#   # Import smtplib for the actual sending function
#   import smtplib

#   # Import the email modules we'll need
#   from email.mime.text import MIMEText

#   # Create a text/plain message
#   msg = MIMEText(body)

#   # me == the sender's email address
#   # you == the recipient's email address
#   msg['Subject'] = env['mail_subject']
#   msg['From'] = env['mail_from']
#   msg['To'] = env['mail_to']

#   # Send the message via our own SMTP server, but don't include the
#   # envelope header.
#   s = smtplib.SMTP(env['mail_smtp'])
#   s.sendmail(msg['From'], msg['To'], msg.as_string())
#   s.quit()

def fetchfiles():
  if os.path.ismount(env["media_location"]) and os.path.isdir(env["media_location"]):
    l_candidates = os.listdir(env["incoming_location"])
    l_dirs = os.listdir(env["media_location"])
  else:
    print('Aborted.  Downloads folder not mounted.')
    sys.exit()
  if not 'Series' in l_dirs:
    print('Something is wrong with %s: no Series folder found.'% location)
    sys.exit()
  else:
    return l_candidates

def fetchsubs():
  from datetime import timedelta

  from babelfish import Language
  from subliminal import download_best_subtitles, region, save_subtitles, scan_videos

  # configure the cache
  try:
    region.configure('dogpile.cache.dbm', arguments={'filename': '/tmp/cachefile.dbm'})
  except IOError:
    region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})

  # scan for videos newer than 2 weeks and their existing subtitles in a folder
  videos = scan_videos(env["incoming_location"], age=timedelta(days=14))

  # download best subtitles
  subtitles = download_best_subtitles(videos, {Language('eng')})

  # save them to disk, next to the video
  for v in videos:
    print('%s - sub found.' % v)
    save_subtitles(v, subtitles[v], single=True)

def ProcessFiles(l_dirs):
  import time
  moveddirs = {}
  for l in sorted(l_dirs):
    l = l.rstrip()
    if l in env['skip_list'] or re.search(r'^\.', l):
      continue
    if re.search(r'[sS]\d{1,2}[eE]\d{1,2}', l):
      if not 'Series' in moveddirs:
        moveddirs['Series'] = []
      root = env["media_location"] + '/Series/'
      resultlist = moveddirs['Series']
      wb = {}
      params = re.match(r'(?P<show>[a-zA-Z0-9\.]*)\.[sS](?P<season>\d{1,2})[eE](?P<episode>\d{1,2})',l)
      wb = params.groupdict()
      if len(wb['season']) == 1:
        wb['season'] = '0' + wb['season']
      location = root + wb['show'] + '/Season ' + wb['season']
    else:
      if not 'Films' in moveddirs:
        moveddirs['Films'] = []
      resultlist = moveddirs['Films']
      movie = False
      l_moviedir = os.listdir(env["incoming_location"] + '/' + l)
      for m in l_moviedir:
        if re.search(r'\.(mp4|avi|mkv)', m):
          movie = True
      if movie:
        location = env["media_location"] + '/Films/'
    modifieddate = time.ctime(os.path.getmtime(env["incoming_location"] + "/" + l))
    if not os.path.exists(location):
      try:
        os.makedirs(location)
      except:
        print('SKIPPED: %s' % l)
        continue
    resultlist.append('%s // (%s)' % (l,modifieddate))
    try:
      shutil.move(env["incoming_location"] + '/' + l,location)
    except OSError as why:
      print("ERROR: move of %s failed: \n %s" % (l, why))
      continue
  # fetchsubs(location)
  return(moveddirs)

def check_ping(target):
  """ICMP check if a host is alive"""
  import os,subprocess
  FNULL = open(os.devnull, 'w')
  result = subprocess.call(["ping","-c 1",target], stdout=FNULL, stderr=subprocess.STDOUT)
  print(result)
  return result

def updateKodi():
  import requests
  if check_ping(env['kodi']) == 0:
    url = 'http://%s:8080/jsonrpc' % env["kodi"]
    data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
    try:
      r = requests.post(url, json=data)
    except ConnectionError:
      print("Something went wrong talking to kodi's API.")
  else:
    print('Kodi station is not online.')

def TeleMeStuff(msg):
  import telepot
  bot = telepot.Bot(env['telegram_token'])
  for key in msg.keys():
    tosend = ''
    if len(msg[key]) > 5:
      for i in range(int(len(msg[key])/5+1)):
        tosend = "\n".join(msg[key][i*5:(i+1)*5]) + "\n"
        if len(tosend) > 0 and not tosend == '\n':
          bot.sendMessage(env['telegram_chat_id'], tosend)
    else:
      for i in msg[key]:
        tosend = tosend + i + "\n"
      if len(tosend) > 0 and not tosend == '\n':
        bot.sendMessage(env['telegram_chat_id'], tosend)

if __name__ == '__main__':
  env = fill_environment()
  check_mount()
  #fetchsubs()
  result = ProcessFiles(fetchfiles())
  #updateKodi()
  TeleMeStuff(result)
