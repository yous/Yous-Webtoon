<?php
  if (strstr($_SERVER["HTTP_USER_AGENT"], "Mobile") && $_GET["pc"] != "y") {
    header("Location: m");
  }
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>Yous Webtoon Viewer</title>
    <link rel="stylesheet" type="text/css" href="/webtoon/style.css"/>
    <script type="text/javascript" src="/webtoon/jquery-1.6.3.js"></script>
    <script type="text/javascript" src="/webtoon/css_browser_selector.js"></script>
    <script type="text/javascript" src="/webtoon/script.js"></script>
    <script>
      $(document).ready(function() {
        $(window).resize(function() { resizeWidth(); });
        resizeWidth();
        toonlist_area_init();
        $(this).bind("keydown", function(e) { bodyKeyDown(e, true); });
        $("#login_area").bind("focusin", function() { $(document).unbind("keydown");$(document).bind("keydown", function(e) { loginKeyDown(e); }); });
        $("#login_area").bind("focusout", function() { $(document).unbind("keydown");$(document).bind("keydown", function(e) { bodyKeyDown(e, true); }); });
        if (navigator.appVersion.indexOf("MSIE") != -1)
        {
          $("#ID").css("display", "inline");
          $("#PW").css("display", "inline");
        }
        $("#login").css("color", btnColor["link"]);
        $("#join").css("color", btnColor["link"]);
        $("#login").bind("click", function() { login(); });
        $("#join").bind("click", function() { join(); });
        $("#login").bind("keydown", function(e) { spanKeyDown("login", e); });
        $("#join").bind("keydown", function(e) { spanKeyDown("join", e); });
        $("#user_id").focus();
        $(window).bind("beforeunload", function() { logout(); });
      });
    </script>
  </head>
  <body>
    <div id="main_area">
      <big><b>Yous</b> Webtoon Viewer</big><span id="loading" style="display: none;"><big><b> Loading</b></big></span>
      <div id="toonlist_area"></div>
      <div id="display_area"></div>
    </div>
    <div id="login_area">
      <span id="ID" style="display: none;">ID </span><input type="text" id="user_id" tabindex="1" placeholder="ID"/><br/>
      <span id="PW" style="display: none;">PW </span><input type="password" id="user_pw" tabindex="2" placeholder="Password"/><br/>
      <span id="login" tabindex="3">Login</span> <span id="join" tabindex="4">Join</span>
    </div>
    <table id="remote">
      <tr>
        <td colspan="4"><b>북마크</b></td>
      </tr>
      <tr>
        <td colspan="2"><input type="button" id="saveBM" value="저장" onclick="add_bookmark();" disabled="true"/><br/><small>(E)</small></td>
        <td colspan="2"><input type="button" id="moveBM" value="이동" onclick="go_to(3);" disabled="true"/><br/><small>(R)</small></td>
      </tr>
      <tr>
        <td colspan="4"><a id="url" target="_blank">주소 링크</a><hr/></td>
      </tr>
      <tr>
        <td><input type="button" id="firstBtn" class="arrowBtn" value="&lt;&lt;" onclick="go_to(-2);" disabled="true"/></td>
        <td><input type="button" id="prevBtn" class="arrowBtn" value="&lt;" onclick="go_to(-1);" disabled="true"/></td>
        <td><input type="button" id="nextBtn" class="arrowBtn" value="&gt;" onclick="go_to(1);" disabled="true"/></td>
        <td><input type="button" id="lastBtn" class="arrowBtn" value="&gt;&gt;" onclick="go_to(2);" disabled="true"/></td>
      </tr>
      <tr>
        <td colspan="2"><input type="text" id="inputNum"/>화</td>
        <td colspan="2"><input type="button" id="dirBtn" value="이동" onclick="go_to(0);" disabled="true"/></td>
      </tr>
      <tr>
        <td colspan="2"><input type="button" value="&uarr;" onclick="location.replace('#title_area');"/><br/><small>(^&uarr; or Q)</small></td>
        <td colspan="2"><input type="button" value="&darr;" onclick="window.scrollTo('0', document.body.clientHeight);"/><br/><small>(^&darr; or Z)</small></td>
      </tr>
      <tr>
        <td colspan="4"><hr/><small>(^&larr;) &uarr;(W) (^&rarr;)<br/>&larr;(A) &darr;(S) &rarr;(D)</small></td>
      </tr>
    </table>
    <a id="bottom">&nbsp;</a>
  </body>
</html>
