#!/usr/local/rvm/wrappers/ruby-1.9.3-p0@webtoon/ruby
# encoding: utf-8
require 'rubygems'
require 'cgi'
require 'cgi/session'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new

if not cgi.cookies["SSID"].nil?
  begin
    session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "prefix" => "rubysess.", "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
    session.delete
    str = "<script>"
    str << "toggle_login(false);"
    str << "toonlist_area_init();"
    str << "</script>"
    puts str
  rescue
  end
end
