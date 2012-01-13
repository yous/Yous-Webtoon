#!/bin/bash
cd $(dirname $0)/..; /usr/local/rvm/bin/ruby-1.9.3-p0@webtoon -Ilib bin/webserver.rb &>> Log &
