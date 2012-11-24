#!/usr/local/rvm/wrappers/ruby-1.9.3-p125@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'
require 'pg'
require 'json'

puts "Content-Type: application/json; charset=utf-8\n\n"

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

# Naver 웹툰
if site == "naver"
  toonBM = Hash.new

  db.exec("SELECT toon_id, toon_num FROM naver_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    toonBM[_toon_id] = _toon_num
  end

  puts toonBM.to_json

# Daum 웹툰
elsif site == "daum"
  toonBM = Hash.new

  db.exec("SELECT toon_id, toon_num FROM daum_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
    _toon_id = row["toon_id"]
    _toon_num = row["toon_num"].to_i
    toonBM[_toon_id] = _toon_num
  end

  puts toonBM.to_json

# Yahoo 웹툰
elsif site == "yahoo"
  day_BM = day_BM.map(&:to_i)
  toonBM = Hash.new
  numList = Hash.new
  lastNum = Hash.new
  finishToon = []

  db.exec("SELECT toon_id, toon_num FROM yahoo_numlist ORDER BY toon_id, toon_num_idx;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"].to_i
    numList[_toon_id] = [] if numList[_toon_id].nil?
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
      if finishToon.include? v
        finishToon.delete v
        str << "finishToon.splice(finishToon.indexOf('#{v}'),1);"
        db.exec("DELETE FROM yahoo_lastnum WHERE toon_id=$1;", [v])
      end
      resp = a.get("http://localhost:#{port}/getNum.cgi?site=yahoo&id=#{v}").body
      numList[v] = resp.split()[1..-1].map(&:to_i)
      lastNum[v] = numList[v][-1]
      str << <<-HTML
        numList[#{v}]=[#{numList[v].join(",")}];
        lastNum[#{v}]=#{lastNum[v]};
      HTML
      if toonBM[v] < lastNum[v]
        col_str << "$('div[name=#{v}]').addClass('saved_update');"
      else
        col_str << "$('div[name=#{v}]').addClass('saved_finish');"
      end
    end
  else
    day_BM.each do |v|
      if toonBM[v] < lastNum[v]
        col_str << "$('div[name=#{v}]').addClass('saved_update');"
      else
        col_str << "$('div[name=#{v}]').addClass('saved_finish');"
      end
    end
  end

  str << col_str
  str << "</script>"

  puts str

# Stoo 웹툰
elsif site == "stoo"
  day_BM = day_BM.map(&:to_i)
  toonBM = Hash.new
  numList = Hash.new
  lastNum = Hash.new
  finishToon = []

  db.exec("SELECT toon_id, toon_num FROM stoo_numlist ORDER BY toon_id, toon_num_idx;").each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"]
    numList[_toon_id] = [] if numList[_toon_id].nil?
    numList[_toon_id].push(_toon_num)
  end

  db.exec("SELECT toon_id, toon_num FROM stoo_bm WHERE id=$1 ORDER BY toon_id;", [session["user_id"]]).each do |row|
    _toon_id = row["toon_id"].to_i
    _toon_num = row["toon_num"]
    toonBM[_toon_id] = _toon_num
    db.exec("SELECT toon_num FROM stoo_lastnum WHERE toon_id=$1;", [_toon_id]).each do |sec_row|
      _lastNum = sec_row["toon_num"]
      lastNum[_toon_id] = _lastNum
      finishToon.push(_toon_id)
    end
  end

  col_str = ""
  str = "<script>"

  if finish == "n"
    day_BM.each do |v|
      if finishToon.include? v
        finishToon.delete v
        str << "finishToon.splice(finishToon.indexOf(#{v}),1);"
        db.exec("DELETE FROM stoo_lastnum WHERE toon_id=$1;", [v])
      end
      resp = a.get("http://localhost:#{port}/getNum.cgi?site=stoo&id=#{v}").body
      numList[v] = resp.split()[1..-1]
      lastNum[v] = numList[v][-1]
      str << <<-HTML
        numList[#{v}]=['#{numList[v].join("','")}'];
        lastNum[#{v}]='#{lastNum[v]}';
      HTML
      if numList[v].index(toonBM[v]) < numList[v].index(lastNum[v])
        col_str << "$('div[name=#{v}]').addClass('saved_update');"
      else
        col_str << "$('div[name=#{v}]').addClass('saved_finish');"
      end
    end
  else
    day_BM.each do |v|
      if numList[v].index(toonBM[v]) < numList[v].index(lastNum[v])
        col_str << "$('div[name=#{v}]').addClass('saved_update');"
      else
        col_str << "$('div[name=#{v}]').addClass('saved_finish');"
      end
    end
  end

  str << col_str
  str << "</script>"

  puts str
end
