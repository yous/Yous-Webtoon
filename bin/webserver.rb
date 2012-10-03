require "webrick"
require "pg"

def db_init()
  db = PGconn.open(:dbname => "webtoon")
  db.exec("CREATE TABLE IF NOT EXISTS usr (id SERIAL PRIMARY KEY, user_id VARCHAR NOT NULL UNIQUE, user_pw VARCHAR NOT NULL);")
  db.exec("CREATE TABLE IF NOT EXISTS naver_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
  db.exec("CREATE TABLE IF NOT EXISTS naver_lastnum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER NOT NULL);")
  db.exec("CREATE TABLE IF NOT EXISTS daum_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id VARCHAR NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
  db.exec("CREATE TABLE IF NOT EXISTS daum_lastnum (toon_id VARCHAR PRIMARY KEY, toon_num INTEGER NOT NULL);")
  db.exec("CREATE TABLE IF NOT EXISTS daum_numlist (toon_id VARCHAR NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (toon_id, toon_num_idx));")
  db.exec("CREATE TABLE IF NOT EXISTS yahoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (id, toon_id));")
  db.exec("CREATE TABLE IF NOT EXISTS yahoo_lastnum (toon_id INTEGER PRIMARY KEY, toon_num INTEGER NOT NULL);")
  db.exec("CREATE TABLE IF NOT EXISTS yahoo_numlist (toon_id INTEGER NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num INTEGER NOT NULL, UNIQUE (toon_id, toon_num_idx));")
  db.exec("CREATE TABLE IF NOT EXISTS stoo_bm (id INTEGER REFERENCES usr(id) ON DELETE CASCADE NOT NULL, toon_id INTEGER NOT NULL, toon_num VARCHAR NOT NULL, UNIQUE (id, toon_id));")
  db.exec("CREATE TABLE IF NOT EXISTS stoo_lastnum (toon_id INTEGER PRIMARY KEY, toon_num VARCHAR NOT NULL);")
  db.exec("CREATE TABLE IF NOT EXISTS stoo_numlist (toon_id INTEGER NOT NULL, toon_num_idx INTEGER NOT NULL, toon_num VARCHAR NOT NULL, UNIQUE (toon_id, toon_num_idx));")
  db.close
end

db_init()

BasicSocket.do_not_reverse_lookup = true

server = WEBrick::HTTPServer.new :DocumentRoot => File.join(File.dirname(__FILE__), "/../html"), :BindAddress => "0.0.0.0", :Port => 8888,
  :AccessLog => [[File.open(File.join(File.dirname(__FILE__), "/../Log"), "a"), WEBrick::AccessLog::COMBINED_LOG_FORMAT]]

trap("INT") { server.shutdown }
server.start
