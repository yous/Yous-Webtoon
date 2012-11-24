require 'webrick'

class SiteJsonHandler < WEBrick::HTTPServlet::AbstractServlet
  def do_GET(req, res)
    res.status = 200
    res["Content-Type"] = "application/json"
    res.body = File.read(File.join(File.dirname(__FILE__) + "/../html", req.path))
  end
end
