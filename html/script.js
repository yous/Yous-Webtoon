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
    this.toonlist_area_init = function() { return '<span style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'naver\');"><u>N</u>aver</span>'; };
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
    this.toonlist_area_init = function() { return '<span style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'daum\');"><u>D</u>aum</span>'; };
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
    this.toonlist_area_init = function() { return '<span style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'yahoo\');"><u>Y</u>ahoo</span>'; };
    this.saveBM = function(_add, _finish)
    {
      var req_numList = numList[id].join(" ");
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, numList: req_numList, finish: _finish});
    };
    this.show_artist_table = function(opt) { return; };
    this.getOtherToon = function(_id) { return; };
    this.getNextToon = function()
    {
      for (i = 0; i < numList[id].length; i++)
      {
        if (numList[id][i] == num)
          $.get("/displayToon", {site: site, id: id, num: numList[id][i + 1]});
      }
    }
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
          tmp = data.split("\n")[0].split(" ").slice(1);
          numList[id] = []
          for (i = 0; i < tmp.length; i++)
            numList[id].push(parseInt(tmp[i]));

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
            Yahoo.getNextToon();
        }
      );
    };
  }
})();

(function() {
  window.classParan = function()
  {
    if (_Paran == null)
      _Paran = new classParan();
    return _Paran;
  }

  var _Paran = null;
  var classParan = function()
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
    this.src = function() { return "http://media.paran.com/cartoon/cartoonview.kth?id=" + id + "&ord=" + num + "&mno=" + ((finishToon.indexOf(id) != -1) ? 5 : 3); };
    this.inputNum = function() { return num; };
    this.toonlist_area_init = function() { return '<span style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'paran\');"><u>P</u>aran</span>'; };
    this.saveBM = function(_add, _finish) { $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, finish: _finish}); };
    this.show_artist_table = function(opt) { return; };
    this.getOtherToon = function(_id) { return; };
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
          lastNum[id] = parseInt(data);
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
            Paran.getNextToon();
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
    this.toonlist_area_init = function() { return '<span style="color: ' + btnColor["link"] + '; cursor: pointer; margin: 10px;" onclick="site_change(\'stoo\');"><u>S</u>too</span>'; };
    this.saveBM = function(_add, _finish)
    {
      var req_numList = numList[id].join(" ");
      $.post("/saveBM.cgi", {site: site, add: _add, toon_id: id, toon_num: num, numList: req_numList, finish: _finish});
    };
    this.show_artist_table = function(opt) { return; };
    this.getOtherToon = function(_id) { return; };
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
          numList[id] = data.split("\n")[0].split(" ").slice(1);
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
            Stoo.getNextToon();
        }
      );
    };
  }
})();

var Naver = new classNaver();
var Daum = new classDaum();
var Yahoo = new classYahoo();
var Paran = new classParan();
var Stoo = new classStoo();
var sites = {
  "naver" : Naver,
  "daum" : Daum,
  "yahoo" : Yahoo,
  "paran" : Paran,
  "stoo" : Stoo
};

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
  // only for Yahoo 웹툰
  if (document.getElementById("special_toonlist"))
  {
    toon = document.getElementById("special_toonlist").getElementsByTagName("div");
    for (i = 0; i < toon.length; i++)
      toon[i].style.width = parseInt(parseInt(main_area.style.width) / 7 - 2) + "px";
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
  setTimeout('$("#loading").append(".");', 1000);
  setTimeout("loading(" + (n - 1) + ");", 1000);
}

// remote 버튼 정리
function change_remote()
{
  $("#saveBM").attr("disabled", (!id || num == sites[site].first_num()) ? true : false);
  $("#moveBM").attr("disabled", (!id || !toonBM[id] || num == toonBM[id]) ? true : false);
  $("#firstBtn").attr("disabled", (!id || num == sites[site].first_num()) ? true : false);
  $("#lastBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#prevBtn").attr("disabled", (!id || num == sites[site].first_num()) ? true : false);
  $("#nextBtn").attr("disabled", (!id || num == lastNum[id]) ? true : false);
  $("#dirBtn").attr("disabled", (!id) ? true : false);

  var src = "";
  if (sites[site] != undefined)
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
          if (toonBM[day_toon[j].id] != undefined)
            day_BM[i].push(day_toon[j].id);
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
        if ($("#" + String(_id)).attr("class") == "finished_toon")
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
  for (key in sites)
    str += sites[key].toonlist_area_init();
  str += "<script>id=null;num=null;site=null;change_remote();</script>";
  $("#toonlist_area").html(str);
  $("#display_area").html("");
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
    if (toonBM[id] && num == sites[site].first_num())
    {
      delete toonBM[id];
      var check = finishToon.indexOf(id);
      var _finish = (check == -1) ? "no" : lastNum[id];

      sites[site].saveBM("no", _finish);

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
      if (site == "yahoo")
      {
        if (same_toon[0].className == "current_toon")
        {
          var _day = parseInt(same_toon[0].parentElement.id.substring(3));
          if (0 <= _day && _day <= 6 && $("#current_toonlist").css("display") == "none")
            show_table(1);
          else if (7 <= _day && _day <= 13 && $("#special_toonlist").css("display") == "none")
            show_table(3);
        }
        else if (same_toon[0].className == "finished_toon" && $("#finished_toonlist").css("display") == "none")
          show_table(2);
      }
      else
      {
        if (same_toon[0].className == "current_toon" && $("#current_toonlist").css("display") == "none")
          show_table();
        else if (same_toon[0].className == "finished_toon" && $("#finished_toonlist").css("display") == "none")
          show_table();
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
          check = i;
      }
      var _finish = (check == -1) ? "no" : lastNum[id];

      sites[site].saveBM("yes", _finish);

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
      if (site == "yahoo")
      {
        if (same_toon[0].className == "current_toon")
        {
          var _day = parseInt(same_toon[0].parentElement.id.substring(3));
          if (0 <= _day && _day <= 6 && $("#current_toonlist").css("display") == "none")
            show_table(1);
          else if (7 <= _day && _day <= 13 && $("#special_toonlist").css("display") == "none")
            show_table(3);
        }
        else if (same_toon[0].className == "finished_toon" && $("#finished_toonlist").css("display") == "none")
          show_table(2);
      }
      else
      {
        if (same_toon[0].className == "current_toon" && $("#current_toonlist").css("display") == "none")
          show_table();
        else if (same_toon[0].className == "finished_toon" && $("#finished_toonlist").css("display") == "none")
          show_table();
      }

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
function show_table(opt /* only for Yahoo 웹툰 */)
{
  if (opt == undefined)
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

// 작가 정보 table 토글
function show_artist_table(opt)
{
  sites[site].show_artist_table(opt);
}

// 작가의 다른 작품 출력
function getOtherToon(_id, /* Daum 웹툰용 */ check_other)
{
  if (check_other == null)
    check_other = true;

  if (site == "daum")
    sites[site].getOtherToon(_id, check_other);
  else
    sites[site].getOtherToon(_id);
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
    if (num < lastNum[id])
      sites[site].getNextToon();

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
      viewToon(id, sites[site].first_num());
      break;
    case 2: // 마지막 화
      viewToon(id, lastNum[id]);
      break;
    case -1: // 이전 화
      if (num == sites[site].first_num())
        alert("첫 화입니다!");
      else
        viewToon(id, sites[site].prev_num());
      break;
    case 1: // 다음 화
      if (num == lastNum[id])
        alert("마지막 화입니다!");
      else
        viewToon(id, sites[site].next_num());
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

      inputNum = sites[site].idx_to_num(inputNum);

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
      case 38: location.replace("#title_area"); break; // ^↑
      case 40: location.replace("#bottom"); break; // ^↓
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
      case 80: // Shift + P
        if (site != "paran")
          site_change("paran");
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
