# encoding: utf-8
require "rubygems"
require "webrick"
require "mechanize"

class GetOtherToon < WEBrick::HTTPServlet::AbstractServlet
  def do_GET(req, res)
    site = req.query["site"]
    id = req.query["id"]
    check_other = (site == "daum") ? req.query["other"] : nil

    res.status = 200
    res["Content-Type"] = "text/html; charset=utf-8"
    res.body = process(site, id, check_other) if site != nil and id != nil
  end

  def process(site, id, check_other = nil)
    str = ""

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
          titleId = $1 if r.at('h4[@class="title"]/a').attributes["href"].to_s =~ /\/webtoon\/detail\.nhn\?titleId=(\d+)/
          title = r.at('h4[@class="title"]/a').inner_html.force_encoding("UTF-8")
          str << "<div id=\"#{titleId}\" style=\"background-color: #{btnColor["buttonB"]}; cursor: default; margin: 3px 0px 3px 0px;\" onclick=\"viewToon('#{titleId}');\">#{title}</div>"
        end
        page += 1
      end while (resp.search('//div[@class="pagenavigation"]/a[@class="next"]').length > 0)
    elsif site == "daum"
      resp = a.get "http://cartoon.media.daum.net/webtoon/view/#{id}"
      check_puts = false

      if check_other == "y"
        resp.
          at('//div[@id="daumContent"]/div/div[@id="mCenter"]/script').
          inner_html.force_encoding("UTF-8").strip.split(';').map(&:strip).
          find_all {|v| v =~ /data2\.push\([\w\W]*\)/}.
          map {|v|
            {"title" => $1, "url" => $2} if v =~ /data2\.push\(\s*\{\s*img\s*:\s*".*"\s*,\s*title\s*:\s*"(.*)"\s*,\s*shortTitle\s*:\s*".*"\s*,\s*url\s*:\s*"\/webtoon\/view\/(.*)"\s*,\s*isAdult\s*:\s*.*\}\s*\)/
          }.
          each do |v|
            str << "<div id=\"#{v["url"]}\" style=\"background-color: #{btnColor["buttonB"]}; cursor: default; margin: 3px 0px 3px 0px;\" onclick=\"viewToon('#{v["url"]}');\">#{v["title"]}</div>"
            check_puts = true if not check_puts
          end
        if not check_puts
          str << "<span>관련 웹툰이 없습니다.</span>"
        end
      else
        str << "<span>준비중입니다.</span>"
=begin
        resp.
          at('//div[@id="daumContent"]/div/div[@id="mCenter"]/script').
          inner_html.strip.split(';').map(&:strip).
          find_all {|v| v =~ /data3\.push\([\w\W]*\)/}.
          map {|v| $1 if v =~ /data3\.push\(\s*\{\s*img\s*:\s*"http:\/\/(.*)"\s*,\s*no\s*:\s*".*"\s*\}\s*\)/}.
          each {|v|
            if not File::exists?("images/#{v.gsub(/\//, "@")}")
              _data = a.get("http://#{v}").body
              if _data != nil
                File.open("images/#{v.gsub(/\//, "@")}", "w") do |f|
                  f.write(_data)
                end
              end
            end
            str << "<img src=\"/images/#{v.gsub(/\//, "@")}\"/>"
            check_puts = true if not check_puts
          }
        if not check_puts
          str << "<span>등록된 이미지가 없습니다.</span>"
        end
=end
      end
    end

    str
  end
end
