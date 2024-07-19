let button=document.querySelector("#button")


// >監聽事件：網頁Load完後，就向後端取得城市資料，並呼叫渲染搜尋欄的函式
document.addEventListener("DOMContentLoaded",function(){

    fetch("/api/v1/city_names")
    .then((response)=>{
        if(response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then((data)=>{
        
        const city_select=document.querySelector("#city")

        // >1.呼叫：渲染縣市選單的函式
        rander_dropdown_city(city_select,data.data) // >data.data的資料內容：['臺北市', '新北市', '基隆市'....]


        // >2.建立監聽事件：針對縣市選單一旦有變動，就呼叫連線函式，取得那個縣市的『 區域資料 』
        city_select.addEventListener("change",function(event){
            let selected_city=event.target.value
            fetch_district_data(selected_city)
        })
    })
    .catch(error => {console.error(error)})
})


// >函式：渲染城市的下拉選單
function rander_dropdown_city(select_element,citys){

    citys.forEach(city => {

        const new_option=document.createElement("option");
        new_option.textContent=city;
        new_option.value=city;

        select_element.appendChild(new_option);
    });
}


// >函式：連線到後端，取得選定的城市的區域資料
function fetch_district_data(selected_city){

    fetch(`/api/v1/${selected_city}`)
    .then((response)=>{
        if(response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then((data)=>{
        console.log("這是取得的區域資料",data.data) // >data.data的資料內容：['東區', '北區', '香山區'...]
        
        // >呼叫：渲染區域選單的函式
        render_dropdown_district(data.data)
    })
    .catch(error => {console.error(error)})
}


// >函式：用來渲染鄉鎮選單
function render_dropdown_district(districts){

    const district_select=document.querySelector("#district");
    district_select.innerHTML=""


    const default_option = document.createElement("option");
    default_option.textContent="選擇鄉鎮";
    default_option.value="";
    default_option.disabled=true;
    default_option.selected=true;
    district_select.appendChild(default_option);


    districts.forEach(district =>{
        const new_option=document.createElement("option");
        new_option.textContent=district;
        new_option.value=district;

        district_select.appendChild(new_option)
    })
}


// >監聽事件：使用者點擊確認按鈕後，要將選擇的城市跟鄉鎮資料做為參數，呼叫慧倫的函式＋轉跳到她的city頁面
button.addEventListener("click",function(){

    const selected_city=document.querySelector("#city").value;
    const selected_district=document.querySelector("#district").value;

    if (!selected_city){
        alert("請選擇選縣市^^我們才能提供更詳細的資料喔！") 
        return
    }

    console.log("這是使用者點擊城市區塊選擇的城市",selected_city)
    console.log("這是使用者點擊城市區塊選擇的區域",selected_district)


    window.location.href = `/city/${selected_city}/${selected_district}`
    
})