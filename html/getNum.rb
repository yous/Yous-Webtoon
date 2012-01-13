require "rubygems"
require "webrick"
require "mechanize"

class GetNum < WEBrick::HTTPServlet::AbstractServlet
  def do_GET(req, res)
    site = req.query["site"]
    id = req.query["id"]

    res.status = 200
    res["Content-Type"] = "text/html; charset=utf-8"
    res.body = process(site, id) if site != nil and id != nil
  end

  def process(site, id)
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
        if v.at('span[@class="pre"]/a').attributes["href"].value =~ /\/webtoon\/detail\.nhn\?titleId=\d+&seq=(\d+)/
          str << "#{$1.to_i + 1}"
        else
          str << "1"
        end
      end

      str

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
      end

      ((str_finish == "") ? "n " : str_finish) + str[0...-1] + "\n" + str_writer.join(" / ") + "\n" + str_toonInfo
    end
  end
end
