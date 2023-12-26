//タイマーの日付を設定
var countDownDate = new Date("Feb 18, 2024 00:00:00").getTime();


//しばらく凍結
/*var targetDate = document.querySelector('#year_name');

targetDate.addEventListener('onchange', function(){

if (value == "year59"){
  Date("Feb 18, 2024 00:00:00").getTime();
}else if(value == "year60"){
  Date("Feb 16, 2025 00:00:00").getTime();
}else if(value == "year61"){
  Date("Feb 15, 2026 00:00:00").getTime();
}else if(value == "year62"){
  Date("Feb 21, 2027 00:00:00"),getTime();
}
});

var countDownDate = targetDate;
const countDownDate = document.getElementById('countTimer');

*/

//1秒おきに更新
var x = setInterval(function()
{
    //今日の日付と時間を取得
    var now = new
Date().getTime();

   //日付と時間の計算
  var distance = countDownDate - now;
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  //出力内容
  document.getElementById("countTimer").innerHTML = days + "<span>日</span>" + hours + "<span>時間</span>"
  + minutes + "<span>分</span>" + seconds + "<span>秒</span>";

  //タイマー終了時
  if (distance < 0) {
    clearInterval(x);
    document.getElementById("countTimer").innerHTML = "国試がんばろう！";
  }
}, 1000);