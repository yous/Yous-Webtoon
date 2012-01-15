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
finish = cgi.params["finish"][0]
day_BM = cgi.params["day_BM"][0].split(",")

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))

db = SQLite3::Database.new(File.join(File.dirname(__FILE__), "/../db/webtoon.db"))
db.execute("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER, toon_id INTEGER, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS naver_lastNum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER, toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_lastNum (toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_numList (toon_id VARCHAR(255), toon_num_idx INTEGER, toon_num INTEGER, toon_date VARCHAR(10));")

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
  day_BM = day_BM.map(&:to_i)
  toonBM = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new

  db.execute("SELECT toon_id, toon_num FROM naver_bm WHERE id=? ORDER BY toon_id;", session["user_id"]) do |_toon_id, _toon_num|
    toonBM[_toon_id] = _toon_num
    db.execute("SELECT toon_num FROM naver_lastNum WHERE toon_id=?;", _toon_id) do |_lastNum|
      lastNum[_toon_id] = _lastNum[0]
      finishToon.push(_toon_id)
    end
  end

  col_str = ""
  str = "<script>"

  if finish == "n"
    day_BM.each do |v|
      resp = a.get("http://#{localhost}/getNum?site=naver&id=#{v}").body.split(" ")
      lastNum[v] = resp[1].to_i
      if toonBM[v] < lastNum[v]
        reqList[v] = toonBM[v] + 1
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_up"]}');"
      else
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved"]}');"
      end
    end
  else
    day_BM.each do |v|
      unless finishToon.include?(v)
        resp = a.get("http://#{localhost}/getNum?site=naver&id=#{v}").body.split(" ")
        lastNum[v] = resp[1].to_i
        db.execute("INSERT INTO naver_lastNum (toon_id, toon_num) VALUES (?, ?);", v, lastNum[v])
        finishToon.push(v)
      end
      if toonBM[v] < lastNum[v]
        reqList[v] = toonBM[v] + 1
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_up"]}');"
      else
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_finish"]}');"
      end
    end
  end

  str << col_str

  str << "lastNum={#{lastNum.keys.map {|v| "#{v}:#{lastNum[v]}"}.join(",")}};"
  str << "finishToon=[#{finishToon.join(",")}];"

  # reqList 처리
  reqList.keys.each do |v|
    str << "$.get(\"/displayToon?site=naver&id=#{v}&num=#{reqList[v]}\");"
  end

  str << "</script>"

  puts str

# Daum 웹툰
elsif site == "daum"
  toonBM = Hash.new
  numList = Hash.new
  dateList = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new

  db.execute("SELECT toon_id, toon_num, toon_date FROM daum_numList ORDER BY toon_num_idx;") do |_toon_id, _toon_num, _toon_date|
    numList[_toon_id] = [] if numList[_toon_id] == nil
    numList[_toon_id].push(_toon_num)
    dateList[_toon_id] = [] if dateList[_toon_id] == nil
    dateList[_toon_id].push(_toon_date)
  end

  db.execute("SELECT toon_id, toon_num FROM daum_bm WHERE id=? ORDER BY toon_id;", session["user_id"]) do |_toon_id, _toon_num|
    toonBM[_toon_id] = _toon_num
    db.execute("SELECT toon_num FROM daum_lastNum WHERE toon_id=?;", _toon_id) do |_lastNum|
      lastNum[_toon_id] = _lastNum[0]
      finishToon.push(_toon_id)
    end
  end

  col_str = ""
  str = "<script>"

  if finish == "n"
    day_BM.each do |v|
      if finishToon.include?(v)
        finishToon.delete(v)
        str << "finishToon.splice(finishToon.indexOf('#{v}'),1);"
        db.execute("DELETE FROM daum_lastNum WHERE toon_id=?;", v)
      end
      resp = a.get("http://#{localhost}/getNum?site=daum&id=#{v}").body.strip.split("\n")[0].split()
      numList[v] = []
      dateList[v] = []
      resp.drop(1).each do |item|
        numList[v].push(item.split(",")[0].to_i)
        dateList[v].push(item.split(",")[1])
      end
      lastNum[v] = numList[v][-1]
      str << "numList['#{v}']=[#{numList[v].join(",")}];"
      str << "lastNum['#{v}']=#{lastNum[v]};"
      str << "dateList['#{v}']=['#{dateList[v].join("','")}'];"
      if toonBM[v] < lastNum[v]
        reqList[v] = numList[v][numList[v].index(toonBM[v]) + 1]
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_up"]}');"
      else
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved"]}');"
      end
    end
  else
    day_BM.each do |v|
      unless finishToon.include?(v)
        resp = a.get("http://#{localhost}/getNum?site=daum&id=#{v}").body.strip.split("\n")[0].split()
        numList[v] = resp.drop(1).map(&:to_i)
        lastNum[v] = numList[v][-1]
        str << "numList['#{v}']=[#{numList[v].join(",")}];"
        str << "lastNum['#{v}']=#{lastNum[v]};"
        db.execute("INSERT INTO daum_lastNum (toon_id, toon_num) VALUES (?, ?);", v, lastNum[v])
        finishToon.push(v)
        str << "finishToon.push('#{v}');"
      end
      if toonBM[v] < lastNum[v]
        reqList[v] = numList[v][numList[v].index(toonBM[v]) + 1]
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_up"]}');"
      else
        col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_finish"]}');"
      end
    end
  end

  str << col_str

  # reqList 처리
  reqList.keys.each do |v|
    str << "$.get(\"/displayToon?site=daum&id=#{v}&num=#{reqList[v]}\");"
  end

  str << "</script>"

  puts str
end
