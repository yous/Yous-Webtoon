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
if site == "naver"
  resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}"

  resp.search('//div[@class="btn_area"]').each {|v|
    v.search('span[@class="pre"]/a').each {|e|
      if e.attributes["href"].value =~ /\/webtoon\/detail\.nhn\?titleId=\d+&seq=(\d+)/
        puts $1.to_i + 1
        exit
      end
    }
    puts 1
  }
# Daum 웹툰
elsif site == "daum"
  str = ""
  str_writer = []
  resp = a.get "http://cartoon.media.daum.net/webtoon/view/#{id}"

  resp.search('//div[@id="daumContent"]/div').each {|r|
    r.search('div[@id="mCenter"]/div[@class="area_toon_info"]/div[@class="wrap_cont"]/dl[1]/dd/a').each {|v|
      str_writer.push(v.inner_html.strip)
    }
    r.search('div[@id="mCenter"]/script')[0].inner_html.strip.split(";").map(&:strip).
      find_all {|v| v =~ /data1\.push\([\w\W]*\)/}.
      map {|v|
        {"num" => $1, "date" => $2} if v =~ /data1\.push\(\s*\{\s*img\s*:\s*"[\w\W]*"\s*,\s*title\s*:\s*"[\w\W]*"\s*,\s*shortTitle\s*:\s*"[\w\W]*"\s*,\s*url\s*:\s*"\/webtoon\/viewer\/(\d+)"\s*,\s*date\s*:\s*"([\w\W]*)"\s*,\s*price\s*:\s*"[\w\W]*"\s*,\s*finishYn\s*:\s*"[\w\W]*"\s*,\s*payYn\s*:\s*"[\w\W]*"\s*\}\s*\)/
      }.
      reverse.
      each {|v|
        str << "#{v["num"]},#{v["date"]} "
      }
  }

  puts str[0...-1] + "\n" + str_writer.join(" / ")
end
