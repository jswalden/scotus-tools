# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

from datetime import date

from .util import MultiMatch

# Don't use this for things, a pattern example right now, unclear later
class POSITIONS(object):
  SGUS = "sg.us"
  SSG = "sg.state"
  PRACTICE = "practice"
  CLINIC = "practice.clinic"
  FIRM = "practice.firm"

ATTYMAP = {}

class Attorney(object):
  def __init__ (self, *names):
    self.names = names
    self.positions = []

    for name in self.names:
      ATTYMAP[unicode(name)] = self

  @property
  def name (self):
    return self.names[0]

  def __str__ (self):
    return self.names[0]

  def setSG (self, entity, start, end = None):
    self.positions.append(("sg.%s" % (entity), start, end))
    return self

  def setAG (self, entity, start, end = None):
    self.positions.append(("ag.%s" % (entity), start, end))
    return self

  def setFirm (self, entity, start, end = None):
    self.positions.append(("practice.firm.%s" % (entity), start, end))
    return self

  def setFPD (self, entity, start, end = None):
    self.positions.append(("fpd.%s" % (entity), start, end))
    return self

  def setSPD (self, entity, start, end = None):
    self.positions.append(("spd.%s" % (entity), start, end))
    return self

  def isSG (self, qdate):
    for (position, start, end) in self.positions:
      if end is None and qdate > start:
        if position.startswith("sg."):
          return True
      elif qdate > start and qdate <= end:
        if position.startswith("sg."):
          return True
    return False

  def isAG (self, qdate):
    for (position, start, end) in self.positions:
      if end is None and qdate > start:
        if position.startswith("ag."):
          return True
      elif qdate > start and qdate <= end:
        if position.startswith("ag."):
          return True
    return False

  def isGov (self, qdate):
    if self.isSG(qdate) or self.isAG(qdate):
      return True
    return False

  def isPrivate (self, qdate):
    # Gov't practice is much easier to track than moves in private firms, so we just assume they were in
    # private practice for dates not covered by known government service.  Of course if you supply some
    # random date instead of one retrieved from a filing, we'll be happy to report private practive even
    # if they weren't alive.
    return not self.isGov(qdate)


# Many of these are conservative date ranges based on filings, they are definitely NOT complete or accurate 

_attys = [
  Attorney("Jerry V. Beard")
    .setFPD("tx.nd", date(2017, 2, 1), None),
  Attorney("Paul D. Clement")
    .setFirm("kirkland-ellis", date(2016, 9, 12), None)
    .setFirm("bancroft", date(2011, 3, 25), date(2016, 9, 12))
    .setFirm("king-spalding", date(2008, 11, 20), date(2011, 3, 25))
    .setSG("us.deputy", date(2001, 2, 1), date(2004, 7, 11))
    .setSG("us.acting", date(2004, 7, 11), date(2005, 6, 13))
    .setSG("us", date(2005, 6, 13), date(2008, 6, 19)),
  Attorney("Trevor Stephen Cox")
    .setAG("va.unknown", date(2017, 2, 21), None),
  Attorney("Stephen R. Creason", "Stephen Richard Creason")
    .setAG("in.unknown", date(2006, 12, 13), None),
  Attorney("Tracy Dreispul", "Tracy M. Dreispul")
    .setFPD("sdfl", date(2006, 11, 20), None),
  Attorney("Noel J. Francisco", "Noel Francisco")
    .setSG("us.acting", date(2017, 1, 23), date(2017, 3, 10))
    .setSG("us", date(2017, 9, 19), None),
  Attorney("Michael Marc Glick")
    .setAG("illinois.ccad", date(2006, 7, 1), None),
  Attorney("Raed Gonzalez")
    .setFirm("gonzalez-olivieri", date(2015, 11, 20), None),
  Attorney("Paul Edward Kalil")
    .setSPD("fl.ccrc", date(2009, 5, 1), None),
  Attorney("John M. Klawikofsky")
    .setAG("fl.unknown", date(2005, 3, 14), None),
  Attorney("Aaron David Lindstrom", "Aaron D. Lindstrom Jr.")
    .setSG("mi", date(2013, 12, 1), None)
    .setSG("mi.assistant", date(2012, 10, 1), date(2013, 11, 30))
    .setFirm("warner-norcross-judd", date(2009, 5, 1), date(2012, 9, 30))
    .setFirm("gibson-dunn-crutcher", date(2005, 10, 1), date(2009, 4, 30)),
  Attorney("Matthew Robert McGuire")
    .setAG("va.unknown", date(2017, 2, 21), None),
  Attorney("Eric E. Murphy")
    .setSG("oh", date(2013, 9, 9), None),
  Attorney("Billy H. Nolas")
    .setFPD("fl.chu", date(2017, 6, 1), None),
  Attorney("Kevin Joel Page")
    .setFPD("tx", date(2016, 5, 1), None),
  Attorney("Kannon K. Shanmugam")
    .setSG("us.assistant", date(2003, 6, 23), date(2008, 3, 24))
    .setFirm("williams-connolly", date(2008, 5, 2), None),
  Attorney("Carolyn M. Snurkowski")
    .setAG("fl", date(2016, 8, 1), None),
  Attorney("Jeffrey B. Wall")
    .setSG("us.acting", date(2017, 3, 10), date(2017, 9, 19))
    .setSG("us.deputy", date(2017, 9, 20), None),
]

