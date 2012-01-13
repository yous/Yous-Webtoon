#!/usr/local/rvm/wrappers/ruby-1.8.7-p352@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'
require 'sqlite3'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
site = (cgi.has_key?("site")) ? cgi.params["site"][0] : nil
add = (cgi.has_key?("add")) ? cgi.params["add"][0] : nil
toon_id = (cgi.has_key?("toon_id")) ? cgi.params["toon_id"][0] : nil
toon_num = (cgi.has_key?("toon_num")) ? cgi.params["toon_num"][0].to_i : nil
finish = (cgi.has_key?("finish")) ? cgi.params["finish"][0] : nil
# only for Daum 웹툰
numList = (cgi.has_key?("numList")) ? cgi.params["numList"][0].split.map(&:to_i) : nil
dateList = (cgi.has_key?("dateList")) ? cgi.params["dateList"][0].split : nil

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => "../sess")

db = SQLite3::Database.new("../db/webtoon.db")
db.execute("CREATE TABLE IF NOT EXISTS usr (id INTEGER PRIMARY KEY, user_id VARCHAR(255), user_pw VARCHAR(255));")
db.execute("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER, toon_id INTEGER, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS naver_lastNum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER, toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_lastNum (toon_id VARCHAR(255), toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_numList (toon_id VARCHAR(255), toon_num_idx INTEGER, toon_num INTEGER, toon_date VARCHAR(10));")

if session["user_id"] != nil and session["user_id"] != "" and add != nil and toon_id != nil and toon_num != nil and finish != nil
  # Naver 웹툰
  if site == "naver"
    if add == "yes"
      db.execute("UPDATE naver_bm SET toon_num=? WHERE id=? AND toon_id=?;", toon_num, session["user_id"], toon_id.to_i)
      db.execute("INSERT INTO naver_bm (id, toon_id, toon_num) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM naver_bm WHERE id=? AND toon_id=?);", session["user_id"], toon_id.to_i, toon_num, session["user_id"], toon_id.to_i)
    else
      db.execute("DELETE FROM naver_bm WHERE id=? AND toon_id=?;", session["user_id"], toon_id.to_i)
    end
    if finish != "no"
      db.execute("UPDATE naver_lastNum SET toon_num=? WHERE toon_id=?;", finish.to_i, toon_id.to_i)
      db.execute("INSERT INTO naver_lastNum (toon_id, toon_num) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM naver_lastNum WHERE toon_id=?);", toon_id.to_i, finish.to_i, toon_id.to_i)
    end
  # Daum 웹툰
  elsif site == "daum" and numList != nil
    (0...numList.length).each do |i|
      db.execute("UPDATE daum_numList SET toon_num=?, toon_date=? WHERE toon_id=? AND toon_num_idx=?;", numList[i], dateList[i], toon_id, i)
      db.execute("INSERT INTO daum_numList (toon_id, toon_num_idx, toon_num, toon_date) SELECT ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_numList WHERE toon_id=? AND toon_num_idx=?);", toon_id, i, numList[i], dateList[i], toon_id, i)
    end
    if add == "yes"
      db.execute("UPDATE daum_bm SET toon_num=? WHERE id=? AND toon_id=?;", toon_num, session["user_id"], toon_id)
      db.execute("INSERT INTO daum_bm (id, toon_id, toon_num) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_bm WHERE id=? AND toon_id=?);", session["user_id"], toon_id, toon_num, session["user_id"], toon_id)
    else
      db.execute("DELETE FROM daum_bm WHERE id=? AND toon_id=?;", session["user_id"], toon_id)
    end
    if finish != "no"
      db.execute("UPDATE daum_lastNum SET toon_num=? WHERE toon_id=?;", finish.to_i, toon_id)
      db.execute("INSERT INTO daum_lastNum (toon_id, toon_num) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM daum_lastNum WHERE toon_id=?);", toon_id, finish.to_i, toon_id)
    end
  end
end
