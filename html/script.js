//jQuery.ajaxSetup({ async: false });

(function() {
  window.classNaver = function(name)
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
    this.toonlist_area_init = function() { return '<span id="Naver" style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'naver\');"><u>N</u>aver</span>'; };
    this.saveBM = function(_add, _finish)
    {
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, finish: _finish});
    };
    this.show_artist_table = function(opt)
    {
      $("#artist_otherlist").attr("name", "");
      $("#artist_otherlist").html("");
      $("#artist_otherlist").css("display", "none");

      if (opt == 0)
      {
        $("#artist_other").css("display", "none");
        if ($("#artist_blog").css("display") == "none")
        {
          $("#artist_blog").css("display", "block");
          location.replace("#artist_info");
        }
        else
          $("#artist_blog").css("display", "none");
      }
      else
      {
        $("#artist_blog").css("display", "none");
        if ($("#artist_other").css("display") == "none")
        {
          $("#artist_other").css("display", "block");
          location.replace("#artist_info");
        }
        else
          $("#artist_other").css("display", "none");
      }
    };
    this.getOtherToon = function(_id)
    {
      if ($("#artist_otherlist").attr("name") != _id)
      {
        $("#artist_otherlist").attr("name", _id);
        $("#artist_otherlist").css("display", "block");
        $.get(
          "/getOtherToon",
          {site: site, id: _id},
          function(data) {
            $("#artist_otherlist").html(data + "<br/>");
            location.replace("#artist_otherlist");
          }
        );
      }
      else
      {
        $("#artist_otherlist").attr("name", "");
        $("#artist_otherlist").html("");
        $("#artist_otherlist").css("display", "none");
      }
    };
    this.getNextToon = function() { $.get("/displayToon", {site: site, id: id, num: num + 1}); };
    this.getNumAndDisplay = function(prev_id, prev_num)
    {
      $.get(
        "/getNum",
        {site: site, id: id},
        function(data) {
          if (data == "")
          {
            alert("접속할 수 없습니다!");
            id = prev_id;
            num = prev_num;
            return;
          }
          lastNum[id] = parseInt(data.split(" ")[1]);
          $.get(
            "/displayToon",
            {site: site, id: id, num: num},
            function(data) {
              $("#display_area").html(data);
              change_remote();
            }
          );
          if (num < lastNum[id])
            Naver.getNextToon();
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
    this.toonlist_area_init = function() { return '<span id="Daum" style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'daum\');"><u>D</u>aum</span>'; };
    this.saveBM = function(_add, _finish)
    {
      var req_numList = numList[id].join(" ");
      var req_dateList = dateList[id].join(" ");
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, numList: req_numList, dateList: req_dateList, finish: _finish});
    };
    this.show_artist_table = function(opt)
    {
      if (opt == 0)
        getOtherToon(id);
      else
        getOtherToon(id, false);
    };
    this.getOtherToon = function(_id, check_other)
    {
      if (check_other)
        var _name = "other";
      else
        var _name = "note";
      check_other = (check_other) ? "y" : "n";

      if ($("#artist_otherlist").attr("name") != _name)
      {
        $("#artist_otherlist").attr("name", _name);
        $("#artist_otherlist").css("display", "block");
        $.get(
          "/getOtherToon",
          {site: site, id: _id, other: check_other},
          function(data) {
            $("#artist_otherlist").html(data + "<br/>");
            location.replace("#artist_otherlist");
          }
        );
      }
      else
      {
        $("#artist_otherlist").attr("name", "");
        $("#artist_otherlist").html("");
        $("#artist_otherlist").css("display", "none");
      }
    };
    this.getNextToon = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          $.get("/displayToon", {site: site, id: id, num: numList[id][i + 1]});
      }
    };
    this.getNumAndDisplay = function(prev_id, prev_num)
    {
      $.get(
        "/getNum",
        {site: site, id: id},
        function(data) {
          if (data == "")
          {
            alert("접속할 수 없습니다!");
            id = prev_id;
            num = prev_num;
            return;
          }
          var tmp = data.split("\n")[0].split(" ").slice(1);
          numList[id] = [];
          dateList[id] = [];
          for (i = 0; i < tmp.length; i++) {
            numList[id].push(parseInt(tmp[i].split(",")[0]));
            dateList[id].push(tmp[i].split(",")[1]);
          }
          writer[id] = data.split("\n")[1];
          lastNum[id] = numList[id][numList[id].length - 1];
          num = numList[id][0];
          $.get(
            "/displayToon",
            {site: site, id: id, num: num},
            function(data) {
              if (data == "")
              {
                alert("접속할 수 없습니다!");
                id = prev_id;
                num = prev_num;
                return;
              }
              $("#display_area").html(data);
              change_remote();
            }
          );
          if (num < lastNum[id])
            Daum.getNextToon();
        }
      );
    };
  }
})();

var Naver = new classNaver();
var Daum = new classDaum();

// width 자동 조절
function resizeWidth()
{
  var main_area = document.getElementById("main_area");
  try {
    main_area.style.width = parseInt(window.innerWidth - 155) + "px";
  } catch (e) {
    main_area.style.width = parseInt(document.documentElement.clientWidth - 138) + "px";
  }

  var current_toonlist = document.getElementById("current_toonlist");
  var finished_toonlist = document.getElementById("finished_toonlist");

  if (current_toonlist && finished_toonlist)
  {
    toon1 = document.getElementById("current_toonlist").getElementsByTagName("div");
    toon2 = document.getElementById("finished_toonlist").getElementsByTagName("div");
    for (i = 0; i < toon1.length; i++)
      toon1[i].style.width = parseInt(parseInt(main_area.style.width) / 7 - 2) + "px";
    for (i = 0; i < toon2.length; i++)
      toon2[i].style.width = parseInt(parseInt(main_area.style.width) / 7 - 2) + "px";
  }

  try {
    document.getElementById("remote").style.top = parseInt(window.innerHeight / 2 - 160) + "px";
  } catch (e) {
    document.getElementById("remote").style.top = parseInt(document.documentElement.clientHeight / 2 - 160) + "px";
  }
}

// Loading 메시지 출력
function loading(n)
{
  if (n <= 0)
    return;
  if ($("#loading").css("display") == "none")
    return;
  setTimeout('$("#loading big b").append(".");', 1000);
  setTimeout("loading(" + (n - 1) + ");", 1000);
}

// remote 버튼 정리
function change_remote()
{
  $("#saveBM").attr("disabled", (!id || (site == "naver" && num == Naver.first_num() || site == "daum" && num == Daum.first_num()) || num == toonBM[id]) ? true : false);
  $("#moveBM").attr("disabled", (!id || !toonBM[id] || num == toonBM[id]) ? true : false);
  $("#firstBtn").attr("disabled", (!id || (site == "naver" && num == Naver.first_num() || site == "daum" && num == Daum.first_num())) ? true : false);
  $("#lastBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#prevBtn").attr("disabled", (!id || (site == "naver" && num == Naver.first_num() || site == "daum" && num == Daum.first_num())) ? true : false);
  $("#nextBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#dirBtn").attr("disabled", (!id) ? true : false);

  var src = "";
  if (site == "naver")
  {
    src = Naver.src();
    $("#inputNum").val(Naver.inputNum());
  }
  else if (site == "daum")
  {
    src = Daum.src();
    $("#inputNum").val(Daum.inputNum());
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
        if (toonBM[day_toon[j].id] != undefined)
          day_BM[i].push(day_toon[j].id);
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
      if ($("#" + String(_id)).attr("class") == "finished_toon")
        finish_BM.push(_id);
    }
    $.post(
      "/putToonColor.cgi",
      {site: site, finish: "y", day_BM: finish_BM.join(",")},
      function (data) { count += 1; if (count == 8) { $("#loading").css("display", "none"); } $("#display_area").append(data); }
    );
  }
  else
  {
    $("#loading").html("<big><b> Loading</b></big>");
    $("#loading").css("display", "inline");
    loading(5);
    var day_toon = $("#day" + String(day) + " div");
    var day_BM = [];
    for (i = 0; i < day_toon.length; i++)
    {
      if (toonBM[day_toon[i].id] != undefined)
        day_BM.push(day_toon[i].id);
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
  $("#inputNum").val("");
  $("#url").removeAttr("href");
  $.get(
    "/getList.cgi",
    {site: _site},
    function (data) {
      site = _site;
      $("#toonlist_area").html(data);
    }
  );
}

// toonlist_area 초기화
function toonlist_area_init()
{
  var str = "<br/>";
  str += Naver.toonlist_area_init();
  str += Daum.toonlist_area_init();
  str += "<script>id=null;num=null;site=null;change_remote();</script>";
  $("#toonlist_area").html(str);
}

// Flash 있을 때 toonlist_area height 설정 토글
function toggle_toonlist(_flash)
{
  if (_flash || (_flash == undefined && $("#toonlist_area").css("overflow") != "scroll"))
  {
    $("#toonlist_area").css("height", parseInt(document.getElementById("toonlist_area").clientHeight - (document.getElementById("content_area").offsetTop - 437)) + "px");
    $("#toonlist_area").css("overflow", "scroll");
    $(document).unbind("keydown");
    $(document).bind("keydown", function(e) { bodyKeyDown(e, false); });
  }
  else
  {
    $("#toonlist_area").css("height", "");
    $("#toonlist_area").css("overflow", "");
    $(document).unbind("keydown");
    $(document).bind("keydown", function (e) { bodyKeyDown(e, true); });
    if (site == "naver")
      $("#largeFlashDiv").remove();
  }
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
function login()
{
  $.post(
    "/login.cgi",
    {user_id: $("#user_id").val(), user_pw: $("#user_pw").val()},
    function (data) { $("#display_area").html(data); }
  );
}

// Logout
function logout()
{
  add_bookmark();
  $.get(
    "/logout.cgi",
    function (data) { $("#display_area").html(data); }
  );
}

// 북마크 추가
function add_bookmark()
{
  if (id && num)
  {
    if (toonBM[id] && (site == "naver" && num == Naver.first_num() || site == "daum" && num == Daum.first_num()))
    {
      delete toonBM[id];
      var check = finishToon.indexOf(id);
      var _finish = (check == -1) ? "no" : lastNum[id];

      if (site == "naver")
        Naver.saveBM("no", _finish);
      else if (site == "daum")
        Daum.saveBM("no", _finish);

      alert("북마크가 저장되었습니다!");
      $("#moveBM").attr("disabled", true);

      var same_toon = document.getElementsByName(id);
      for (i = 0; i < same_toon.length; i++)
      {
        var same_td = same_toon[i].parentNode.childNodes;
        for (j = 0; j < same_td.length; j++)
        {
          if (same_td[j] == same_toon[i])
            same_td[j].style.backgroundColor = (j % 2) ? btnColor["buttonA"] : btnColor["buttonB"];
        }
      }
      if (same_toon[0].className == "current_toon" && $("#current_toonlist").css("display") == "none")
        show_table();
      else if (same_toon[0].className == "finished_toon" && $("#finished_toonlist").css("display") == "none")
        show_table();

      location.replace("#");
    }
    else if (!toonBM[id] && (site == "naver" && num != Naver.first_num() || site == "daum" && num != Daum.first_num()) || toonBM[id] && toonBM[id] != num)
    {
      toonBM[id] = num;
      var check = -1;
      for (i = 0; i < finishToon.length; i++)
      {
        if (finishToon[i] == id)
          check = i;
      }
      var _finish = (check == -1) ? "no" : lastNum[id];

      if (site == "naver")
        Naver.saveBM("yes", _finish);
      else if (site == "daum")
        Daum.saveBM("yes", _finish);

      alert("북마크가 저장되었습니다!");
      $("#saveBM").attr("disabled", true);
      $("#moveBM").attr("disabled", true);

      var same_toon = document.getElementsByName(id);
      for (i = 0; i < same_toon.length; i++)
      {
        var same_td = same_toon[i].parentNode.childNodes;
        for (j = 0; j < same_td.length; j++)
        {
          if (same_td[j] == same_toon[i])
          {
            if (same_td[j].className == "current_toon")
              same_td[j].style.backgroundColor = (toonBM[id] == lastNum[id]) ? btnColor["saved"] : btnColor["saved_up"];
            else
            {
              finishToon.push(id);
              same_td[j].style.backgroundColor = (toonBM[id] == lastNum[id]) ? btnColor["saved_finish"] : btnColor["saved_up"];
            }
          }
        }
      }
      if (same_toon[0].className == "current_toon" && $("#current_toonlist").css("display") == "none")
        show_table();
      else if (same_toon[0].className == "finished_toon" && $("#finished_toonlist").css("display") == "none")
        show_table();

      location.replace("#");
    }
  }
}

// BGM Control
function toggle_play_pause(opt)
{
  var music_player_obj = document.getElementById("music_player_obj");

  if (opt == 0)
    if (play_status == "play")
    {
      music_player_obj.controls.pause();
      play_status = "pause";
      $("#BGM_play_pause").html("▶");
    }
    else
    {
      music_player_obj.controls.play();
      play_status = "play";
      $("#BGM_play_pause").html("∥");
    }
  else if (opt == 1)
  {
    music_player_obj.controls.stop();
    play_status = "stop";
    $("#BGM_play_pause").html("▶");
  }
  else
  {
    if ($("#music_player").css("display") == "none")
    {
      $("#music_player").css("display", "block");
      $("#BGM_play_pause").html("■");
    }
    else
    {
      $("#music_player").css("display", "none");
      $("#BGM_play_pause").html("▶");
    }
  }
}

// table display 토글
function show_table()
{
  if ($("#finished_toonlist").css("display") == "none")
  {
    $("#current_toonlist").css("display", "none");
    $("#finished_toonlist").css("display", "table");
    $("#table_toggle_button").html("연재 웹툰");
  }
  else
  {
    $("#finished_toonlist").css("display", "none");
    $("#current_toonlist").css("display", "table");
    $("#table_toggle_button").html("완결 웹툰");
  }
}

// 작가 정보 table 토글
function show_artist_table(opt)
{
  if (site == "naver")
    Naver.show_artist_table(opt);
  else if (site == "daum")
    Daum.show_artist_table(opt);
}

// 작가의 다른 작품 출력
function getOtherToon(_id, /* Daum 웹툰용 */ check_other)
{
  if (check_other == null)
    check_other = true;

  if (site == "naver")
    Naver.getOtherToon(_id);
  else if (site == "daum")
    Daum.getOtherToon(_id, check_other);
}

// 웹툰 출력
function viewToon(_id, _num)
{
  var prev_id = id;
  var prev_num = num;

  if (typeof(_id) == "undefined")
  {
    alert("웹툰을 선택해 주세요!");
    return;
  }

  toggle_toonlist(false);

  if (_id != id)
    add_bookmark();

  if (site == "naver")
    id = Naver.id(_id);
  else if (site == "daum")
    id = Daum.id(_id);

  if (typeof(_num) == "undefined")
  {
    if (toonBM[id])
      _num = toonBM[id];
    else if (site == "naver")
      _num = Naver.first_num();
    else if (site == "daum")
      _num = Daum.first_num();
  }
  num = parseInt(_num);

  if (typeof(lastNum[id]) == "undefined")
  {
    if (site == "naver")
      Naver.getNumAndDisplay(prev_id, prev_num);
    else if (site == "daum")
      Daum.getNumAndDisplay(prev_id, prev_num);
  }
  else
  {
    if (num < lastNum[id])
    {
      if (site == "naver")
        Naver.getNextToon();
      else if (site == "daum")
        Daum.getNextToon();
    }

    $.get(
      "/displayToon",
      {site: site, id: id, num: num},
      function (data) {
        if (data == "")
        {
          alert("접속할 수 없습니다!");
          id = prev_id;
          num = prev_num;
          return;
        }
        $("#display_area").html(data);
        change_remote();
      }
    );
  }
}

function go_to(opt)
{
  if (!id || !num)
  {
    alert("웹툰을 선택해 주세요!");
    return;
  }
  switch (opt) {
    case -2: // 첫 화
      if (site == "naver")
        viewToon(id, Naver.first_num());
      else if (site == "daum")
        viewToon(id, Daum.first_num());
      break;
    case 2: // 마지막 화
      viewToon(id, lastNum[id]);
      break;
    case -1: // 이전 화
      if (site == "naver")
      {
        if (num == Naver.first_num())
          alert("첫 화입니다!");
        else
          viewToon(id, Naver.prev_num());
      }
      else if (site == "daum")
      {
        if (num == Daum.first_num())
          alert("첫 화입니다!");
        else
          viewToon(id, Daum.prev_num());
      }
      break;
    case 1: // 다음 화
      if (num == lastNum[id])
        alert("마지막 화입니다!");
      else if (site == "naver")
        viewToon(id, Naver.next_num());
      else if (site == "daum")
        viewToon(id, Daum.next_num());
      break;
    case 0: // 직접 이동
      var inputNum = parseInt($("#inputNum").val());
      if (isNaN(inputNum))
      {
        alert("잘못 입력하셨습니다!");
        return;
      }
      if (inputNum < 1)
        inputNum = 1;

      if (site == "naver")
        inputNum = Naver.idx_to_num(inputNum);
      else if (site == "daum")
        inputNum = Daum.idx_to_num(inputNum);

      viewToon(id, inputNum);
      break;
    case 3: // 북마크 이동
      if (toonBM[id])
        viewToon(id, toonBM[id]);
      else
        alert("저장된 북마크가 없습니다!");
      break;
  }
}

// Login, Join 키 입력 처리
function spanKeyDown(spanId, e)
{
  if (event == null)
    var event = e;

  if (event.keyCode == 13 || event.keyCode == 32) // Enter
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
      case 38: location.replace("#title_area"); break; // ^↑
      case 40: location.replace("#bottom"); break; // ^↓
    }
  }
  else if (event.shiftKey)
  {
    switch (event.keyCode) {
      case 78: // Shift + N
        if (document.getElementById("Naver"))
          $("#Naver").trigger("click");
        else if (site != "naver")
          $("#site_button").trigger("click");
        break;
      case 68: // Shift + D
        if (document.getElementById("Daum"))
          $("#Daum").trigger("click");
        else if (site != "daum")
          $("#site_button").trigger("click");
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
      case 87: // W
        if ($("#display_area hr").length == 0)
        {
          for (i = 0; i < 10; i++)
            window.scrollBy('0', '-9');
        }
        else
        {
          var hrs = $("#display_area hr");
          switch (location.hash) {
            case "#bottom": location.replace("#anchor_" + String(hrs.length - 1)); break;
            case "#anchor_0": location.replace("#title_area"); break;
            case "#title_area": location.replace("#"); break;
            default:
              if (location.hash.substring(0, 8) == "#anchor_")
                location.replace("#anchor_" + String(parseInt(location.hash.substring(8)) - 1));
              break;
          }
        }
        break;
      case 83: // S
        if ($("#display_area hr").length == 0)
        {
          for (i = 0; i < 10; i++)
            window.scrollBy('0', '9');
        }
        else
        {
          var hrs = $("#display_area hr");
          switch (location.hash) {
            case "": location.replace("#title_area"); break;
            case "#title_area": location.replace("#anchor_0"); break;
            case "#anchor_" + String(hrs.length - 1): location.replace("#bottom"); break;
            default:
              if (location.hash.substring(0, 8) == "#anchor_")
                location.replace("#anchor_" + String(parseInt(location.hash.substring(8)) + 1));
              break;
          }
        }
        break;
      case 81: // Q
        if (document.getElementById("title_area"))
          location.replace("#title_area");
        else
          location.replace("#");
        break;
      case 90: location.replace("#bottom"); break; // Z
    }
  }
}

// Login Form 단축키 입력 처리
function loginKeyDown(e)
{
  if (event == null)
    var event = e;

  if (event.keyCode == 13) { // Enter
    if ($("#user_id").val() == "")
      $("#user_id").focus();
    else if ($("#user_pw").val() == "")
      $("#user_pw").focus();
    else
      $("#login").trigger("click");
  }
}

site = null;
id = null;
num = null;
btnColor = {
  "buttonA" : "#FAFAFA",
  "buttonB" : "#EAEAEA",
  "saved" : "#88DD88",
  "saved_up" : "#DD8888",
  "saved_finish" : "#888888",
  "link" : "#0066CC"};
toonBM = new Object();
numList = new Object();
dateList = new Object();
writer = new Object();
lastNum = new Object();
finishToon = [];
