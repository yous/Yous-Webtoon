#!/usr/local/rvm/wrappers/ruby-1.9.3-p327@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'cgi/session'
require 'pg'
require 'digest/sha1'

cgi = CGI.new
user_id = (cgi.has_key?("user_id")) ? cgi.params["user_id"][0] : nil
user_pw = (cgi.has_key?("user_pw")) ? cgi.params["user_pw"][0] : nil
check = (cgi.has_key?("check")) ? cgi.params["check"][0] : nil

if check == "y" # Login 확인
  puts "Content-Type: text/html; charset=utf-8\n\n"

  db = PGconn.open(:dbname => "webtoon")

  if not cgi.cookies["SSID"].nil?
    begin
      session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
      puts <<-HTML
        <script>
          $('#user_id').val('#{db.exec("SELECT usr_id FROM usr WHERE id=$1;", [session["user_id"]])[0]["usr_id"]}');
          toggle_login(true);
        </script>
      HTML
    rescue
      session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))
    end
  end
elsif user_id != nil and user_pw != nil
  db = PGconn.open(:dbname => "webtoon")

  session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => true)

  check = true

  db.exec("SELECT id FROM usr WHERE usr_id=$1::VARCHAR AND usr_pw=$2::VARCHAR;", [user_id, Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")]).each do |row|
    _id = row["id"].to_i
    session["user_id"] = _id
    cookie = CGI::Cookie.new("name" => "SSID", "value" => session.session_id)
    cgi.out("type" => "text/html; charset=utf-8") { "<script>toggle_login(true);sitelist_init();</script>" }
    session.close
    check = false
  end

  if check
    session.delete
    puts "Content-Type: text/html; charset=utf-8\n\n"
    puts <<-HTML
      <script>
        alert('Wrong ID or Password!');
        toggle_login(false);
      </script>
    HTML
  end
else
  puts "Content-Type: text/html; charset=utf-8\n\n"
end
