#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'cgi/session'
require 'pg'
require 'digest/sha1'

def db_init(db)
  db.exec("CREATE TABLE IF NOT EXISTS usr (id SERIAL PRIMARY KEY, usr_id VARCHAR NOT NULL UNIQUE, usr_pw VARCHAR NOT NULL);")
end

cgi = CGI.new
user_id = (cgi.has_key?("user_id")) ? cgi.params["user_id"][0] : nil
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil
check = (cgi.has_key?("check")) ? cgi.params["check"][0] : nil

if check == "y" # Login 확인
  puts "Content-Type: text/html; charset=utf-8\n\n"

  db = PGconn.open(:dbname => "webtoon")
  db_init(db)

  if not cgi.cookies["SSID"].nil?
    begin
      session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
      str = "<script>"
      str << "$('#user_id').val('#{db.exec("SELECT usr_id FROM usr WHERE id=$1;", [session["user_id"]])[0]["usr_id"]}');"
      str << "toggle_login(true);"
      str << "</script>"
      puts str
    rescue
      session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))
    end
  end
elsif user_id != nil and user_pw != nil
  db = PGconn.open(:dbname => "webtoon")
  db_init(db)

  session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => true)

  check = true

  db.exec("SELECT id FROM usr WHERE usr_id=$1::VARCHAR AND usr_pw=$2::VARCHAR;", [user_id, Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")]).each do |row|
    _id = row["id"].to_i
    session["user_id"] = _id
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
