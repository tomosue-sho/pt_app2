document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('addEventForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // フォームからデータを取得
            var title = document.getElementById('eventTitle').value;
            var start = document.getElementById('eventStart').value;
            var end = document.getElementById('eventEnd').value;

            // Ajaxリクエストを作成してサーバーに送信
            fetch( '/add-event/' , {
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
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('サーバーからのレスポンスが不正です。');
                }
            })
            .then(data => {
                console.log('Success:', data);
                // ...
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }
});
