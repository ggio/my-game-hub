<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ID CARD</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: monospace; background: #000; color: #00ff41; padding: 20px; text-align: center; }
        .id-card { border: 2px solid #00ff41; padding: 20px; border-radius: 15px; background: #050505; box-shadow: 0 0 15px #00ff41; }
        .role { font-size: 24px; color: #fff; font-weight: bold; margin: 10px 0; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .trait { background: #111; padding: 10px; border-radius: 5px; color: #ff4141; margin-top: 15px; }
        button { background: #00ff41; color: #000; border: none; padding: 15px; width: 100%; margin-top: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="id-card">
        <h2 id="name">ЗАГРУЗКА...</h2>
        <div class="role" id="role">РОЛЬ</div>
        <p>ВАША ПРИМЕТА:</p>
        <div class="trait" id="trait">ПРИМЕТА</div>
    </div>
    <p style="font-size: 12px; color: #555; margin-top: 15px;">Сравни свою примету с уликой в чате. Если они совпадают — ты Самозванец!</p>
    <button onclick="Telegram.WebApp.close()">ВЕРНУТЬСЯ К ОБСУЖДЕНИЮ</button>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        const params = new URLSearchParams(window.location.search);
        
        document.getElementById('name').innerText = params.get('name');
        document.getElementById('role').innerText = params.get('role');
        document.getElementById('trait').innerText = params.get('trait');
    </script>
</body>
</html>