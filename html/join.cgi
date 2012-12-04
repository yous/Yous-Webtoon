#!/usr/local/rvm/wrappers/ruby-1.9.3-p327@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'pg'
require 'digest/sha1'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new
user_id = (cgi.has_key?("user_id")) ? cgi.params["user_id"][0] : nil
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil

db = PGconn.open(:dbname => "webtoon")
db.exec("CREATE TABLE IF NOT EXISTS usr (id SERIAL PRIMARY KEY, usr_id VARCHAR NOT NULL UNIQUE, usr_pw VARCHAR NOT NULL);")

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
  str << <<-HTML
      $('#user_id').val('');
      $('#user_pw').val('');
      $('#user_id').focus();
    </script>
  HTML
  puts str
else
  db.exec("INSERT INTO usr (usr_id, usr_pw) VALUES ($1::VARCHAR, $2::VARCHAR);", [user_id, Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")])
  puts <<-HTML
    <script>
      alert('Hello, #{user_id}!');
      toggle_login(false);
    </script>
  HTML
end
