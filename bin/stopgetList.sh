#!/bin/bash
ps x | grep "ruby -Ilib bin/getList.rb" | grep -v "grep" | grep -o -E "^\ *[0-9]+" | grep -o -E "[0-9]+" | xargs kill -QUIT 2>/dev/null && echo "getList stopped.";
