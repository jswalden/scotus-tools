# Copyright (c) 2018-2019  Floyd Terbo

from __future__ import absolute_import

import logging

import dateutil.parser

from . import decorators as SD
from .courts import NAMEMAP as LCNAMEMAP
from .attorneys import Attorney, ATTYMAP

FILTERTYPES = {}

def srcfilter (typ):
  def decorator(k):
    FILTERTYPES[typ] = k
    return k
  return decorator

@srcfilter("case-status")
@SD.inputs("docket-reference")
class CaseStatus(object):
  def __init__ (self, pending = None, dismissed = None, granted = None, argued = None, denied = None,
                judgment_issued = None, gvr = None):
    self.pending = pending
    self.dismissed = dismissed
    self.granted = granted
    self.argued = argued
    self.denied = denied
    self.judgment_issued = judgment_issued
    self.gvr = gvr

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    di = docket_ref.info

    if self.pending is not None:
      if self.pending != di.pending:
        return False

    if self.dismissed is not None:
      if self.dismissed != di.dismissed:
        return False

    if self.granted is not None:
      if self.granted != di.granted:
        return False

    if self.argued is not None:
      if self.argued != di.argued:
        return False

    if self.denied is not None:
      if self.denied != di.denied:
        return False

    if self.judgment_issued is not None:
      if self.judgment_issued != di.judgment_issued:
        return False

    if self.gvr is not None:
      if self.gvr != di.gvr:
        return False

    return True

@srcfilter("distribution")
@SD.inputs("docket-reference")
class Distribution(object):
  def __init__ (self, min_count = 1, conf_date = None, rescheduled = None):
    self.conf_date = None
    self.count = min_count
    self.rescheduled = rescheduled

    if conf_date:
      self.conf_date = dateutil.parser.parse(conf_date).date()
      logging.debug("conference date parsed as: %s" % (self.conf_date))

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    if self.count:
      if len(docket_ref.info.distributed) < self.count:
        return False

    if self.conf_date:
      for (edate, cdate, was_rescheduled) in docket_ref.info.distributed:
        if self.conf_date == cdate:
          if self.rescheduled is not None and was_rescheduled != self.rescheduled:
            return False
          return True
      return False
    elif self.rescheduled is not None:
      if not self.rescheduled:
        # Return True only if we've never been rescheduled
        for (edate, cdate, was_rescheduled) in docket_ref.info.distributed:
          if was_rescheduled:
            return False
        return True
      else:
        # Return True if we've been rescheduled min_count times
        rcount = 0
        for (edate, cdate, was_rescheduled) in docket_ref.info.distributed:
          if was_rescheduled:
            rcount += 1
        if rcount >= self.count:
          return True
        return False

    return True



@srcfilter("case-type")
@SD.inputs("docket-reference")
class CaseType(object):
  def __init__ (self, type):
    self.case_type = type

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    return docket_ref.info.casetype == self.case_type


@srcfilter("capital")
@SD.inputs("docket-reference")
class CapitalFilter(object):
  def __init__ (self, is_capital = True):
    self.is_capital = is_capital

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    return docket_ref.info.capital == self.is_capital


@srcfilter("cvsg")
@SD.inputs("docket-reference")
class CVSGFilter(object):
  def __init__ (self, has_cvsg = True):
    self.has_cvsg = has_cvsg

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    return docket_ref.info.cvsg == self.has_cvsg



@srcfilter("lowercourt")
@SD.inputs("docket-reference")
class LowerCourtFilter(object):
  def __init__ (self, court_abbrevs):
    self.cabbrs = court_abbrevs

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    if not docket_ref.info.lowercourt:
      return False

    for abbr in self.cabbrs:
      if LCNAMEMAP[abbr] == docket_ref.info.lowercourt:
        return True


@srcfilter("docketdate")
@SD.inputs("docket-reference")
class DocketDate(object):
  def __init__ (self, datestr):
    self.ddate = dateutil.parser.parse(datestr).date()

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    if self.ddate == docket_ref.info.docket_date:
      return True


ATTY_ROLES = {
  "gov" : "isGov",
  "sg" : "isSG",
  "ag" : "isAG",
  "pd" : "isPD",
  "priv" : "isPrivate",
}

@srcfilter("attorney")
@SD.inputs("docket-reference")
class PartyAttorney(object):
  def __init__ (self, atty_name, role = None, petitioner = None, respondent = None, require_cor = False):
    self.atty_name = atty_name
    self.role = None
    self.petitioner = petitioner
    self.respondent = respondent
    self.require_cor = require_cor
    if role:
      self.role = getattr(Attorney, ATTY_ROLES[role])

  def __match (self, source, target):
    if source != target:
      return False
    if self.role:
      if self.role(source, docket.docket_date):
        return True
      return False
    else:
      return True

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    try:
      fobj = ATTYMAP[self.atty_name]
    except KeyError:
      fobj = Attorney(self.atty_name)

    docket = docket_ref.info

    if self.petitioner or self.petitioner is None:
      if self.require_cor:
        for atty in docket.attys_petitioner_cor:
          try:
            aobj = ATTYMAP[atty]
            if self.__match(aobj, fobj):
              return True
          except KeyError:
           continue
      else:
        for atty in docket.attys_petitioner:
          try:
            aobj = ATTYMAP[atty]
            if fobj == aobj:
              if self.role:
                if self.role(aobj, docket.docket_date):
                  return True
              else:
                return True
          except KeyError:
            continue

    if self.respondent or self.respondent is None:
      if self.require_cor:
        for atty in docket.attys_respondent_cor:
          try:
            aobj = ATTYMAP[atty]
            if self.__match(aobj, fobj):
              return True
          except KeyError:
           continue
      else:
        for atty in docket.attys_respondent:
          try:
            aobj = ATTYMAP[atty]
            if fobj == aobj:
              if self.role:
                if self.role(aobj, docket.docket_date):
                  return True
              else:
                return True
          except KeyError:
            continue

