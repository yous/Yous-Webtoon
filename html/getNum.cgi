#!/usr/local/rvm/wrappers/ruby-1.9.3-p125@webtoon/ruby
# encoding: utf-8
require "rubygems"
require "mechanize"
require "pg"
require "json"
require "cgi"
require "cgi/session"

cgi = CGI.new
site = (cgi.has_key? "site") ? cgi.params["site"][0] : nil
id = (cgi.has_key? "id") ? cgi.params["id"][0] : nil

a = Mechanize.new
a.history.max_size = 0

puts "Content-Type: text/html; charset=utf-8\n\n"

# Naver 웹툰
if site == "naver"
  str = ""
  resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}"

  # 성인 인증 필요한 웹툰
  if resp.search('//div[@id="log_adult"]').length > 0
    if cgi.cookies["SSID"] != nil
      begin
        session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
      rescue
        session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))
      end

      if session[site] != nil and session[site]["cookie"] != nil
        a = Mechanize.new
        a.cookie_jar = session[site]["cookie"]

        resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}"
        if resp.search('//div[@id="log_adult"]').length > 0
          print "auth"
          exit
        end
      else
        print "auth"
        exit
      end
    else
      print "auth"
      exit
    end
  end

  str << case resp.at('//div[@id="header"]/div[@id="submenu"]/ul[@class="submenu"]/li/a[@class="current"]').attr("href")
  when "/webtoon/weekday.nhn" then "n "
  when "/webtoon/finish.nhn" then "y "
  else "x "
  end
  str << resp.at('//div[@id="comicRemocon"]/div[@class="remote_cont"]/div[@class="pg_area"]/span[@class="total"]').inner_text

  print str

# Daum 웹툰
elsif site == "daum"
  str = ""
  str_writer = []
  str_toonInfo = ""
  str_finish = ""
  resp = a.get "http://cartoon.media.daum.net/webtoon/view/#{id}"

  # 로그인 필요한 웹툰
  exit if resp.search('//div[@id="wrap"]/div[@id="content"]/form[@id="loginForm"]').length > 0

  str = resp.at('//div[@id="daumContent"]/div[@id="cMain"]/div[@id="mCenter"]/script[2]').inner_html.strip.split(";").map(&:strip)
  str = str.find_all {|v| v =~ /data1\.push\([\w\W]*\)/}.map {|v|
    if v =~ /data1\.push\(\s*\{\s*img\s*:\s*"[\w\W]*"\s*,\s*title\s*:\s*"[\w\W]*"\s*,\s*shortTitle\s*:\s*"[\w\W]*"\s*,\s*url\s*:\s*"\/webtoon\/viewer\/(\d+)"\s*,\s*date\s*:\s*"([\w\W]*)"\s*,\s*price\s*:\s*"[\w\W]*"\s*,\s*finishYn\s*:\s*"([\w\W]*)"\s*,\s*payYn\s*:\s*"[\w\W]*"\s*\}\s*\)/
      if $3 == "Y" and str_finish == ""
        str_finish = "y "
      end
      $1.to_i
    end
  }.reverse.join(" ")

  print ((str_finish == "") ? "n " : str_finish) + str

# Yahoo 웹툰
elsif site == "yahoo"
  db = PGconn.open(:dbname => "webtoon")

  a.default_encoding = "CP949"
  a.force_default_encoding = true

  str_finish = ""
  numList = []
  tmp_numList = []

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

  check = true
  while check
    resp.search('//div[@id="cth"]/ol/li').each do |r|
      if r.at('./a').attr("href") =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shellview2\.htm\?linkid=series_cartoon&sidx=(\d+)/
        if numList.include?($1.to_i)
          check = false
          break
        else
          tmp_numList.push($1.to_i)
        end
      end
    end
    if check and resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attr("href")
    else
      break
    end
  end

  numList += tmp_numList.reverse

  print ((str_finish == "") ? "n " : str_finish) + numList.join(" ")

# Stoo 웹툰
elsif site == "stoo"
  db = PGconn.open(:dbname => "webtoon")

  str_finish = ""
  numList = []
  tmp_numList = []

  db.exec("SELECT toon_num FROM stoo_numlist WHERE toon_id=$1 ORDER BY toon_num_idx;", [id]).each do |row|
    _toon_num = row["toon_num"]
    numList.push(_toon_num)
  end
  db.exec("SELECT toon_num FROM stoo_lastnum WHERE toon_id=$1;", [id]).each do |row|
    str_finish = "y "
  end
  db.close

  _lastNum = (_lastNum.nil?) ? "" : _lastNum

  resp = a.get "http://stoo.asiae.co.kr/cartoon/ctlist.htm?sc2=#{(str_finish == "y ") ? "end" : "ing"}&sc3=#{id}"
  if resp.at('//div[@id="content"]/div[@class="ct_topdesc"]/div[@class="rt"]/dl[2]/dd').inner_html == "" or resp.at('//div[@id="content"]/div[@class="ct_topdesc"]/div[@class="rt"]/dl[4]/dd').inner_html == ""
    resp = a.get "http://stoo.asiae.co.kr/cartoon/ctlist.htm?sc2=end&sc3=#{id}"
  end

  page = 1
  resp = a.get "http://stoo.asiae.co.kr/cartoon/ctlist.php?strForm=s_list&sc3=#{id}&pg=#{page}"

  check = true
  while check
    resp.search('//table/tr/td').each do |td|
      if td.at('./a[2]').attr("href") =~ /\/cartoon\/ctview\.htm\?sc2=[\w\W]*&sc3=#{id}&tpg=[\w\W]+&id=([\w\W]*)/
        if numList.include? $1
          check = false
          break
        else
          tmp_numList.push($1)
        end
      end
    end
    if check and resp.search('//div[@class="pagination"]/a[@class="arrow next"]').attr("href").value =~ /javascript\s*:\s*s_list\(\s*'(\d+)'\s*,\s*'[\w\W]*'\s*,\s*'[\w\W]*'\s*,\s*'[\w\W]*'\s*,\s*'[\w\W]*'\s*\)/
      if $1.to_i == page
        break
      else
        page = $1.to_i
        resp = a.get "http://stoo.asiae.co.kr/cartoon/ctlist.php?strForm=s_list&sc3=#{id}&pg=#{page}"
      end
    else
      break
    end
  end

  numList += tmp_numList.reverse

  print ((str_finish == "") ? "n " : str_finish) + numList.join(" ")
end
