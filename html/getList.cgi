#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'
require 'pg'

def db_init(db, site)
  case site
  when "naver"
    db.exec("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
    db.exec("CREATE TABLE IF NOT EXISTS naver_lastnum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER NOT NULL);")
    db.exec("CREATE TABLE IF NOT EXISTS naver_tmplist (toon_id INTEGER PRIMARY KEY);")
  when "daum"
    db.exec("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id VARCHAR NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
    db.exec("CREATE TABLE IF NOT EXISTS daum_lastnum (toon_id VARCHAR PRIMARY KEY, toon_num INTEGER NOT NULL);")
    db.exec("CREATE TABLE IF NOT EXISTS daum_numlist (toon_id VARCHAR NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num INTEGER NOT NULL, toon_date VARCHAR(10), UNIQUE (toon_id, toon_num_idx));")
    db.exec("CREATE TABLE IF NOT EXISTS daum_tooninfo (toon_id VARCHAR PRIMARY KEY, toon_writer VARCHAR, toon_intro VARCHAR);")
  when "yahoo"
    db.exec("CREATE TABLE IF NOT EXISTS yahoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
    db.exec("CREATE TABLE IF NOT EXISTS yahoo_lastnum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER NOT NULL);")
    db.exec("CREATE TABLE IF NOT EXISTS yahoo_numlist (toon_id INTEGER NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (toon_id, toon_num_idx));")
    db.exec("CREATE TABLE IF NOT EXISTS yahoo_tooninfo (toon_id INTEGER PRIMARY KEY, toon_title VARCHAR, toon_intro VARCHAR);")
  when "stoo"
    db.exec("CREATE TABLE IF NOT EXISTS stoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num VARCHAR NOT NULL, UNIQUE (id, toon_id));")
    db.exec("CREATE TABLE IF NOT EXISTS stoo_lastnum (toon_id INTEGER PRIMARY KEY, toon_num VARCHAR NOT NULL);")
    db.exec("CREATE TABLE IF NOT EXISTS stoo_numlist (toon_id INTEGER NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num VARCHAR NOT NULL, UNIQUE (toon_id, toon_num_idx));")
    db.exec("CREATE TABLE IF NOT EXISTS stoo_tooninfo (toon_id INTEGER PRIMARY KEY, toon_writer VARCHAR, toon_intro VARCHAR);")
  end
end

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = cgi.params["site"][0]

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))

db = PGconn.open(:dbname => "yous")
db.exec("CREATE TABLE IF NOT EXISTS usr (id SERIAL PRIMARY KEY, usr_id VARCHAR NOT NULL UNIQUE, usr_pw VARCHAR NOT NULL);")
db_init(db, site)

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

  db.exec("SELECT toon_id FROM naver_tmplist ORDER BY toon_id;").each do |row|
    _toon_id = row["toon_id"].to_i
    tmpList.push(_toon_id)
  end

  # 연재
  resp = a.get "http://comic.naver.com/webtoon/weekday.nhn"

  str = '<span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>'
  str << '<span class="site_button" onclick="site_change(\'stoo\');"><u>S</u>too</span>'
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
        _titleId = $1.to_i if _a.attr("href") =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
        _title = _a.attr("title")
        _up = (_a.search('em').length != 0) ? '(UP)' : ''
        _new = (_a.search('img').length > 1) ? '(NEW)' : ''
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList[_titleId] = 1 unless tmpList.include? _titleId

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
    _titleId = $1.to_i if _a.attr("href") =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
    _title = _a.attr("title")
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = 1 unless tmpList.include? _titleId

    str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
    count += 1
  end

  (0...str_td.length).each {|i| str << str_td[i] + "</td>" }
  str << '</tr></table><br/><br/>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    str << "$.get(\"/displayToon?site=naver&id=#{v}&num=1\");"
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

    str << "toonBM={#{toonBM.keys.map {|v| "#{v}:#{toonBM[v]}"}.join(",")}};"
    str << "lastNum={#{lastNum.keys.map {|v| "#{v}:#{lastNum[v]}"}.join(",")}};"
    str << "finishToon=[#{finishToon.join(",")}];"

    str << '$("#loading").html(" Loading");'
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

  db.exec("SELECT toon_id, toon_num FROM daum_lastnum;").each do |row|
    _toon_id = row["toon_id"]
    _toon_num = row["toon_num"].to_i
    lastNum[_toon_id] = _toon_num
    finishToon.push(_toon_id)
  end

  db.exec("SELECT toon_id, toon_num, toon_date FROM daum_numlist ORDER BY toon_num_idx;").each do |row|
    _toon_id = row["toon_id"]
    _toon_num = row["toon_num"]
    _toon_date = row["toon_date"]
    tmpList.push(_toon_id) unless tmpList.include? _toon_id
    if _toon_num.nil? or _toon_date.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    else
      numList[_toon_id] = [] if numList[_toon_id].nil?
      numList[_toon_id].push(_toon_num.to_i)
      dateList[_toon_id] = [] if dateList[_toon_id].nil?
      dateList[_toon_id].push(_toon_date)
    end
  end

  db.exec("SELECT toon_id, toon_writer, toon_intro FROM daum_tooninfo;").each do |row|
    _toon_id = row["toon_id"]
    _toon_writer = row["toon_writer"]
    _toon_intro = row["toon_intro"]
    if _toon_writer.nil? or _toon_intro.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    else
      toonInfo[_toon_id] = [_toon_writer, _toon_intro]
    end
  end

  # 연재
  resp = a.get "http://cartoon.media.daum.net/webtoon/week"

  str = '<span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>'
  str << '<span class="site_button" onclick="site_change(\'stoo\');"><u>S</u>too</span>'
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
        _titleId = $1 if v1.attr("href") =~ /\/webtoon\/view\/(.+)$/
        _title = v1.attr("title")
        _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

        reqList[_titleId] = 0 unless tmpList.include? _titleId

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
    _titleId = $1 if r.at('a').attr("href") =~ /\/webtoon\/view\/(.+)$/
    _title = r.at('p').attr("title")
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = -1 unless tmpList.include? _titleId

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
    num_resp = a.get("http://#{localhost}/getNum?site=daum&id=#{v}").body

    # 로그인 필요한 웹툰
    next if num_resp == ""

    num_resp = num_resp.split("\n").map {|item| item.strip.force_encoding("UTF-8") }
    num_resp[0].split()[1..-1].map {|item|
      numList[v].push(item.split(",")[0].to_i)
      dateList[v].push(item.split(",")[1])
    }
    toonInfo[v] = [num_resp[1], (num_resp[2].nil?) ? nil : num_resp[2].gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;")]

    str << "$.get(\"/displayToon?site=daum&id=#{v}&num=#{numList[v][0]}\");"
    (0...numList[v].length).each do |i|
      db.exec("UPDATE daum_numlist SET toon_num=$1, toon_date=$2::VARCHAR WHERE toon_id=$3::VARCHAR AND toon_num_idx=$4;", [numList[v][i], dateList[v][i], v, i])
      db.exec("INSERT INTO daum_numlist (toon_id, toon_num_idx, toon_num, toon_date) SELECT $1::VARCHAR, $2, $3, $4::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM daum_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, i, numList[v][i], dateList[v][i]])
      db.exec("UPDATE daum_tooninfo SET toon_writer=$1::VARCHAR, toon_intro=$2::VARCHAR WHERE toon_id=$3;", [toonInfo[v][0], toonInfo[v][1], v])
      db.exec("INSERT INTO daum_tooninfo (toon_id, toon_writer, toon_intro) SELECT $1::VARCHAR, $2::VARCHAR, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM daum_tooninfo WHERE toon_id=$1);", [v, toonInfo[v][0], toonInfo[v][1]])
    end
    if reqList[v] == -1 # 완결
      db.exec("UPDATE daum_lastnum SET toon_num=$1 WHERE toon_id=$2::VARCHAR;", [numList[v][-1], v])
      db.exec("INSERT INTO daum_lastnum (toon_id, toon_num) SELECT $1::VARCHAR, $2 WHERE NOT EXISTS (SELECT 1 FROM daum_lastnum WHERE toon_id=$1);", [v, numList[v][-1]])
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

    db.exec("SELECT toon_id, toon_num FROM daum_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
      _toon_id = row["toon_id"]
      _toon_num = row["toon_num"].to_i
      toonBM[_toon_id] = _toon_num
    end

    str << "toonBM={#{toonBM.keys.map {|v| "'#{v}':#{toonBM[v]}"}.join(",")}};"

    str << '$("#loading").html(" Loading");'
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

  db.exec("SELECT toon_id, toon_num FROM yahoo_lastnum;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    lastNum[_toon_id] = _toon_num
    finishToon.push(_toon_id)
  end

  db.exec("SELECT toon_id, toon_num FROM yahoo_numlist ORDER BY toon_num_idx;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"]
    tmpList.push(_toon_id) unless tmpList.include? _toon_id
    if _toon_num.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    else
      numList[_toon_id] = [] if numList[_toon_id].nil?
      numList[_toon_id].push(_toon_num.to_i)
    end
  end

  db.exec("SELECT toon_id, toon_title, toon_intro FROM yahoo_tooninfo;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_title = row["toon_title"]
    _toon_intro = row["toon_intro"]
    reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0 if _toon_intro.nil? or _toon_title.nil?
    toonInfo[_toon_id] = [_toon_title, _toon_intro]
  end

  # 연재
  resp = a.get "http://kr.news.yahoo.com/service/cartoon/shelllist.htm?linkid=webtoon&kind=cont"

  str = '<span class="table_toggle_button" id="table_toggle_button1" style="display: none;" onclick="show_table(1);">연재 웹툰</span>'
  str << '<span class="table_toggle_button" id="table_toggle_button2" onclick="show_table(2);">완결 웹툰</span>'
  str << '<span class="table_toggle_button" id="table_toggle_button3" onclick="show_table(3);">특집 웹툰</span>'
  str << '<span class="site_button" onclick="site_change(\'stoo\');"><u>S</u>too</span>'
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
      _titleId = $1.to_i if r.at('a[2]').attr("href") =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      if not tmpList.include? _titleId
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
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attr("href")
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
      _titleId = $1.to_i if r.at('a[2]').attr("href") =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      if not tmpList.include? _titleId
        reqList[_titleId] = -1
        if toonInfo[_titleId].nil?
          toonInfo[_titleId] = [_title, nil]
        else
          toonInfo[_titleId][0] = _title
        end
      end
      if (not finishToon.include? _titleId) and reqList[_titleId].nil?
        finishToon.push(_titleId)
        reqList[_titleId] = -1
      end

      str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
      count += 1
    end

    if resp.search('//div[@id="pa0"]/span[@class="nxt"]').length > 0
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attr("href")
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
      _titleId = $1.to_i if r.at('a[2]').attr("href") =~ /http:\/\/kr\.news\.yahoo\.com\/service\/cartoon\/shelllist.htm\?linkid=toon_series&work_idx=(\d+)/
      _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

      if not tmpList.include? _titleId
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
      resp = a.get resp.at('//div[@id="pa0"]/span[@class="nxt"]/a').attr("href")
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
    num_resp = a.get("http://#{localhost}/getNum?site=yahoo&id=#{v}").body.split("\n").map(&:strip)
    numList[v] = num_resp[0].split()[1..-1].map(&:to_i)
    toonInfo[v][1] = (num_resp[1].nil?) ? nil : num_resp[1].force_encoding("UTF-8").gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;").gsub(/&lt;br\/?&gt;/, "<br/>")
    lastNum[v] = numList[v][-1]

    str << "$.get(\"/displayToon?site=yahoo&id=#{v}&num=#{numList[v][0]}\");"
    (0...numList[v].length).each do |i|
      db.exec("UPDATE yahoo_numlist SET toon_num=$1 WHERE toon_id=$2 AND toon_num_idx=$3;", [numList[v][i], v, i])
      db.exec("INSERT INTO yahoo_numlist (toon_id, toon_num_idx, toon_num) SELECT $1, $2, $3 WHERE NOT EXISTS (SELECT 1 FROM yahoo_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, i, numList[v][i]])
      db.exec("UPDATE yahoo_tooninfo SET toon_title=$1::VARCHAR, toon_intro=$2::VARCHAR WHERE toon_id=$3;", [toonInfo[v][0], toonInfo[v][1], v])
      db.exec("INSERT INTO yahoo_tooninfo (toon_id, toon_title, toon_intro) SELECT $1, $2::VARCHAR, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM yahoo_tooninfo WHERE toon_id=$1);", [v, toonInfo[v][0], toonInfo[v][1]])
    end
    if reqList[v] == -1 # 완결
      db.exec("UPDATE yahoo_lastnum SET toon_num=$1 WHERE toon_id=$2;", [numList[v][-1], v])
      db.exec("INSERT INTO yahoo_lastnum (toon_id, toon_num) SELECT $1, $2 WHERE NOT EXISTS (SELECT 1 FROM yahoo_lastnum WHERE toon_id=$1);", [v, numList[v][-1]])
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

    db.exec("SELECT toon_id, toon_num FROM yahoo_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
      _toon_id = row["toon_id"].to_i
      _toon_num = row["toon_num"].to_i
      toonBM[_toon_id] = _toon_num
    end

    str << "toonBM={#{toonBM.keys.map {|v| "#{v}:#{toonBM[v]}"}.join(",")}};"

    str << '$("#loading").html(" Loading");'
    str << '$("#loading").css("display", "inline");'
    str << 'loading(10);'
    str << "putToonColor();"
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

  db.exec("SELECT toon_id, toon_num FROM stoo_numlist ORDER BY toon_num_idx;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"]
    tmpList.push(_toon_id) unless tmpList.include?(_toon_id)
    if _toon_num.nil?
      reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0
    else
      numList[_toon_id] = [] if numList[_toon_id].nil?
      numList[_toon_id].push(_toon_num.to_i)
    end
  end

  db.exec("SELECT toon_id, toon_writer, toon_intro FROM stoo_tooninfo;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_writer = row["toon_writer"]
    _toon_intro = row["toon_intro"]
    reqList[_toon_id] = (finishToon.include? _toon_id) ? -1 : 0 if _toon_writer.nil? or _toon_intro.nil?
    toonInfo[_toon_id] = [_toon_writer, _toon_intro]
  end

  resp = a.get "http://stoo.asiae.co.kr/cartoon/"

  # 연재
  str = '<span class="table_toggle_button" onclick="show_table();">완결 웹툰</span>'
  str << '<span class="site_button" onclick="site_change(\'yahoo\');"><u>Y</u>ahoo</span>'
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

  resp.search('//ul[@id="serialcm"]/li').each do |r|
    _a = r.at('dl/dt[@class="desc"]/a')
    _titleId = $1.to_i if _a.attr("href") =~ /\/cartoon\/ctlist\.htm\?sc1=cartoon&sc2=ing&sc3=(\d+)/
    _title = _a.attr("title").gsub(/<br\/?>/, " ")
    _color = (count[day] % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = 1 unless tmpList.include? _titleId

    str_td[day] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
    count[day] += 1
    day = (day + 1) % 7
  end

  str_td.each do |v|
    str << v + "</td>"
  end
  str << '</tr></table>'

  # 완결
  str << '<table id="finished_toonlist" class="toonlist" style="display: none;"><tr valign="top">'
  str_td = ["<td>", "<td>", "<td>", "<td>", "<td>", "<td>", "<td>"]

  count = 0

  resp.search('//ul[@id="endcm"]/li').each do |r|
    _a = r.at('dl/dt[@class="desc"]/a')
    _titleId = $1.to_i if _a.attr("href") =~ /\/cartoon\/ctlist\.htm\?sc1=cartoon&sc2=end&sc3=(\d+)/
    _title = _a.attr("title").gsub(/<br\/?>/, " ")
    _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]

    reqList[_titleId] = -1 unless tmpList.include? _titleId

    str_td[count % 7] << "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
    count += 1
  end

  str_td.each do |v|
    str << v + "</td>"
  end
  str << '</tr></table><br/><br/>'

  # reqList 처리
  str << '<script>'
  reqList.keys.each do |v|
    num_resp = a.get("http://#{localhost}/getNum?site=stoo&id=#{v}").body.split("\n").map(&:strip)
    numList[v] = num_resp[0].split()[1..-1]
    toonInfo[v] = [num_resp[1].force_encoding("UTF-8"), (num_resp[2].nil?) ? nil : num_resp[2].force_encoding("UTF-8").gsub('"', "&quot;").gsub("'", "&#39;").gsub("<", "&lt;").gsub(">", "&gt;").gsub(/&lt;br\/?&gt;/, "<br/>")]
    lastNum[v] = numList[v][-1]

    str << "$.get(\"/displayToon?site=yahoo&id=#{v}&num=#{numList[v][0]}\");"
    (0...numList[v].length).each do |i|
      db.exec("UPDATE stoo_numlist SET toon_num=$1::VARCHAR WHERE toon_id=$2 AND toon_num_idx=$3;", [numList[v][i], v, i])
      db.exec("INSERT INTO stoo_numlist (toon_id, toon_num_idx, toon_num) SELECT $1, $2, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM stoo_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, i, numList[v][i]])
      db.exec("UPDATE stoo_tooninfo SET toon_writer=$1::VARCHAR, toon_intro=$2::VARCHAR WHERE toon_id=$3;", [toonInfo[v][0], toonInfo[v][1], v])
      db.exec("INSERT INTO stoo_tooninfo (toon_id, toon_writer, toon_intro) SELECT $1, $2::VARCHAR, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM stoo_tooninfo WHERE toon_id=$1);", [v, toonInfo[v][0], toonInfo[v][1]])
    end
    if reqList[v] == -1 # 완결
      db.exec("UPDATE stoo_lastnum SET toon_num=$1::VARCHAR WHERE toon_id=$2;", [numList[v][-1], v])
      db.exec("INSERT INTO stoo_lastnum (toon_id, toon_num) SELECT $1, $2::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM yahoo_lastnum WHERE toon_id=$1);", [v, numList[v][-1]])
    end
  end
  str << 'resizeWidth();'

  # 웹툰 정보 입력
  str << "numList={#{numList.keys.map {|v| "#{v}:['#{numList[v].join("','")}']"}.join(",")}};"
  str << "toonInfo={#{toonInfo.keys.map {|v| "#{v}:['#{toonInfo[v].join("','")}']"}.join(",")}};"
  str << "lastNum={#{lastNum.keys.map {|v| "#{v}:'#{lastNum[v]}'"}.join(",")}};"
  str << "finishToon=[#{finishToon.join(",")}];"

  # toonlist background-color 처리
  if session["user_id"] != nil and session["user_id"] != ""
    toonBM = Hash.new
    lastNum = Hash.new
    finishToon = []

    db.exec("SELECT toon_id, toon_num FROM stoo_bm WHERE id=$1;", [session["user_id"]]).each do |row|
      _toon_id = row["toon_id"].to_i
      _toon_num = row["toon_num"]
      toonBM[_toon_id] = _toon_num
      db.exec("SELECT toon_num FROM stoo_lastnum WHERE toon_id=$1;", [_toon_id]).each do |sec_row|
        _lastNum = sec_row["toon_num"]
        lastNum[_toon_id] = _lastNum
        finishToon.push(_toon_id)
      end
    end

    str << "toonBM={#{toonBM.keys.map {|v| "#{v}:'#{toonBM[v]}'"}.join(",")}};"
    str << "lastNum={#{lastNum.keys.map {|v| "#{v}:'#{lastNum[v]}'"}.join(",")}};"
    str << "finishToon=[#{finishToon.join(",")}];"

    str << '$("#loading").html(" Loading");'
    str << '$("#loading").css("display", "inline");'
    str << 'loading(10);'
    str << "putToonColor();"
  end

  str << '</script>'

  puts str
end

db.close
