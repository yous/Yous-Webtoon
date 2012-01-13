require "webrick"
require "displayToon"
require "getNum"
require "getOtherToon"

BasicSocket.do_not_reverse_lookup = true

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(File.dirname(__FILE__), "/../html"), :Port => 8888,
  :DocumentRootOptions => {:NondisclosureName => ["*.rb"]}

server.mount "/displayToon", DisplayToon
server.mount "/getNum", GetNum
server.mount "/getOtherToon", GetOtherToon

trap("INT") { server.shutdown }
server.start
