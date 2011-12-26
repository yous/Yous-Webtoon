#!/usr/bin/ruby
require 'rubygems'
require 'mechanize'
require 'cgi'
require 'json'

def flashObj(_url, _flashID, _width, _height, _wmode = "transparent", _flashVars = "", _bgColor = "#FFFFFF", _allowFullScreen = true)
  s = "<object width=\"#{_width}\" height=\"#{_height}\" id=\"#{_flashID}\" classid=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\" codebase=\"http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0\">"
  s << '<param name="allowScriptAccess" value="always"/>'
  s << '<param name="quality" value="high"/>'
  s << '<param name="menu" value="false"/>'
  s << "<param name=\"movie\" value=\"/webtoon/tmp/#{_url.gsub(/\//, "@")}\"/>"
  s << "<param name=\"wmode\" value=\"#{_wmode}\"/>"
  s << "<param name=\"bgcolor\" value=\"#{_bgColor}\"/>"
  s << "<param name=\"FlashVars\" value=\"#{_flashVars}\"/>"
  s << "<param name=\"allowFullScreen\" value=\"#{_allowFullScreen}\"/>"
  s << "<embed src=\"/webtoon/tmp/#{_url.gsub(/\//, "@")}\" quality=\"high\" wmode=\"#{_wmode}\" menu=\"false\" FlashVars=\"#{_flashVars}\" bgcolor=\"#{_bgColor}\" width=\"#{_width}\" height=\"#{_height}\" name=\"#{_flashID}\" allowFullScreen=\"#{_allowFullScreen}\" align=\"middle\" allowScriptAccess=\"always\" type=\"application/x-shockwave-flash\" pluginspage=\"http://www.macromedia.com/go/getflashplayer\"/>"
  s << '</object>'
end

def naverPutObj(mechanObj, _imageURL, _imageWidth, _imageHeight, _first_img = false)
  str = ""
  # Flash
  if _imageURL.downcase.index(".swf") != nil or _imageURL.downcase.index(".flv") != nil
    if _imageURL.downcase.index(".swf") != nil
      if not File::exists?("/var/www/webtoon/tmp/#{_imageURL.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}")
        _data = mechanObj.get("http://#{_imageURL.gsub(/\?[\w\W]*$/, "")}").body
        if _data != nil
          File.open("/var/www/webtoon/tmp/#{_imageURL.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}", "w") do |f|
            f.write(_data)
          end
        end
      end
      str << flashObj(_imageURL.gsub(/\//, "@"), id, _imageWidth, _imageHeight, "transparent", "", "", "")
    else
      if not File::exists?("/var/www/webtoon/tmp/#{_imageURL.gsub(/\//, "@")}")
        _data = mechanObj.get("http://flash.comic.naver.com/webtoon/flvPlayer.swf").body
        if _data != nil
          File.open("/var/www/webtoon/tmp/#{"flash.comic.naver.com/webtoon/flvPlayer.swf".gsub(/\//, "@")}", "w") do |f|
            f.write(_data)
          end
        end
      end
      str << flashObj("/webtoon/tmp/#{"flash.comic.naver.com/webtoon/flvPlayer.swf".gsub(/\//, "@")}", "flvPlayer", "640", "395", "transparent", "flvURL=#{_imageURL}&imgURL=http://static.comic.naver.com/staticImages/COMICWEB/NAVER/images/flash/#{id}/flv.jpg&autoPlay=true&defaultVolume=0.5&flvWidth=640&flvHeight=360", "#FFFFFF", true)
    end
  # Image
  else
    if not File::exists?("/var/www/webtoon/tmp/#{_imageURL.gsub(/\//, "@")}")
      _data = mechanObj.get("http://#{_imageURL}").body
      if _data != nil
        File.open("/var/www/webtoon/tmp/#{_imageURL.gsub(/\//, "@")}", "w") do |f|
          f.write(_data)
        end
      end
    end
    if _first_img
      str << "<img src=\"/webtoon/tmp/#{_imageURL.gsub(/\//, "@")}\" onload=\"location.replace('#title_area');\">"
    else
      str << "<img src=\"/webtoon/tmp/#{_imageURL.gsub(/\//, "@")}\">"
    end
  end
  str
end

puts "Content-Type: text/html; charset=utf-8\n\n"

put = CGI.new
site = put.params["site"][0]
id = put.params["id"][0]
num = put.params["num"][0]

btnColor = {
  "buttonA" => "#FAFAFA",
  "buttonB" => "#EAEAEA",
  "saved" => "#88DD88",
  "saved_up" => "#DD8888",
  "saved_finish" => "#888888",
  "link" => "#0066CC"}

a = Mechanize.new

# Naver 웹툰
if site == "naver"
  resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}&seq=#{num}"

  _title = '<div id="title_area">'
  _content = '<div id="content_area">'

  # 웹툰 제목, 작가, 설명 출력
  resp.search('//div[@class="dsc"]').each {|r|
    comic_title, writer = $1, $2 if r.search('h2')[0].inner_html =~ /([\w\W]*)<em>([\w\W]*)<\/em>/
    if resp.body =~ /<p class="txt">([\w\W]*)<\/p>[\w\W]*<ul class="btn_group">[\w\W]*<div class="tit_area">/
      comic_text = $1.gsub(/^<br\/?>/i, "").gsub(/<br\/?>$/i, "").gsub(/<br\/?>/i, " ").gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;").gsub("'", "&#39;")
    end
    #comic_text = r.search('p[@class="txt"]')[0].inner_html.strip().gsub(/^<br\/?>/i, "").gsub(/<br\/?>$/i, "").gsub(/<br\/?>/i, " ")
    comic_title = comic_title.strip()
    writer = writer.strip().gsub(/^<span>\s*/i, "").gsub(/\s*<\/span>/i, "")
    _title << "<div style=\"padding: 15px 0px 15px 0px; background-color: #{btnColor["buttonB"]};\">#{comic_title} - #{writer}<br/><small style=\"font-size: 12px;\">#{comic_text}</small><br/><br/>"
  }
  # 웹툰 회, 날짜 출력
  resp.search('//div[@class="tit_area"]').each {|r|
    title = r.search('div[@class="view"]/h3')[0].inner_html
    date = r.search('div[@class="vote_lst"]/dl[@class="rt"]/dd[@class="date"]')[0].inner_html
    _title << "<b>#{title}</b></div><small id=\"toon_date\">#{date}</small>"
  }

  # BGM 출력
  resp.search('//div[@id="bgm_player"]').each {|r|
    r.search('script').each {|e|
      bgmURL = $1 if e.inner_html =~ /showMusicPlayer\("http:\/\/(.*)"\);/
      if not File::exists?("/var/www/webtoon/tmp/#{bgmURL.gsub(/\//, "@")}")
        _data = a.get("http://#{bgmURL}").body
        if _data != nil
          File.open("/var/www/webtoon/tmp/#{bgmURL.gsub(/\//, "@")}", "w") do |f|
            f.write(_data)
          end
        end
      end
      if ENV["HTTP_USER_AGENT"] =~ /MSIE/
        _content << '<script>play_status = "play";</script>'
        _content << '<div id="toonBGM" style="float: left; position: absolute;">'
        _content << '<span style="color: gray; cursor: default;">BGM</span><br/>'
        _content << '<span id="BGM_play_pause" style="color: gray; cursor: pointer;" onclick="toggle_play_pause(0);">∥</span>'
        _content << '<span id="BGM_stop" style="color: gray; cursor: pointer;" onclick="toggle_play_pause(1);">■</span>'
        _content << '<div id="music_player" style="display: none;">'
      else
        _content << '<div id="toonBGM" style="float: left; position: absolute;">'
        _content << '<span style="color: gray; cursor: default;">BGM</span><br/>'
        _content << '<span id="BGM_play_pause" style="color: gray; cursor: pointer;" onclick="toggle_play_pause(2);">■</span>'
        _content << '<div id="music_player">'
      end
      _content << '<object id="music_player_obj" classid="CLSID:6BF52A52-394A-11d3-B153-00C04F79FAA6" width="0" height="0">'
      _content << "<param name=\"URL\" value=\"/webtoon/tmp#{bgmURL.gsub(/\//, "@")}\"/>"
      _content << '<param name="AutoStart" value="1"/>'
      _content << '<param name="uiMode" value="none"/>'
      _content << '<param name="StretchToFit" value="1"/>'
      _content << '<param name="invokeURLs" value="false"/>'
      _content << '<param name="WindowlessVideo" value="1"/>'
      _content << '<param name="Volume" value="50"/>'
      _content << "<embed src=\"/webtoon/tmp/#{bgmURL.gsub(/\//, "@")}\" type=\"application/x-mplayer2\" pluginspage=\"http://www.microsoft.com/Windows/MediaPlayer/\" width=\"0\" height=\"0\"/>"
      _content << '</object></div>'
      _content << '</div><br/><br/>'
    }
  }

  # 스크롤 형식의 웹툰
  resp.search('//div[@class="wt_viewer"]').each {|r|
    imageList = nil
    imageWidth = nil
    imageHeight = nil
    check_link = nil
    link_url = nil
    resp.search('//head/script[last()]')[0].inner_html.strip.split(/;\s*\n/).map(&:strip).each {|v|
      if v =~ /imageList\s*=\s*\[([\w\W]*)\]/
        imageList = $1.split(/\s*,\s*/).map {|item| $1 if item =~ /"http:\/\/(.*)"/}
      elsif v =~ /var\s*imageWidth\s*=\s*\[([\w\W]*)\]/
        imageWidth = $1.split(/\s*,\s*/).map(&:strip)
      elsif v =~ /var\s*imageHeight\s*=\s*\[([\w\W]*)\]/
        imageHeight = $1.split(/\s*,\s*/).map(&:strip)
      elsif v =~ /var\s*lastImageYN\s*=\s*"(.*)"/
        check_link = ($1.strip == "Y") ? true : false
      elsif v =~ /aContent\.push\('<a\s+href="([\w\W]*)"\s*>\s*<[\w\W]*>\s*<\/a>\s*'\)/
        link_url = $1
      end
    }
    first_img = true
    f_exist = true
    i = 0
    r.element_children.each {|v|
      # Image
      if v.name == "img"
        if first_img
          _content << naverPutObj(a, imageList[i], imageWidth[i], imageHeight[i], true)
          first_img = false
        else
          _content << naverPutObj(a, imageList[i], imageWidth[i], imageHeight[i])
        end
        i += 1
      # Flash
      elsif v.name == "script"
        if f_exist
          _content << '<script>$("#title_area").append("<small style=\'float: left;\'>Flash Exist</small>");document.getElementById("toonlist_area").style.height=parseInt(document.getElementById(\'toonlist_area\').clientHeight-(document.getElementById(\'content_area\').offsetTop-437))+\'px\';document.getElementById("toonlist_area").style.overflow="scroll";$(document).unbind("keydown");$(document).bind("keydown",function(e){bodyKeyDown(e,false);});location.replace("#title_area");</script>'
          f_exist = false
        end
        _content << naverPutObj(a, imageList[i], imageWidth[i], imageHeight[i])
        i += 1
      # a tag
      elsif v.name == "a"
        (imageList.length - 1 - i).times {
          _content << naverPutObj(a, imageList[i], imageWidth[i], imageHeight[i])
          i += 1
        }
        _content << "<a target=\"_blank\" href=\"#{link_url}\">"
        if not File::exists?("/var/www/webtoon/tmp/#{imageList[i].gsub(/\//, "@")}")
          _data = a.get("http://#{imageList[i]}").body
          if _data != nil
            File.open("/var/www/webtoon/tmp/#{imageList[i].gsub(/\//, "@")}", "w") do |f|
              f.write(_data)
            end
          end
        end
        _content << "<img src=\"/webtoon/tmp/#{imageList[i].gsub(/\//, "@")}\"></a>"
        i += 1
      # br tag
      elsif v.name == "br"
        _content << "<br/>"
      # 예외 alert
      else
        _content << "<script>alert('예상하지 못한 태그 <#{v.name}>을 관리자에게 알려주세요.');</script>"
      end
    }
    (i..imageList.length - 1).each {|idx|
      if check_link and idx == imageList.length - 1
        _content << "<a target=\"_blank\" href=\"#{link_url}\">"
        if not File::exists?("/var/www/webtoon/tmp/#{imageList[idx].gsub(/\//, "@")}")
          _data = a.get("http://#{imageList[idx]}").body
          if _data != nil
            File.open("/var/www/webtoon/tmp/#{imageList[idx].gsub(/\//, "@")}", "w") do |f|
              f.write(_data)
            end
          end
        end
        _content << "<img src=\"/webtoon/tmp/#{imageList[idx].gsub(/\//, "@")}\"></a>"
      else
        _content << naverPutObj(a, imageList[idx], imageWidth[idx], imageHeight[idx])
      end
    }
  }

  # 만화책 형식의 웹툰
  resp.search('//div[@class="view_group"]').each {|r|
    count = 0
    r.search('div[@class="book_viewer"]/div[@class="flip-cached_page"]/div').each {|v|
      v.search('img').each {|e|
        if e.attributes["class"].to_s =~ /real_url\(http:\/\/(.*)\)/
          url = $1
          if not File::exists?("/var/www/webtoon/tmp/#{url.gsub(/\//, "@")}")
            _data = a.get("http://#{url}").body
            if _data != nil
              File.open("/var/www/webtoon/tmp/#{url.gsub(/\//, "@")}", "w") do |f|
                f.write(_data)
              end
            end
          end
          if count <= 1
            _content << "<hr id=\"anchor_0\" style=\"width: 80%; height: 1px; border: 0px;\"/>" if count == 0
            _content << "<img src=\"/webtoon/tmp/#{url.gsub(/\//, "@")}\" style=\"display: inline; width: 470px; height: 670px;\" onload=\"location.replace('#title_area');\">"
            count += 1
          else
            _content << ((count % 2 == 0) ? "<br/><br/><br/><hr id=\"anchor_#{count / 2}\" style=\"width: 80%; height: 1px; border: 0px;\"/>" : "")
            _content << "<img src=\"/webtoon/tmp/#{url.gsub(/\//, "@")}\" style=\"display: inline; width: 470px; height: 670px;\">"
            count += 1
          end
        end
      }
    }
    _content << '<br/>'
  }

  # 작가 블로그, 다른 작품 출력
  resp.search('//script').each {|r|
    if r.inner_html =~ /artistData/
      _content << '<br/><br/>'
      _content << '<div id="artist_area" style="width: 85%; clear: both; margin: 0 auto;">'
      _content << '<table id="artist_info" align="right"><tr>'
      _content << "<td><div style=\"text-align: center; width: 100px; margin: 0px 10px 0px 10px; cursor: pointer; background-color: #{btnColor["buttonB"]};\" onclick=\"show_artist_table(0);\">블로그</div></td>"
      _content << "<td><div style=\"text-align: center; width: 100px; margin: 0px 10px 0px 10px; cursor: pointer; background-color: #{btnColor["buttonB"]};\" onclick=\"show_artist_table(1);\">다른 작품</div></td>"
      _content << '</tr><tr style="font-size: 13px;">'
      _blog = '<td><div id="artist_blog" style="display: none;">'
      _other = '<td><div id="artist_other" style="display: none;">'
      if r.inner_html =~ /artistData\s*=\s*\[([\w\W]*)\];[\w\W]*var actionRunner;/
        _info = $1.scan(/\{"artistId" : (\d+),[\s\n\r]*"nickname": '(.*)',[\s\n\r]*"blogUrl" : '(.*)'[\s\n\r]*\}/).collect {|artistId, nickname, blogUrl|
          { "artistId" => artistId, "nickname" => nickname, "blogUrl" => blogUrl }
        }
      end
      _info.each {|v|
        _blog << "<a href=\"#{v["blogUrl"]}\" target=\"_blank\">#{v["nickname"]}</a><br/>" if v["blogUrl"] != ""
        _other << "<span style=\"cursor: pointer; color: #{btnColor["link"]}; text-decoration: underline;\" onclick=\"getOtherToon(#{v["artistId"]});\">#{v["nickname"]} &gt;&gt;</span><br/>"
      }
      _blog << '</div></td>'
      _other << '</div></td>'
      _content << _blog
      _content << _other
      _content << '</tr><tr>'
      _content << '<td colspan="2"><div id="artist_otherlist"></div></td>'
      _content << '</tr></table></div>'
    end
  }

  # 작가의 말, 별점 출력
  _writerCmt = $1.gsub("<", "&lt;").gsub(">", "&gt;").gsub(/&lt;br&gt;/i, "<br>") if resp.body =~ /<div\s+class="writer_info">[\w\W]*<p>([\w\W]*)<\/p>\s*<ul\s+class="btn_group">[\w\W]*<\/div>/
  _rating = resp.search('//span[@id="bottomPointTotalNumber"]/strong')[0].inner_html
  _ratingPerson = resp.search('//span[@class="pointTotalPerson"]/em')[0].inner_html
  _content << "<div id=\"writer_info\" style=\"width: 85%; text-align: left; clear: both; margin: 0 auto;\"><div style=\"background-color: #{btnColor["buttonB"]}; padding: 2px 15px 2px 15px;\"><b>작가의 말</b></div><p style=\"padding: 0px 20px 0px 20px;\">#{_writerCmt}</p><p style=\"padding: 0px 20px 0px 20px; text-align: right;\">별점 #{_rating} (#{_ratingPerson}명)</p></div></br>"

  _title << '</div>'
  _content << '</div>'

  puts _title
  puts '<br/>'
  puts _content
  puts "<script>setTimeout(\"location.replace('#title_area');\", 100);</script>"
# Daum 웹툰
elsif site == "daum"
  resp = a.get "http://cartoon.media.daum.net/webtoon/viewer/#{num}"

  _title = '<div id="title_area">'
  _content = '<div id="content_area">'

  # 웹툰 제목, 작가, 설명 출력
  comic_title = ""
  resp.search('//div[@class="episode_info"]').each {|r|
    comic_title = r.search('a[@class="title"]')[0].inner_html.strip()
    _title << "<div style=\"padding: 15px 0px 15px 0px; background-color: #{btnColor["buttonB"]};\"></div>"
  }
  # 웹툰 회, 날짜 출력
  title = resp.search('//div[@class="others"]/span/span[@class="episode_title"]')[0].inner_html.gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;").gsub("'", "&#39;")
  _title << "<small id=\"toon_date\"></small>"
  _title << "<script>$('#title_area div').append('#{comic_title} - ' + toonInfo['#{id}'][0] + '<br/><small style=\"font-size: 12px;\">' + toonInfo['#{id}'][1] + '</small><br/><br/><b>#{title}</b>');$('#toon_date').html(dateList['#{id}'][numList['#{id}'].indexOf(#{num})]);</script>"

  # 스크롤 형식의 웹툰
  if resp.search('//div[@class="img_list_wrap"]').length > 0
    count = 1
    toon_resp = JSON.parse(a.post("http://cartoon.media.daum.net/webtoon/viewer_images.js?webtoon_episode_id=#{num}").body)
    toon_resp["images"].each {|r|
      url = $1 if r["url"] =~ /http:\/\/(.+)/

      if r["mediaType"] == "image"
        if not File::exists?("/var/www/webtoon/tmp/#{url.gsub(/\//, "@")}")
          _data = a.get("http://#{url}").body
          if _data != nil
            File.open("/var/www/webtoon/tmp/#{url.gsub(/\//, "@")}", "w") do |f|
              f.write(_data)
            end
          end
        end
        if count == 1
          _content << "<img src=\"/webtoon/tmp/#{url.gsub(/\//, "@")}\" width=\"#{r["width"]}\" onload=\"location.replace('#title_area');\"/>"
        else
          _content << "<img src=\"/webtoon/tmp/#{url.gsub(/\//, "@")}\" width=\"#{r["width"]}\"/>"
        end
      else
        daum_tvpot = (url =~ /flvs\.daum\.net\/flvPlayer\.swf/) ? true : false
        if not daum_tvpot and not File::exists?("/var/www/webtoon/tmp/#{url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}")
          _data = a.get("http://#{url.gsub(/\?[\w\W]*$/, "")}").body
          if _data != nil
            File.open("/var/www/webtoon/tmp/#{url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}", "w") do |f|
              f.write(_data)
            end
          end
        end
        if r["mediaType"] == "flash"
          if daum_tvpot
            _content << "<iframe src=\"http://#{url}\" width=\"700\" height=\"560\" frameborder=\"0\"></iframe>"
          else
            _content << flashObj(url.gsub(/\//, "@"), "flash#{count}", 700, 560, "transparent")
            count += 1
          end
        elsif r["mediaType"] == "movie"
          if daum_tvpot
            _content << "<iframe src=\"http://#{url}\" width=\"502\" height=\"399\" frameborder=\"0\"></iframe>"
          else
            _content << flashObj(url.gsub(/\//, "@"), "flash#{count}", 502, 399, "transparent")
            count += 1
          end
        elsif r["mediaType"] == "hdmovie"
          if daum_tvpot
            _content << "<iframe src=\"http://#{url}\" width=\"760\" height=\"450\" frameborder=\"0\"></iframe>"
          else
            _content << flashObj(url.gsub(/\//, "@"), "flash#{count}", 760, 450, "transparent")
            count += 1
          end
        end
      end
    }
    _content << '<br/>'
    resp.search('//div[@class="img_list"]/div[@class="by_daum"]').each {|r|
      url = "photo-section.daum-img.net/-cartoon10/img/published.png"
      if not File::exists?("/var/www/webtoon/tmp/#{url.gsub(/\//, "@")}")
        _data = a.get("http://#{url}").body
        if _data != nil
          File.open("/var/www/webtoon/tmp/#{url.gsub(/\//, "@")}", "w") do |f|
            f.write(_data)
          end
        end
      end
      _content << "<img src=\"/webtoon/tmp/#{url.gsub(/\//, "@")}\"/>"
    }
  # 만화책 형식의 웹툰
  else
    _content << "<iframe width=\"95%\" height=\"3600\" src=\"http://cartoon.media.daum.net/webtoon/viewer/#{num}\" onload=\"location.replace('#title_area');\"></iframe>"
=begin
    _ids, _recentId, _nick = $1, $2, $3 if resp.search('//div[@class="img_list"]/script')[0].inner_html =~ /Webtoon\.EmbedViewer\.init\('([\d,]*)','(\d+)','(.*)'\);/
    _url = "photo-section.daum-img.net/-cartoon10/swf/webtoon/GaroViewer2011.swf"
    if not File::exists?("/var/www/webtoon/tmp/#{_url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}")
      _data = a.get("http://#{_url.gsub(/\?[\w\W]*$/, "")}").body
      if _data != nil
        File.open("/var/www/webtoon/tmp/#{_url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}", "w") do |f|
          f.write(_data)
        end
      end
    end
    _content << flashObj(_url.gsub(/\//, "@") + "?v=21&episode_ids=#{_ids}&recent_id=#{_recentId}&img_cnt=&page_no=1", 'viewerFla', 940, 700, 'transparent');
=end
  end

  # 작가 블로그, 다른 작품 출력
  _content << "<br/><br/>"
  _content << '<div id="artist_area" style="width: 85%; clear: both; margin: 0 auto;">'
  _content << '<table id="artist_info" align="right"><tr>'
  _content << "<td><div style=\"text-align: center; width: 100px; margin: 0px 10px 0px 10px; cursor: pointer; background-color: #{btnColor["buttonB"]};\" onclick=\"show_artist_table(0);\">다른 작품</div></td>"
  _content << "<td><div style=\"text-align: center; width: 100px; margin: 0px 10px 0px 10px; cursor: pointer; background-color: #{btnColor["buttonB"]};\" onclick=\"show_artist_table(1);\">갤러리</div></td>"
  _content << "</tr><tr>"
  _content << '<td colspan="2"><div id="artist_otherlist"></div></td>'
  _content << '</tr></table></div>'

  _title << '</div>'
  _content << '</div>'

  puts _title
  puts '<br/>'
  puts _content
  puts '<br/><br/>'
  puts "<script>setTimeout(\"location.replace('#title_area');\", 100);</script>"
end
