require "webrick"

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(Dir.pwd, "/html"), :Port => 8888

trap("INT") { server.shutdown }
server.start
