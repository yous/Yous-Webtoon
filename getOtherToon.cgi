#!/usr/bin/ruby
require 'rubygems'
require 'mechanize'
require 'cgi'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = cgi.params["site"][0]
id = cgi.params["id"][0]

btnColor = {
  "buttonA" => "#FAFAFA",
  "buttonB" => "#EAEAEA",
  "saved" => "#88DD88",
  "saved_up" => "#DD8888",
  "saved_finish" => "#888888",
  "link" => "#0066CC"
}

a = Mechanize.new

if site == "naver"
  artistId = id
  page = 1
  begin
    resp = a.get "http://comic.naver.com/artistTitle.nhn?artistId=#{artistId}&page=#{page}"

    resp.search('//ul[@class="authorList"]/li').each do |r|
      titleId = $1 if r.search('h4[@class="title"]/a')[0].attributes["href"].to_s =~ /\/webtoon\/detail\.nhn\?titleId=(\d+)/
        title = r.search('h4[@class="title"]/a')[0].inner_html
      puts "<div id=\"#{titleId}\" style=\"background-color: #{btnColor["buttonB"]}; cursor: default; margin: 3px 0px 3px 0px;\" onclick=\"viewToon('#{titleId}');\">#{title}</div>"
    end
    page += 1
  end while (resp.search('//div[@class="pagenavigation"]/a[@class="next"]').length > 0)
elsif site == "daum"
  check_other = cgi.params["other"][0]
  resp = a.get "http://cartoon.media.daum.net/webtoon/view/#{id}"
  check_puts = false

  if check_other == "y"
    resp.
      search('//div[@id="daumContent"]/div/div[@id="mCenter"]/script')[0].
      inner_html.strip.split(';').map(&:strip).
      find_all {|v| v =~ /data2\.push\([\w\W]*\)/}.
      map {|v|
        {"title" => $1, "url" => $2} if v =~ /data2\.push\(\s*\{\s*img\s*:\s*".*"\s*,\s*title\s*:\s*"(.*)"\s*,\s*shortTitle\s*:\s*".*"\s*,\s*url\s*:\s*"\/webtoon\/view\/(.*)"\s*\}\s*\)/
      }.
      each do |v|
        puts "<div id=\"#{v["url"]}\" style=\"background-color: #{btnColor["buttonB"]}; cursor: default; margin: 3px 0px 3px 0px;\" onclick=\"viewToon('#{v["url"]}');\">#{v["title"]}</div>"
        check_puts = true if not check_puts
      end
    if not check_puts
      puts "<span>관련 웹툰이 없습니다.</span>"
    end
  else
    resp.
      search('//div[@id="daumContent"]/div/div[@id="mCenter"]/script')[0].
      inner_html.strip.split(';').map(&:strip).
      find_all {|v| v =~ /data3\.push\([\w\W]*\)/}.
      map {|v| $1 if v =~ /data3\.push\(\s*\{\s*img\s*:\s*"http:\/\/(.*)"\s*,\s*no\s*:\s*".*"\s*\}\s*\)/}.
      each {|v|
        if not File::exists?("/var/www/webtoon/tmp/#{v.gsub(/\//, "@")}")
          _data = a.get("http://#{v}").body
          if _data != nil
            File.open("/var/www/webtoon/tmp/#{v.gsub(/\//, "@")}", "w") do |f|
              f.write(_data)
            end
          end
        end
        puts "<img src=\"/webtoon/tmp/#{v.gsub(/\//, "@")}\"/>"
        check_puts = true if not check_puts
      }
    if not check_puts
      puts "<span>등록된 이미지가 없습니다.</span>"
    end
  end
end
