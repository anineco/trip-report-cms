#!/bin/bash

for arg in $@; do
  ./html_formatter.py $arg | diff -q $arg -
done
