#!/usr/local/rvm/wrappers/ruby-1.9.3-p125@webtoon/ruby
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
      puts <<-HTML
        <script>
          alert('Enter your Password Again!');
          $('#user_pw').focus();
        </script>
      HTML
    else
      res = db.exec("SELECT id FROM usr WHERE id=$1 AND usr_pw=$2::VARCHAR;", [session["user_id"], Digest::SHA1.hexdigest("YoUs" + user_pw + "wEbt00N").force_encoding("UTF-8")])
      if res.count < 1
        puts <<-HTML
          <script>
            alert('Wrong Password!');
            $('#user_pw').val('');
            $('#user_pw').focus();
          </script>
        HTML
      else
        res.each do |row|
          _id = row["id"].to_i
          db.exec("DELETE FROM usr WHERE id=$1;", [_id])
          session.delete
          puts <<-HTML
            <script>
              alert('Bye!');
              toggle_login(false);
              location.href='/';
            </script>
          HTML
        end
      end
    end
  rescue
  end
end
