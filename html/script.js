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
    this.id = function(_id) { return parseInt(_id); };
    this.first_num = function() { return 1; };
    this.prev_num = function() { return num - 1; };
    this.next_num = function() { return num + 1; };
    this.idx_to_num = function(_inputNum)
    {
      if (_inputNum > lastNum[id])
        return lastNum[id];
      else
        return _inputNum;
    }
    this.src = function() { return "http://comic.naver.com/webtoon/detail.nhn?titleId=" + id + "&seq=" + num; };
    this.inputNum = function() { return num; };
    this.toonlist_area_init = function() { return '<span class="toonlist_site" onclick="site_change(\'naver\');"><u>N</u>aver</span>'; };
    this.saveBM = function(_add, _finish)
    {
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, finish: _finish});
    };
    this.getNumAndDisplay = function(prev_id, prev_num)
    {
      $.get(
        "/getNum.cgi",
        {site: site, id: id},
        function(data) {
          if (data == "")
          {
            noty({text: "접속할 수 없습니다!"});
            id = prev_id;
            num = prev_num;
            return;
          }
          else if (data == "auth")
            return;

          lastNum[id] = parseInt(data.split(" ")[1]);

          $("#display_iframe").attr("src", sites[site].src());
          location.replace("#display_iframe");
          change_remote();
        }
      );
    };
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
    this.id = function(_id) { return _id; };
    this.first_num = function() { return (numList[id]) ? numList[id][0] : 0; };
    this.prev_num = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return numList[id][i - 1];
      }
    };
    this.next_num = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return numList[id][i + 1];
      }
    };
    this.idx_to_num = function(_inputNum)
    {
      _inputNum -= 1;
      if (_inputNum >= numList[id].length)
        _inputNum = numList[id].length - 1;
      return numList[id][_inputNum];
    }
    this.src = function() { return "http://cartoon.media.daum.net/webtoon/viewer/" + num; };
    this.inputNum = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return i + 1;
      }
    };
    this.toonlist_area_init = function() { return '<span class="toonlist_site" onclick="site_change(\'daum\');"><u>D</u>aum</span>'; };
    this.saveBM = function(_add, _finish)
    {
      var req_numList = numList[id].join(" ");
      var req_dateList = dateList[id].join(" ");
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, numList: req_numList, dateList: req_dateList, finish: _finish});
    };
    this.getNumAndDisplay = function(prev_id, prev_num)
    {
      $.get(
        "/getNum.cgi",
        {site: site, id: id},
        function(data) {
          if (data == "")
          {
            noty({text: "접속할 수 없습니다!"});
            id = prev_id;
            num = prev_num;
            return;
          }
          else if (data == "auth")
            return;
          numList[id] = data.split(" ").slice(1);
          lastNum[id] = numList[id][numList[id].length - 1];
          num = numList[id][0];

          $("#display_iframe").attr("src", sites[site].src());
          location.replace("#display_iframe");
          change_remote();
        }
      );
    };
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
    this.id = function(_id) { return parseInt(_id); };
    this.first_num = function() { return (numList[id]) ? numList[id][0] : 0; };
    this.prev_num = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return numList[id][i - 1];
      }
    }
    this.next_num = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return numList[id][i + 1];
      }
    }
    this.idx_to_num = function(_inputNum)
    {
      _inputNum -= 1;
      if (_inputNum >= numList[id].length)
        _inputNum = numList[id].length - 1;
      return numList[id][_inputNum];
    }
    this.src = function() { return "http://kr.news.yahoo.com/service/cartoon/shellview2.htm?linkid=series_cartoon&sidx=" + num + "&widx=" + id; };
    this.inputNum = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return i + 1;
      }
    };
    this.toonlist_area_init = function() { return '<span class="toonlist_site" onclick="site_change(\'yahoo\');"><u>Y</u>ahoo</span>'; };
    this.saveBM = function(_add, _finish)
    {
      var req_numList = numList[id].join(" ");
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, numList: req_numList, finish: _finish});
    };
    this.getNumAndDisplay = function(prev_id, prev_num)
    {
      $.get(
        "/getNum.cgi",
        {site: site, id: id},
        function(data) {
          if (data == "")
          {
            noty({text: "접속할 수 없습니다!"});
            id = prev_id;
            num = prev_num;
            return;
          }
          numList[id] = data.split(" ").slice(1);
          lastNum[id] = numList[id][numList[id].length - 1];
          num = numList[id][0];

          $("#display_iframe").attr("src", sites[site].src());
          location.replace("#display_iframe");
          change_remote();
        }
      );
    };
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
    this.id = function(_id) { return parseInt(_id); };
    this.first_num = function() { return (numList[id]) ? numList[id][0] : 0; };
    this.prev_num = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return numList[id][i - 1];
      }
    };
    this.next_num = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return numList[id][i + 1];
      }
    };
    this.idx_to_num = function(_inputNum)
    {
      _inputNum -= 1;
      if (_inputNum >= numList[id].length)
        _inputNum = numList[id].length - 1;
      return numList[id][_inputNum];
    }
    this.src = function() { return "http://stoo.asiae.co.kr/cartoon/ctview.htm?sc3=" + id + "&id=" + num; };
    this.inputNum = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          return i + 1;
      }
    };
    this.toonlist_area_init = function() { return '<span class="toonlist_site" onclick="site_change(\'stoo\');"><u>S</u>too</span>'; };
    this.saveBM = function(_add, _finish)
    {
      var req_numList = numList[id].join(" ");
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, numList: req_numList, finish: _finish});
    };
    this.getNumAndDisplay = function(prev_id, prev_num)
    {
      $.get(
        "/getNum.cgi",
        {site: site, id: id},
        function(data) {
          if (data == "")
          {
            noty({text: "접속할 수 없습니다!"});
            id = prev_id;
            num = prev_num;
            return;
          }
          numList[id] = data.split(" ").slice(1);
          lastNum[id] = numList[id][numList[id].length - 1];
          num = numList[id][0];

          $("#display_iframe").attr("src", sites[site].src());
          location.replace("#display_iframe");
          change_remote();
        }
      );
    };
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

// Loading 메시지 출력
function loading(n)
{
  if (n <= 0)
    return;
  if ($("#loading").css("display") == "none")
    return;
  setTimeout('$("#loading").append(".");', 1000);
  setTimeout("loading(" + (n - 1) + ");", 1000);
}

// remote 버튼 정리
function change_remote()
{
  $("#saveBM").attr("disabled", (!id || (site && num == sites[site].first_num()) || num == toonBM[id]) ? true : false);
  $("#moveBM").attr("disabled", (!id || !toonBM[id] || num == toonBM[id]) ? true : false);
  $("#firstBtn").attr("disabled", (!id || (site && num == sites[site].first_num())) ? true : false);
  $("#lastBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#prevBtn").attr("disabled", (!id || (site && num == sites[site].first_num())) ? true : false);
  $("#nextBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#dirBtn").attr("disabled", (!id) ? true : false);

  var src = "";
  if (site)
  {
    src = sites[site].src();
    $("#inputNum").val(sites[site].inputNum());
  }

  $("#url").removeAttr("href");
  if (src != "")
    $("#url").attr("href", src);
}

// toon div background color 변경
function putToonColor(day)
{
  if (day == null)
  {
    if (site == "yahoo") // special_toonlist
    {
      var day = 0;
      var day_BM = new Object();
      for (i = 0; i < 14; i++)
      {
        var day_toon = $("#day" + String(day + i) + " div");
        day_BM[i] = [];
        for (j = 0; j < day_toon.length; j++)
        {
          if (day_toon[j].attributes["name"] && toonBM[day_toon[j].attributes["name"].value] != undefined)
            day_BM[i].push(day_toon[j].attributes["name"].value);
        }
      }

      var count = 0;
      for (i = 0; i < 14; i++)
      {
        $.post(
          "/putToonColor.cgi",
          {site: site, finish: "n", day_BM: day_BM[i].join(",")},
          function (data) { count += 1; if (count == 15) { $("#loading").css("display", "none"); } $("#display_area").append(data); }
        );
      }

      var finish_BM = [];
      for (_id in toonBM)
      {
        if ($("div[name=" + String(_id) + "]").attr("class") == "finished_toon")
          finish_BM.push(_id);
      }
      $.post(
        "/putToonColor.cgi",
        {site: site, finish: "y", day_BM: finish_BM.join(",")},
        function (data) { count += 1; if (count == 15) { $("#loading").css("display", "none"); } $("#display_area").append(data); }
      );
    }
    else
    {
      var day = ((new Date()).getDay() + 6) % 7;
      // getDay() -> 0 : 일, 1 : 월, 2 : 화, ... , 6 : 토
      // HTML td -> 0 : 월, 1 : 화, 2 : 수, ... , 6 : 일
      var day_BM = new Object();
      for (i = 1; i <= 7; i++)
      {
        var day_toon = $("#day" + String((day + i) % 7) + " div");
        day_BM[i] = [];
        for (j = 0; j < day_toon.length; j++)
        {
          if (day_toon[j].attributes["name"] && toonBM[day_toon[j].attributes["name"].value] != undefined)
            day_BM[i].push(day_toon[j].attributes["name"].value);
        }
      }

      var count = 0;
      for (i = 7; i >= 1; i--)
      {
        $.post(
          "/putToonColor.cgi",
          {site: site, finish: "n", day_BM: day_BM[i].join(",")},
          function (data) { count += 1; if (count == 8) { $("#loading").css("display", "none"); } $("#display_area").append(data); }
        );
      }

      var finish_BM = [];
      for (_id in toonBM)
      {
        if ($("div[name=" + String(_id) + "]").attr("class") == "finished_toon")
          finish_BM.push(_id);
      }
      $.post(
        "/putToonColor.cgi",
        {site: site, finish: "y", day_BM: finish_BM.join(",")},
        function (data) { count += 1; if (count == 8) { $("#loading").css("display", "none"); } $("#display_area").append(data); }
      );
    }
  }
  else
  {
    $("#loading").html(" Loading");
    $("#loading").css("display", "inline");
    loading(5);
    var day_toon = $("#day" + String(day) + " div");
    var day_BM = [];
    for (i = 0; i < day_toon.length; i++)
    {
      if (day_toon[i].attributes["name"] && toonBM[day_toon[i].attributes["name"].value] != undefined)
        day_BM.push(day_toon[i].attributes["name"].value);
    }

    $.post(
      "/putToonColor.cgi",
      {site: site, finish: "n", day_BM: day_BM.join(",")},
      function (data) { $("#loading").css("display", "none"); $("#display_area").append(data); }
    );
  }
}

// 웹툰 사이트 변경
function site_change(_site)
{
  site = null;
  id = null;
  num = null;
  toonBM = new Object();
  numList = new Object();
  dateList = new Object();
  toonInfo = new Object();
  lastNum = new Object();
  finishToon = [];
  change_remote();

  $("#display_area").html("");
  $("#display_iframe").attr("src", "");
  $("#inputNum").val("");
  $("#url").removeAttr("href");
  $.get(
    "/getList.cgi",
    {site: _site},
    function (data) {
      site = _site;
      $("#toonlist_area").html(data);
      resizeWidth();
    }
  );
}

// toonlist_area 초기화
function toonlist_area_init()
{
  var str = "<br/>";
  for (key in sites)
    str += sites[key].toonlist_area_init();

  id = null;
  num = null;
  site = null;
  change_remote();

  $("#toonlist_area").html(str);
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
    if (toonBM[id] && num == sites[site].first_num())
    {
      delete toonBM[id];
      var check = finishToon.indexOf(id);
      var _finish = (check == -1) ? "no" : lastNum[id];

      sites[site].saveBM("no", _finish);

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
    else if (!toonBM[id] && num != sites[site].first_num() || toonBM[id] && toonBM[id] != num)
    {
      toonBM[id] = num;
      var check = -1;
      for (i = 0; i < finishToon.length; i++)
      {
        if (finishToon[i] == id)
        {
          check = i;
          break;
        }
      }
      var _finish = (check == -1) ? "no" : lastNum[id];

      sites[site].saveBM("yes", _finish);

      noty({type: "success", text: "북마크가 저장되었습니다!"});
      $("#saveBM").attr("disabled", true);
      $("#moveBM").attr("disabled", true);

      if (toonBM[id] == lastNum[id])
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

  id = sites[site].id(_id);

  if (typeof(_num) == "undefined")
  {
    if (toonBM[id])
      _num = toonBM[id];
    else
      _num = sites[site].first_num();
  }
  if (site == "stoo")
    num = _num;
  else
    num = parseInt(_num);

  if (typeof(lastNum[id]) == "undefined")
    sites[site].getNumAndDisplay(prev_id, prev_num);
  else
  {
    $("#display_iframe").attr("src", sites[site].src());
    location.replace("#display_iframe");
    change_remote();
  }
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
      viewToon(id, sites[site].first_num());
      break;
    case 2: // 마지막 화
      viewToon(id, lastNum[id]);
      break;
    case -1: // 이전 화
      if (num == sites[site].first_num())
        noty({text: "첫 화입니다!"});
      else
        viewToon(id, sites[site].prev_num());
      break;
    case 1: // 다음 화
      if (num == lastNum[id])
        noty({text: "마지막 화입니다!"});
      else
        viewToon(id, sites[site].next_num());
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

      inputNum = sites[site].idx_to_num(inputNum);

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
toonBM = new Object();
numList = new Object();
lastNum = new Object();
finishToon = [];
