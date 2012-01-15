#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'cgi/session'
require 'sqlite3'
require 'digest/sha1'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))

db = SQLite3::Database.new(File.join(File.dirname(__FILE__), "/../db/webtoon.db"))
db.execute("CREATE TABLE IF NOT EXISTS usr (id INTEGER PRIMARY KEY, usr_id VARCHAR(255), usr_pw VARCHAR(255));")
db.execute("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER, toon_id INTEGER, toon_num INTEGER);")
db.execute("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER, toon_id VARCHAR(255), toon_num INTEGER);")

if session["user_id"] != nil and session["user_id"] != ""
  if user_pw == nil or user_pw == ""
    str = "<script>"
    str << "alert('Enter your Password Again!');"
    str << "$('#user_pw').focus();"
    str << "</script>"
    puts str
  else
    check = true
    db.execute("SELECT id FROM usr WHERE id=? AND usr_pw=?;", session["user_id"], Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")) do |_id|
      db.execute("DELETE FROM usr WHERE id=?;", _id[0])
      db.execute("DELETE FROM naver_bm WHERE id=?;", _id[0])
      db.execute("DELETE FROM daum_bm WHERE id=?;", _id[0])
      session["user_id"] = nil
      session.delete
      str = "<script>"
      str << "alert('Bye!');"
      str << "toggle_login(false);"
      str << "location.href='/';"
      str << "</script>"
      puts str
      check = false
    end
    if check
      str = "<script>"
      str << "alert('Wrong Password!');"
      str << "$('#user_pw').val('');"
      str << "$('#user_pw').focus();"
      str << "</script>"
      puts str
    end
  end
end
