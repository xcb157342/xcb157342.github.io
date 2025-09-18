// 获取当前天气
WeatherService.getWeather('西安').then(data => {
    console.log(data);
});

// 获取天气预报
WeatherService.getForecast('西安').then(data => {
    console.log(data);
});