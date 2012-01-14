require "webrick"
require "displayToon"
require "getNum"
require "getOtherToon"

BasicSocket.do_not_reverse_lookup = true

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(File.dirname(__FILE__), "/../html"), :BindAddress => "0.0.0.0", :Port => 8888,
  :AccessLog => [[File.open(File.join(File.dirname(__FILE__), "/../Log"), "a"), WEBrick::AccessLog::COMBINED_LOG_FORMAT]]

server.mount "/displayToon", DisplayToon
server.mount "/getNum", GetNum
server.mount "/getOtherToon", GetOtherToon

trap("INT") { server.shutdown }
server.start
