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
db.execute("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER, toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_lastNum (toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_numList (toon_id VARCHAR(255), toon_num_idx INTEGER, toon_num INTEGER, toon_date VARCHAR(10));")

a = Mechanize.new

localhost = "192.168.90.128"
btnColor = {
  "buttonA" => "#FAFAFA",
  "buttonB" => "#EAEAEA",
  "saved" => "#88DD88", # rgb(136, 221, 136)
  "saved_up" => "#DD8888",
  "saved_finish" => "#888888",
  "link" => "#0066CC"
}

# Naver 웹툰
if site == "naver"
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

  str << "toonBM={#{toonBM.keys.map {|v|
    if not finishToon.include?(v)
      resp = a.get("http://#{localhost}/cgi-bin/webtoon/getNum.cgi?site=naver&id=#{v}").body.split(" ")
      lastNum[v] = resp[1].to_i
      if resp[0] == "y"
        db.execute("INSERT INTO naver_lastNum (toon_id, toon_num) VALUES (?, ?);", v, lastNum[v])
        finishToon.push(v)
      end
    end
    if toonBM[v] < lastNum[v]
      reqList[v] = toonBM[v] + 1
      col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_up"]}');"
    elsif finishToon.include?(v)
      col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_finish"]}');"
    else
      col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved"]}');"
    end
    "#{v}:#{toonBM[v]}"
  }.join(",")}};"

  str << col_str

  str << "lastNum={#{lastNum.keys.map {|v| "#{v}:#{lastNum[v]}"}.join(",")}};"
  str << "finishToon=[#{finishToon.join(",")}];"
  str << "id=null;num=null;"

  # reqList 처리
  reqList.keys.each do |v|
    str << "$.get(\"/cgi-bin/webtoon/displayToon.cgi?site=naver&id=#{v}&num=#{reqList[v]}\");"
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

  str << "toonBM={#{toonBM.keys.map {|v|
    if not finishToon.include?(v)
      resp = a.get("http://#{localhost}/cgi-bin/webtoon/getNum.cgi?site=daum&id=#{v}").body.strip.split("\n")[0].split()
      numList[v] = resp.drop(1).map(&:to_i)
      lastNum[v] = numList[v][-1]
      if resp[0] == "y"
        db.execute("INSERT INTO daum_lastNum (toon_id, toon_num) VALUES (?, ?);", v, lastNum[v])
        finishToon.push(v)
      end
    end
    if toonBM[v] < lastNum[v]
      reqList[v] = numList[v][numList[v].index(toonBM[v]) + 1]
      col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_up"]}');"
    elsif finishToon.include?(v)
      col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved_finish"]}');"
    else
      col_str << "$('div[name=#{v}]').css('background-color', '#{btnColor["saved"]}');"
    end
    "'#{v}':#{toonBM[v]}"
  }.join(",")}};"

  str << col_str

  str << numList.keys.map {|v| "numList['#{v}']=[#{numList[v].join(",")}];"}.join()
  str << dateList.keys.map {|v| "dateList['#{v}']=['#{dateList[v].join("','")}'];"}.join()
  str << lastNum.keys.map {|v| "lastNum['#{v}']=#{lastNum[v]};"}.join()
  str << finishToon.map {|v| "finishToon.push('#{v}');"}.join()
  str << "id=null;num=null;"

  # reqList 처리
  reqList.keys.each do |v|
    str << "$.get(\"/cgi-bin/webtoon/displayToon.cgi?site=daum&id=#{v}&num=#{reqList[v]}\");"
  end

  str << "</script>"

  puts str
end
