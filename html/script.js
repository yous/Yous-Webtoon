(function() {
  window.classNaver = function()
  {
    if (_Naver == null)
      _Naver = new classNaver();
    return _Naver;
  }

  var _Naver = null;
  var classNaver = function()
  {
    this.src = function() { return "http://comic.naver.com/webtoon/detail.nhn?titleId=" + id + "&no=" + numList[id][num - 1]; }
  }
})();

(function() {
  window.classDaum = function()
  {
    if (_Daum == null)
      _Daum = new classDaum();
    return _Daum;
  }

  var _Daum = null;
  var classDaum = function()
  {
    this.src = function() { return "http://cartoon.media.daum.net/webtoon/viewer/" + numList[id][num - 1]; }
  }
})();

(function() {
  window.classYahoo = function()
  {
    if (_Yahoo == null)
      _Yahoo = new classYahoo();
    return _Yahoo;
  }

  var _Yahoo = null;
  var classYahoo = function()
  {
    this.src = function() { return "http://kr.news.yahoo.com/service/cartoon/shellview2.htm?linkid=series_cartoon&sidx=" + numList[id][num - 1] + "&widx=" + id; }
  }
})();

(function() {
  window.classStoo = function()
  {
    if (_Stoo == null)
      _Stoo = new classStoo();
    return _Stoo;
  }

  var _Stoo = null;
  var classStoo = function()
  {
    this.src = function() { return "http://stoo.asiae.co.kr/cartoon/ctview.htm?sc3=" + id + "&id=" + numList[id][num - 1]; }
  }
})();

var Naver = new classNaver();
var Daum = new classDaum();
var Yahoo = new classYahoo();
var Stoo = new classStoo();
var sites = {
  "naver" : Naver,
  "daum" : Daum,
  "yahoo" : Yahoo,
  "stoo" : Stoo
};

// width 자동 조절
function resizeWidth()
{
  $("#main_area").css("width", $(window).width() - $("#remote").width() - 21 + "px");
  $("#display_iframe").css("height", $(window).height() + "px");
}

// remote scroll 자동 조절
function scrollControl()
{
  var _height = $(window).height() / 2 - 160;
  var _scroll = $(window).scrollTop();
  if (_scroll + _height < 80)
  {
    $("#remote").css("top", "80px");
    $("#remote").css("position", "absolute");
  }
  else
  {
    $("#remote").css("top", _height + "px");
    $("#remote").css("position", "fixed");
  }
}

// remote 버튼 정리
function change_remote()
{
  $("#saveBM").attr("disabled", (!id || num == 1 || num == toonBM[id]) ? true : false);
  $("#moveBM").attr("disabled", (!id || !toonBM[id] || num == toonBM[id]) ? true : false);
  $("#firstBtn").attr("disabled", (!id || num == 1) ? true : false);
  $("#lastBtn").attr("disabled", (!id || num == numList[id].length) ? true : false);
  $("#prevBtn").attr("disabled", (!id || num == 1) ? true : false);
  $("#nextBtn").attr("disabled", (!id || num == numList[id].length) ? true : false);
  $("#dirBtn").attr("disabled", (!id) ? true : false);

  var src = "";
  if (site)
  {
    src = sites[site].src();
    $("#inputNum").val(num);
  }

  $("#url").removeAttr("href");
  if (src != "")
    $("#url").attr("href", src);
}

// 웹툰 사이트 변경
function site_change(_site)
{
  site = null;
  id = null;
  num = null;
  daysToon = new Object();
  toonInfo = new Object();
  numList = new Object();
  toonBM = new Object();
  change_remote();

  $("#toonlist_area").html("");
  $("#display_area").html("");
  $("#display_iframe").attr("src", "");
  $("#inputNum").val("");
  $("#url").removeAttr("href");
  $.get(
    "/" + _site + ".json",
    function (json) {
      site = _site;
      daysToon = json["daysToon"];
      toonInfo = json["toonInfo"];
      numList = json["numList"];
      $("<span>")
        .addClass("table_toggle_button")
        .click(function() { show_table(); })
        .html("완결 웹툰")
        .appendTo("#toonlist_area");
      $("<br/>").appendTo("#toonlist_area");
      $("<div>")
        .attr("id", "current_toonlist")
        .addClass("toonlist")
        .appendTo("#toonlist_area");
      var days = ["월", "화", "수", "목", "금", "토", "일"];
      for (var i = 0; i < 7; i++)
      {
        var dayDiv = $("<div>");
        $("<div>")
          .css("font-weight", "bold")
          .html(days[i])
          .appendTo(dayDiv);
        for (var j = 0; j < daysToon[i].length; j++)
        {
          $("<div>")
            .attr("name", daysToon[i][j])
            .addClass("current_toon")
            .attr("title", toonInfo[daysToon[i][j]]["title"])
            .click(function() { viewToon($(this).attr("name")); })
            .html(toonInfo[daysToon[i][j]]["title"] + (toonInfo[daysToon[i][j]]["new"] ? "<small>(NEW)</small>" : "") + (toonInfo[daysToon[i][j]]["up"] ? "<small>(UP)</small>" : ""))
            .appendTo(dayDiv);
        }
        dayDiv.appendTo("#current_toonlist");
      }
      $("<div>")
        .attr("id", "finished_toonlist")
        .addClass("toonlist")
        .css("display", "none")
        .appendTo("#toonlist_area");
      var dayDiv = [];
      for (var i = 0; i < 7; i++)
        dayDiv.push($("<div>"));
      for (var i = 0; i < daysToon[7].length; i++)
      {
        $("<div>")
          .attr("name", daysToon[7][i])
          .addClass("finished_toon")
          .attr("title", toonInfo[daysToon[7][i]]["title"])
          .click(function() { viewToon($(this).attr("name")); })
          .html(toonInfo[daysToon[7][i]]["title"])
          .appendTo(dayDiv[i % 7]);
      }
      for (var i = 0; i < 7; i++)
        dayDiv[i].appendTo("#finished_toonlist");
      resizeWidth();
      $.get(
        "/putToonColor.cgi",
        {site: site},
        function (data) {
          toonBM = data;
          for (var key in toonBM)
          {
            if (toonBM[key] < numList[key].length)
              $("div[name=" + key + "]").addClass("saved_update");
            else if (toonBM[key] == numList[key].length)
              $("div[name=" + key + "]").addClass("saved_finish");
          }
        }
      );
    }
  );
}

// sitelist_area 초기화
function sitelist_init()
{
  id = null;
  num = null;
  site = null;
  change_remote();

  $("#sitelist_area").html("<br/>");
  for (key in sites)
    $("<span>")
      .addClass("sitelist")
      .attr("name", key)
      .click(function() { site_change($(this).attr("name")); })
      .html("<u>" + key.charAt(0).toUpperCase() + "</u>" + key.slice(1))
      .appendTo("#sitelist_area");
  $("#toonlist_area").html("");
  $("#display_area").html("");
  $("#display_iframe").attr("src", "");
}

// Login, Join 토글
function toggle_login(log)
{
  if (log)
  {
    document.getElementById("user_id").disabled = true;
    $("#user_pw").val("");
    $("#login").html("Logout");
    $("#join").html("Leave");
    $("#login").unbind("click");
    $("#join").unbind("click");
    $("#login").bind("click", function() { logout(); });
    $("#join").bind("click", function() { leave(); });
    $("#login").blur();
    $("#user_id").blur();
    $("#user_pw").blur();
  }
  else
  {
    document.getElementById("user_id").disabled = false;
    $("#user_id").val("");
    $("#user_pw").val("");
    $("#login").html("Login");
    $("#join").html("Join");
    $("#login").unbind("click");
    $("#join").unbind("click");
    $("#login").bind("click", function() { login(); });
    $("#join").bind("click", function() { join(); });
    $("#user_id").focus();
  }
}

// Join
function join()
{
  $.post(
    "/join.cgi",
    {user_id: $("#user_id").val(), user_pw: $("#user_pw").val()},
    function (data) { $("#display_area").html(data); }
  );
}

// Leave
function leave()
{
  $.post(
    "/leave.cgi",
    {user_pw: $("#user_pw").val()},
    function (data) { $("#display_area").html(data); }
  );
}

// Login
function login(check)
{
  if (check == undefined)
    $.post(
      "/login.cgi",
      {user_id: $("#user_id").val(), user_pw: $("#user_pw").val()},
      function (data) {
        $("#display_area").html(data);
        $("#display_iframe").attr("src", "");
      }
    );
  else if (check)
    $.post(
      "/login.cgi",
      {check: "y"},
      function (data) { $("#display_area").html(data); }
    );
}

// Logout
function logout()
{
  add_bookmark(false);
  $.get(
    "/logout.cgi",
    function (data) {
      $("#display_area").html(data);
      $("#display_iframe").attr("src", "");
    }
  );
}

// 북마크 추가
function add_bookmark(show_table)
{
  if (id && num)
  {
    if (toonBM[id] && num == 1)
    {
      delete toonBM[id];
      $.post("/saveBM.cgi", {site: site, toon_id: id, toon_num: num});

      noty({type: "success", text: "북마크가 저장되었습니다!"});
      $("#moveBM").attr("disabled", true);

      $(".toonlist div[name=" + id + "]").removeClass("saved_update").removeClass("saved_finish");
      if (show_table)
      {
        var toonlist_id = $(".toonlist div[name=" + id + "]").parent().parent().attr("id");
        if ($("#" + toonlist_id).css("display") == "none")
        {
          if (site == "yahoo")
          {
            if (toonlist_id == "current_toonlist")
              show_table(1);
            else if (toonlist_id == "finished_toonlist")
              show_table(2);
            else if (toonlist_id == "special_toonlist")
              show_table(3);
          }
          else
            show_table();
        }
      }

      location.replace("#");
    }
    else if (!toonBM[id] && num != 1 || toonBM[id] && toonBM[id] != num)
    {
      toonBM[id] = num;
      $.post("/saveBM.cgi", {site: site, toon_id: id, toon_num: num});

      noty({type: "success", text: "북마크가 저장되었습니다!"});
      $("#saveBM").attr("disabled", true);
      $("#moveBM").attr("disabled", true);

      if (toonBM[id] == numList[id].length)
        $(".toonlist div[name=" + id + "]").removeClass("saved_update").removeClass("saved_finish").addClass("saved_finish");
      else
        $(".toonlist div[name=" + id + "]").removeClass("saved_update").removeClass("saved_finish").addClass("saved_update");

      var toonlist_id = $(".toonlist div[name=" + id + "]").parent().parent().attr("id");
      if ($("#" + toonlist_id).css("display") == "none")
      {
        if (site == "yahoo")
        {
          if (toonlist_id == "current_toonlist")
            show_table(1);
          else if (toonlist_id == "finished_toonlist")
            show_table(2);
          else if (toonlist_id == "special_toonlist")
            show_table(3);
        }
        else
          show_table();
      }

      location.replace("#");
    }
  }
}

// table display 토글
function show_table(opt /* only for Yahoo 웹툰 */)
{
  if (opt == undefined)
  {
    if ($("#finished_toonlist").css("display") == "none")
    {
      $("#current_toonlist").css("display", "none");
      $("#finished_toonlist").css("display", "table");
      $(".table_toggle_button").html("연재 웹툰");
    }
    else
    {
      $("#finished_toonlist").css("display", "none");
      $("#current_toonlist").css("display", "table");
      $(".table_toggle_button").html("완결 웹툰");
    }
  }
  else // Yahoo 웹툰
  {
    switch (opt) {
      case 1:
        $("#current_toonlist").css("display", "table");
        $("#finished_toonlist").css("display", "none");
        $("#special_toonlist").css("display", "none");
        $("#table_toggle_button1").css("display", "none");
        $("#table_toggle_button2").css("display", "block");
        $("#table_toggle_button3").css("display", "block");
        break;
      case 2:
        $("#current_toonlist").css("display", "none");
        $("#finished_toonlist").css("display", "table");
        $("#special_toonlist").css("display", "none");
        $("#table_toggle_button1").css("display", "block");
        $("#table_toggle_button2").css("display", "none");
        $("#table_toggle_button3").css("display", "block");
        break;
      case 3:
        $("#current_toonlist").css("display", "none");
        $("#finished_toonlist").css("display", "none");
        $("#special_toonlist").css("display", "table");
        $("#table_toggle_button1").css("display", "block");
        $("#table_toggle_button2").css("display", "block");
        $("#table_toggle_button3").css("display", "none");
        break;
    }
  }
}

// 웹툰 출력
function viewToon(_id, _num)
{
  var prev_id = id;
  var prev_num = num;

  if (typeof(_id) == "undefined")
  {
    noty({text: "웹툰을 선택해 주세요!"});
    return;
  }

  if (_id != id)
    add_bookmark(false);
  id = _id;

  if (typeof(_num) == "undefined")
  {
    if (toonBM[id])
      _num = toonBM[id];
    else
      _num = 1;
  }
  num = _num;

  $("#display_iframe").attr("src", sites[site].src());
  location.replace("#display_iframe");
  change_remote();
}

function go_to(opt)
{
  if (!id || !num)
  {
    noty({text: "웹툰을 선택해 주세요!"});
    return;
  }
  switch (opt) {
    case -2: // 첫 화
      viewToon(id, 1);
      break;
    case 2: // 마지막 화
      viewToon(id, numList[id].length);
      break;
    case -1: // 이전 화
      if (num == 1)
        noty({text: "첫 화입니다!"});
      else
        viewToon(id, num - 1);
      break;
    case 1: // 다음 화
      if (num == numList[id].length)
        noty({text: "마지막 화입니다!"});
      else
        viewToon(id, num + 1);
      break;
    case 0: // 직접 이동
      var inputNum = parseInt($("#inputNum").val());
      if (isNaN(inputNum))
      {
        noty({text: "잘못 입력하셨습니다!"});
        return;
      }
      if (inputNum < 1)
        inputNum = 1;
      else if (inputNum > numList[id].length)
        inputNum = numList[id].length;
      viewToon(id, inputNum);
      break;
    case 3: // 북마크 이동
      if (toonBM[id])
        viewToon(id, toonBM[id]);
      else
        noty({text: "지정된 북마크가 없습니다!"});
      break;
  }
}

// Login, Join 키 입력 처리
function spanKeyDown(spanId, e)
{
  if (event == null)
    var event = e;

  if (event.keyCode == 13 || event.keyCode == 32) // Enter || Space
    $("#" + spanId).trigger("click");
}

// 단축키 입력 처리
function bodyKeyDown(e, lr_arrow)
{
  if (event == null)
    var event = e;

  if (event.ctrlKey)
  {
    switch (event.keyCode) {
      case 37: $("#firstBtn").trigger("click"); break; // ^←
      case 39: $("#lastBtn").trigger("click"); break; // ^→
    }
  }
  else if (event.shiftKey)
  {
    switch (event.keyCode) {
      case 78: // Shift + N
        if (site != "naver")
          site_change("naver");
        break;
      case 68: // Shift + D
        if (site != "daum")
          site_change("daum");
        break;
      case 89: // Shift + Y
        if (site != "yahoo")
          site_change("yahoo");
        break;
      case 83: // Shift + S
        if (site != "stoo")
          site_change("stoo");
        break;
    }
  }
  else
  {
    switch (event.keyCode) {
      case 69: $("#saveBM").trigger("click"); break; // E
      case 82: $("#moveBM").trigger("click"); break; // R
      case 13: $("#dirBtn").trigger("click"); break; // Enter
      case 37: if (lr_arrow) { $("#prevBtn").trigger("click"); } break; // ←
      case 39: if (lr_arrow) { $("#nextBtn").trigger("click"); } break; // →
      case 65: $("#prevBtn").trigger("click"); break; // A
      case 68: $("#nextBtn").trigger("click"); break; // D
      case 38: // ↑
        event.preventDefault();
      case 87: // W
        for (i = 0; i < 10; i++)
          window.scrollBy('0', '-9');
        break;
      case 40: // ↓
        event.preventDefault();
      case 83: // S
        for (i = 0; i < 10; i++)
          window.scrollBy('0', '9');
        break;
      case 72: $("#shortcutBtn").trigger("click"); break; // H
    }
  }
}

// Login Form 단축키 입력 처리
function loginKeyDown(e)
{
  if (event == null)
    var event = e;

  if (event.keyCode == 13) { // Enter
    if (event.srcElement.id == "user_id")
    {
      $("#user_id").blur();
      $("#user_pw").focus();
    }
    else if (event.srcElement.id == "user_pw")
      $("#login").trigger("click");
  }
}

site = null;
id = null;
num = null;
daysToon = new Object();
toonInfo = new Object();
numList = new Object();
toonBM = new Object();
