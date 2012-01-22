#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'
require 'sqlite3'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = cgi.params["site"][0]

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))

db = SQLite3::Database.new("../db/webtoon.db")
db.execute("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER, toon_id INTEGER, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS naver_lastNum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS naver_tmpList (toon_id INTEGER PRIMARY KEY);")
db.execute("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER, toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_lastNum (toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_numList (toon_id VARCHAR(255), toon_num_idx INTEGER, toon_num INTEGER, toon_date VARCHAR(10));")
db.execute("CREATE TABLE IF NOT EXISTS daum_toonInfo (toon_id VARCHAR(255), toon_writer VARCHAR(255), toon_intro VARCHAR(255));")
db.execute("CREATE TABLE IF NOT EXISTS yahoo_bm (id INTEGER, toon_id INTEGER, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS yahoo_lastNum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS yahoo_numList (toon_id INTEGER, toon_num_idx INTEGER, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS yahoo_toonInfo (toon_id INTEGER, toon_title VARCHAR(255), toon_intro VARCHAR(255));")

a = Mechanize.new

localhost = "192.168.90.128:8888"
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
  reqList = Hash.new
  tmpList = []

  db.execute("SELECT toon_id FROM naver_tmpList ORDER BY toon_id;") do |_toon_id|
    tmpList.push(_toon_id[0])
  end

  # 연재
  resp = a.get "http://comic.naver.com/webtoon/weekday.nhn"

  str = '<span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>'
  str << '<span class="site_button" onclick="site_change(\'yahoo\');"><u>Y</u>ahoo</span>'
  str << '<span class="site_button" onclick="site_change(\'daum\');"><u>D</u>aum</span><br/>'
  str << '<table id="current_toonlist" class="toonlist">'
  str << '<tr style="font-weight: bold;">'
  str << '<td>월<span class="refreshBtn" onclick="putToonColor(0);">Re</span></td>'
  str << '<td>화<span class="refreshBtn" onclick="putToonColor(1);">Re</span></td>'
  str << '<td>수<span class="refreshBtn" onclick="putToonColor(2);">Re</span></td>'
  str << '<td>목<span class="refreshBtn" onclick="putToonColor(3);">Re</span></td>'
  str << '<td>금<span class="refreshBtn" onclick="putToonColor(4);">Re</span></td>'
  str << '<td>토<span class="refreshBtn" onclick="putToonColor(5);">Re</span></td>'
  str << '<td>일<span class="refreshBtn" onclick="putToonColor(6);">Re</span></td>'
  str << '</tr>'
  str << '<tr valign="top">'

  count = 0

  resp.search('//div[@class="list_area daily_all"]').each do |r|
    day = 0
    r.search('div/div[@class="col_inner"]').each do |v|
      str << "<td id=\"day#{day}\">"
      v.search('ul/li/div[@class="thumb"]').each do |v1|
        _a = v1.at('a')
        _titleId = $1.to_i if _a.attributes["href"].value =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
        _title = _a.attributes["title"].value
        _up = (_a.search('em').length != 0) ? '(UP)' : ''
        _new = (_a.search('img').length > 1) ? '(NEW)' : ''
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList[_titleId] = 1 if tmpList.index(_titleId) == nil

        str << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}#{_new}#{_up}\" onclick=\"viewToon(#{_titleId});\">#{_title}<small>#{_new}#{_up}</small></div>"
        count += 1
      end
      count = 0
      str << '</td>'
      day += 1
    end
    str << '</td></tr></table>'
  end

  # 완결
  resp = a.get 'http://comic.naver.com/webtoon/finish.nhn'

  str << '<table id="finished_toonlist" class="toonlist" style="display: none;"><tr valign="top">'
  str_td = ["<td>", "<td>", "<td>", "<td>", "<td>", "<td>", "<td>"]

  count = 0

  resp.search('//div[@class="thumb"]').each do |r|
    _a = r.at('a')
    _titleId = $1.to_i if _a.attributes["href"].value =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
    _title = _a.attributes["title"].value
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = 1 if tmpList.index(_titleId) == nil

    str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
    count += 1
  end

  (0...str_td.length).each {|i| str << str_td[i] + "</td>" }
  str << '</tr></table><br/><br/>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    str << "$.get(\"/displayToon?site=naver&id=#{v}&num=1\");"
    db.execute("INSERT INTO naver_tmpList (toon_id) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM naver_tmpList WHERE toon_id=?);", v, v)
  end
  str << 'resizeWidth();'

  # toonlist background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new
    lastNum = Hash.new
    finishToon = []

    db.execute("SELECT toon_id, toon_num FROM naver_bm WHERE id=?;", session["user_id"]) do |_toon_id, _toon_num|
      toonBM[_toon_id] = _toon_num
      db.execute("SELECT toon_num FROM naver_lastNum WHERE toon_id=?;", _toon_id) do |_lastNum|
        lastNum[_toon_id] = _lastNum[0]
        finishToon.push(_toon_id)
      end
    end

    str << "toonBM={#{toonBM.keys.map {|v| "#{v}:#{toonBM[v]}"}.join(",")}};"
    str << "lastNum={#{lastNum.keys.map {|v| "#{v}:#{lastNum[v]}"}.join(",")}};"
    str << "finishToon=[#{finishToon.join(",")}];"

    str << '$("#loading").html("<big><b> Loading</b></big>");'
    str << '$("#loading").css("display", "inline");'
    str << 'loading(10);'
    str << "putToonColor();"
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

  db.execute("SELECT toon_id FROM daum_numList ORDER BY toon_num_idx;") do |_toon_id|
    tmpList.push(_toon_id[0]) unless tmpList.include?(_toon_id[0])
  end

  db.execute("SELECT toon_id, toon_num FROM daum_lastNum;") do |_toon_id, _lastNum|
    lastNum[_toon_id] = _lastNum
    finishToon.push(_toon_id)
  end

  db.execute("SELECT toon_id, toon_num, toon_date FROM daum_numList ORDER BY toon_num_idx;") do |_toon_id, _toon_num, _toon_date|
    if _toon_num.nil? or _toon_date.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    else
      numList[_toon_id] = [] if numList[_toon_id] == nil
      numList[_toon_id].push(_toon_num)
      dateList[_toon_id] = [] if dateList[_toon_id] == nil
      dateList[_toon_id].push(_toon_date)
    end
  end

  db.execute("SELECT toon_id, toon_writer, toon_intro FROM daum_toonInfo;") do |_toon_id, _toon_writer, _toon_intro|
    if _toon_writer.nil? or _toon_intro.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    else
      toonInfo[_toon_id] = [_toon_writer, _toon_intro]
    end
  end

  # 연재
  resp = a.get "http://cartoon.media.daum.net/webtoon/week"

  str = '<span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>'
  str << '<span class="site_button" onclick="site_change(\'yahoo\');"><u>Y</u>ahoo</span>'
  str << '<span class="site_button" onclick="site_change(\'naver\');"><u>N</u>aver</span><br/>'
  str << '<table id="current_toonlist" class="toonlist">'
  str << '<tr style="font-weight: bold;">'
  str << '<td>월<span class="refreshBtn" onclick="putToonColor(0);">Re</span></td>'
  str << '<td>화<span class="refreshBtn" onclick="putToonColor(1);">Re</span></td>'
  str << '<td>수<span class="refreshBtn" onclick="putToonColor(2);">Re</span></td>'
  str << '<td>목<span class="refreshBtn" onclick="putToonColor(3);">Re</span></td>'
  str << '<td>금<span class="refreshBtn" onclick="putToonColor(4);">Re</span></td>'
  str << '<td>토<span class="refreshBtn" onclick="putToonColor(5);">Re</span></td>'
  str << '<td>일<span class="refreshBtn" onclick="putToonColor(6);">Re</span></td>'
  str << '</tr>'
  str << '<tr valign="top">'

  count = 0

  resp.search('//div[@class="area_toonlist area_bg"]').each do |r|
    day = 0
    r.search('div/div[@class="bg_line"]').each do |v|
      str << "<td id=\"day#{day}\">"
      v.search('ul/li/a').each do |v1|
        _titleId = $1 if v1.attributes["href"].value =~ /\/webtoon\/view\/(.+)$/
        _title = v1.attributes["title"].value
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList[_titleId] = 0 if tmpList.index(_titleId) == nil

        str << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon('#{_titleId}');\">#{_title}</div>"
        count += 1
      end
      count = 0
      str << '</td>'
      day += 1
    end
    str << '</td></tr></table>'
  end

  # 완결
  resp = a.get 'http://cartoon.media.daum.net/webtoon/finished'

  str << '<table id="finished_toonlist" class="toonlist" style="display: none;"><tr valign="top">'
  str_td = ["<td>", "<td>", "<td>", "<td>", "<td>", "<td>", "<td>"]

  count = 0

  resp.search('//ul[@class="list_type_image list_incount list_year"]/li').each do |r|
    next if r.attributes["class"].value == "line_dot"
    _titleId = $1 if r.at('a').attributes["href"].value =~ /\/webtoon\/view\/(.+)$/
    _title = r.at('p').attributes["title"].value
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = -1 if tmpList.index(_titleId) == nil

    str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon('#{_titleId}');\">#{_title}</div>"
    count += 1
  end

  (0...str_td.length).each {|i| str << str_td[i] + "</td>" }
  str << '</tr></table><br/><br/>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    numList[v] = []
    dateList[v] = []
    num_resp = a.get("http://#{localhost}/getNum?site=daum&id=#{v}").body.strip.split("\n").map {|item| item.strip.force_encoding("UTF-8") }
    num_resp[0].split()[1..-1].map {|item|
      numList[v].push(item.split(",")[0].to_i)
      dateList[v].push(item.split(",")[1])
    }
    toonInfo[v] = [num_resp[1], (num_resp[2].nil?) ? nil : num_resp[2].gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;")]

    str << "$.get(\"/displayToon?site=daum&id=#{v}&num=#{numList[v][0]}\");"
    (0...numList[v].length).each do |i|
      db.execute("UPDATE daum_numList SET toon_num=?, toon_date=? WHERE toon_id=? AND toon_num_idx=?;", numList[v][i], dateList[v][i], v, i)
      db.execute("INSERT INTO daum_numList (toon_id, toon_num_idx, toon_num, toon_date) SELECT ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_numList WHERE toon_id=? AND toon_num_idx=?);", v, i, numList[v][i], dateList[v][i], v, i)
      db.execute("UPDATE daum_toonInfo SET toon_writer=?, toon_intro=? WHERE toon_id=?;", toonInfo[v][0], toonInfo[v][1], v)
      db.execute("INSERT INTO daum_toonInfo (toon_id, toon_writer, toon_intro) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_toonInfo WHERE toon_id=?);", v, toonInfo[v][0], toonInfo[v][1], v)
    end
    if reqList[v] == -1 # 완결
      db.execute("UPDATE daum_lastNum SET toon_num=? WHERE toon_id=?;", numList[v][-1], v)
      db.execute("INSERT INTO daum_lastNum (toon_id, toon_num) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_lastNum WHERE toon_id=?);", v, numList[v][-1], v)
    end
  end
  str << 'resizeWidth();'

  # 웹툰 정보 입력
  str << "numList={#{numList.keys.map {|v| "'#{v}':[#{numList[v].join(",")}]"}.join(",")}};"
  str << "dateList={#{dateList.keys.map {|v| "'#{v}':['#{dateList[v].join("','")}']"}.join(",")}};"
  str << "toonInfo={#{toonInfo.keys.map {|v| "'#{v}':['#{toonInfo[v].join("','")}']"}.join(",")}};"
  str << "lastNum={#{lastNum.keys.map {|v| "'#{v}':#{lastNum[v]}"}.join(",")}};"
  str << "finishToon=[#{finishToon.map {|v| "'#{v}'"}.join(",")}];"

  # toon background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new

    db.execute("SELECT toon_id, toon_num FROM daum_bm WHERE id=? ORDER BY toon_id;", session["user_id"]) do |_toon_id, _toon_num|
      toonBM[_toon_id] = _toon_num
    end

    str << "toonBM={#{toonBM.keys.map {|v| "'#{v}':#{toonBM[v]}"}.join(",")}};"

    str << '$("#loading").html("<big><b> Loading</b></big>");'
    str << '$("#loading").css("display", "inline");'
    str << 'loading(10);'
    str << "putToonColor();"
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

  db.execute("SELECT toon_id FROM yahoo_numList ORDER BY toon_num_idx;") do |_toon_id|
    tmpList.push(_toon_id[0]) unless tmpList.include?(_toon_id[0])
  end

  db.execute("SELECT toon_id, toon_num FROM yahoo_lastNum;") do |_toon_id, _lastNum|
    lastNum[_toon_id] = _lastNum
    finishToon.push(_toon_id)
  end

  db.execute("SELECT toon_id, toon_num FROM yahoo_numList ORDER BY toon_num_idx;") do |_toon_id, _toon_num|
    if _toon_num.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    else
      numList[_toon_id] = [] if numList[_toon_id].nil?
      numList[_toon_id].push(_toon_num)
    end
  end

  db.execute("SELECT toon_id, toon_title, toon_intro FROM yahoo_toonInfo;") do |_toon_id, _toon_title, _toon_intro|
    if _toon_intro.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    elsif _toon_title.nil?
      toonInfo[_toon_id] = [nil, _toon_intro]
    else
      toonInfo[_toon_id] = [_toon_title, _toon_intro]
    end
  end

  # 연재
  resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=webtoon&kind=cont"

  str = '<span class="table_toggle_button" id="table_toggle_button1" style="display: none;" onclick="show_table(1);">연재 웹툰</span>'
  str << '<span class="table_toggle_button" id="table_toggle_button2" onclick="show_table(2);">완결 웹툰</span>'
  str << '<span class="table_toggle_button" id="table_toggle_button3" onclick="show_table(3);">특집 웹툰</span>'
  str << '<span class="site_button" onclick="site_change(\'daum\');"><u>D</u>aum</span>'
  str << '<span class="site_button" onclick="site_change(\'naver\');"><u>N</u>aver</span><br/>'
  str << '<table id="current_toonlist" class="toonlist">'
  str << '<tr style="font-weight: bold;">'
  str << '<td><span class="refreshBtn" onclick="putToonColor(0);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(1);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(2);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(3);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(4);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(5);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(6);">Re</span></td>'
  str << '</tr>'
  str << '<tr valign="top">'
  str_td = ['<td id="day0">', '<td id="day1">', '<td id="day2">', '<td id="day3">', '<td id="day4">', '<td id="day5">', '<td id="day6">']

  count = [0, 0, 0, 0, 0, 0, 0]
  day = 0

  while true
    resp.search('//div[@id="cll"]/ol/li').each do |r|
      _title = r.at('a[2]').inner_html.encode("UTF-8").strip
      _titleId = $1.to_i if r.at('a[2]').attributes["href"].value =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      if tmpList.index(_titleId).nil?
        reqList[_titleId] = 0
        if toonInfo[_titleId].nil?
          toonInfo[_titleId] = [_title, nil]
        else
          toonInfo[_titleId][0] = _title
        end
      end

      str_td[day] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
      count[day] += 1
      day = (day + 1) % 7
    end

    if resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attributes["href"].value
    else
      break
    end
  end

  str_td.each do |v|
    str << v + "</td>"
  end

  str << '</tr></table>'

  # 완결
  resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=webtoon&kind=done"

  str << '<table id="finished_toonlist" class="toonlist" style="display: none;"><tr valign="top">'
  str_td = ["<td>", "<td>", "<td>", "<td>", "<td>", "<td>", "<td>"]

  count = 0

  while true
    resp.search('//div[@id="cll"]/ol/li').each do |r|
      _title = r.at('a[2]').inner_html.encode("UTF-8").strip.force_encoding("UTF-8")
      _titleId = $1.to_i if r.at('a[2]').attributes["href"].value =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      if tmpList.index(_titleId).nil?
        reqList[_titleId] = -1
        if toonInfo[_titleId].nil?
          toonInfo[_titleId] = [_title, nil]
        else
          toonInfo[_titleId][0] = _title
        end
      end
      if finishToon.index(_titleId).nil? and reqList[_titleId].nil?
        finishToon.push(_titleId)
        reqList[_titleId] = -1
      end

      str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
      count += 1
    end

    if resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attributes["href"].value
    else
      break
    end
  end

  str_td.each do |v|
    str << v + "</td>"
  end

  str << '</tr></table>'

  # 특집
  resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=webtoon&kind=special"

  str << '<table id="special_toonlist" class="toonlist" style="display: none;">'
  str << '<tr style="font-weight: bold;">'
  str << '<td><span class="refreshBtn" onclick="putToonColor(7);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(8);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(9);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(10);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(11);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(12);">Re</span></td>'
  str << '<td><span class="refreshBtn" onclick="putToonColor(13);">Re</span></td>'
  str << '</tr>'
  str << '<tr valign="top">'
  str_td = ['<td id="day7">', '<td id="day8">', '<td id="day9">', '<td id="day10">', '<td id="day11">', '<td id="day12">', '<td id="day13">']

  count = [0, 0, 0, 0, 0, 0, 0]
  day = 0

  while true
    resp.search('//div[@id="cll"]/ol/li').each do |r|
      _title = r.at('a[2]').inner_html.encode("UTF-8").strip
      _titleId = $1.to_i if r.at('a[2]').attributes["href"].value =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      if tmpList.index(_titleId).nil?
        reqList[_titleId] = 0
        if toonInfo[_titleId].nil?
          toonInfo[_titleId] = [_title, nil]
        else
          toonInfo[_titleId][0] = _title
        end
      end

      str_td[day] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
      count[day] += 1
      day = (day + 1) % 7
    end

    if resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attributes["href"].value
    else
      break
    end
  end

  str_td.each do |v|
    str << v + "</td>"
  end

  str << '</tr></table><br/><br/>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    num_resp = a.get("http://#{localhost}/getNum?site=yahoo&id=#{v}").body.strip.split("\n").map(&:strip)
    numList[v] = num_resp[0].split()[1..-1].map(&:to_i)
    toonInfo[v][1] = (num_resp[1].nil?) ? nil : num_resp[1].force_encoding("UTF-8").gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;").gsub(/&lt;br\/?&gt;/, "<br/>")
    lastNum[v] = numList[v][-1]

    str << "$.get(\"/displayToon?site=yahoo&id=#{v}&num=#{numList[v][0]}\");"
    (0...numList[v].length).each do |i|
      db.execute("UPDATE yahoo_numList SET toon_num=? WHERE toon_id=? AND toon_num_idx=?;", numList[v][i], v, i)
      db.execute("INSERT INTO yahoo_numList (toon_id, toon_num_idx, toon_num) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM yahoo_numList WHERE toon_id=? AND toon_num_idx=?);", v, i, numList[v][i], v, i)
      db.execute("UPDATE yahoo_toonInfo SET toon_title=?, toon_intro=? WHERE toon_id=?;", toonInfo[v][0], toonInfo[v][1], v)
      db.execute("INSERT INTO yahoo_toonInfo (toon_id, toon_title, toon_intro) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM yahoo_toonInfo WHERE toon_id=?);", v, toonInfo[v][0], toonInfo[v][1], v)
    end
    if reqList[v] == -1 # 완결
      db.execute("UPDATE yahoo_lastNum SET toon_num=? WHERE toon_id=?;", numList[v][-1], v)
      db.execute("INSERT INTO yahoo_lastNum (toon_id, toon_num) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM yahoo_lastNum WHERE toon_id=?);", v, numList[v][-1], v)
    end
  end
  str << 'resizeWidth();'

  # 웹툰 정보 입력
  str << "numList={#{numList.keys.map {|v| "#{v}:[#{numList[v].join(",")}]"}.join(",")}};"
  str << "toonInfo={#{toonInfo.keys.map {|v| "#{v}:['#{toonInfo[v].join("','")}']"}.join(",")}};"
  str << "lastNum={#{lastNum.keys.map {|v| "#{v}:#{lastNum[v]}"}.join(",")}};"
  str << "finishToon=[#{finishToon.join(",")}];"

  # toon background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new

    db.execute("SELECT toon_id, toon_num FROM yahoo_bm WHERE id=? ORDER BY toon_id;", session["user_id"]) do |_toon_id, _toon_num|
      toonBM[_toon_id] = _toon_num
    end

    str << "toonBM={#{toonBM.keys.map {|v| "#{v}:#{toonBM[v]}"}.join(",")}};"

    str << '$("#loading").html("<big><b> Loading</b></big>");'
    str << '$("#loading").css("display", "inline");'
    str << 'loading(10);'
    str << "putToonColor();"
  end

  str << '</script>'

  puts str
end

db.close
