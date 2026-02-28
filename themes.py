<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mafia Dashboard</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; padding: 20px; }
        .player-list { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
        .player-card { background: #1a1a1a; border: 2px solid #333; border-radius: 15px; padding: 15px; }
        .alive { border-color: #00ff41; }
        .dead { border-color: #ff4141; opacity: 0.5; }
        .avatar { font-size: 40px; display: block; margin-bottom: 5px; }
        .role-hidden { color: #555; font-size: 12px; }
        h2 { color: #0088cc; }
    </style>
</head>
<body>
    <h2>🕵️‍♂️ Статус игры</h2>
    <div id="status">Ожидание начала...</div>

    <div class="player-list" id="players">
        <!-- Сюда бот будет "подставлять" игроков в будущем -->
        <div class="player-card alive">
            <span class="avatar">❓</span>
            <span>Игрок 1</span><br>
            <span class="role-hidden">Роль скрыта</span>
        </div>
        <div class="player-card alive">
            <span class="avatar">❓</span>
            <span>Игрок 2</span><br>
            <span class="role-hidden">Роль скрыта</span>
        </div>
    </div>

    <button onclick="window.location.reload()" style="margin-top:30px; background:#333; color:white; border:none; padding:10px; border-radius:10px;">Обновить данные</button>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        // В будущем мы научим эту страницу получать данные о том, кто жив, а кто нет
    </script>
</body>
</html>