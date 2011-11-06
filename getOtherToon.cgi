#!/usr/bin/ruby
require 'rubygems'
require 'mechanize'
require 'cgi'

puts "Content-Type: text/html; charset=utf-8\n\n"

put = CGI.new
artistId = put.params["artistId"][0]
page = 1

btnColor = {
  "buttonA" => "#FAFAFA",
  "buttonB" => "#EAEAEA",
  "saved" => "#88DD88",
  "saved_up" => "#DD8888",
  "saved_finish" => "#888888",
  "link" => "#0066CC"}

a = Mechanize.new

begin
  resp = a.get "http://comic.naver.com/artistTitle.nhn?artistId=#{artistId}&page=#{page}"

  resp.search('//ul[@class="authorList"]/li').each {|r|
    titleId = $1 if r.search('h4[@class="title"]/a')[0].attributes["href"].to_s =~ /\/webtoon\/detail\.nhn\?titleId=(\d+)/
      title = r.search('h4[@class="title"]/a')[0].inner_html
    puts "<div id=\"#{titleId}\" style=\"background-color: #{btnColor["buttonB"]}; cursor: default; margin: 3px 0px 3px 0px;\" onclick=\"viewToon('#{titleId}');\">#{title}</div>"
  }
  page += 1
end while (resp.search('//div[@class="pagenavigation"]/a[@class="next"]').length > 0)
