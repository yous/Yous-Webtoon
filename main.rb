require "webrick"
require "./html/displayToon"

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(Dir.pwd, "/html"), :Port => 8888
server.mount "displayToon.cgi", DisplayToon

trap("INT") { server.shutdown }
server.start
