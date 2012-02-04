#!/bin/bash
ps x | grep "ruby -Ilib bin/webserver.rb" | grep -v "grep" | grep -o -E "^\ *[0-9]+" | grep -o -E "[0-9]+" | xargs kill -9 2>/dev/null; rm sess/* 2>/dev/null
