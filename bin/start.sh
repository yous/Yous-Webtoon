#!/bin/bash
cd $(dirname $0)/..;
/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby -Ilib bin/webserver.rb &>> Log &
