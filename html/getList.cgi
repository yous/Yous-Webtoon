#!/usr/local/rvm/wrappers/ruby-1.9.3-p125@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'
require 'pg'

def site_button(site)
  sites = ["naver", "daum", "yahoo", "stoo"].reverse
  str = ""
  sites.each do |site_name|
    next if site_name == site
    str << <<-HTML
      <span class="site_button" onclick="site_change('#{site_name}');"><u>#{site_name.slice(0).upcase}</u>#{site_name.slice(1, site_name.length - 1)}</span>
    HTML
  end
  str << "<br/>"
end

def generate_toon(toon_id, toon_class, color, title, options = {:quote => false})
  if options[:new].nil? and options[:up].nil?
    return <<-HTML
      <div name="#{toon_id}" class="#{toon_class}" style="background-color: #{color};" title="#{title}" onclick="viewToon(#{options[:quote] ? "'#{toon_id}'" : toon_id});">#{title}</div>
    HTML
  else
    return <<-HTML
      <div name="#{toon_id}" class="#{toon_class}" style="background-color: #{color};" title="#{title}#{options[:new]}#{options[:up]}" onclick="viewToon(#{options[:quote] ? "'#{toon_id}'" : toon_id});">#{title}<small>#{options[:new]}#{options[:up]}</small></div>
    HTML
  end
end

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = cgi.params["site"][0]

if not cgi.cookies["SSID"].nil?
  begin
    session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
  rescue
    session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))
  end
end

db = PGconn.open(:dbname => "webtoon")

a = Mechanize.new
a.history.max_size = 0

port = 8888
btnColor = {
  "buttonA" => "#FAFAFA",
  "buttonB" => "#EAEAEA",
  "saved" => "#88DD88",
  "saved_up" => "#DD8888",
  "saved_finish" => "#888888",
  "link" => "#0066CC"
}

# Naver 웹툰
if site == "naver"
  reqList = []
  tmpList = []

  db.exec("SELECT toon_id FROM naver_tmplist ORDER BY toon_id;").each do |row|
    _toon_id = row["toon_id"].to_i
    tmpList.push(_toon_id)
  end

  # 연재
  resp = a.get "http://comic.naver.com/webtoon/weekday.nhn"

  str = <<-HTML
    <span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>
    #{site_button(site)}
    <div id="current_toonlist" class="toonlist">
  HTML

  count = 0

  resp.search('//div[@class="list_area daily_all"]').each do |r|
    str_div = []
    day = 0
    days = ["월", "화", "수", "목", "금", "토", "일"]
    r.search('./div/div[@class="col_inner"]').each do |v|
      str_div.push <<-HTML
        <div id="day#{day}">
          <div style="font-weight: bold;">#{days[day]}<span class="refreshBtn" onclick="putToonColor(#{day});">Re</span></div>
      HTML
      v.search('./ul/li/div[@class="thumb"]').each do |v1|
        _a = v1.at('./a')
        _titleId = $1.to_i if _a.attr("href") =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
        _title = _a.attr("title")
        _up = (_a.search('./em').length != 0) ? '(UP)' : ''
        _new = (_a.search('./img').length > 1) ? '(NEW)' : ''
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList.push(_titleId) unless tmpList.include? _titleId

        str_div[day] << generate_toon(_titleId, "current_toon", _color, _title, :new => _new, :up => _up)
        count += 1
      end
      count = 0
      str << str_div[day] + '</div>'
      day += 1
    end
    str << '</div>'
  end

  # 완결
  resp = a.get 'http://comic.naver.com/webtoon/finish.nhn'

  str << '<div id="finished_toonlist" class="toonlist" style="display: none;">'
  str_div = ["<div>", "<div>", "<div>", "<div>", "<div>", "<div>", "<div>"]

  count = 0

  resp.search('//div[@class="thumb"]').each do |r|
    _a = r.at('./a')
    _titleId = $1.to_i if _a.attr("href") =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
    _title = _a.attr("title")
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList.push(_titleId) unless tmpList.include? _titleId

    str_div[count % 7] << generate_toon(_titleId, "finished_toon", _color, _title)
    count += 1
  end

  str_div.each do |v|
    str << v + "</div>"
  end
  str << '</div><div class="clear">&nbsp;</div>'

  # reqList 처리
  str << '<script>'
  reqList.each do |v|
    str << <<-HTML
      $.get("/displayToon.cgi?site=naver&id=#{v}&num=1");
    HTML
    db.exec("INSERT INTO naver_tmplist (toon_id) SELECT $1 WHERE NOT EXISTS (SELECT 1 FROM naver_tmplist WHERE toon_id=$1);", [v])
  end
  str << 'resizeWidth();'

  # toonlist background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new
    lastNum = Hash.new
    finishToon = []

    db.exec("SELECT toon_id, toon_num FROM naver_bm WHERE id=$1;", [session["user_id"]]).each do |row|
      _toon_id = row["toon_id"].to_i
      _toon_num = row["toon_num"].to_i
      toonBM[_toon_id] = _toon_num
      db.exec("SELECT toon_num FROM naver_lastnum WHERE toon_id=$1;", [_toon_id]).each do |sec_row|
        _lastNum = sec_row["toon_num"].to_i
        lastNum[_toon_id] = _lastNum
        finishToon.push(_toon_id)
      end
    end

    str << <<-HTML
      toonBM={#{toonBM.keys.map {|v| "#{v}:#{toonBM[v]}"}.join(",")}};
      lastNum={#{lastNum.keys.map {|v| "#{v}:#{lastNum[v]}"}.join(",")}};
      finishToon=[#{finishToon.join(",")}];

      $("#loading").html(" Loading");
      $("#loading").css("display", "inline");
      loading(10);
      putToonColor();
    HTML
  end

  str << '</script>'

  puts str

# Daum 웹툰
elsif site == "daum"
  numList = Hash.new
  dateList = Hash.new
  toonInfo = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new
  tmpList = []

  db.exec("SELECT toon_id, toon_num FROM daum_lastnum;").each do |row|
    _toon_id = row["toon_id"]
    _toon_num = row["toon_num"].to_i
    lastNum[_toon_id] = _toon_num
    finishToon.push(_toon_id)
  end

  db.exec("SELECT toon_id, toon_num, toon_date FROM daum_numlist ORDER BY toon_id, toon_num_idx;").each do |row|
    _toon_id = row["toon_id"]
    _toon_num = row["toon_num"].to_i
    _toon_date = row["toon_date"]
    if _toon_date.nil?
      reqList[_toon_id] = false
    else
      numList[_toon_id] = [] if numList[_toon_id].nil?
      numList[_toon_id].push(_toon_num.to_i)
      dateList[_toon_id] = [] if dateList[_toon_id].nil?
      dateList[_toon_id].push(_toon_date)
    end
    unless tmpList.include? _toon_id
      tmpList.push(_toon_id)
      res = db.exec("SELECT toon_writer, toon_intro FROM daum_tooninfo WHERE toon_id=$1::VARCHAR;", [_toon_id])
      if res.count < 1
        reqList[_toon_id] = false
      else
        _toon_writer = res[0]["toon_writer"]
        _toon_intro = res[0]["toon_intro"]
        reqList[_toon_id] = false if _toon_writer.nil? or _toon_intro.nil?
        toonInfo[_toon_id] = [_toon_writer, _toon_intro]
      end
    end
  end

  # 연재
  resp = a.get "http://cartoon.media.daum.net/webtoon/week"

  str = <<-HTML
    <span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>
    #{site_button(site)}
    <div id="current_toonlist" class="toonlist">
  HTML

  count = 0

  resp.search('//div[@class="area_toonlist area_bg"]').each do |r|
    str_div = []
    day = 0
    days = ["월", "화", "수", "목", "금", "토", "일"]
    r.search('./div/div[@class="bg_line"]').each do |v|
      str_div.push <<-HTML
        <div id="day#{day}">
          <div style="font-weight: bold;">#{days[day]}<span class="refreshBtn" onclick="putToonColor(#{day});">Re</span></div>
      HTML
      v.search('./ul/li/a').each do |v1|
        _titleId = $1 if v1.attr("href") =~ /\/webtoon\/view\/(.+)$/
        _title = v1.attr("title")
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList[_titleId] = true unless tmpList.include? _titleId

        str_div[day] << generate_toon(_titleId, "current_toon", _color, _title, :quote => true)
        count += 1
      end
      count = 0
      str << str_div[day] + '</div>'
      day += 1
    end
    str << '</div>'
  end

  # 완결
  resp = a.get 'http://cartoon.media.daum.net/webtoon/finished'

  str << '<div id="finished_toonlist" class="toonlist" style="display: none;">'
  str_div = ["<div>", "<div>", "<div>", "<div>", "<div>", "<div>", "<div>"]

  count = 0

  resp.search('//ul[@class="list_type_image list_incount list_year"]/li').each do |r|
    next if r.attributes["class"].value == "line_dot"
    _titleId = $1 if r.at('./a').attr("href") =~ /\/webtoon\/view\/(.+)$/
    _title = r.at('./p').attr("title")
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    if not finishToon.include? _titleId
      finishToon.push(_titleId)
      reqList[_titleId] = (tmpList.include? _titleId) ? false : true
    end

    str_div[count % 7] << generate_toon(_titleId, "finished_toon", _color, _title, :quote => true)
    count += 1
  end

  str_div.each do |v|
    str << v + "</div>"
  end
  str << '</div><div class="clear">&nbsp;</div>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    numList[v] = []
    dateList[v] = []
    num_resp = a.get("http://localhost:#{port}/getNum.cgi?site=daum&id=#{v}").body

    # 로그인 필요한 웹툰
    next if num_resp == ""

    num_resp = num_resp.split("\n").map {|item| item.strip.force_encoding("UTF-8") }
    num_resp[0].split()[1..-1].map {|item|
      numList[v].push(item.split(",")[0].to_i)
      dateList[v].push(item.split(",")[1])
    }
    toonInfo[v] = [num_resp[1], (num_resp[2].nil?) ? nil : num_resp[2].gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;")]
    lastNum[v] = numList[v][-1]

    str << "$.get(\"/displayToon.cgi?site=daum&id=#{v}&num=#{numList[v][0]}\");" if reqList[v]
    numList[v].each_with_index do |num, idx|
      db.exec("UPDATE daum_numlist SET toon_num=$1, toon_date=$2::VARCHAR WHERE toon_id=$3::VARCHAR AND toon_num_idx=$4;", [num, dateList[v][idx], v, idx])
      db.exec("INSERT INTO daum_numlist (toon_id, toon_num_idx, toon_num, toon_date) SELECT $1::VARCHAR, $2, $3, $4::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM daum_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, idx, num, dateList[v][idx]])
      db.exec("UPDATE daum_tooninfo SET toon_writer=$1::VARCHAR, toon_intro=$2::VARCHAR WHERE toon_id=$3;", [toonInfo[v][0], toonInfo[v][1], v])
      db.exec("INSERT INTO daum_tooninfo (toon_id, toon_writer, toon_intro) SELECT $1::VARCHAR, $2::VARCHAR, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM daum_tooninfo WHERE toon_id=$1);", [v, toonInfo[v][0], toonInfo[v][1]])
    end
    if finishToon.include? v # 완결
      db.exec("UPDATE daum_lastnum SET toon_num=$1 WHERE toon_id=$2::VARCHAR;", [numList[v][-1], v])
      db.exec("INSERT INTO daum_lastnum (toon_id, toon_num) SELECT $1::VARCHAR, $2 WHERE NOT EXISTS (SELECT 1 FROM daum_lastnum WHERE toon_id=$1);", [v, numList[v][-1]])
    end
  end
  str << 'resizeWidth();'

  # 웹툰 정보 입력
  str << <<-HTML
    numList={#{numList.keys.map {|v| "'#{v}':[#{numList[v].join(",")}]"}.join(",")}};
    dateList={#{dateList.keys.map {|v| "'#{v}':['#{dateList[v].join("','")}']"}.join(",")}};
    toonInfo={#{toonInfo.keys.map {|v| "'#{v}':['#{toonInfo[v].join("','")}']"}.join(",")}};
    lastNum={#{lastNum.keys.map {|v| "'#{v}':#{lastNum[v]}"}.join(",")}};
    finishToon=[#{finishToon.map {|v| "'#{v}'"}.join(",")}];
  HTML

  # toon background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new

    db.exec("SELECT toon_id, toon_num FROM daum_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
      _toon_id = row["toon_id"]
      _toon_num = row["toon_num"].to_i
      toonBM[_toon_id] = _toon_num
    end

    str << <<-HTML
      toonBM={#{toonBM.keys.map {|v| "'#{v}':#{toonBM[v]}"}.join(",")}};

      $("#loading").html(" Loading");
      $("#loading").css("display", "inline");
      loading(10);
      putToonColor();
    HTML
  end

  str << '</script>'

  puts str

# Yahoo 웹툰
elsif site == "yahoo"
  numList = Hash.new
  toonInfo = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new
  tmpList = []

  db.exec("SELECT toon_id, toon_num FROM yahoo_lastnum;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    lastNum[_toon_id] = _toon_num
    finishToon.push(_toon_id)
  end

  db.exec("SELECT toon_id, toon_num FROM yahoo_numlist ORDER BY toon_id, toon_num_idx;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    numList[_toon_id] = [] if numList[_toon_id].nil?
    numList[_toon_id].push(_toon_num.to_i)
    unless tmpList.include? _toon_id
      tmpList.push(_toon_id)
      res = db.exec("SELECT toon_title, toon_intro FROM yahoo_tooninfo WHERE toon_id=$1;", [_toon_id])
      if res.count < 1
        reqList[_toon_id] = false
      else
        _toon_title = res[0]["toon_title"]
        _toon_intro = res[0]["toon_intro"]
        reqList[_toon_id] = false if _toon_title.nil? or _toon_intro.nil?
        toonInfo[_toon_id] = [_toon_title, _toon_intro]
      end
    end
  end

  # 연재
  resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=webtoon&kind=cont"

  str = <<-HTML
    <span class="table_toggle_button" id="table_toggle_button1" style="display: none;" onclick="show_table(1);">연재 웹툰</span>
    <span class="table_toggle_button" id="table_toggle_button2" onclick="show_table(2);">완결 웹툰</span>
    <span class="table_toggle_button" id="table_toggle_button3" onclick="show_table(3);">특집 웹툰</span>
    #{site_button(site)}
    <div id="current_toonlist" class="toonlist">
  HTML

  str_div = []
  7.times do |day|
    str_div.push <<-HTML
      <div id="day#{day}">
        <div style="font-weight: bold;"><span class="refreshBtn" onclick="putToonColor(#{day});">Re</span></div>
    HTML
  end

  count = [0, 0, 0, 0, 0, 0, 0]
  day = 0

  while true
    resp.search('//div[@id="cll"]/ol/li').each do |r|
      _title = r.at('./a').inner_html.encode("UTF-8").strip
      _titleId = $1.to_i if r.at('./a').attr("href") =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      reqList[_titleId] = true unless tmpList.include? _titleId
      if toonInfo[_titleId].nil?
        toonInfo[_titleId] = [_title, nil]
      else
        toonInfo[_titleId][0] = _title
      end

      str_div[day] << generate_toon(_titleId, "current_toon", _color, _title)
      count[day] += 1
      day = (day + 1) % 7
    end

    if resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attr("href")
    else
      break
    end
  end

  str_div.each do |v|
    str << v + "</div>"
  end

  str << '</div>'

  # 완결
  resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=webtoon&kind=done"

  str << '<div id="finished_toonlist" class="toonlist" style="display: none;">'
  str_div = ["<div>", "<div>", "<div>", "<div>", "<div>", "<div>", "<div>"]

  count = 0

  while true
    resp.search('//div[@id="cll"]/ol/li').each do |r|
      _title = r.at('./a').inner_html.encode("UTF-8").strip.force_encoding("UTF-8")
      _titleId = $1.to_i if r.at('./a').attr("href") =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      if not finishToon.include? _titleId
        finishToon.push(_titleId)
        reqList[_titleId] = (tmpList.include? _titleId) ? false : true
      end
      if toonInfo[_titleId].nil?
        toonInfo[_titleId] = [_title, nil]
      else
        toonInfo[_titleId][0] = _title
      end

      str_div[count % 7] << generate_toon(_titleId, "finished_toon", _color, _title)
      count += 1
    end

    if resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attr("href")
    else
      break
    end
  end

  str_div.each do |v|
    str << v + "</div>"
  end

  str << '</div>'

  # 특집
  resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=webtoon&kind=special"

  str << <<-HTML
    <div id="special_toonlist" class="toonlist" style="display: none;">
  HTML

  str_div = []
  7.times do |day|
    str_div.push <<-HTML
      <div id="day#{day + 7}">
        <div><span class="refreshBtn" onclick="putToonColor(#{day + 7});">Re</span></div>
    HTML
  end

  count = [0, 0, 0, 0, 0, 0, 0]
  day = 0

  while true
    resp.search('//div[@id="cll"]/ol/li').each do |r|
      _title = r.at('./a').inner_html.encode("UTF-8").strip
      _titleId = $1.to_i if r.at('./a').attr("href") =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      reqList[_titleId] = true unless tmpList.include? _titleId
      if toonInfo[_titleId].nil?
        toonInfo[_titleId] = [_title, nil]
      else
        toonInfo[_titleId][0] = _title
      end

      str_div[day] << generate_toon(_titleId, "current_toon", _color, _title)
      count[day] += 1
      day = (day + 1) % 7
    end

    if resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attr("href")
    else
      break
    end
  end

  str_div.each do |v|
    str << v + "</div>"
  end

  str << '</div><div class="clear">&nbsp;</div>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    num_resp = a.get("http://localhost:#{port}/getNum.cgi?site=yahoo&id=#{v}").body.split("\n").map(&:strip)
    numList[v] = num_resp[0].split()[1..-1].map(&:to_i)
    toonInfo[v][1] = (num_resp[1].nil?) ? nil : num_resp[1].force_encoding("UTF-8").gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;").gsub(/&lt;br\/?&gt;/, "<br/>")
    lastNum[v] = numList[v][-1]

    str << "$.get(\"/displayToon.cgi?site=yahoo&id=#{v}&num=#{numList[v][0]}\");" if reqList[v]
    numList[v].each_with_index do |num, idx|
      db.exec("UPDATE yahoo_numlist SET toon_num=$1 WHERE toon_id=$2 AND toon_num_idx=$3;", [num, v, idx])
      db.exec("INSERT INTO yahoo_numlist (toon_id, toon_num_idx, toon_num) SELECT $1, $2, $3 WHERE NOT EXISTS (SELECT 1 FROM yahoo_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, idx, num])
      db.exec("UPDATE yahoo_tooninfo SET toon_title=$1::VARCHAR, toon_intro=$2::VARCHAR WHERE toon_id=$3;", [toonInfo[v][0], toonInfo[v][1], v])
      db.exec("INSERT INTO yahoo_tooninfo (toon_id, toon_title, toon_intro) SELECT $1, $2::VARCHAR, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM yahoo_tooninfo WHERE toon_id=$1);", [v, toonInfo[v][0], toonInfo[v][1]])
    end
    if finishToon.include? v # 완결
      db.exec("UPDATE yahoo_lastnum SET toon_num=$1 WHERE toon_id=$2;", [numList[v][-1], v])
      db.exec("INSERT INTO yahoo_lastnum (toon_id, toon_num) SELECT $1, $2 WHERE NOT EXISTS (SELECT 1 FROM yahoo_lastnum WHERE toon_id=$1);", [v, numList[v][-1]])
    end
  end
  str << 'resizeWidth();'

  # 웹툰 정보 입력
  str << <<-HTML
    numList={#{numList.keys.map {|v| "#{v}:[#{numList[v].join(",")}]"}.join(",")}};
    toonInfo={#{toonInfo.keys.map {|v| "#{v}:['#{toonInfo[v].join("','")}']"}.join(",")}};
    lastNum={#{lastNum.keys.map {|v| "#{v}:#{lastNum[v]}"}.join(",")}};
    finishToon=[#{finishToon.join(",")}];
  HTML

  # toon background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new

    db.exec("SELECT toon_id, toon_num FROM yahoo_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
      _toon_id = row["toon_id"].to_i
      _toon_num = row["toon_num"].to_i
      toonBM[_toon_id] = _toon_num
    end

    str << <<-HTML
      toonBM={#{toonBM.keys.map {|v| "#{v}:#{toonBM[v]}"}.join(",")}};

      $("#loading").html(" Loading");
      $("#loading").css("display", "inline");
      loading(10);
      putToonColor();
    HTML
  end

  str << '</script>'

  puts str

# Stoo 웹툰
elsif site == "stoo"
  numList = Hash.new
  toonInfo = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new
  tmpList = []

  db.exec("SELECT toon_id, toon_num FROM stoo_lastnum;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"]
    lastNum[_toon_id] = _toon_num
    finishToon.push(_toon_id)
  end

  db.exec("SELECT toon_id, toon_num FROM stoo_numlist ORDER BY toon_id, toon_num_idx;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"]
    numList[_toon_id] = [] if numList[_toon_id].nil?
    numList[_toon_id].push(_toon_num.to_i)
    unless tmpList.include? _toon_id
      tmpList.push(_toon_id)
      res = db.exec("SELECT toon_writer, toon_intro FROM stoo_tooninfo WHERE toon_id=$1;", [_toon_id])
      if res.count < 1
        reqList[_toon_id] = false
      else
        _toon_writer = res[0]["toon_writer"]
        _toon_intro = res[0]["toon_intro"]
        reqList[_toon_id] = false if _toon_writer.nil? or _toon_intro.nil?
        toonInfo[_toon_id] = [_toon_writer, _toon_intro]
      end
    end
  end

  resp = a.get "http://stoo.asiae.co.kr/cartoon/"

  # 연재
  str = <<-HTML
    <span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>
    #{site_button(site)}
    <div id="current_toonlist" class="toonlist">
  HTML

  str_div = []
  7.times do |day|
    str_div.push <<-HTML
      <div id="day#{day}">
        <div style="font-weight: bold;"><span class="refreshBtn" onclick="putToonColor(#{day});">Re</span></div>
    HTML
  end

  count = [0, 0, 0, 0, 0, 0, 0]
  day = 0

  resp.search('//ul[@id="serialcm"]/li').each do |r|
    _a = r.at('./dl/dt[@class="desc"]/a')
    _titleId = $1.to_i if _a.attr("href") =~ /\/cartoon\/ctlist\.htm\?sc1=cartoon&sc2=ing&sc3=(\d+)/
    _title = _a.attr("title").gsub(/<br\/?>/, " ")
    _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = true unless tmpList.include? _titleId

    str_div[day] << generate_toon(_titleId, "current_toon", _color, _title)
    count[day] += 1
    day = (day + 1) % 7
  end

  str_div.each do |v|
    str << v + "</div>"
  end
  str << '</div>'

  # 완결
  str << '<div id="finished_toonlist" class="toonlist" style="display: none;">'
  str_div = ["<div>", "<div>", "<div>", "<div>", "<div>", "<div>", "<div>"]

  count = 0

  resp.search('//ul[@id="endcm"]/li').each do |r|
    _a = r.at('./dl/dt[@class="desc"]/a')
    _titleId = $1.to_i if _a.attr("href") =~ /\/cartoon\/ctlist\.htm\?sc1=cartoon&sc2=end&sc3=(\d+)/
    _title = _a.attr("title").gsub(/<br\/?>/, " ")
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    if not finishToon.include? _titleId
      finishToon.push(_titleId)
      reqList[_titleId] = (tmpList.include? _titleId) ? false : true
    end

    str_div[count % 7] << generate_toon(_titleId, "finished_toon", _color, _title)
    count += 1
  end

  str_div.each do |v|
    str << v + "</div>"
  end
  str << '</div><div class="clear">&nbsp;</div>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    num_resp = a.get("http://localhost:#{port}/getNum.cgi?site=stoo&id=#{v}").body.split("\n").map(&:strip)
    numList[v] = num_resp[0].split()[1..-1]
    toonInfo[v] = [num_resp[1].force_encoding("UTF-8"), (num_resp[2].nil?) ? nil : num_resp[2].force_encoding("UTF-8").gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;").gsub(/&lt;br\/?&gt;/, "<br/>")]
    lastNum[v] = numList[v][-1]

    str << "$.get(\"/displayToon.cgi?site=stoo&id=#{v}&num=#{numList[v][0]}\");" if reqList[v]
    numList[v].each_with_index do |num, idx|
      db.exec("UPDATE stoo_numlist SET toon_num=$1::VARCHAR WHERE toon_id=$2 AND toon_num_idx=$3;", [num, v, idx])
      db.exec("INSERT INTO stoo_numlist (toon_id, toon_num_idx, toon_num) SELECT $1, $2, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM stoo_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, idx, num])
      db.exec("UPDATE stoo_tooninfo SET toon_writer=$1::VARCHAR, toon_intro=$2::VARCHAR WHERE toon_id=$3;", [toonInfo[v][0], toonInfo[v][1], v])
      db.exec("INSERT INTO stoo_tooninfo (toon_id, toon_writer, toon_intro) SELECT $1, $2::VARCHAR, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM stoo_tooninfo WHERE toon_id=$1);", [v, toonInfo[v][0], toonInfo[v][1]])
    end
    if finishToon.include? v # 완결
      db.exec("UPDATE stoo_lastnum SET toon_num=$1::VARCHAR WHERE toon_id=$2;", [numList[v][-1], v])
      db.exec("INSERT INTO stoo_lastnum (toon_id, toon_num) SELECT $1, $2::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM yahoo_lastnum WHERE toon_id=$1);", [v, numList[v][-1]])
    end
  end
  str << 'resizeWidth();'

  # 웹툰 정보 입력
  str << <<-HTML
    numList={#{numList.keys.map {|v| "#{v}:['#{numList[v].join("','")}']"}.join(",")}};
    toonInfo={#{toonInfo.keys.map {|v| "#{v}:['#{toonInfo[v].join("','")}']"}.join(",")}};
    lastNum={#{lastNum.keys.map {|v| "#{v}:'#{lastNum[v]}'"}.join(",")}};
    finishToon=[#{finishToon.join(",")}];
  HTML

  # toonlist background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new

    db.exec("SELECT toon_id, toon_num FROM stoo_bm WHERE id=$1;", [session["user_id"]]).each do |row|
      _toon_id = row["toon_id"].to_i
      _toon_num = row["toon_num"]
      toonBM[_toon_id] = _toon_num
    end

    str << <<-HTML
      toonBM={#{toonBM.keys.map {|v| "#{v}:'#{toonBM[v]}'"}.join(",")}};

      $("#loading").html(" Loading");
      $("#loading").css("display", "inline");
      loading(10);
      putToonColor();
    HTML
  end

  str << '</script>'

  puts str
end

db.close
