//jQuery.ajaxSetup({ async: false });

// width 자동 조절
function resizeWidth()
{
  var main_area = document.getElementById("main_area");
  try {
    main_area.style.width = parseInt(window.innerWidth - 185) + "px";
  } catch (e) {
    main_area.style.width = parseInt(document.documentElement.clientWidth - 168) + "px";
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

// 웹툰 사이트 변경
function site_change(_site)
{
  id = null;
  num = null;
  toonBM = new Object();
  numList = new Object();
  lastNum = new Object();
  finishToon = [];

  $("#display_area").html("");
  $("#loading").html("<big><b> Loading</b></big>");
  $("#loading").css("display", "inline");
  loading(10);
  $.get(
    "/cgi-bin/webtoon/getList.cgi",
    {site: _site},
    function (data) {
      site = _site;
      $("#loading").css("display", "none");
      $("#toonlist_area").html(data);
    }
  );
}

// toonlist_area 초기화
function toonlist_area_init()
{
  var str = "<br/>";
  str += '<span id="Naver" style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'naver\');"><u>N</u>aver</span>';
  str += '<span id="Daum" style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'daum\');"><u>D</u>aum</span>';
  $("#toonlist_area").html(str);
}

// Login, Join 토글
function toggle_login(log)
{
  if (log)
  {
    document.getElementById("user_id").disabled = true;
    $("#user_pw").val("");
    $("#login").val("Logout");
    $("#join").val("Leave");
    $("#login").unbind("click");
    $("#join").unbind("click");
    $("#login").bind("click", function() { logout(); });
    $("#join").bind("click", function() { leave(); });
    $("#login").blur();
  }
  else
  {
    document.getElementById("user_id").disabled = false;
    $("#user_id").val("");
    $("#user_pw").val("");
    $("#login").val("Login");
    $("#join").val("Join");
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
    "/cgi-bin/webtoon/join.cgi",
    {user_id: $("#user_id").val(), user_pw: $("#user_pw").val()},
    function (data) { $("#display_area").html(data); }
  );
}

// Leave
function leave()
{
  $.post(
    "/cgi-bin/webtoon/leave.cgi",
    {user_pw: $("#user_pw").val()},
    function (data) { $("#display_area").html(data); }
  );
}

// Login
function login()
{
  $.post(
    "/cgi-bin/webtoon/login.cgi",
    {user_id: $("#user_id").val(), user_pw: $("#user_pw").val()},
    function (data) { $("#display_area").html(data); }
  );
}

// Logout
function logout()
{
  add_bookmark();
  $.post(
    "/cgi-bin/webtoon/logout.cgi",
    function (data) { $("#display_area").html(data); }
  );
}

// 북마크 추가
function add_bookmark()
{
  if (id && num)
  {
    if (toonBM[id] && (site == "naver" && num == 1 || site == "daum" && num == numList[id][0]))
    {
      delete toonBM[id];
      var check = -1;
      for (i = 0; i < finishToon.length; i++)
      {
        if (finishToon[i] == id)
          check = i;
      }
      var _finish = (check == -1) ? "no" : lastNum[id];
      if (site == "naver")
        $.post("/cgi-bin/webtoon/saveBM.cgi", {site: site, add: "no", toon_id: id, toon_num: num, finish: _finish});
      else if (site == "daum")
      {
        req_numList = numList[id].join(" ");
        $.post("/cgi-bin/webtoon/saveBM.cgi", {site: site, add: "no", toon_id: id, toon_num: num, numList: req_numList, finish: _finish});
      }
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

      window.scrollTo('0', '0');
    }
    else if (!toonBM[id] && (site == "naver" && num != 1 || site == "daum" && num != numList[id][0]) || toonBM[id] && toonBM[id] != num)
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
        $.post("/cgi-bin/webtoon/saveBM.cgi", {site: site, add: "yes", toon_id: id, toon_num: num, finish: _finish});
      else if (site == "daum")
      {
        req_numList = numList[id].join(" ");
        $.post("/cgi-bin/webtoon/saveBM.cgi", {site: site, add: "yes", toon_id: id, toon_num: num, numList: req_numList, finish: _finish});
      }
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

            window.scrollTo('0', '0');
          }
        }
      }
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
}

// 작가의 다른 작품 출력
function getOtherToon(_artistId)
{
  if ($("#artist_otherlist").attr("name") != _artistId)
  {
    $("#artist_otherlist").attr("name", _artistId);
    $("#artist_otherlist").css("display", "block");
    $.get(
      "/cgi-bin/webtoon/getOtherToon.cgi",
      {artistId : _artistId},
      function (data) {
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
}

// remote 버튼 정리
function change_remote()
{
  $("#saveBM").attr("disabled", (!id || (site == "naver" && num == 1 || site == "daum" && numList[id] && num == numList[id][0]) || num == toonBM[id]) ? true : false);
  $("#moveBM").attr("disabled", (!id || !toonBM[id] || num == toonBM[id]) ? true : false);
  $("#firstBtn").attr("disabled", (!id || (site == "naver" && num == 1 || site == "daum" && numList[id] && num == numList[id][0])) ? true : false);
  $("#lastBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#prevBtn").attr("disabled", (!id || (site == "naver" && num == 1 || site == "daum" && numList[id] && num == numList[id][0])) ? true : false);
  $("#nextBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#dirBtn").attr("disabled", (!id) ? true : false);

  if (site == "naver")
  {
    src = "http://comic.naver.com/webtoon/detail.nhn?titleId=" + id + "&seq=" + num;
    $("#inputNum").val(num);
  }
  else if (site == "daum")
  {
    src = "http://cartoon.media.daum.net/webtoon/viewer/" + num;
    for (i = 0; i < numList[id].length; i++)
    {
      if (numList[id][i] == num)
        $("#inputNum").val(i + 1);
    }
  }

  $("#url").attr("href", src);
}

// 웹툰 출력
function viewToon(_id, _num)
{
  if (typeof(_id) == "undefined")
  {
    alert("웹툰을 선택해 주세요!");
    return;
  }
  var toonlist_area = document.getElementById("toonlist_area");
  toonlist_area.style.height = "";
  toonlist_area.style.overflow = "";
  $(document).unbind("keydown");
  $(document).bind("keydown", function (e) { bodyKeyDown(e, true); });

  if (_id != id)
    add_bookmark();

  id = (site == "naver") ? parseInt(_id) : _id;

  if (typeof(_num) == "undefined")
  {
    if (toonBM[id])
      _num = toonBM[id];
    else if (site == "naver")
      _num = 1;
    else if (site == "daum")
      _num = (numList[id]) ? numList[id][0] : 0;
  }
  num = parseInt(_num);

  if (typeof(lastNum[id]) == "undefined")
  {
    if (site == "naver")
      $.get(
        "/cgi-bin/webtoon/getNum.cgi",
        {site: site, id: id},
        function (data) {
          if (data == "")
          {
            alert("접속할 수 없습니다!");
            return;
          }
          lastNum[id] = parseInt(data);
          $.get(
            "/cgi-bin/webtoon/displayToon.cgi",
            {site: site, id: id, num: num},
            function (data) {
              $("#display_area").html(data);
              change_remote();
            }
          );
          if (num < lastNum[id])
            $.get("/cgi-bin/webtoon/displayToon.cgi", {site: site, id: id, num: num + 1});
        }
      );
    else if (site == "daum")
      $.get(
        "/cgi-bin/webtoon/getNum.cgi",
        {site: site, id: id},
        function (data) {
          if (data == "")
          {
            alert("접속할 수 없습니다!");
            return;
          }
          numList[id] = data.split(" ");
          for (i = 0; i < numList[id].length; i++)
            numList[id][i] = parseInt(numList[id][i]);
          lastNum[id] = numList[id][numList[id].length - 1];
          num = numList[id][0];
          $.get(
            "/cgi-bin/webtoon/displayToon.cgi",
            {site: site, id: id, num: num},
            function (data) {
              if (data == "")
              {
                alert("접속할 수 없습니다!");
                return;
              }
              $("#display_area").html(data);
              change_remote();
            }
          );
          if (num < lastNum[id])
            for (i = 0; i < numList[id].length; i++)
              if (numList[id][i] == num)
                $.get("/cgi-bin/webtoon/displayToon.cgi", {site: site, id: id, num: numList[id][i + 1]});
        }
      );
  }
  else if (num < lastNum[id])
  {
    if (site == "naver")
      $.get("/cgi-bin/webtoon/displayToon.cgi", {site: site, id: id, num: num + 1});
    else if (site == "daum")
    {
      for (i = 0; i < numList[id].length; i++)
        if (numList[id][i] == num)
          $.get("/cgi-bin/webtoon/displayToon.cgi", {site: site, id: id, num: numList[id][i + 1]});
    }

    $.get(
      "/cgi-bin/webtoon/displayToon.cgi",
      {site: site, id: id, num: num},
      function (data) {
        if (data == "")
        {
          alert("접속할 수 없습니다!");
          return;
        }
        $("#display_area").html(data);
        change_remote();
      }
    );
  }
  else
  {
    $.get(
      "/cgi-bin/webtoon/displayToon.cgi",
      {site: site, id: id, num: num},
      function (data) {
        if (data == "")
        {
          alert("접속할 수 없습니다!");
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
  // 첫 화
  if (opt == -2)
  {
    if (site == "naver")
      viewToon(id, 1);
    else if (site == "daum")
      viewToon(id, numList[id][0]);
  }
  // 마지막 화
  else if (opt == 2)
    viewToon(id, lastNum[id]);
  // 이전 화
  else if (opt == -1)
  {
    if (site == "naver")
      if (num == 1)
        alert("첫 화입니다!");
      else
        viewToon(id, num - 1);
    else if (site == "daum")
    {
      if (num == numList[id][0])
        alert("첫 화입니다!");
      else
      {
        for (i = 0; i < numList[id].length; i++)
          if (numList[id][i] == num)
          {
            viewToon(id, numList[id][i - 1]);
            return;
          }
      }
    }
  }
  // 다음 화
  else if (opt == 1)
  {
    if (num == lastNum[id])
      alert("마지막 화입니다!");
    else if (site == "naver")
      viewToon(id, num + 1);
    else if (site == "daum")
    {
      for (i = 0; i < numList[id].length; i++)
        if (numList[id][i] == num)
        {
          viewToon(id, numList[id][i + 1]);
          return;
        }
    }
  }
  // 직접 이동
  else if (opt == 0)
  {
    var inputNum = parseInt($("#inputNum").val());
    if (isNaN(inputNum))
    {
      alert("잘못 입력하셨습니다!");
      return;
    }

    if (inputNum < 1)
      inputNum = 1;

    if (site == "naver")
    {
      if (inputNum > lastNum[id])
        inputNum = lastNum[id];
    }
    else if (site == "daum")
    {
      inputNum -= 1;
      if (inputNum >= numList[id].length)
        inputNum = numList[id].length - 1;
      inputNum = numList[id][inputNum];
    }

    viewToon(id, inputNum);
  }
  // 북마크 이동
  else if (opt == 3)
  {
    if (toonBM[id])
      viewToon(id, toonBM[id]);
    else
      alert("저장된 북마크가 없습니다!");
  }
}

// 단축키 입력 처리
function bodyKeyDown(e, lr_arrow)
{
  if (event == null)
    var event = e;

  if (event.ctrlKey)
  {
    if (event.keyCode == 37) // ^←
      $("#firstBtn").trigger("click");
    else if (event.keyCode == 39) // ^→
      $("#lastBtn").trigger("click");
    else if (event.keyCode == 38) // ^↑
      window.scrollTo('0', '0');
    else if (event.keyCode == 40) // ^↓
      window.scrollTo('0', document.body.clientHeight);
  }
  else if (event.shiftKey)
  {
    if (event.keyCode == 78) // Shift + N
    {
      if (document.getElementById("Naver"))
        $("#Naver").trigger("click");
      else if (site != "naver")
        $("#site_button").trigger("click");
    }
    else if (event.keyCode == 68) // Shift + D
    {
      if (document.getElementById("Daum"))
        $("#Daum").trigger("click");
      else if (site != "daum")
        $("#site_button").trigger("click");
    }
  }
  else
  {
    if (event.keyCode == 69) // E
      $("#saveBM").trigger("click");
    else if (event.keyCode == 82) // R
      $("#moveBM").trigger("click");
    else if (event.keyCode == 13) // Enter
      $("#dirBtn").trigger("click");
    else if ((event.keyCode == 37 && lr_arrow == true) || event.keyCode == 65) // ← or A
      $("#prevBtn").trigger("click");
    else if ((event.keyCode == 39 && lr_arrow == true) || event.keyCode == 68) // → or D
      $("#nextBtn").trigger("click");
    else if (event.keyCode == 87) // W
      for (i = 0; i < 10; i++)
        window.scrollBy('0', '-9');
    else if (event.keyCode == 83) // S
      for (i = 0; i < 10; i++)
        window.scrollBy('0', '9');
    else if (event.keyCode == 81) // Q
    {
      if (document.getElementById("title_area"))
        location.replace('#title_area');
      else
        window.scrollTo('0', '0');
    }
    else if (event.keyCode == 90) // Z
      window.scrollTo('0', document.body.clientHeight);
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
lastNum = new Object();
finishToon = [];
