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
  str = ""
  resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}"

  resp.search('//div[@id="header"]/div[@id="submenu"]/ul[@class="submenu"]/li').each do |v|
    v.search('a[@class="current"]').each do |e|
      str << case e.attributes["href"].value
      when "/webtoon/weekday.nhn" then "n "
      when "/webtoon/finish.nhn" then "y "
      else "x "
      end
    end
  end
  resp.search('//div[@class="btn_area"]').each do |v|
    v.search('span[@class="pre"]/a').each do |e|
      if e.attributes["href"].value =~ /\/webtoon\/detail\.nhn\?titleId=\d+&seq=(\d+)/
        puts str << "#{$1.to_i + 1}"
        exit
      end
    end
    puts str << "1"
  end

# Daum 웹툰
elsif site == "daum"
  str = ""
  str_writer = []
  str_toonInfo = ""
  str_finish = ""
  resp = a.get "http://cartoon.media.daum.net/webtoon/view/#{id}"

  resp.search('//div[@id="daumContent"]/div[@id="cMain"]').each do |r|
    r.search('div[@id="mCenter"]/div[@class="area_toon_info"]').each do |v|
      str_writer.push(v.at('div[@class="wrap_cont"]/dl[1]/dd/a').inner_html.strip)
      str_toonInfo = v.at('div[@class="wrap_more"]/dl[@class="list_intro"]/dd').inner_html.strip
    end
    r.at('div[@id="mCenter"]/script').inner_html.strip.split(";").map(&:strip).
      find_all {|v| v =~ /data1\.push\([\w\W]*\)/}.
      map {|v|
        if v =~ /data1\.push\(\s*\{\s*img\s*:\s*"[\w\W]*"\s*,\s*title\s*:\s*"[\w\W]*"\s*,\s*shortTitle\s*:\s*"[\w\W]*"\s*,\s*url\s*:\s*"\/webtoon\/viewer\/(\d+)"\s*,\s*date\s*:\s*"([\w\W]*)"\s*,\s*price\s*:\s*"[\w\W]*"\s*,\s*finishYn\s*:\s*"([\w\W]*)"\s*,\s*payYn\s*:\s*"[\w\W]*"\s*\}\s*\)/
          str_finish = "y " if $3 == "Y" and str_finish == ""
          {"num" => $1, "date" => $2, "finish" => $3}
        end
      }.
      reverse.
      each {|v| str << "#{v["num"]},#{v["date"]} " }
  }

  puts ((str_finish == "") ? "n " : str_finish) + str[0...-1] + "\n" + str_writer.join(" / ") + "\n" + str_toonInfo
end
