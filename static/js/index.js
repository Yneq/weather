let weather_container=document.querySelector("#weather_container");
let date_time=document.querySelector("#date_time")


// >監聽事件：網頁Load完後，就向後端取得
document.addEventListener("DOMContentLoaded",function(){

    fetch("/api/v1/weather/all/all/daily")
    .then(response => {
        if(response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then(data => {
        

        console.log("後端取回的，最原始的資料",data)

        // >1.呼叫渲染畫面日期與時間的函式
        render_date_time(data)


        // >2.透過迴圈，將每筆城市資料單獨做後續處理
        data.forEach(city_data => {
            
            console.log(city_data)

            // >因後端資料結構的關係，先取得每筆資料的key值，也就是縣市名稱
            let city_name=Object.keys(city_data)[0]; 

            // >將單一縣市的資料，做為參數，並呼叫專門生成HTML架構的函式
            let new_weather_row=create_weather_row(city_name,city_data);
            weather_container.appendChild(new_weather_row);

        })

        // >3.透過迴圈，針對每個城市方塊建立『點擊』＆『滑鼠移入』的監聽事件
        let all_weather_rows=document.querySelectorAll(".weather__row");
        
        all_weather_rows.forEach(row => {
            row.addEventListener("click",function(){

                const selected_city=row.querySelector(".weather__city-name").textContent.trim();

                console.log("這是使用者點擊城市區塊選擇的城市",selected_city)
                window.location.href = `/city/${selected_city}`
            })
        })


        all_weather_rows.forEach(row => {

            row.addEventListener('mousemove',function(event){
                const weather_tooltip=row.querySelector('.weather__tooltip');
                const mouse_x=event.clientX;
                const mouse_y=event.clientY;
                
                weather_tooltip.style.left=`${mouse_x+10}px`;
                weather_tooltip.style.top=`${mouse_y+10}px`;
            });

        })
    })
    .catch(error => {console.error(error)})
})


// >函式：用來渲染畫面顯示的報表所屬日期與時間區段
function render_date_time(data){

    // >因為只是要取得時間，哪個縣市都一樣，所以直接使用臺北市
    let raw_start_data=data[0]["臺北市"]["MaxT"][0]["start"]
    let raw_end_data=data[0]["臺北市"]["MaxT"][0]["end"]


    let clean_start_date=raw_start_data.slice(5,10);
    let clean_start_time=raw_start_data.slice(11,16);
    let clean_end_date=raw_end_data.slice(5,10);
    let clean_end_time=raw_end_data.slice(11,16)


    clean_start_date=clean_start_date.replace("-", "/"); // >將 "07-17"這樣的資料內容替換為"07/17"
    clean_end_date=clean_end_date.replace("-", "/");


    date_time.textContent=`${clean_start_date}-${clean_start_time}~${clean_end_date}-${clean_end_time}`
}


// >函式：專門生成22個縣市，HTML區塊架構的函式
function create_weather_row(city_name,city_data){

    console.log("產生ＨＴＭＬ架構的函式",city_data)
    // console.log(city_data[city_name].briefDescription[0].para[0])
    // console.log(city_data[city_name].PoP[0].para[0])

    // >建立『最外層』的div
    let new_weather_row=document.createElement("div");
    new_weather_row.classList.add("weather__row");


    // >建立『城市名稱』的div
    let new_city_name=document.createElement("div");
    new_city_name.classList.add("weather__city-name");
    new_city_name.textContent=city_name;
    new_weather_row.appendChild(new_city_name);


    // >建立『天氣icon』的image
    let icon_string=city_data[city_name].briefDescription[0].para[0]; //>因圖片編號需再加工處理，故取出編號字串後，後續做為參數，傳入專門處理Icon URL的函式

    let new_weather_icon=document.createElement("img");
    new_weather_icon.classList.add("weather__icon");
    new_weather_icon.alt="Weather Icon";
    new_weather_icon.src=get_weather_icon_url(icon_string);
    new_weather_row.appendChild(new_weather_icon);


    // >建立『放置雨傘圖示+濕度』的容器div
    let new_chance_container=document.createElement("div");
    new_chance_container.classList.add("weather__chance-container")


    //>建立『雨傘圖式』的image
    let new_chance_icon=document.createElement("img");
    new_chance_icon.classList.add("weather__chance-icon");
    new_chance_icon.alt="Chance Icon";
    new_chance_icon.src="static/umbrella.png"
    new_chance_container.appendChild(new_chance_icon)


    // >建立『呈現降雨機率』的div
    let chance_string=city_data[city_name].PoP[0].para[0]

    let new_chance_text=document.createElement("div");
    new_chance_text.textContent=`${chance_string}%`;
    new_chance_container.appendChild(new_chance_text);


    // >將『放置雨傘圖示+濕度』的容器div加入『最外層』的div，並回傳
    new_weather_row.appendChild(new_chance_container);



    // >建立『小提示語』得div
    let weather_brief_description=city_data[city_name].briefDescription[0].para[1]; // >取得天氣簡短文字描述，EX:"晴時多雲"
    let new_tooltip_text=document.createElement("div");
    new_tooltip_text.classList.add("weather__tooltip");
    new_tooltip_text.textContent=`${weather_brief_description}，降雨機率${chance_string}%，請點此進入${city_name}網頁看詳細天氣內容。`

    new_weather_row.appendChild(new_tooltip_text);

    return new_weather_row
}


// >函式：用來特別處理天氣icon，所對應的URL，有注意此時此刻是白天還晚上（圖片URL會不同）
function get_weather_icon_url(icon_string){

    let icon_num=parseInt(icon_string)
    let current_hour=new Date().getHours(); // >取得當前時間的整點數值，EX:現在是晚上11:30，會得到『23』這個數值
    let day_or_night
    

    // >判斷：icon編號是不是小於10，如果是，會在前面加上0(Icon URL格式的規定)
    if (icon_num < 10){
        icon_string=icon_num.toString().padStart(2,'0')
    }
    else{
        icon_string=icon_num.toString()
    }

    
    // >判斷：當前時間是白天還晚上，這會影響icon URL的路徑內容
    if (current_hour >= 6 && current_hour <= 18){
        day_or_night="day"
    }
    else {
        day_or_night="night"
    }

    let url=`https://www.cwa.gov.tw/V8/assets/img/weather_icons/weathers/svg_icon/${day_or_night}/${icon_string}.svg`
    return url
}


