#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'cgi/session'
require 'pg'
require 'digest/sha1'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))

db = PGconn.open(:dbname => "yous")
db.exec("CREATE TABLE IF NOT EXISTS usr (id SERIAL PRIMARY KEY, usr_id VARCHAR NOT NULL UNIQUE, usr_pw VARCHAR NOT NULL);")
db.exec("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
db.exec("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id VARCHAR NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
db.exec("CREATE TABLE IF NOT EXISTS yahoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
db.exec("CREATE TABLE IF NOT EXISTS stoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num VARCHAR NOT NULL, UNIQUE (id, toon_id));")

if session["user_id"] != nil and session["user_id"] != ""
  if user_pw.nil? or user_pw == ""
    str = "<script>"
    str << "alert('Enter your Password Again!');"
    str << "$('#user_pw').focus();"
    str << "</script>"
    puts str
  else
    check = true
    db.execute("SELECT id FROM usr WHERE id=$1 AND usr_pw=$2::VARCHAR;", [session["user_id"], Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")]).each do |row|
      _id = row["id"].to_i
      db.exec("DELETE FROM usr WHERE id=$1;", [_id])
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
