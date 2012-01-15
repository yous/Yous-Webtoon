#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'cgi/session'
require 'sqlite3'
require 'digest/sha1'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
user_id = (cgi.has_key?("user_id")) ? cgi.params["user_id"][0] : nil
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil

db = SQLite3::Database.new(File.join(File.dirname(__FILE__), "/../db/webtoon.db"))
db.execute("CREATE TABLE IF NOT EXISTS usr (id INTEGER PRIMARY KEY, usr_id VARCHAR(255), usr_pw VARCHAR(255));")

check = true

str = "<script>"
if user_id == nil or user_id.length < 3
  str << "alert('ID must be longer than 3');"
  check = false
elsif not user_id =~ /^[A-Za-z0-9_-]+$/
  str << "alert('You can use only A~Z, a~z, 0~9, _, -');"
  check = false
elsif not user_id =~ /^[A-Za-z0-9][A-Za-z0-9_-]*$/
  str << "alert('ID must starts with A~Z, a~z, 0~9');"
  check = false
elsif user_pw == nil or user_pw.length < 3
  str << "alert('Password must be longer than 3');"
  check = false
else
  db.execute("SELECT id FROM usr WHERE usr_id=?;", user_id) do |_id|
    str << "alert('ID Already Exists!');"
    check = false
  end
end

if not check
  str << "$('#user_id').val('');"
  str << "$('#user_pw').val('');"
  str << "$('#user_id').focus();"
  str << "</script>"
  puts str
else
  db.execute("INSERT INTO usr (usr_id, usr_pw) VALUES (?, ?);", user_id, Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8"))
  str = "<script>"
  str << "alert('Hello, #{user_id}!');"
  str << "toggle_login(false);"
  str << "</script>"
  puts str
end
