year59 = newDate(2024,(2-1),18)
year60 = newDate(2025,(2-1),16)
year61 = newDate(2026,(2-1),15)
year62 = newDate(2027,(2-1),21)

function countdowntimer(){
    var countdown = setTimeout(function(){
        var today = new Date(); //今の日時
        
       //ターゲットの設定

        
        var targetDay = select_year; //設定国試
        var daysBetween = Math.ceil((targetDay - today) / (24*60*60*1000));//経過日時を1日のミリ秒で割る
        var remainDay = (targetDay - today); //残り日時

        if (remainDay >= 0){//もし残りの日時が0より多かったら、
            var h = Math.floor(remainDay / 3600000);//残りの日時を1hで割った時間を取得(1h＝3600000ms)
            var h1 = h % 24;//hを24で割った余り。ここでは使っていないが、残り○時間を取得したい時に。
            var m = Math.floor((remainDay - h * 3600000) / 60000);//分を取得(1分＝60000 ms)
            var s = Math.round((remainDay - h * 3600000 - m * 60000) / 1000);//秒を取得(1秒＝1000ms)
            $("#countdown").html("国試まであと" + daysBetween + "日です!");//文中にhtmlタグを使いたい場合はhtmlメソッド使う
            if ((h == 0) && (m == 0) && (s == 0)) {//指定の日時が来たら、
             clearTimeout(countdown);//カウントダウンを止める
             }
            }
           }, 1000);//処理を1秒後に予約
         }
         countdowntimer();//関数を呼び出す
