#!/bin/bash

for arg in $@; do
  ./formatter.py $arg | diff -q $arg -
done
