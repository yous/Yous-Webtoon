#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'pg'
require 'digest/sha1'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
user_id = (cgi.has_key?("user_id")) ? cgi.params["user_id"][0] : nil
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil

db = PGconn.open(:dbname => "yous")
db.exec("CREATE TABLE usr (id SERIAL, usr_id VARCHAR, usr_pw VARCHAR);") rescue nil

check = false

str = "<script>"
if user_id.nil? or user_id.length < 3
  str << "alert('ID must be longer than 3');"
elsif not user_id =~ /^[A-Za-z0-9_-]+$/
  str << "alert('You can use only A~Z, a~z, 0~9, _, -');"
elsif not user_id =~ /^[A-Za-z0-9][A-Za-z0-9_-]*$/
  str << "alert('ID must starts with A~Z, a~z, 0~9');"
elsif user_pw.nil? or user_pw.length < 3
  str << "alert('Password must be longer than 3');"
elsif db.exec("SELECT id FROM usr WHERE usr_id=$1::VARCHAR;", [user_id]).count > 0
  str << "alert('ID Already Exists!');"
else
  check = true
end

if not check
  str << "$('#user_id').val('');"
  str << "$('#user_pw').val('');"
  str << "$('#user_id').focus();"
  str << "</script>"
  puts str
else
  db.exec("INSERT INTO usr (usr_id, usr_pw) VALUES ($1::VARCHAR, $2::VARCHAR);", [user_id, Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")])
  str = "<script>"
  str << "alert('Hello, #{user_id}!');"
  str << "toggle_login(false);"
  str << "</script>"
  puts str
end
