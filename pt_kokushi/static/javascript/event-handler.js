document.getElementById('addEventForm').addEventListener('submit', function(e) {
    e.preventDefault();
  
    // フォームからデータを取得
    var title = document.getElementById('eventTitle').value;
    var start = document.getElementById('eventStart').value;
    var end = document.getElementById('eventEnd').value;
  
    // Ajaxリクエストを作成してサーバーに送信
    fetch('/add-event/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        title: title,
        start: start,
        end: end
      }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      // カレンダーを更新
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  });
  