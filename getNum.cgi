#!/usr/bin/ruby
require 'rubygems'
require 'mechanize'
require 'cgi'

puts "Content-Type: text/html; charset=utf-8\n\n"

put = CGI.new
site = put.params["site"][0]
id = put.params["id"][0]

a = Mechanize.new

# Naver 웹툰
if site == "naver" then
  resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}"

  resp.search('//div[@class="btn_area"]').each {|v|
    v.search('span[@class="pre"]/a').each {|e|
      if e.attributes["href"].value =~ /\/webtoon\/detail\.nhn\?titleId=\d+&seq=(\d+)/ then
        puts $1.to_i + 1
        exit
      end
    }
    puts 1
  }
# Daum 웹툰
elsif site == "daum" then
  str = []
  resp = a.get "http://cartoon.media.daum.net/webtoon/view/#{id}"

  num_resp = a.get "http://cartoon.media.daum.net/webtoon/viewer/#{$1 if resp.search('//div[@class="webtoon"]/script').inner_html =~ /url:"\/webtoon\/viewer\/(\d+)"/}"

  num_resp.search('//div[@class="episode_list"]/div/div[@class="scroll_wrap"]/ul/li').each {|r|
    str.push($1) if r.search('a')[0].attributes["href"].value =~ /\/webtoon\/viewer\/(\d+)/
  }
  puts str.join(" ")
end
