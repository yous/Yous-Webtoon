require "webrick"
require "./html/displayToon"
require "./html/getNum"
require "./html/getOtherToon"

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(Dir.pwd, "/html"), :Port => 8888
server.mount "/displayToon", DisplayToon
server.mount "/getNum", GetNum
server.mount "/getOtherToon", GetOtherToon

trap("INT") { server.shutdown }
server.start
