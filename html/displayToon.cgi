#!/usr/local/rvm/wrappers/ruby-1.9.3-p125@webtoon/ruby
# encoding: utf-8
require "rubygems"
require "mechanize"
require "json"
require "cgi"
require "cgi/session"

cgi = CGI.new
site = (cgi.has_key? "site") ? cgi.params["site"][0] : nil
id = (cgi.has_key? "id") ? cgi.params["id"][0] : nil
num = (cgi.has_key? "num") ? cgi.params["num"][0] : nil

def flashObj(_url, _flashID, _width, _height, _wmode = "transparent", _flashVars = "", _bgColor = "#FFFFFF", _allowFullScreen = true)
  return <<-HTML
    <object width="#{_width}" height="#{_height}" id="#{_flashID}" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0">
      <param name="allowScriptAccess" value="always"/>
      <param name="quality" value="high"/>
      <param name="menu" value="false"/>
      <param name="movie" value="/images/#{_url.gsub(/\//, "@")}"/>
      <param name="wmode" value="#{_wmode}"/>
      <param name="bgcolor" value="#{_bgColor}"/>
      <param name="FlashVars" value="#{_flashVars}"/>
      <param name="allowFullScreen" value="#{_allowFullScreen}"/>
      <embed src="/images/#{_url.gsub(/\//, "@")}" quality="high" wmode="#{_wmode}" menu="false" FlashVars="#{_flashVars}" bgcolor="#{_bgColor}" width="#{_width}" height="#{_height}" name="#{_flashID}" allowFullScreen="#{_allowFullScreen}" align="middle" allowScriptAccess="always" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"/>
    </object>
  HTML
end

def naverPutObj(mechanObj, id, _imageURL, _imageWidth, _imageHeight, _first_img = false)
  str = ""
  # Flash
  if _imageURL.downcase.index(".swf") != nil or _imageURL.downcase.index(".flv") != nil
    if _imageURL.downcase.index(".swf") != nil
      if not File::exists?("images/#{_imageURL.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}")
        _data = mechanObj.get("http://#{_imageURL.gsub(/\?[\w\W]*$/, "")}")
        _data.save("images/#{_imageURL.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}") if not _data.body.nil?
      end
      str << flashObj(_imageURL.gsub(/\//, "@"), id, _imageWidth, _imageHeight, "transparent", "", "", "")
    else
      if not File::exists?("images/#{_imageURL.gsub(/\//, "@")}")
        _data = mechanObj.get("http://flash.comic.naver.com/webtoon/flvPlayer.swf")
        _data.save("images/#{"flash.comic.naver.com/webtoon/flvPlayer.swf".gsub(/\//, "@")}") if not _data.body.nil?
      end
      str << flashObj("flash.comic.naver.com/webtoon/flvPlayer.swf".gsub(/\//, "@"), "flvPlayer", "640", "395", "transparent", "flvURL=http://#{_imageURL}&imgURL=http://static.comic.naver.com/staticImages/COMICWEB/NAVER/images/flash/#{id}/flv.jpg&autoPlay=true&defaultVolume=0.5&flvWidth=640&flvHeight=360", "#FFFFFF", true)
    end
  # Image
  else
    if not File::exists?("images/#{_imageURL.gsub(/\//, "@")}")
      _data = mechanObj.get("http://#{_imageURL}")
      _data.save("images/#{_imageURL.gsub(/\//, "@")}") if not _data.body.nil?
    end
    if _first_img
      str << "<img src=\"/images/#{_imageURL.gsub(/\//, "@")}\" onload=\"location.replace('#title_area');\">"
    else
      str << "<img src=\"/images/#{_imageURL.gsub(/\//, "@")}\">"
    end
  end
  str
end

puts "Content-Type: text/html; charset=utf-8\n\n"

if site != nil and id != nil and num != nil
  str = ""

  a = Mechanize.new
  a.history.max_size = 0

  # Naver 웹툰
  if site == "naver"
    resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}&seq=#{num}"

    # 성인 인증 웹툰
    if resp.search('//div[@id="log_adult"]').length > 0
      print_flag = false
      if cgi.cookies["SSID"] != nil
        begin
          session = CGI::Session.new(cgi, "session_id" => cgi.cookies["SSID"][0], "tmpdir" => File.join(File.dirname(__FILE__), "/../sess"), "new_session" => false)
        rescue
          print_flag = true
        end

        if session[site] != nil and session[site]["cookie"] != nil
          a = Mechanize.new
          a.cookie_jar = session[site]["cookie"]

          resp = a.get "http://comic.naver.com/webtoon/detail.nhn?titleId=#{id}&seq=#{num}"

          print_flag = true if resp.search('//div[@id="log_adult"]').length > 0
        else
          print_flag = true
        end
      else
        print_flag = true
      end

      if print_flag
        print <<-HTML
          <a href="#" onclick="window.open('auth.cgi?site=#{site}&id=#{id}&num=#{num}', 'auth', 'width=600, height=400');">성인 인증이 필요합니다.</a>
        HTML
        exit
      end
    end

    _title = '<div id="title_area">'
    _content = '<div id="content_area">'

    # 웹툰 제목, 작가, 설명 출력
    writer = nil
    resp.search('//div[@class="dsc"]').each do |r|
      comic_title, writer = $1, $2 if r.at('./h2').inner_html =~ /([\w\W]*)<em>([\w\W]*)<\/em>/
      if resp.body =~ /<p class="txt">([\w\W]*)<\/p>[\w\W]*<ul class="btn_group">[\w\W]*<div class="tit_area">/
        comic_text = $1.gsub(/^<br\/?>/i, "").gsub(/<br\/?>$/i, "").gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;").gsub("'", "&#39;").gsub(/&lt;br\/?&gt;/i, "<br/>").force_encoding("UTF-8")
      end
      #comic_text = r.at('./p[@class="txt"]').inner_html.strip().gsub(/^<br\/?>/i, "").gsub(/<br\/?>$/i, "").gsub(/<br\/?>/i, " ")
      comic_title = comic_title.strip()
      writer = writer.strip().gsub(/^<span>\s*/i, "").gsub(/\s*<\/span>/i, "")
      _title << <<-HTML
        <div id="title">
          #{comic_title} - #{writer}<br/>
          <small style="font-size: 12px;">#{comic_text}</small><br/><br/>
      HTML
    end
    # 웹툰 회 제목, 날짜 출력
    title = resp.at('//form[@name="reportForm"]/input[@name="itemTitle"]').attr("value").gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;").gsub("'", "&#39;")
      date = resp.at('//div[@class="section_spot"]/div[@class="tit_area"]/div[@class="vote_lst"]/dl[@class="rt"]/dd[@class="date"]').inner_html
    _title << "<b>#{title}</b></div><small id=\"toon_date\">#{date}</small>"

    # BGM 출력
    resp.search('//div[@id="bgm_player"]').each do |r|
      r.search('./script').each do |e|
        bgmURL = $1 if e.inner_html =~ /showMusicPlayer\("http:\/\/(.*)"\);/
        if not File::exists?("images/#{bgmURL.gsub(/\//, "@")}")
          _data = a.get("http://#{bgmURL}")
          _data.save("images/#{bgmURL.gsub(/\//, "@")}") if not _data.body.nil?
        end
        if ENV["HTTP_USER_AGENT"] =~ /MSIE/
          _content << <<-HTML
            <script>play_status = "play";</script>
            <div id="toonBGM">
              <span style="cursor: default;">BGM</span><br/>
              <span id="BGM_play_pause" onclick="toggle_play_pause(0);">∥</span>
              <span id="BGM_stop" onclick="toggle_play_pause(1);">■</span>
              <div id="music_player">
          HTML
        else
          _content << <<-HTML
            <div id="toonBGM">
              <span style="cursor: default;">BGM</span><br/>
              <span id="BGM_play_pause" onclick="toggle_play_pause(2);">■</span>
              <div id="music_player">
          HTML
        end
        _content << <<-HTML
                <object id="music_player_obj" classid="CLSID:6BF52A52-394A-11d3-B153-00C04F79FAA6" width="0" height="0">
                  <param name="URL" value="/images#{bgmURL.gsub(/\//, "@")}"/>
                  <param name="AutoStart" value="1"/>
                  <param name="uiMode" value="none"/>
                  <param name="StretchToFit" value="1"/>
                  <param name="invokeURLs" value="false"/>
                  <param name="WindowlessVideo" value="1"/>
                  <param name="Volume" value="50"/>
                  <embed src="/images/#{bgmURL.gsub(/\//, "@")}" type="application/x-mplayer2" pluginspage="http://www.microsoft.com/Windows/MediaPlayer/" width="0" height="0"/>
                </object>
              </div>
            </div><br/><br/>
        HTML
      end
    end

    # 스크롤 형식의 웹툰
    resp.search('//div[@class="wt_viewer"]').each do |r|
      imageList = nil
      imageWidth = nil
      imageHeight = nil
      check_link = nil
      link_url = nil
      resp.at('//head/script[last()]').inner_html.strip.split(/;\s*\n/).map(&:strip).each do |v|
        if v =~ /imageList\s*=\s*\[([\w\W]*)\]/
          imageList = $1.split(/\s*,\s*/).map {|item| $1 if item =~ /"http:\/\/(.*)"/}
        elsif v =~ /var\s*imageWidth\s*=\s*\[([\w\W]*)\]/
          imageWidth = $1.split(/\s*,\s*/).map(&:strip)
        elsif v =~ /var\s*imageHeight\s*=\s*\[([\w\W]*)\]/
          imageHeight = $1.split(/\s*,\s*/).map(&:strip)
        elsif v =~ /var\s*lastImageYN\s*=\s*"(.*)"/
          check_link = ($1.strip == "Y") ? true : false
        elsif v =~ /aContent\.push\('<a(\s+target="_blank")?\s+href="([\w\W]*)"\s*>\s*<[\w\W]*>\s*<\/a>\s*'\)/
          link_url = $2
        end
      end
      first_img = true
      f_exist = true
      i = 0
      r.element_children.each do |v|
        # Image
        if v.name == "img"
          if first_img
            _content << naverPutObj(a, id, imageList[i], imageWidth[i], imageHeight[i], true)
            first_img = false
          else
            _content << naverPutObj(a, id, imageList[i], imageWidth[i], imageHeight[i])
          end
          i += 1
        # Flash
        elsif v.name == "script"
          if f_exist
            _content << <<-HTML
              <script>
                $("#title_area").append("<small style='float: left;'>Flash Exist <span style='cursor: pointer;' onclick='toggle_toonlist();'>목록 접기/펼치기</span></small>");
                toggle_toonlist(true);
                location.replace("#title_area");
              </script>
            HTML
            f_exist = false
          end
          _content << naverPutObj(a, id, imageList[i], imageWidth[i], imageHeight[i])
          i += 1
        # a tag
        elsif v.name == "a"
          (imageList.length - 1 - i).times do
            _content << naverPutObj(a, id, imageList[i], imageWidth[i], imageHeight[i])
            i += 1
          end
          _content << "<a target=\"_blank\" href=\"#{link_url}\">"
          if not File::exists?("images/#{imageList[i].gsub(/\//, "@")}")
            _data = a.get("http://#{imageList[i]}")
            _data.save("images/#{imageList[i].gsub(/\//, "@")}") if not _data.body.nil?
          end
          _content << "<img src=\"/images/#{imageList[i].gsub(/\//, "@")}\"></a>"
          i += 1
        # br tag
        elsif v.name == "br"
          _content << "<br/>"
        # 예외 alert
        else
          _content << "<script>alert('예상하지 못한 태그 <#{v.name}>을 관리자에게 알려주세요.');</script>"
        end
      end
      (i..imageList.length - 1).each do |idx|
        if check_link and idx == imageList.length - 1
          _content << "<a target=\"_blank\" href=\"#{link_url}\">"
          if not File::exists?("images/#{imageList[idx].gsub(/\//, "@")}")
            _data = a.get("http://#{imageList[idx]}")
            _data.save("images/#{imageList[idx].gsub(/\//, "@")}") if not _data.body.nil?
          end
          _content << "<img src=\"/images/#{imageList[idx].gsub(/\//, "@")}\"></a>"
        else
          _content << naverPutObj(a, id, imageList[idx], imageWidth[idx], imageHeight[idx])
        end
      end
    end

    # 만화책 형식의 웹툰
    resp.search('//div[@class="view_group"]').each do |r|
      count = 0
      r.search('./div[@class="book_viewer"]/div[@class="flip-cached_page"]/div').each do |v|
        v.search('./img').each do |e|
          if e.attributes["class"].to_s =~ /real_url\(http:\/\/(.*)\)/
            url = $1
            if not File::exists?("images/#{url.gsub(/\//, "@")}")
              _data = a.get("http://#{url}")
              _data.save("images/#{url.gsub(/\//, "@")}") if not _data.body.nil?
            end
            if count % 2 == 0
              if count > 1
                _content << <<-HTML
                    <input type="button" value="&uarr;" style="position: relative; top: 650px;" onclick="scrollAnchor(-1);">
                    <input type="button" value="&darr;" style="position: relative; top: 650px;" onclick="scrollAnchor(1);">
                  </div><br/><br/><br/>
                HTML
              end
              _content << <<-HTML
                <hr id="anchor_#{count / 2}"/>
                <div style="position: relative; margin: 0 auto; width: 900px; height: 650px;">
              HTML
            end
            _content << <<-HTML
              <div style="position: absolute; width: 450px; height: 650px; left: #{(count % 2 == 0) ? 0 : 450}px;">
                <img src="/images/#{url.gsub(/\//, "@")}"#{(count <= 1) ? " onload=\"location.replace('#title_area');\"" : ""}/>
              </div>
            HTML
            count += 1
          end
        end
      end
      _content << <<-HTML
          <input type="button" value="&uarr;" style="position: relative; top: 650px;" onclick="scrollAnchor(-1);">
          <input type="button" value="&darr;" style="position: relative; top: 650px;" onclick="scrollAnchor(1);">"
        </div><br/>
      HTML
    end

    # 작가 블로그, 다른 작품 출력
    resp.search('//script').each do |r|
      if r.inner_html =~ /artistData/
        _content << <<-HTML
          <br/><br/>
          <div id="artist_area">
            <table id="artist_info" align="right">
              <tr>
                <td><div onclick="show_artist_table(0);">블로그</div></td>
                <td><div onclick="show_artist_table(1);">다른 작품</div></td>
              </tr>
              <tr style="font-size: 13px;">
        HTML
        _blog = '<td><div id="artist_blog" style="display: none;">'
        _other = '<td><div id="artist_other" style="display: none;">'
        if r.inner_html =~ /artistData\s*=\s*\[([^\]]*)\]/
          _info = $1.scan(/"artistId"\s*:\s*(\d+),[\s\n\r]*"nickname"\s*:\s*'([^']*)',[\s\n\r]*"blogUrl"\s*:\s*'([^']*)'/).collect {|artistId, nickname, blogUrl|
            { "artistId" => artistId, "nickname" => nickname, "blogUrl" => blogUrl }
          }
        end
        _info.each do |v|
          _blog << "<a href=\"#{v["blogUrl"]}\" target=\"_blank\">#{v["nickname"]}</a><br/>" if v["blogUrl"] != ""
          _other << "<span onclick=\"getOtherToon(#{v["artistId"]});\">#{v["nickname"]} &gt;&gt;</span><br/>"
        end
        _blog << '</div></td>'
        _other << '</div></td>'
        _content << _blog
        _content << _other
        _content << <<-HTML
              </tr>
              <tr>
                <td colspan="2">
                  <div id="artist_otherlist"></div>
                </td>
              </tr>
            </table>
          </div>
        HTML
      end
    end

    # 작가의 말, 별점 출력
    _writerCmt = $1.gsub("<", "&lt;").gsub(">", "&gt;").gsub(/&lt;br&gt;/i, "<br>").force_encoding("UTF-8") if resp.body =~ /<div\s+class="writer_info">[\w\W]*?<p>([\w\W]*?)<\/p>/
    _rating = resp.at('//span[@id="bottomPointTotalNumber"]/strong').inner_html
    _ratingPerson = resp.at('//span[@class="pointTotalPerson"]/em').inner_html
    _content << <<-HTML
      <div id="writer_info">
        <div>
          <b>작가의 말 (#{writer})</b>
        </div>
        <p style="padding: 0px 20px 0px 20px;">#{_writerCmt}</p>
        <p style="padding: 0px 20px 0px 20px; text-align: right;">별점 #{_rating} (#{_ratingPerson}명)</p>
      </div></br>
    HTML

    _title << '</div>'
    _content << '</div>'

    str << _title
    str << '<br/>'
    str << _content

    print str

  # Daum 웹툰
  elsif site == "daum"
    resp = a.get "http://cartoon.media.daum.net/webtoon/viewer/#{num}"

    # 로그인 필요한 웹툰
    return nil if resp.search('//div[@id="wrap"]/div[@id="content"]/form[@id="loginForm"]').length > 0

    _title = '<div id="title_area">'
    _content = '<div id="content_area">'

    # 웹툰 제목, 작가, 설명 출력
    comic_title = ""
    resp.search('//div[@class="episode_info"]').each do |r|
      comic_title = r.at('./a[@class="title"]').inner_html.strip()
      _title << '<div id="title"></div>'
    end
    # 웹툰 회, 날짜 출력
    title = resp.at('//div[@class="others"]/span/span[@class="episode_title"]').inner_html.gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;").gsub("'", "&#39;")
    _title << <<-HTML
      <small id="toon_date"></small>
      <script>
        $('#title_area div').append('#{comic_title} - ' + toonInfo['#{id}'][0] + '<br/><small style="font-size: 12px;">' + toonInfo['#{id}'][1] + '</small><br/><br/><b>#{title}</b>');
        $('#toon_date').html(dateList['#{id}'][numList['#{id}'].indexOf(#{num})]);
      </script>
    HTML

    # 스크롤 형식의 웹툰
    if resp.search('//div[@class="img_list_wrap"]').length > 0
      count = 1
      toon_resp = JSON.parse(a.post("http://cartoon.media.daum.net/webtoon/viewer_images.js?webtoon_episode_id=#{num}").body)
      toon_resp["images"].each do |r|
        url = $1 if r["url"] =~ /http:\/\/(.+)/

        if r["mediaType"] == "image"
          if not File::exists?("images/#{url.gsub(/\//, "@")}")
            _data = a.get("http://#{url}")
            _data.save("images/#{url.gsub(/\//, "@")}") if not _data.body.nil?
          end
          if count == 1
            _content << "<img src=\"/images/#{url.gsub(/\//, "@")}\" width=\"#{r["width"]}\" onload=\"location.replace('#title_area');\"/>"
          else
            _content << "<img src=\"/images/#{url.gsub(/\//, "@")}\" width=\"#{r["width"]}\"/>"
          end
        else
          daum_tvpot = (url =~ /flvs\.daum\.net\/flvPlayer\.swf/) ? true : false
          if not daum_tvpot and not File::exists?("images/#{url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}")
            _data = a.get("http://#{url.gsub(/\?[\w\W]*$/, "")}")
            _data.save("images/#{url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}") if not _data.body.nil?
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
      end
      _content << '<br/>'
      resp.search('//div[@class="img_list"]/div[@class="by_daum"]').each do |r|
        url = "photo-section.daum-img.net/-cartoon10/img/published.png"
        if not File::exists?("images/#{url.gsub(/\//, "@")}")
          _data = a.get("http://#{url}")
          _data.save("images/#{url.gsub(/\//, "@")}") if not _data.body.nil?
        end
        _content << "<img src=\"/images/#{url.gsub(/\//, "@")}\"/>"
      end
    # 만화책 형식의 웹툰
    else
      _content << "<iframe width=\"95%\" height=\"3600\" src=\"http://cartoon.media.daum.net/webtoon/viewer/#{num}\" onload=\"location.replace('#title_area');\"></iframe>"
=begin
      _ids, _recentId, _nick = $1, $2, $3 if resp.at('//div[@class="img_list"]/script').inner_html =~ /Webtoon\.EmbedViewer\.init\('([\d,]*)','(\d+)','(.*)'\);/
      _url = "photo-section.daum-img.net/-cartoon10/swf/webtoon/GaroViewer2011.swf"
      if not File::exists?("images/#{_url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}")
        _data = a.get("http://#{_url.gsub(/\?[\w\W]*$/, "")}")
        _data.save("images/#{_url.gsub(/\//, "@").gsub(/\?[\w\W]*$/, "")}") if not _data.body.nil?
      end
      _content << flashObj(_url.gsub(/\//, "@") + "?v=21&episode_ids=#{_ids}&recent_id=#{_recentId}&img_cnt=&page_no=1", 'viewerFla', 940, 700, 'transparent');
=end
    end

    # 관련 웹툰, 작품 노트 출력
    _content << <<-HTML
      <br/><br/>
      <div id="artist_area">
        <table id="artist_info" align="right">
          <tr>
            <td><div onclick="show_artist_table(0);">관련 웹툰</div></td>
            <td><div onclick="show_artist_table(1);">작품 노트</div></td>
            </tr><tr>
            <td colspan="2"><div id="artist_otherlist"></div></td>
          </tr>
        </table>
      </div>
    HTML

    _title << '</div>'
    _content << '</div>'

    str << _title
    str << '<br/>'
    str << _content
    str << '<br/><br/>'

    print str

  # Yahoo 웹툰
  elsif site == "yahoo"
    resp = JSON.parse(a.get("http://kr.news.yahoo.com/cartoon/series/get_series.php?sidx=#{num}").body.force_encoding("CP949").encode("UTF-8").gsub(/<!-[^>]+>/, "").gsub('SEQ', '"SEQ"').gsub('URL', '"URL"'))

    _title = '<div id="title_area">'
    _content = '<div id="content_area">'

    # 웹툰 제목, 작가, 설명, 회 제목, 날짜 출력
    _title << <<-HTML
      <div id="title"></div>
      <small id="toon_date">#{resp["DATE"]}</small>
      <script>
        $('#title_area div').append(toonInfo[#{id}][0] + ' - #{resp["NAME"]}<br/><small style="font-size: 12px;">' + toonInfo[#{id}][1] + '</small><br/><br/><b>#{resp["TITLE"]}</b>');
      </script>
    HTML

    # 웹툰 출력
    resp["IMAGES"].each_with_index do |img, idx|
      url = $1.strip if img["URL"] =~ /http:\/\/([\w\W]*)/

      if not File::exists?("images/#{url.gsub(/\//, "@")}")
        _data = a.get("http://#{url}")
        _data.save("images/#{url.gsub(/\//, "@")}") if not _data.body.nil?
      end

      if idx == 0
        _content << "<img src=\"/images/#{url.gsub(/\//, "@")}\" onload=\"location.replace('#title_area');\"/>"
      else
        _content << "<img src=\"/images/#{url.gsub(/\//, "@")}\"/>"
      end
    end

    _title << '</div>'
    _content << '</div>'

    str << _title
    str << '<br/>'
    str << _content
    str << '<br/><br/>'

    print str

  # Stoo 웹툰
  elsif site == "stoo"
    resp = a.get "http://stoo.asiae.co.kr/cartoon/ctview.htm?sc3=#{id}&id=#{num}"

    # 성인 인증 웹툰
    return nil if resp.at('script').inner_html =~ /document\.location\.href\s*=\s*\"http:\/\/user\.asiae\.co\.kr\/19_login\.htm\"\s*;/

    _title = '<div id="title_area">'
    _content = '<div id="content_area">'

    # 웹툰 제목 출력
    comic_title = resp.at('//div[@id="content"]/div[@class="location"]/strong/a').attr("title")
    _title << '<div id="title"></div>'

    # 작가, 설명, 웹툰 회, 날짜 출력
    resp.search('//div[@id="content"]/div[@class="cttop"]').each do |r|
      title = r.at('./h3/span').inner_html.encode("UTF-8").strip.gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;").gsub("'", "&#39;")
      date = "#{$1}.#{$2}.#{$3}" if r.at('./span[@class="date"]').inner_html.encode("UTF-8") =~ /(\d+)년\s+(\d+)월\s+(\d+)일/
      _title << "<small id=\"toon_date\">#{date}</small>"
    end
    _title << <<-HTML
      <script>
        $('#title_area div').append('#{comic_title} - ' + toonInfo[#{id}][0] + '<br/><small style="font-size: 12px;">' + toonInfo[#{id}][1] + '</small><br/><br/><b>#{title}</b>');
      </script>
    HTML

    # 웹툰 출력
    while true
      resp.search('//div[@id="content"]/div[@class="ct_box"]/div[@class="ctview"]/img').each_with_index do |img, idx|
        url = $1.strip if img.attr("src") =~ /http:\/\/([\w\W]*)/

        if not File::exists?("images/#{url.gsub(/\//, "@")}")
          _data = a.get("http://#{url}")
          _data.save("images/#{url.gsub(/\//, "@")}") if not _data.body.nil?
        end

        if idx == 0
          _content << "<img src=\"/images/#{url.gsub(/\//, "@")}\" onload=\"location.replace('#title_area');\"/>"
        else
          _content << "<img src=\"/images/#{url.gsub(/\//, "@")}\"/>"
        end
      end
      if resp.search('//div[@id="content"]/div[@class="ct_box"]/div[@class="ctview"]/p').length > 0 and resp.at('//div[@id="content"]/div[@class="ct_box"]/div[@class="ctview"]/p/a[2]').attr("href") =~ /(\/cartoon\/ctview\.htm\?[\w\W]*)/
        resp = a.get "http://stoo.asiae.co.kr#{$1}"
      else
        break
      end
    end

    _title << '</div>'
    _content << '</div>'

    str << _title
    str << '<br/>'
    str << _content
    str << '<br/><br/>'

    print str
  end
end
