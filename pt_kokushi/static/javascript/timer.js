document.addEventListener("DOMContentLoaded", function() {
    function updateRemainingTime() {
        fetch('/get-remaining-time/')
            .then(response => response.json())
            .then(data => {
                const remainingDays = data.remaining_days;
                if (remainingDays !== null) {
                    document.getElementById("remaining-days").textContent = remainingDays + " 日";
                } else {
                    document.getElementById("remaining-days").textContent = "情報がありません";
                }
            });
    }

    updateRemainingTime();
    setInterval(updateRemainingTime, 60000);  // 例えば、10秒ごとに更新
});
