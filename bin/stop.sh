#!/bin/bash
ps -C "ruby -Ilib bin/webserver.rb" -o pid= | xargs kill -9
