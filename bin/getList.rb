# encoding: utf-8
require 'logger'
require 'site'

logger = Logger.new(STDERR)
logger.level = Logger::INFO

trap("QUIT") {
  logger.close
  exit
}

sites = [SiteNaver.new, SiteDaum.new]
count = 0
while true
  if count % (6 * 24) == 0
    sites.each do |site|
      begin
        site.getList :all => true
        logger.info "#{site.site} ALL"
      rescue Exception => e
        logger.error "#{site.site} ALL\n#{e.backtrace[0]}: #{e.message} (#{e.class})\n#{e.backtrace.drop(1).map {|msg| "\tfrom #{msg}"}.join("\n")}"
      end
    end
  else
    sites.each do |site|
      begin
        site.getList :all => false
        logger.info site.site
      rescue Exception => e
        logger.error "#{site.site}\n#{e.backtrace[0]}: #{e.message} (#{e.class})\n#{e.backtrace.drop(1).map {|msg| "\tfrom #{msg}"}.join("\n")}"
      end
    end
  end
  sleep(60 * 10)
  count += 1
end
