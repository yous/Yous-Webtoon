require "webrick"

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(Dir.pwd, "/"), :Port => (ARGV[0] or 8888).to_i

trap("INT") { server.shutdown }
server.start
