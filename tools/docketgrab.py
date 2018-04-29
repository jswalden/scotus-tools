#!/usr/bin/env python

# Copyright (c) 2018  Floyd Terbo

import argparse
import json
import logging
import os
import os.path
import sys
import time

import BeautifulSoup as BS
import requests

logging.basicConfig(level=logging.INFO)

HEADERS = {"User-Agent" : "SCOTUS Docket Grabber (https://github.com/fterbo/scotus-tools)"}
BASE = "https://www.supremecourt.gov/rss/cases/JSON/"

PETITION_LINKS = set(["Petition", "Appendix", "Jurisdictional Statement"])
PETITION_TYPES = set(["certiorari", "mandamus", "habeas", "jurisdiction"])

def GET (url):
  logging.debug("GET: %s" % (url))
  return requests.get(url, headers=HEADERS)


def parse_args ():
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--term", dest="term", type=int)
  parser.add_argument("-n", "--docket-num", dest="docket_num", type=int)
  parser.add_argument("-a", "--action", dest="action", type=str, default="scan-petition")
  parser.add_argument("--root", dest="root", type=str, default=".")
  args = parser.parse_args()
  return args


# TODO: We really should use some exceptions to better handle control flow
def scanPetitions (path, opts):
  nextnum = opts.docket_num
  while True:
    newpath = "%s/%d/" % (path, nextnum)
    docketstr = "%d-%d" % (opts.term, nextnum)

    if os.path.exists(newpath):
      # We already scanned this docket
      nextnum += 1
      continue

    url = "%s/%d-%d.json" % (BASE, opts.term, nextnum)
    r = GET(url)
    if r.status_code != 200:
      logging.info("Stopped for URL <%s> with code %d" % (url, r.status_code))
      break

    docket_obj = r.json()
    founditem = None
    for item in docket_obj["ProceedingsandOrder"]:
      try:
        for link in item["Links"]:
          if link["Description"] == "Petition":
            # TODO: This does not tend to capture original actions or mandatory appeals
            founditem = item
            break
        if founditem:
          break
      except KeyError:
        # Likely original extension of time to file
        logging.debug("[%s] No links: %s" % (docketstr, item["Text"]))
        continue

    if not founditem:
      logging.error("Couldn't find a petition for docket %s" % (docketstr))
      nextnum += 1
      continue

    match = list(set(founditem["Text"].split()) & PETITION_TYPES)
    if len(match) == 0:
      logging.warning("[%s] Unknown petition type for: %s" % (docketstr, founditem["Text"]))
    elif len(match) == 1:
      logging.info("[%s] %s" % (docketstr, match[0]))
    elif len(match) > 1:
      logging.info("[%s] Too many type matches for: %s" % (docketstr, founditem["Text"]))

    os.makedirs(newpath)
    with open("%s/docket.json" % (newpath), "w+") as f:
      f.write(json.dumps(r.json()))

    for link in founditem["Links"]:
      if link["Description"] in PETITION_LINKS:
        logging.debug("[%s] Downloading %s" % (docketstr, link["File"]))
        dl = GET(link["DocumentUrl"])
        if dl.status_code != 200:
          logging.error("[%s] FAILED: %d" % (docketstr, dl.status_code))
          continue
        outpath = "%s/%s" % (newpath, link["File"])
        with open(outpath, "w+") as f:
          f.write(dl.content)

    nextnum += 1
        


def downloadFull (path, opts):
  pass


ACTIONS = {
  "scan-petition" : scanPetitions,
  "petitions" : scanPetitions,
  "download-full" : downloadFull,
  "download" : downloadFull
}

if __name__ == '__main__':
  opts = parse_args()
  path = "%s/OT-%d/dockets" % (opts.root, opts.term)
  try:
    os.makedirs(path)
  except OSError:
    pass

  func = ACTIONS[opts.action]
  func(path, opts)
