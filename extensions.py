#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from const import namespaces


def icon(t):
    e = t.find("extensions", namespaces)
    return (e if e else t).find("kashmir3d:icon", namespaces).text


def line_color(t):
    e = t.find("extensions", namespaces)
    return e.find("kashmir3d:line_color", namespaces).text


def line_size(t):
    e = t.find("extensions", namespaces)
    return e.find("kashmir3d:line_size", namespaces).text


def line_style(t):
    e = t.find("extensions", namespaces)
    return e.find("kashmir3d:line_style", namespaces).text


# __END__
