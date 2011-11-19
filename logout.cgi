#!/usr/bin/ruby
require 'rubygems'
require 'cgi'
require 'cgi/session'
require 'sqlite3'

puts "Content-Type: text/html; charset=utf-8\n\n"

cgi = CGI.new

session = CGI::Session.new(cgi, "session_key" => "SSID", "prefix" => "rubysess.", "tmpdir" => "sess")

if session["user_id"] != nil and session["user_id"] != ""
  session["user_id"] = nil
  str = "<script>"
  str << "toggle_login(false);"
  str << "toonlist_area_init();"
  str << "</script>"
  puts str
end

session.delete
