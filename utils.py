#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime


def iso_period(s, e):  # datetime object
    """Return a string of period in ISO format."""
    start = s.strftime("%Y-%m-%d")
    if s.year != e.year:
        end = e.strftime("%Y-%m-%d")
    elif s.month != e.month:
        end = e.strftime("%m-%d")
    elif s.day != e.day:
        end = e.strftime("%d")
    else:
        return start
    return f"{start}/{end}"


def jp_period(s, e):  # datetime object
    """Return a string of period in Japanese format."""
    start = f"{s.year}年{s.month}月{s.day}日"
    if s.year != e.year:
        end = f"{e.year}年{e.month}月{e.day}日"
    elif s.month != e.month:
        end = f"{e.month}月{e.day}日"
    elif s.day != e.day:
        end = f"{e.day}日"
    else:
        return start
    return f"{start}〜{end}"


def jp_period_short(s, e):  # datetime object
    """Return a string of period in Japanese short format."""
    start = f"{s.month}月{s.day}日"
    if s.year != e.year or s.month != e.month:
        end = f"{e.month}月{e.day}日"
    elif s.day != e.day:
        end = f"{e.day}日"
    else:
        return start
    return f"{start}〜{end}"


days = ["月", "火", "水", "木", "金", "土", "日"]


def jp_datespan(s, e):  # datetime object
    """Return a string of date span in Japanese format."""
    ws = days[s.weekday()]
    we = days[e.weekday()]
    start = f"{s.year}年{s.month}月{s.day}日（{ws}）"
    if s.year != e.year:
        end = f"{e.year}年{e.month}月{e.day}日（{we}）"
    elif s.month != e.month:
        end = f"{e.month}月{e.day}日（{we}）"
    elif s.day != e.day:
        end = f"{e.day}日（{we}）"
    else:
        end = ""
    return start, end


# __END__
