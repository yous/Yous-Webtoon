#!/usr/bin/ruby
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'
require 'sqlite3'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = cgi.params["site"][0]

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => "sess")

db = SQLite3::Database.new('/var/www/db/webtoon.db')
db.execute("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER, toon_id INTEGER, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS naver_lastNum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS naver_tmpList (toon_id INTEGER PRIMARY KEY);")
db.execute("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER, toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_lastNum (toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_numList (toon_id VARCHAR(255), toon_num_idx INTEGER, toon_num INTEGER, toon_date VARCHAR(10));")
db.execute("CREATE TABLE IF NOT EXISTS daum_toonInfo (toon_id VARCHAR(255), toon_writer VARCHAR(255), toon_intro VARCHAR(255));")

a = Mechanize.new

localhost = "192.168.90.128"
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

  db.execute("SELECT toon_id FROM naver_tmpList ORDER BY toon_id;") do |_toon_id|
    tmpList.push(_toon_id[0])
  end

  # 연재
  resp = a.get "http://comic.naver.com/webtoon/weekday.nhn"

  str = '<span id="table_toggle_button" style="float: left; cursor: pointer; text-decoration: underline; color: ' + btnColor["link"] + ';" onclick="show_table();">완결 웹툰</span>'
  str << '<span id="site_button" style="float: right; cursor: pointer; color: ' + btnColor["link"] + ';" onclick="site_change(\'daum\');"><u>D</u>aum</span><br/>'
  str << '<table id="current_toonlist">'
  str << '<tr style="font-weight: bold;">'
  str << '<td>월</td><td>화</td><td>수</td><td>목</td><td>금</td><td>토</td><td>일</td>'
  str << '</tr>'
  str << '<tr valign="top">'

  count = 0

  resp.search('//div[@class="list_area daily_all"]').each {|r|
    r.search('div/div[@class="col_inner"]').each {|v|
      str << '<td>'
      v.search('ul/li/div[@class="thumb"]').each {|v1|
        _a = v1.search('a')[0]
        _titleId = $1.to_i if _a.attributes["href"].value =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
        _title = _a.attributes["title"].value
        _up = (_a.search('em').length != 0) ? '(UP)' : ''
        _new = (_a.search('img').length > 1) ? '(NEW)' : ''
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList[_titleId] = 1 if tmpList.index(_titleId) == nil

        str << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}#{_new}#{_up}\" onclick=\"viewToon(#{_titleId});\">#{_title}<small>#{_new}#{_up}</small></div>"
        count += 1
      }
      count = 0
      str << '</td>'
    }
    str << '</td></tr></table>'
  }

  # 완결
  resp = a.get 'http://comic.naver.com/webtoon/finish.nhn'

  str << '<table id="finished_toonlist" style="display: none;"><tr valign="top">'
  str_td = ["<td>", "<td>", "<td>", "<td>", "<td>", "<td>", "<td>"]

  count = 0

  resp.search('//div[@class="thumb"]').each {|r|
    _a = r.search('a')[0]
    _titleId = $1.to_i if _a.attributes["href"].value =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
    _title = _a.attributes["title"].value
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = 1 if tmpList.index(_titleId) == nil

    str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
    count += 1
  }
  (0...str_td.length).each {|i|
    str << str_td[i] + "</td>"
  }
  str << '</tr></table><br/><br/>'

  # reqList 처리
  str << '<script>'
  reqList.each do |v|
    str << "$.get(\"/cgi-bin/webtoon/displayToon.cgi?site=naver&id=#{v}&num=1\");"
    db.execute("INSERT INTO naver_tmpList (toon_id) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM naver_tmpList WHERE toon_id=?);", v, v)
  end
  str << 'resizeWidth();'

  # toonlist background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    str << '$("#loading").html("<big><b> Loading</b></big>");'
    str << '$("#loading").css("display", "inline");'
    str << 'loading(10);'
    str << '$.get("/cgi-bin/webtoon/putToonColor.cgi", {site: "naver"}, function (data) { $("#loading").css("display", "none");$("#display_area").html(data); });'
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

  db.execute("SELECT toon_id, toon_num, toon_date FROM daum_numList ORDER BY toon_num_idx;") do |_toon_id, _toon_num, _toon_date|
    numList[_toon_id] = [] if numList[_toon_id] == nil
    numList[_toon_id].push(_toon_num)
    dateList[_toon_id] = [] if dateList[_toon_id] == nil
    dateList[_toon_id].push(_toon_date)
  end
  db.execute("SELECT toon_id, toon_writer, toon_intro FROM daum_toonInfo;") do |_toon_id, _toon_writer, _toon_intro|
    toonInfo[_toon_id] = [_toon_writer, _toon_intro]
  end

  # 연재
  resp = a.get "http://cartoon.media.daum.net/webtoon/week"

  str = '<span id="table_toggle_button" style="float: left; cursor: pointer; text-decoration: underline; color: ' + btnColor["link"] + ';" onclick="show_table();">완결 웹툰</span>'
  str << '<span id="site_button" style="float: right; cursor: pointer; color: ' + btnColor["link"] + ';" onclick="site_change(\'naver\');"><u>N</u>aver</span><br/>'
  str << '<table id="current_toonlist">'
  str << '<tr style="font-weight: bold;">'
  str << '<td>월</td><td>화</td><td>수</td><td>목</td><td>금</td><td>토</td><td>일</td>'
  str << '</tr>'
  str << '<tr valign="top">'

  count = 0

  resp.search('//div[@class="area_toonlist area_bg"]').each {|r|
    r.search('div/div[@class="bg_line"]').each {|v|
      str << '<td>'
      v.search('ul/li/a').each {|v1|
        _titleId = $1 if v1.attributes["href"].value =~ /\/webtoon\/view\/(.+)$/
        _title = v1.attributes["title"].value
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList[_titleId] = 0 if numList[_titleId] == nil or dateList[_titleId] == nil or dateList[_titleId].include?(nil) or toonInfo[_titleId] == nil or toonInfo[_titleId].include?(nil)

        str << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon('#{_titleId}');\">#{_title}</div>"
        count += 1
      }
      count = 0
      str << '</td>'
    }
    str << '</td></tr></table>'
  }

  # 완결
  resp = a.get 'http://cartoon.media.daum.net/webtoon/finished'

  str << '<table id="finished_toonlist" style="display: none;"><tr valign="top">'
  str_td = ["<td>", "<td>", "<td>", "<td>", "<td>", "<td>", "<td>"]

  count = 0

  resp.search('//ul[@class="list_type_image list_incount list_year"]/li').each {|r|
    next if r.attributes["class"].value == "line_dot"
    _titleId = $1 if r.search('a')[0].attributes["href"].value =~ /\/webtoon\/view\/(.+)$/
    _title = r.search('p')[0].attributes["title"].value
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = -1 if numList[_titleId] == nil or dateList[_titleId] == nil or dateList[_titleId].include?(nil) or toonInfo[_titleId] == nil or toonInfo[_titleId].include?(nil)

    str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon('#{_titleId}');\">#{_title}</div>"
    count += 1
  }
  (0...str_td.length).each {|i|
    str << str_td[i] + "</td>"
  }
  str << '</tr></table><br/><br/>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    numList[v] = []
    dateList[v] = []
    num_resp = a.get("http://#{localhost}/cgi-bin/webtoon/getNum.cgi?site=daum&id=#{v}").body.strip.split("\n").map(&:strip)
    num_resp[0].split().map {|item|
      numList[v].push(item.split(",")[0].to_i)
      dateList[v].push(item.split(",")[1])
    }
    toonInfo[v] = [num_resp[1], num_resp[2].gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;")]

    str << "$.get(\"/cgi-bin/webtoon/displayToon.cgi?site=daum&id=#{v}&num=#{numList[v][0]}\");"
    (0...numList[v].length).each {|i|
      db.execute("UPDATE daum_numList SET toon_num=?, toon_date=? WHERE toon_id=? AND toon_num_idx=?;", numList[v][i], dateList[v][i], v, i)
      db.execute("INSERT INTO daum_numList (toon_id, toon_num_idx, toon_num, toon_date) SELECT ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_numList WHERE toon_id=? AND toon_num_idx=?);", v, i, numList[v][i], dateList[v][i], v, i)
      db.execute("UPDATE daum_toonInfo SET toon_writer=?, toon_intro=? WHERE toon_id=?;", toonInfo[v][0], toonInfo[v][1], v)
      db.execute("INSERT INTO daum_toonInfo (toon_id, toon_writer, toon_intro) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_toonInfo WHERE toon_id=?);", v, toonInfo[v][0], toonInfo[v][1], v)
    }
    if reqList[v] == -1 # 완결
      lastNum[v] = numList[v][-1]
      finishToon.push(v)
      db.execute("UPDATE daum_lastNum SET toon_num=? WHERE toon_id=?;", numList[v][-1], v)
      db.execute("INSERT INTO daum_lastNum (toon_id, toon_num) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_lastNum WHERE toon_id=?);", v, numList[v][-1], v)
    end
  end
  str << 'resizeWidth();'

  str << "numList={#{numList.keys.map {|v| "'#{v}':[#{numList[v].join(",")}]"}.join(",")}};"
  str << "dateList={#{dateList.keys.map {|v| "'#{v}':['#{dateList[v].join("','")}']"}.join(",")}};"
  str << "toonInfo={#{toonInfo.keys.map {|v| "'#{v}':['#{toonInfo[v].join("','")}']"}.join(",")}};"
  str << "finishToon=[#{finishToon.map {|v| "'#{v}'"}.join(",")}];"
  
  # toon background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    str << '$("#loading").html("<big><b> Loading</b></big>");'
    str << '$("#loading").css("display", "inline");'
    str << 'loading(10);'
    str << '$.get("/cgi-bin/webtoon/putToonColor.cgi", {site: "daum"}, function (data) { $("#loading").css("display", "none");$("#display_area").html(data); });'
  end

  str << '</script>'

  puts str
end

db.close
