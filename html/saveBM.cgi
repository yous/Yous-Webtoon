#!/usr/local/rvm/wrappers/ruby-1.9.3-p125@webtoon/ruby
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
  when "daum"
    db.exec("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id VARCHAR NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
    db.exec("CREATE TABLE IF NOT EXISTS daum_lastnum (toon_id VARCHAR PRIMARY KEY, toon_num INTEGER NOT NULL);")
    db.exec("CREATE TABLE IF NOT EXISTS daum_numlist (toon_id VARCHAR NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num INTEGER NOT NULL, toon_date VARCHAR(10), UNIQUE (toon_id, toon_num_idx));")
  when "yahoo"
    db.exec("CREATE TABLE IF NOT EXISTS yahoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
    db.exec("CREATE TABLE IF NOT EXISTS yahoo_lastnum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER NOT NULL);")
    db.exec("CREATE TABLE IF NOT EXISTS yahoo_numlist (toon_id INTEGER NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (toon_id, toon_num_idx));")
  when "stoo"
    db.exec("CREATE TABLE IF NOT EXISTS stoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num VARCHAR NOT NULL, UNIQUE (id, toon_id));")
    db.exec("CREATE TABLE IF NOT EXISTS stoo_lastnum (toon_id INTEGER PRIMARY KEY, toon_num VARCHAR NOT NULL);")
    db.exec("CREATE TABLE IF NOT EXISTS stoo_numlist (toon_id INTEGER NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num VARCHAR NOT NULL, UNIQUE (toon_id, toon_num_idx));")
  end
end

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = (cgi.has_key?("site")) ? cgi.params["site"][0] : nil
add = (cgi.has_key?("add")) ? cgi.params["add"][0] : nil
toon_id = (cgi.has_key?("toon_id")) ? cgi.params["toon_id"][0] : nil
toon_num = (cgi.has_key?("toon_num")) ? cgi.params["toon_num"][0] : nil
finish = (cgi.has_key?("finish")) ? cgi.params["finish"][0] : nil
# only for Daum, Yahoo, Stoo 웹툰
numList = (cgi.has_key?("numList")) ? cgi.params["numList"][0].split : nil
# only for Daum 웹툰
dateList = (cgi.has_key?("dateList")) ? cgi.params["dateList"][0].split : nil

if not cgi.cookies["SSID"].nil?
  begin
    session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
  rescue
    session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))
  end
end

db = PGconn.open(:dbname => "webtoon")
db.exec("CREATE TABLE usr (id SERIAL PRIMARY KEY, user_id VARCHAR NOT NULL UNIQUE, user_pw VARCHAR NOT NULL);") rescue nil
db_init(db, site)

if session["user_id"] != nil and session["user_id"] != "" and add != nil and toon_id != nil and toon_num != nil and finish != nil
  # Naver 웹툰
  if site == "naver"
    toon_id = toon_id.to_i
    toon_num = toon_num.to_i
    if add == "yes"
      db.exec("UPDATE naver_bm SET toon_num=$1 WHERE id=$2 AND toon_id=$3;", [toon_num, session["user_id"], toon_id])
      db.exec("INSERT INTO naver_bm (id, toon_id, toon_num) SELECT $1, $2, $3 WHERE NOT EXISTS (SELECT 1 FROM naver_bm WHERE id=$1 AND toon_id=$2);", [session["user_id"], toon_id, toon_num])
    else
      db.exec("DELETE FROM naver_bm WHERE id=$1 AND toon_id=$2;", [session["user_id"], toon_id])
    end
    if finish != "no"
      db.exec("UPDATE naver_lastnum SET toon_num=$1 WHERE toon_id=$2;", [finish.to_i, toon_id])
      db.exec("INSERT INTO naver_lastnum (toon_id, toon_num) SELECT $1, $2 WHERE NOT EXISTS (SELECT 1 FROM naver_lastnum WHERE toon_id=$1);", [toon_id, finish.to_i])
    end
  # Daum 웹툰
  elsif site == "daum" and numList != nil
    toon_num = toon_num.to_i
    numList.map(&:to_i).each_with_index do |num, idx|
      db.exec("UPDATE daum_numlist SET toon_num=$1, toon_date=$2::VARCHAR WHERE toon_id=$3::VARCHAR AND toon_num_idx=$4;", [num, dateList[idx], toon_id, idx])
      db.exec("INSERT INTO daum_numlist (toon_id, toon_num_idx, toon_num, toon_date) SELECT $1::VARCHAR, $2, $3, $4::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM daum_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [toon_id, idx, num, dateList[idx]])
    end
    if add == "yes"
      db.exec("UPDATE daum_bm SET toon_num=$1 WHERE id=$2 AND toon_id=$3::VARCHAR;", [toon_num, session["user_id"], toon_id])
      db.exec("INSERT INTO daum_bm (id, toon_id, toon_num) SELECT $1, $2::VARCHAR, $3 WHERE NOT EXISTS (SELECT 1 FROM daum_bm WHERE id=$1 AND toon_id=$2);", [session["user_id"], toon_id, toon_num])
    else
      db.exec("DELETE FROM daum_bm WHERE id=$1 AND toon_id=$2::VARCHAR;", [session["user_id"], toon_id])
    end
    if finish != "no"
      db.exec("UPDATE daum_lastnum SET toon_num=$1 WHERE toon_id=$2::VARCHAR;", [finish.to_i, toon_id])
      db.exec("INSERT INTO daum_lastnum (toon_id, toon_num) SELECT $1::VARCHAR, $2 WHERE NOT EXISTS (SELECT 1 FROM daum_lastnum WHERE toon_id=$1);", [toon_id, finish.to_i])
    end
  # Yahoo 웹툰
  elsif site == "yahoo" and numList != nil
    toon_id = toon_id.to_i
    toon_num = toon_num.to_i
    numList.map(&:to_i).each_with_index do |num, idx|
      db.exec("UPDATE yahoo_numlist SET toon_num=$1 WHERE toon_id=$2 AND toon_num_idx=$3;", [num, toon_id, idx])
      db.exec("INSERT INTO yahoo_numlist (toon_id, toon_num_idx, toon_num) SELECT $1, $2, $3 WHERE NOT EXISTS (SELECT 1 FROM yahoo_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [toon_id, idx, num])
    end
    if add == "yes"
      db.exec("UPDATE yahoo_bm SET toon_num=$1 WHERE id=$2 AND toon_id=$3;", [toon_num, session["user_id"], toon_id])
      db.exec("INSERT INTO yahoo_bm (id, toon_id, toon_num) SELECT $1, $2, $3 WHERE NOT EXISTS (SELECT 1 FROM yahoo_bm WHERE id=$1 AND toon_id=$2);", [session["user_id"], toon_id, toon_num])
    else
      db.exec("DELETE FROM yahoo_bm WHERE id=$1 AND toon_id=$2;", [session["user_id"], toon_id])
    end
    if finish != "no"
      db.exec("UPDATE yahoo_lastnum SET toon_num=$1 WHERE toon_id=$2;", [finish.to_i, toon_id])
      db.exec("INSERT INTO yahoo_lastnum (toon_id, toon_num) SELECT $1, $2 WHERE NOT EXISTS (SELECT 1 FROM yahoo_lastnum WHERE toon_id=$1);", [toon_id, finish.to_i])
    end
  # Stoo 웹툰
  elsif site == "stoo" and numList != nil
    toon_id = toon_id.to_i
    numList.each_with_index do |num, idx|
      db.exec("UPDATE stoo_numlist SET toon_num=$1::VARCHAR WHERE toon_id=$2 AND toon_num_idx=$3;", [num, toon_id, idx])
      db.exec("INSERT INTO stoo_numlist (toon_id, toon_num_idx, toon_num) SELECT $1, $2, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM stoo_numlist WHERE toon_id=$1 AND toon_num_idx=$2);", [toon_id, idx, num])
    end
    if add == "yes"
      db.exec("UPDATE stoo_bm SET toon_num=$1::VARCHAR WHERE id=$2 AND toon_id=$3;", [toon_num, session["user_id"], toon_id])
      db.exec("INSERT INTO stoo_bm (id, toon_id, toon_num) SELECT $1, $2, $3::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM stoo_bm WHERE id=$1 AND toon_id=$2);", [session["user_id"], toon_id, toon_num])
    else
      db.exec("DELETE FROM stoo_bm WHERE id=$1 AND toon_id=$2;", [session["user_id"], toon_id])
    end
    if finish != "no"
      db.exec("UPDATE stoo_lastnum SET toon_num=$1::VARCHAR WHERE toon_id=$2;", [finish.to_i, toon_id])
      db.exec("INSERT INTO stoo_lastnum (toon_id, toon_num) SELECT $1, $2::VARCHAR WHERE NOT EXISTS (SELECT 1 FROM stoo_lastnum WHERE toon_id=$1);", [toon_id, finish.to_i])
    end
  end
end
