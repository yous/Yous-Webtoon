#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'cgi/session'
require 'sqlite3'
require 'digest/sha1'

cgi = CGI.new
user_id = (cgi.has_key?("user_id")) ? cgi.params["user_id"][0] : nil
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil

if user_id != nil and user_pw != nil
  db = SQLite3::Database.new(File.join(File.dirname(__FILE__), "/../db/webtoon.db"))
  db.execute("CREATE TABLE IF NOT EXISTS usr (id INTEGER PRIMARY KEY, usr_id VARCHAR(255), usr_pw VARCHAR(255));")

  session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => true)

  check = true

  db.execute("SELECT id FROM usr WHERE usr_id=? AND usr_pw=?;", user_id, Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")) do |_id|
    session["user_id"] = _id[0]
    cookie = CGI::Cookie.new("name" => "SSID", "value" => session.session_id)
    cgi.out("type" => "text/html; charset=utf-8") { "<script>toggle_login(true);toonlist_area_init();</script>" }
    session.close
    check = false
  end

  if check
    session.delete
    str = "Content-Type: text/html; charset=utf-8\n\n"
    str << "<script>"
    str << "alert('Wrong ID or Password!');"
    str << "toggle_login(false);"
    str << "</script>"
    puts str
  end
else
  puts "Content-Type: text/html; charset=utf-8\n\n"
end
