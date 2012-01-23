# encoding: utf-8
require "rubygems"
require "webrick"
require "mechanize"
require "pg"

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

    # Yahoo 웹툰
    elsif site == "yahoo"
      str_finish = ""
      str_intro = ""
      numList = []
      tmp_numList = []

      db = PGconn.open(:dbname => "yous")
      db.exec("CREATE TABLE yahoo_numlist (toon_id INTEGER, toon_num_idx INTEGER, toon_num INTEGER);") rescue nil
      db.exec("SELECT toon_num FROM yahoo_numlist WHERE toon_id=$1 ORDER BY toon_num_idx;", [id]).each do |row|
        _toon_num = row["toon_num"].to_i
        numList.push(_toon_num)
      end
      db.exec("SELECT toon_num FROM yahoo_lastnum WHERE toon_id=$1;", [id]).each do |row|
        str_finish = "y "
      end
      db.close

      _lastNum = (_lastNum.nil?) ? 0 : _lastNum

      resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=toon_series&work_idx=#{id}"

      str_intro = resp.at('//div[@id="ctg"]/span[@class="dsc"]/dl/dd').inner_html.encode("UTF-8").strip.gsub("\r", "").gsub("\n", "")

      check = true
      while check
        resp.search('//div[@id="cth"]/ol/li').each do |r|
          if r.at('a[2]').attributes["href"].value =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shellview2\.htm\?linkid=series_cartoon&sidx=(\d+)/
            if numList.include?($1.to_i)
              check = false
              break
            else
              tmp_numList.push($1.to_i)
            end
          end
        end
        if check and resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
          resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attributes["href"].value
        else
          break
        end
      end

      numList += tmp_numList.reverse

      ((str_finish == "") ? "n " : str_finish) + numList.join(" ") + "\n" + str_intro
    end
  end
end
