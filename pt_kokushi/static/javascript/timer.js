// 受験日の設定
const testDates = {
    "2024": new Date("2024-02-18T09:50:00"),
    "2025": new Date("2025-02-16T09:50:00"),
    "2026": new Date("2026-02-15T09:50:00"),
    "2027": new Date("2027-02-21T09:50:00"),
};

// 残り時間をフォーマットする関数
function formatRemainingTime(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    const formattedTime = `${days}日 ${hours % 24}時間 ${minutes % 60}分 ${seconds % 60}秒`;
    return formattedTime;
}

// カウントダウンの更新を行う関数
function updateCountdown(selectedYear) {
    if (selectedYear in testDates) {
        const testDate = testDates[selectedYear];
        const countdownElement = document.getElementById("countdownElement"); // countdownElementはカウントダウンを表示する要素のID

        const countdownInterval = setInterval(() => {
            const now = new Date();
            const remainingTime = testDate - now;

            if (remainingTime <= 0) {
                clearInterval(countdownInterval);
                countdownElement.textContent = "国試終了";
            } else {
                // 残り時間を適切なフォーマットで表示
                countdownElement.textContent = formatRemainingTime(remainingTime);
            }
        }, 1000);

        return countdownInterval;
    }
    return null;
}

// ドキュメントがロードされたときの処理
document.addEventListener("DOMContentLoaded", function() {
    const yearSelectElement = document.getElementById("testYearElement");

    let currentInterval = updateCountdown(yearSelectElement.value);

    // 年度が変更されたときのイベントリスナー
    yearSelectElement.addEventListener("change", function() {
        clearInterval(currentInterval);
        currentInterval = updateCountdown(this.value);
    });
});
