require "webrick"
require "./html/displayToon"
require "./html/getNum"

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(Dir.pwd, "/html"), :Port => 8888
server.mount "/displayToon.cgi", DisplayToon
server.mount "/getNum.cgi", GetNum

trap("INT") { server.shutdown }
server.start
