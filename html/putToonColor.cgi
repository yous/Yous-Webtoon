#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'
require 'pg'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = cgi.params["site"][0]
finish = cgi.params["finish"][0]
day_BM = cgi.params["day_BM"][0].split(",")

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))

db = PGconn.open(:dbname => "yous")
db.exec("CREATE TABLE naver_bm (id INTEGER, toon_id INTEGER, toon_num INTEGER);") rescue nil
db.exec("CREATE TABLE naver_lastnum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER);") rescue nil
db.exec("CREATE TABLE daum_bm (id INTEGER, toon_id VARCHAR, toon_num INTEGER);") rescue nil
db.exec("CREATE TABLE daum_lastnum (toon_id VARCHAR, toon_num INTEGER);") rescue nil
db.exec("CREATE TABLE daum_numlist (toon_id VARCHAR, toon_num_idx INTEGER, toon_num INTEGER, toon_date VARCHAR(10));") rescue nil

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

  db.exec("SELECT toon_id, toon_num FROM naver_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    toonBM[_toon_id] = _toon_num
    db.exec("SELECT toon_num FROM naver_lastnum WHERE toon_id=$1;", [_toon_id]).each do |sec_row|
      _lastNum = sec_row["toon_num"].to_i
      lastNum[_toon_id] = _lastNum
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
        db.exec("INSERT INTO naver_lastnum (toon_id, toon_num) VALUES ($1, $2);", [v, lastNum[v]])
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

  db.exec("SELECT toon_id, toon_num, toon_date FROM daum_numlist ORDER BY toon_num_idx;").each do |row|
    _toon_id = row["toon_id"]
    _toon_num = row["toon_num"].to_i
    _toon_date = row["toon_date"]
    numList[_toon_id] = [] if numList[_toon_id] == nil
    numList[_toon_id].push(_toon_num)
    dateList[_toon_id] = [] if dateList[_toon_id] == nil
    dateList[_toon_id].push(_toon_date)
  end

  db.exec("SELECT toon_id, toon_num FROM daum_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
    _toon_id = row["toon_id"]
    _toon_num = row["toon_num"].to_i
    toonBM[_toon_id] = _toon_num
    db.exec("SELECT toon_num FROM daum_lastnum WHERE toon_id=$1::VARCHAR;", [_toon_id]).each do |sec_row|
      _lastNum = sec_row["toon_num"].to_i
      lastNum[_toon_id] = _lastNum
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
        db.exec("DELETE FROM daum_lastnum WHERE toon_id=$1::VARCHAR;", [v])
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
        (0...numList[v].length).each do |i|
          db.exec("UPDATE daum_numlist SET toon_num=$1, toon_date=$2::VARCHAR WHERE toon_id=$3::VARCHAR AND toon_num_idx=$4;", [numList[v][i], dateList[v][i], v, i])
          db.exec("INSERT INTO daum_numlist (toon_id, toon_num_idx, toon_num, toon_date) SELECT $1::VARCHAR, $2, $3, $4::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM daum_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, i, numList[v][i], dateList[v][i]])
        end
        db.exec("INSERT INTO daum_lastnum (toon_id, toon_num) VALUES ($1::VARCHAR, $2);", [v, lastNum[v]])
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

# Yahoo 웹툰
elsif site == "yahoo"
  day_BM = day_BM.map(&:to_i)
  toonBM = Hash.new
  numList = Hash.new
  lastNum = Hash.new
  finishToon = []
  reqList = Hash.new

  db.exec("SELECT toon_id, toon_num FROM yahoo_numlist ORDER BY toon_num_idx;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    numList[_toon_id] = [] if numList[_toon_id] == nil
    numList[_toon_id].push(_toon_num)
  end

  db.exec("SELECT toon_id, toon_num FROM yahoo_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    toonBM[_toon_id] = _toon_num
    db.exec("SELECT toon_num FROM yahoo_lastnum WHERE toon_id=$1;", [_toon_id]).each do |sec_row|
      _lastNum = sec_row["toon_num"].to_i
      lastNum[_toon_id] = _lastNum
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
        db.exec("DELETE FROM yahoo_lastnum WHERE toon_id=$1;", [v])
      end
      resp = a.get("http://#{localhost}/getNum?site=yahoo&id=#{v}").body.strip.split("\n")[0].split()
      numList[v] = resp.drop(1).map(&:to_i)
      lastNum[v] = numList[v][-1]
      str << "numList[#{v}]=[#{numList[v].join(",")}];"
      str << "lastNum[#{v}]=#{lastNum[v]};"
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
        resp = a.get("http://#{localhost}/getNum?site=yahoo&id=#{v}").body.strip.split("\n")[0].split()
        numList[v] = resp.drop(1).map(&:to_i)
        lastNum[v] = numList[v][-1]
        str << "numList[#{v}]=[#{numList[v].join(",")}];"
        str << "lastNum[#{v}]=#{lastNum[v]};"
        (0...numList[v].length).each do |i|
          db.exec("UPDATE yahoo_numlist SET toon_num=$1 WHERE toon_id=$2 AND toon_num_idx=$3;", [numList[v][i], v, i])
          db.exec("INSERT INTO yahoo_numlist (toon_id, toon_num_idx, toon_num) SELECT $1, $2, $3 WHERE NOT EXISTS (SELECT 1 FROM yahoo_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [v, i, numList[v][i]])
        end
        db.exec("INSERT INTO yahoo_lastnum (toon_id, toon_num) VALUES ($1, $2);", [v, lastNum[v]])
        finishToon.push(v)
        str << "finishToon.push(#{v});"
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
    str << "$.get(\"/displayToon?site=yahoo&id=#{v}&num=#{reqList[v]}\");"
  end

  str << "</script>"

  puts str
end
