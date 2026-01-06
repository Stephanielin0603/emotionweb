let weatherDataStorage = {
    city: "",
    temp: "",
    humidity: "",
    wind: ""
};
let selectedEmotion = "";
let selectedSeason = "";
const supabaseUrl = 'https://ukctpgmbglntfwvfulrz.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrY3RwZ21iZ2xudGZ3dmZ1bHJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNzA0ODYsImV4cCI6MjA4Mjc0NjQ4Nn0.V0kAJMRywAkzH45B8yfYrlNeFA5Xvmy4k6sWQPBl3r4'; 
const _supabase = supabase.createClient(supabaseUrl, supabaseKey);
 async function search() {
    const cityInput = document.getElementById('city').value.trim();
    const resultDiv = document.getElementById('result');
            
    if (!cityInput) {
        alert("請先輸入城市名稱");
        return;
    }
    resultDiv.innerText = "正在搜尋城市位置...";
            
    try {
        // 1. 座標轉換 (Geocoding)
        const geoUrl = `https://nominatim.openstreetmap.org/search?city=${cityInput}&format=json&limit=1`;
        const geoRes = await fetch(geoUrl);
        const geoData = await geoRes.json();
        if (geoData.length === 0) {
            resultDiv.innerText = "❌ 找不到該城市，請嘗試輸入英文（如: Tokyo）";
            return;
        }

        const { lat, lon, display_name } = geoData[0];
        const shortName = display_name.split(',')[0];
            
        resultDiv.innerText = `獲取 ${shortName} 氣象中...`;

    // 2. 查詢 Open-Meteo 天氣資料
        const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=auto`;
        const weatherRes = await fetch(weatherUrl);
        const weatherData = await weatherRes.json();

    // 3. 渲染結果
        const temp = weatherData.current.temperature_2m;
        const wind = weatherData.current.wind_speed_10m;
        const time = new Date(weatherData.current.time).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
        const humidity = weatherData.current.relative_humidity_2m;// 這裡就是濕度！
        const humidityUnit = weatherData.current_units.relative_humidity_2m; // 這裡是單位 %

        weatherDataStorage.temp = temp;
        weatherDataStorage.wind = wind;
        weatherDataStorage.humidity = humidity + humidityUnit;
        weatherDataStorage.city = shortName;
        resultDiv.innerHTML = `
        <div style="border-left: 4px solid #007bff; padding-left: 10px;">
            <div>📍 ${shortName}</div>
            <div style="font-size: 1.5em;">🌡️ ${temp}°C</div>
            <div style="font-size: 0.9em; color: #666;">💨 風速: ${wind} km/h  | 💧 濕度:${humidity}${humidityUnit} | 🕒 更新: ${time}</div>
        </div>
        `;
    } catch (error) {
        resultDiv.innerText = "⚠️ 查詢失敗，請檢查網路連線。";
        console.error("Weather Error:", error);
    }
}
function checkEmotion(element, feeling) {
    // 1. 移除所有按鈕的 active 狀態
    const allButtons = document.querySelectorAll('.emotion-btn');
    allButtons.forEach(btn => btn.classList.remove('active'));

    // 2. 幫當前點擊的按鈕加上 active 狀態
    element.classList.add('active');

    // 3. 原有的分析邏輯 (保持不變)
    selectedEmotion = feeling; // 記住心情

    //display.innerHTML = `已選擇${feeling}`;
    display.style.textAlign = "center"; // 確保結果文字也置中
}
function checkSeaon(element,name) {
    const allButtons = document.querySelectorAll('.season-btn');
    allButtons.forEach(btn => btn.classList.remove('active'));
    
    element.classList.add('active');
    selectedSeason = name; // 記住季節
}
// --- 4. 生成推薦並切換頁面 ---
async function generateRecommendation() {
    if (!weatherDataStorage.city || !selectedEmotion || !selectedSeason) {
        alert("儀式尚未完成喔！✨");
        return;
    }

    // --- A. 標籤轉換邏輯 ---
    // 溫度標籤
    let tRange = "moderate";
    if (weatherDataStorage.temp >= 28) tRange = "hot";
    if (weatherDataStorage.temp <= 15) tRange = "cold";

    // 濕度標籤 (數字轉標籤)
    let hValue = parseInt(weatherDataStorage.humidity);
    let hRange = hValue >= 65 ? "humid" : "dry";

    // --- B. 呼叫 Supabase 智庫 ---
    const { data: reco, error } = await _supabase
        .from('scent_recommendations')
        .select('*')
        .eq('season', selectedSeason)
        .eq('emotion', selectedEmotion)
        .eq('temp_range', tRange)
        .eq('humidity_range', hRange)
        .single();

    const scent = reco ? reco.scent_name : "晨露白茶";
    const desc = reco ? reco.description : "這款香氣能平衡當下的氣候變幻。";

    // --- C. 風速即時建議 (JS 邏輯) ---
    let windAdvice = "🍃 今日風速穩定，適合正常噴灑於耳後與手腕。";
    let windSpeed = parseFloat(weatherDataStorage.wind);
    if (windSpeed > 20) {
        windAdvice = "💨 <b>今日強風警告：</b>香味散發較快，建議噴在衣物內側或圍巾上，並增加噴灑次數。";
    } else if (windSpeed < 5) {
        windAdvice = "✨ <b>今日微風舒緩：</b>非常適合讓香氣自然擴散，建議噴在胸前感受「香氛雲」。";
    }

    // --- D. 渲染結果與切換頁面 ---
    document.getElementById('res-city').innerText = `📍 ${weatherDataStorage.city}`;
    document.getElementById('res-weather').innerText = 
        `🌡️ ${weatherDataStorage.temp}°C | 💧 濕度 ${weatherDataStorage.humidity} | 💨 風速 ${weatherDataStorage.wind} km/h`;
    
    document.getElementById('res-recommendation').innerHTML = `
        <div style="font-size: 1.4em; color: #b5838d; margin-bottom: 10px;">專屬香氛：【${scent}】</div>
        <p style="color: #6d6875; line-height: 1.6;">${desc}</p>
        <div style="background: #fffcf2; padding: 12px; border-radius: 8px; font-size: 0.9em; border: 1px solid #f8bbbb; color: #403d39;">
            ${windAdvice}
        </div>
    `;
}
function backToInput() {
    document.getElementById('result-page').style.display = 'none';
    document.getElementById('input-page').style.display = 'block';
}

///------
// 控制漸入的共用函式
function showStage(targetId) {
    // 隱藏所有階段
    document.querySelectorAll('.stage-container').forEach(el => {
        el.style.display = 'none';
        el.style.opacity = '0';
    });
    
    // 顯示目標階段
    const target = document.getElementById(targetId);
    target.style.display = 'flex';
    setTimeout(() => {
        target.style.opacity = '1';
    }, 50);
}

// 1 -> 2: 確認城市後切換
async function goToStep2() {
    await search(); // 執行原本的天氣查詢
    
    // 檢查是否成功拿到天氣資料
    if (weatherDataStorage.city) {
        showStage('step-2');
    }
}

// 2 -> 3: 生成推薦後切換
async function goToStep3() {

    await generateRecommendation(); // 執行原本的 Supabase 查詢與渲染
    showStage('step-3');
}

// 重置儀式
function backToStart() {
    location.reload(); 
}