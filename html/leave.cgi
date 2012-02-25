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

if not cgi.cookies["SSID"].nil?
  begin
    session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)

    db = PGconn.open(:dbname => "webtoon")
    db.exec("CREATE TABLE IF NOT EXISTS usr (id SERIAL PRIMARY KEY, usr_id VARCHAR NOT NULL UNIQUE, usr_pw VARCHAR NOT NULL);")

    if user_pw.nil?
      str = "<script>"
      str << "alert('Enter your Password Again!');"
      str << "$('#user_pw').focus();"
      str << "</script>"
      puts str
    else
      res = db.exec("SELECT id FROM usr WHERE id=$1 AND usr_pw=$2::VARCHAR;", [session["user_id"], Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")])
      if res.count < 1
        str = "<script>"
        str << "alert('Wrong Password!');"
        str << "$('#user_pw').val('');"
        str << "$('#user_pw').focus();"
        str << "</script>"
        puts str
      else
        res.each do |row|
          _id = row["id"].to_i
          db.exec("DELETE FROM usr WHERE id=$1;", [_id])
          session.delete
          str = "<script>"
          str << "alert('Bye!');"
          str << "toggle_login(false);"
          str << "location.href='/';"
          str << "</script>"
          puts str
        end
      end
    end
  rescue
  end
end
