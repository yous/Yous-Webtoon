# encoding: utf-8
require 'mechanize'
require 'pg'
require 'json'
require 'rss'

class Site
  attr_reader :site

  def getList args
    daysToon, toonInfo, reqList = getInfo
    numList = getNum(reqList, args)

    File.open(File.join(File.dirname(__FILE__), "/../html/#{@site}.json"), "w") do |f|
      f.write({"daysToon" => daysToon, "toonInfo" => toonInfo, "numList" => numList}.to_json)
    end
  end
end

class SiteNaver < Site
  def initialize
    @site = "naver"
  end

  def getInfo
    db = PGconn.open(:dbname => "webtoon")

    a = Mechanize.new
    a.history.max_size = 0

    toonInfo = Hash.new
    daysToon = Hash.new
    reqList = []

    db.exec("SELECT toon_day, toon_id FROM naver_daystoon ORDER BY toon_day, toon_idx;").each do |row|
      _toon_day = row["toon_day"].to_i
      _toon_id = row["toon_id"].to_i
      daysToon[_toon_day] = [] if daysToon[_toon_day].nil?
      daysToon[_toon_day].push _toon_id
    end

    db.exec("SELECT toon_id, toon_title, toon_finished, toon_up, toon_new FROM naver_tooninfo ORDER BY toon_id;").each do |row|
      _toon_id = row["toon_id"].to_i
      _toon_title = row["toon_title"]
      _toon_finished = (row["toon_finished"] == "t") ? true : false
      _toon_up = (row["toon_up"] == "t") ? true : false
      _toon_new = (row["toon_new"] == "t") ? true : false
      toonInfo[_toon_id] = {
        "title" => _toon_title,
        "finished" => _toon_finished,
        "up" => _toon_up,
        "new" => _toon_new
      }
    end

    # 연재 웹툰
    resp = a.get "http://comic.naver.com/webtoon/weekday.nhn"

    resp.search('//div[@class="list_area daily_all"]').each do |all|
      all.search('./div/div[@class="col_inner"]').each_with_index do |col, day|
        newDayToon = []
        col.search('./ul/li/div[@class="thumb"]').each do |v|
          _a = v.at('./a')
          _titleId = $1.to_i if _a.attr("href") =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
          _title = _a.attr("title")
          _up = (_a.search('./em[@class="ico_updt"]').length > 0) ? true : false
          _new = (_a.search('./img').length > 1) ? true : false

          newDayToon.push _titleId

          currentInfo = {"title" => _title, "finished" => false, "up" => _up, "new" => _new}
          if toonInfo[_titleId].nil?
            toonInfo[_titleId] = currentInfo
            db.exec("INSERT INTO naver_tooninfo (toon_id, toon_title, toon_finished, toon_up, toon_new) VALUES ($1, $2::VARCHAR, $3::BOOLEAN, $4::BOOLEAN, $5::BOOLEAN);", [_titleId, _title, false, _up, _new])
          elsif toonInfo[_titleId] != currentInfo
            toonInfo[_titleId] = currentInfo
            db.exec("UPDATE naver_tooninfo SET toon_title=$1::VARCHAR, toon_finished=$2::BOOLEAN, toon_up=$3::BOOLEAN, toon_new=$4::BOOLEAN WHERE toon_id=$5;", [_title, false, _up, _new, _titleId])
          end
        end

        if daysToon[day] != newDayToon
          db.exec("DELETE FROM naver_daystoon WHERE toon_day=$1;", [day]) if daysToon[day] != nil
          newDayToon.each_with_index do |id, idx|
            db.exec("INSERT INTO naver_daystoon (toon_day, toon_idx, toon_id) VALUES ($1, $2, $3);", [day, idx, id])
          end
          daysToon[day] = newDayToon
        end
      end
    end

    # 완결 웹툰
    resp = a.get "http://comic.naver.com/webtoon/finish.nhn"

    newDayToon = []
    resp.search('//div[@class="thumb"]').each_with_index do |r, idx|
      _a = r.at('./a')
      _titleId = $1.to_i if _a.attr("href") =~ /\/webtoon\/list\.nhn\?titleId=(\d+)/
      _title = _a.attr("title")

      newDayToon.push _titleId

      currentInfo = {"title" => _title, "finished" => true, "up" => nil, "new" => nil}
      if toonInfo[_titleId].nil?
        reqList.push _titleId
        toonInfo[_titleId] = currentInfo
        db.exec("INSERT INTO naver_tooninfo (toon_id, toon_title, toon_finished, toon_up, toon_new) VALUES ($1, $2::VARCHAR, $3::BOOLEAN, NULL, NULL);", [_titleId, _title, true])
      elsif toonInfo[_titleId] != currentInfo
        reqList.push _titleId if not toonInfo[_titleId]["finished"]
        toonInfo[_titleId] = currentInfo
        db.exec("UPDATE naver_tooninfo SET toon_title=$1::VARCHAR, toon_finished=$2::BOOLEAN, toon_up=NULL, toon_new=NULL WHERE toon_id=$3;", [_title, true, _titleId])
      end
    end

    if daysToon[7] != newDayToon
      db.exec("DELETE FROM naver_daystoon WHERE toon_day=7;") if daysToon[7] != nil
      newDayToon.each_with_index do |id, idx|
        db.exec("INSERT INTO naver_daystoon (toon_day, toon_idx, toon_id) VALUES (7, $1, $2);", [idx, id])
      end
      daysToon[7] = newDayToon
    end

    (toonInfo.keys - daysToon.values.reduce(:+)).each do |id|
      db.exec("DELETE FROM naver_tooninfo WHERE toon_id=$1;", [id])
      db.exec("DELETE FROM naver_numlist WHERE toon_id=$1;", [id])
      toonInfo.delete id
    end

    db.close

    return daysToon, toonInfo, reqList
  end

  def getNum(ids, args)
    db = PGconn.open(:dbname => "webtoon")

    a = Mechanize.new
    a.history.max_size = 0

    numList = Hash.new

    if args[:all]
      db.exec("SELECT toon_id FROM naver_tooninfo ORDER BY toon_id;").each do |row|
        _toon_id = row["toon_id"].to_i
        ids.push _toon_id
      end
    else
      db.exec("SELECT toon_id FROM naver_tooninfo WHERE toon_finished=FALSE ORDER BY toon_id;").each do |row|
        _toon_id = row["toon_id"].to_i
        ids.push _toon_id
      end
    end

    db.exec("SELECT toon_id, toon_num FROM naver_numlist ORDER BY toon_id, toon_num_idx;").each do |row|
      _toon_id = row["toon_id"].to_i
      _toon_num = row["toon_num"].to_i
      numList[_toon_id] = [] if numList[_toon_id].nil?
      numList[_toon_id].push _toon_num
    end

    ids.each do |id|
      newNumList = []
      catch :done do
        page = 1
        while true
          resp = a.get "http://comic.naver.com/webtoon/list.nhn?titleId=#{id}&page=#{page}"

          resp.search('//div[@id="content"]/table[@class="viewList"]/tr[position()>2]').each do |tr|
            num = $1.to_i if tr.at('./td[2]/a').attr("href") =~ /[\?&]no=(\d+)/
            newNumList.insert(0, num)
            throw :done if numList[id] and num == numList[id][-1]
          end

          pages = resp.at('//div[@id="content"]/div[@class="pagenavigation"]')
          if pages.search('./a[@class="next"]').count > 0
            page = $1.to_i if pages.at('./a[@class="next"]').attr("href") =~ /[\?&]page=(\d+)/
          else
            throw :done
          end
        end
      end

      if numList[id].nil?
        newNumList.each_with_index do |num, idx|
          db.exec("INSERT INTO naver_numlist (toon_id, toon_num_idx, toon_num) VALUES ($1, $2, $3);", [id, idx, num])
        end
        numList[id] = newNumList
      elsif not newNumList.empty?
        lastIdx = numList[id].index(newNumList[0])
        if lastIdx.nil?
          db.exec("DELETE FROM naver_numlist WHERE toon_id=$1;", [id])
          newNumList.each_with_index do |num, idx|
            db.exec("INSERT INTO naver_numlist (toon_id, toon_num_idx, toon_num) VALUES ($1, $2, $3);", [id, idx, num])
          end
          numList[id] = newNumList
        else
          db.exec("DELETE FROM naver_numlist WHERE toon_id=$1 AND toon_num_idx>$2;", [id, lastIdx])
          newNumList.drop(1).each_with_index do |num, idx|
            db.exec("INSERT INTO naver_numlist (toon_id, toon_num_idx, toon_num) VALUES ($1, $2, $3);", [id, lastIdx + idx + 1, num])
          end
          numList[id] = numList[id].take(lastIdx + 1) + newNumList.drop(1)
        end
      end
    end

    db.close

    return numList
  end
end

class SiteDaum < Site
  def initialize
    @site = "daum"
  end

  def getInfo
    db = PGconn.open(:dbname => "webtoon")

    a = Mechanize.new
    a.history.max_size = 0

    toonInfo = Hash.new
    daysToon = Hash.new
    reqList = []

    db.exec("SELECT toon_day, toon_id FROM daum_daystoon ORDER BY toon_day, toon_idx;").each do |row|
      _toon_day = row["toon_day"].to_i
      _toon_id = row["toon_id"]
      daysToon[_toon_day] = [] if daysToon[_toon_day].nil?
      daysToon[_toon_day].push _toon_id
    end

    db.exec("SELECT toon_id, toon_title, toon_finished, toon_up FROM daum_tooninfo ORDER BY toon_id;").each do |row|
      _toon_id = row["toon_id"]
      _toon_title = row["toon_title"]
      _toon_finished = (row["toon_finished"] == "t") ? true : false
      _toon_up = (row["toon_up"] == "t") ? true : false
      toonInfo[_toon_id] = {
        "title" => _toon_title,
        "finished" => _toon_finished,
        "up" => _toon_up,
      }
    end

    # 연재 웹툰
    resp = a.get "http://cartoon.media.daum.net/webtoon/week"

    resp.search('//div[@id="mCenter"]/div[@class="area_toonlist area_bg"]').each do |all|
      all.search('./div/div[@class="bg_line"]').each_with_index do |col, day|
        newDayToon = []
        col.search('./ul/li').each do |v|
          _a = v.at('./a')
          _titleId = $1 if _a.attr("href") =~ /\/webtoon\/view\/(.+)$/
          _title = _a.attr("title")
          _up = (v.search('./span[@class="new"]').length > 0) ? true : false

          newDayToon.push _titleId

          currentInfo = {"title" => _title, "finished" => false, "up" => _up}
          if toonInfo[_titleId].nil?
            toonInfo[_titleId] = currentInfo
            db.exec("INSERT INTO daum_tooninfo (toon_id, toon_title, toon_finished, toon_up) VALUES ($1::VARCHAR, $2::VARCHAR, $3::BOOLEAN, $4::BOOLEAN);", [_titleId, _title, false, _up])
          elsif toonInfo[_titleId] != currentInfo
            toonInfo[_titleId] = currentInfo
            db.exec("UPDATE daum_tooninfo SET toon_title=$1::VARCHAR, toon_finished=$2::BOOLEAN, toon_up=$3::BOOLEAN WHERE toon_id=$4::VARCHAR;", [_title, false, _up, _titleId])
          end
        end

        if daysToon[day] != newDayToon
          db.exec("DELETE FROM daum_daystoon WHERE toon_day=$1;", [day]) if daysToon[day] != nil
          newDayToon.each_with_index do |id, idx|
            db.exec("INSERT INTO daum_daystoon (toon_day, toon_idx, toon_id) VALUES ($1, $2, $3::VARCHAR);", [day, idx, id])
          end
          daysToon[day] = newDayToon
        end
      end
    end

    # 완결 웹툰
    resp = a.get "http://cartoon.media.daum.net/webtoon/finished"

    newDayToon = []
    resp.search('//div[@id="mCenter"]/div[@class="area_toonlist"]/ul[@class="list_type_image list_incount list_year"]/li').each_with_index do |r, idx|
      next if r.attr("class") == "line_dot"
      _titleId = $1 if r.at('./a').attr("href") =~ /\/webtoon\/view\/(.+)$/
      _title = r.at('./p').attr("title")

      newDayToon.push _titleId

      currentInfo = {"title" => _title, "finished" => true, "up" => nil}
      if toonInfo[_titleId].nil?
        reqList.push _titleId
        toonInfo[_titleId] = currentInfo
        db.exec("INSERT INTO daum_tooninfo (toon_id, toon_title, toon_finished, toon_up) VALUES ($1::VARCHAR, $2::VARCHAR, $3::BOOLEAN, NULL);", [_titleId, _title, true])
      elsif toonInfo[_titleId] != currentInfo
        reqList.push _titleId if not toonInfo[_titleId]["finished"]
        toonInfo[_titleId] = currentInfo
        db.exec("UPDATE daum_tooninfo SET toon_title=$1::VARCHAR, toon_finished=$2::BOOLEAN, toon_up=NULL WHERE toon_id=$3::VARCHAR;", [_title, true, _titleId])
      end
    end

    if daysToon[7] != newDayToon
      db.exec("DELETE FROM daum_daystoon WHERE toon_day=7;") if daysToon[7] != nil
      newDayToon.each_with_index do |id, idx|
        db.exec("INSERT INTO daum_daystoon (toon_day, toon_idx, toon_id) VALUES (7, $1, $2::VARCHAR);", [idx, id])
      end
      daysToon[7] = newDayToon
    end

    (toonInfo.keys - daysToon.values.reduce(:+)).each do |id|
      db.exec("DELETE FROM daum_tooninfo WHERE toon_id=$1::VARCHAR;", [id])
      db.exec("DELETE FROM daum_numlist WHERE toon_id=$1::VARCHAR;", [id])
      toonInfo.delete id
    end

    db.close

    return daysToon, toonInfo, reqList
  end

  def getNum(ids, args)
    db = PGconn.open(:dbname => "webtoon")

    a = Mechanize.new
    a.history.max_size = 0

    numList = Hash.new

    if args[:all]
      db.exec("SELECT toon_id FROM daum_tooninfo ORDER BY toon_id;").each do |row|
        _toon_id = row["toon_id"]
        ids.push _toon_id
      end
    else
      db.exec("SELECT toon_id FROM daum_tooninfo WHERE toon_finished=FALSE ORDER BY toon_id;").each do |row|
        _toon_id = row["toon_id"]
        ids.push _toon_id
      end
    end

    db.exec("SELECT toon_id, toon_num FROM daum_numlist ORDER BY toon_id, toon_num_idx;").each do |row|
      _toon_id = row["toon_id"]
      _toon_num = row["toon_num"].to_i
      numList[_toon_id] = [] if numList[_toon_id].nil?
      numList[_toon_id].push _toon_num
    end

    ids.each do |id|
      newNumList = []
      resp = a.get "http://cartoon.media.daum.net/webtoon/rss/#{id}"

      RSS::Parser.parse(resp.body, false).items.each do |item|
        num = $1.to_i if item.link =~ /\/webtoon\/viewer\/(\d+)/
        newNumList.insert(0, num)
        break if numList[id] and num == numList[id][-1]
      end

      if numList[id].nil?
        newNumList.each_with_index do |num, idx|
          db.exec("INSERT INTO daum_numlist (toon_id, toon_num_idx, toon_num) VALUES ($1::VARCHAR, $2, $3);", [id, idx, num])
        end
        numList[id] = newNumList
      elsif not newNumList.empty?
        lastIdx = numList[id].index(newNumList[0])
        if lastIdx.nil?
          db.exec("DELETE FROM daum_numlist WHERE toon_id=$1::VARCHAR;", [id])
          newNumList.each_with_index do |num, idx|
            db.exec("INSERT INTO daum_numlist (toon_id, toon_num_idx, toon_num) VALUES ($1::VARCHAR, $2, $3);", [id, idx, num])
          end
          numList[id] = newNumList
        else
          db.exec("DELETE FROM daum_numlist WHERE toon_id=$1::VARCHAR AND toon_num_idx>$2;", [id, lastIdx])
          newNumList.drop(1).each_with_index do |num, idx|
            db.exec("INSERT INTO daum_numlist (toon_id, toon_num_idx, toon_num) VALUES ($1::VARCHAR, $2, $3);", [id, lastIdx + idx + 1, num])
          end
          numList[id] = numList[id].take(lastIdx + 1) + newNumList.drop(1)
        end
      end
    end

    db.close

    return numList
  end
end
