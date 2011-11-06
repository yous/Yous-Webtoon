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
db.execute("CREATE TABLE IF NOT EXISTS daum_numList (toon_id VARCHAR(255), toon_num_idx INTEGER, toon_num INTEGER);")

a = Mechanize.new

btnColor = {
  "buttonA" => "#FAFAFA",
  "buttonB" => "#EAEAEA",
  "saved" => "#88DD88",
  "saved_up" => "#DD8888",
  "saved_finish" => "#888888",
  "link" => "#0066CC"
}

# Naver 웹툰
if site == "naver" then
  toonBM = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new

  tmpList = []
  db.execute("SELECT toon_id FROM naver_tmpList;") do |_toon_id|
    tmpList.push(_toon_id[0])
  end

  if session["user_id"] != nil and session["user_id"] != ""
    db.execute("SELECT toon_id, toon_num FROM naver_bm WHERE id=?;", session["user_id"]) do |_toon_id, _toon_num|
      toonBM[_toon_id] = _toon_num
      db.execute("SELECT toon_num FROM naver_lastNum WHERE toon_id=?;", _toon_id) do |_lastNum|
        lastNum[_toon_id] = _lastNum[0]
        finishToon.push(_toon_id)
      end
    end
  end

  str = "<script>"
  str += "toonBM={ "
  toonBM.keys.each {|v|
    str += "#{v}:#{toonBM[v]},"
    lastNum[v] = a.get("http://192.168.92.128/cgi-bin/webtoon/getNum.cgi?site=naver&id=#{v}").body.to_i if lastNum[v] == nil
    reqList[v] = toonBM[v] + 1 if toonBM[v] < lastNum[v]
  }
  str = str[0...(str.length - 1)] + "};"

  str += "lastNum={ "
  lastNum.keys.each {|v|
    str += "#{v}:#{lastNum[v]},"
  }
  str = str[0...(str.length - 1)] + "};"

  str += "finishToon=[#{finishToon.join(",")}];"

  str += "</script>"

  # 연재
  resp = a.get "http://comic.naver.com/webtoon/weekday.nhn"

  str += '<span id="table_toggle_button" style="float: left; cursor: pointer; text-decoration: underline; color: ' + btnColor["link"] + ';" onclick="show_table();">완결 웹툰</span>'
  str += '<span id="site_button" style="float: right; cursor: pointer; text-decoration: underline; color: ' + btnColor["link"] + ';" onclick="site_change(\'daum\');">Daum</span><br/>'
  str += '<table id="current_toonlist">'
  str += '<tr style="font-weight: bold;">'
  str += '<td>월</td>'
  str += '<td>화</td>'
  str += '<td>수</td>'
  str += '<td>목</td>'
  str += '<td>금</td>'
  str += '<td>토</td>'
  str += '<td>일</td>'
  str += '</tr>'
  str += '<tr valign="top">'

  count = 0

  resp.search('//div[@class="list_area daily_all"]').each {|r|
    r.search('div/div[@class="col_inner"]').each {|v|
      str += '<td>'
      v.search('ul/li/div[@class="thumb"]').each {|v1|
        _a = v1.search('a')[0]
        _titleId = $1.to_i if _a.attributes["href"].value =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
        _title = _a.attributes["title"].value
        _up = (_a.search('em').length != 0) ? '(UP)' : ''
        _new = (_a.search('img').length > 1) ? '(NEW)' : ''

        reqList[_titleId] = 1 if tmpList.index(_titleId) == nil

        if toonBM[_titleId] then
          _color = (toonBM[_titleId] == lastNum[_titleId]) ? btnColor["saved"] : btnColor["saved_up"]
        else
          _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]
        end

        str += "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}#{_new}#{_up}\" onclick=\"viewToon(#{_titleId});\">#{_title}<small>#{_new}#{_up}</small></div>"
        count += 1
      }
      count = 0
      str += '</td>'
    }
    str += '</td></tr></table>'
  }

  # 완결
  resp = a.get 'http://comic.naver.com/webtoon/finish.nhn'

  str += '<table id="finished_toonlist" style="display: none;"><tr valign="top">'
  str_td = ['<td>'] * 7

  count = 0

  resp.search('//div[@class="thumb"]').each {|r|
    _a = r.search('a')[0]
    _titleId = $1.to_i if _a.attributes["href"].value =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
    _title = _a.attributes["title"].value

    reqList[_titleId] = 1 if tmpList.index(_titleId) == nil

    if toonBM[_titleId] != nil then
      _color = (toonBM[_titleId] == lastNum[_titleId]) ? btnColor["saved_finish"] : btnColor["saved_up"]
    else
      _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]
    end

    str_td[count % 7] += "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon(#{_titleId});\">#{_title}</div>"
    count += 1
  }
  (0...str_td.length).each {|i|
    str_td[i] += '</td>'
    str += str_td[i]
  }
  str += '</tr></table><br/><br/>'

  str += '<script>'
  reqList.keys.each do |v|
    str += "$.get(\"/cgi-bin/webtoon/displayToon.cgi?site=naver&id=#{v}&num=#{reqList[v]}\");"
    if reqList[v] == 1 then
      check = true
      db.execute("SELECT toon_id FROM naver_tmpList WHERE toon_id=?;", v) do |_toon_id|
        check = false
      end
      if check
        db.execute("INSERT INTO naver_tmpList (toon_id) VALUES (?);", v)
      end
    end
  end
  str += 'resizeWidth();</script>'

  puts str
# Daum 웹툰
elsif site == "daum" then
  toonBM = Hash.new
  numList = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new

  db.execute("SELECT toon_id, toon_num FROM daum_numList ORDER BY toon_num_idx;") do |_toon_id, _toon_num|
    numList[_toon_id] = [] if numList[_toon_id] == nil
    numList[_toon_id].push(_toon_num)
  end

  if session["user_id"] != nil and session["user_id"] != ""
    db.execute("SELECT toon_id, toon_num FROM daum_bm WHERE id=?;", session["user_id"]) do |_toon_id, _toon_num|
      toonBM[_toon_id] = _toon_num
      db.execute("SELECT toon_num FROM daum_lastNum WHERE toon_id=?;", _toon_id) do |_lastNum|
        lastNum[_toon_id] = _lastNum[0]
        finishToon.push(_toon_id)
      end
    end
  end

  str = "<script>"
  str += "toonBM={ "
  toonBM.keys.each {|v|
    str += "\'#{v}\':#{toonBM[v]},"
    numList[v] = a.get("http://192.168.92.128/cgi-bin/webtoon/getNum.cgi?site=daum&id=#{v}").body.split().map(&:to_i) if finishToon.index(v) == nil
    lastNum[v] = numList[v][-1]
    reqList[v] = numList[v][numList[v].index(toonBM[v]) + 1] if toonBM[v] < lastNum[v]
  }
  str = str[0...(str.length - 1)] + "};"

  str += "numList={ "
  numList.keys.each {|v|
    str += "'#{v}':[#{numList[v].join(',')}],"
  }
  str = str[0...(str.length - 1)] + "};"

  str += "lastNum={ "
  lastNum.keys.each {|v|
    str += "'#{v}':#{lastNum[v]},"
  }
  str = str[0...(str.length - 1)] + "};"

  str += "finishToon=[ "
  finishToon.each {|v|
    str += "'#{v}',"
  }
  str = str[0...(str.length - 1)] + "];"

  str += "</script>"

  # 연재
  resp = a.get "http://cartoon.media.daum.net/webtoon/week"

  str += '<span id="table_toggle_button" style="float: left; cursor: pointer; text-decoration: underline; color: ' + btnColor["link"] + ';" onclick="show_table();">완결 웹툰</span>'
  str += '<span id="site_button" style="float: right; cursor: pointer; text-decoration: underline; color: ' + btnColor["link"] + ';" onclick="site_change(\'naver\');">Naver</span><br/>'
  str += '<table id="current_toonlist">'
  str += '<tr style="font-weight: bold;">'
  str += '<td>월</td>'
  str += '<td>화</td>'
  str += '<td>수</td>'
  str += '<td>목</td>'
  str += '<td>금</td>'
  str += '<td>토</td>'
  str += '<td>일</td>'
  str += '</tr>'
  str += '<tr valign="top">'

  count = 0

  resp.search('//div[@class="area_toonlist area_bg"]').each {|r|
    r.search('div/div[@class="bg_line"]').each {|v|
      str += '<td>'
      v.search('ul/li/a').each {|v1|
        _titleId = $1 if v1.attributes["href"].value =~ /\/webtoon\/view\/(.+)$/
        _title = v1.attributes["title"].value

        reqList[_titleId] = 0 if numList[_titleId] == nil

        if toonBM[_titleId] then
          _color = (toonBM[_titleId] == lastNum[_titleId]) ? btnColor["saved"] : btnColor["saved_up"]
        else
          _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]
        end

        str += "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"current_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon('#{_titleId}');\">#{_title}</div>"
        count += 1
      }
      count = 0
      str += '</td>'
    }
    str += '</td></tr></table>'
  }

  # 완결
  resp = a.get 'http://cartoon.media.daum.net/webtoon/finished'

  str += '<table id="finished_toonlist" style="display: none;"><tr valign="top">'
  str_td = ['<td>'] * 7

  count = 0

  resp.search('//ul[@class="list_type_image list_incount list_year"]/li').each {|r|
    next if r.attributes["class"].value == "line_dot"
    _titleId = $1 if r.search('a')[0].attributes["href"].value =~ /\/webtoon\/view\/(.+)$/
    _title = r.search('p')[0].attributes["title"].value

    reqList[_titleId] = -1 if numList[_titleId] == nil

    if toonBM[_titleId] != nil then
      _color = (toonBM[_titleId] == lastNum[_titleId]) ? btnColor["saved_finish"] : btnColor["saved_up"]
    else
      _color = (count % 2 == 1) ? btnColor["buttonA"] : btnColor["buttonB"]
    end

    str_td[count % 7] += "<div id=\"#{_titleId}\" name=\"#{_titleId}\" class=\"finished_toon\" style=\"background-color: #{_color}; padding: 1px 0px 1px 0px; cursor: default;\" title=\"#{_title}\" onclick=\"viewToon('#{_titleId}');\">#{_title}</div>"
    count += 1
  }
  (0...str_td.length).each {|i|
    str_td[i] += '</td>'
    str += str_td[i]
  }
  str += '</tr></table><br/><br/>'

  str += '<script>'
  reqList.keys.each do |v|
    if reqList[v] <= 0 then
      _numList = a.get("http://192.168.92.128/cgi-bin/webtoon/getNum.cgi?site=daum&id=#{v}").body.split().map(&:to_i)
      str += "numList['#{v}']=[#{_numList.join(',')}];"
      (0..._numList.length).each {|i|
        check = true
        db.execute("SELECT toon_num FROM daum_numList WHERE toon_id=? AND toon_num_idx=?;", v, i) do |_toon_num|
          if _toon_num[0] != numList[i]
            db.execute("UPDATE daum_numList SET toon_num=? WHERE toon_id=? AND toon_num_idx=?;", numList[i], v, i)
          end
          check = false
        end
        if check
          db.execute("INSERT INTO daum_numList (toon_id, toon_num_idx, toon_num) VALUES (?, ?, ?);", v, i, numList[i])
        end
      }
      if reqList[v] == -1
        str += "finishToon.push('#{v}');"
        db.execute("SELECT toon_num FROM daum_lastNum WHERE toon_id=?;", v) do |_toon_num|
          check = true
          if _toon_num[0] != numList[-1]
            db.execute("UPDATE daum_lastNum SET toon_num=? WHERE toon_id=?;", numList[-1], v)
            check = false
          end
          if check
            db.execute("INSERT INTO daum_lastNum (toon_id, toon_num) VALUES (?, ?);", v, numList[-1])
          end
        end
      end
      str += "$.get(\"/cgi-bin/webtoon/displayToon.cgi?site=daum&id=#{v}&num=#{_numList[0]}\");"
    else
      str += "$.get(\"/cgi-bin/webtoon/displayToon.cgi?site=daum&id=#{v}&num=#{reqList[v]}\");"
    end
  end
  str += 'resizeWidth();</script>'

  puts str
end
