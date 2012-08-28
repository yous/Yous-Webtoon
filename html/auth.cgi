#!/usr/local/rvm/wrappers/ruby-1.9.3-p125@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'cgi/session'

cgi = CGI.new
site = (cgi.has_key? "site") ? cgi.params["site"][0] : nil
id = (cgi.has_key? "id") ? cgi.params["id"][0] : nil
num = (cgi.has_key? "num") ? cgi.params["num"][0] : nil
authid = (cgi.has_key? "authid") ? cgi.params["authid"][0] : nil
authpw = (cgi.has_key? "authpw") ? cgi.params["authpw"][0] : nil

if not cgi.cookies["SSID"].nil?
  begin
    session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
  rescue
    session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"))
  end
else
  session = CGI::Session.new(cgi, "session_key" => "SSID", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => true)
end

if site != nil
  if authid != nil and authpw != nil
    session[site] = Hash.new
    session[site]["authid"] = authid
    session[site]["authpw"] = authpw
  end
  if session[site].nil? or session[site]["authid"].nil? or session[site]["authpw"].nil?
    puts "Content-Type: text/html; charset=utf-8\n\n"
    print <<-HTML
    <html>
      <body>
        <form action="auth.cgi" method="post">
          <input type="hidden" name="site" value="#{site}"/>
    HTML
    if id != nil
      print <<-HTML
          <input type="hidden" name="id" value="#{id}"/>
      HTML
    end
    if num != nil
      print <<-HTML
          <input type="hidden" name="num" value="#{num}"/>
      HTML
    end
    print <<-HTML
          <input type="text" name="authid" placeholder="ID"/>
          <input type="password" name="authpw" placeholder="Password"/>
          <input type="submit" value="Login"/>
        </form>
      </body>
    </html>
    HTML
  else
    a = Mechanize.new
    a.history.max_size = 0

    if site == "naver"
      resp = a.get "http://nid.naver.com/nidlogin.login"
      form = resp.forms[0]
      form.field_with(:id => "uid").value = session[site]["authid"]
      form.field_with(:id => "upw").value = session[site]["authpw"]
      resp = form.submit
      resp = a.get $1 if resp.at('script').inner_html =~ /location\.replace\("([^"]+)"\)/

      cookie = CGI::Cookie.new("name" => "SSID", "value" => session.session_id)
      if resp.search('//div[@class="error"]').count > 0
        session[site] = nil
        cgi.out("type" => "text/html; charset=utf-8") { "<script>document.location = \"auth.cgi?site=#{site}#{"&id=" + id if id != nil}#{"&num=" + num if num != nil}\";</script>" }
      else
        session[site]["cookie"] = a.cookie_jar
        if id.nil?
          str = "<script>window.close();</script>"
        elsif num.nil?
          str = "<script>opener.viewToon(#{id});window.close();</script>"
        else
          str = "<script>opener.viewToon(#{id}, #{num});window.close();</script>"
        end
        cgi.out("type" => "text/html; charset=utf-8") { str }
      end
    elsif site == "daum"
    elsif site == "yahoo"
    elsif site == "stoo"
    end
  end
else
  puts "Content-Type: text/html; charset=utf-8\n\n"
end

session.close
