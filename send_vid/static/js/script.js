const videoFrame = document.getElementById('videoFrame');
const fpsElement =document.getElementById('fps');
const ballsCountElement = document.getElementById('ballsCount');
const statusElement = document.getElementById('status');
const ws = new WebSocket('ws://ballretrieving.ddns.net:8000/ws/video/');
let fpsValue = 0;
let ballsCountValue = 0;
let statusValue = '';

//jquery code to hide/show mode
$(document).ready(function(){
$("#hand").click(function(){
    $("#controlButton").addClass("showDirection").removeClass("fadeDirection")
});
$("#auto").click(function(){
    $("#controlButton").addClass("fadeDirection").removeClass("showDirection")
});
});

ws.onopen = () => {
    console.log('WebSocket connection opened');
};

ws.onclose = () => {
    console.log('WebSocket connection closed');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data && data.frame) {
        videoFrame.src = 'data:image/jpeg;base64,' + data.frame;
    }
    else {
        videoFrame.src = '';
    }
    fpsValue = data.fps;
    ballsCountValue = data.balls_count;
    statusValue = data.status;
};
// Set time for showing FPS, number of balls and status
setInterval(function () {
    fpsElement.textContent = fpsValue.toFixed(2);
    ballsCountElement.textContent = ballsCountValue;
    statusElement.textContent = statusValue;
}, 1000);

// Catch buttons event
$(document).ready(function(){
    $("#start").click(function(){
        ws.send(JSON.stringify({ 'message': 'start' }));
        $("videoFrame").removeClass("placeHolder");
    });
    $("#stop").click(function(){
        ws.send(JSON.stringify({ 'message': 'stop' }));
        $("#videoFrame").addClass("placeHolder");
    });
    $("#forward").click(function(){
        ws.send(JSON.stringify({ 'message': 'forward' }));
    });
    $("#backward").click(function(){
        ws.send(JSON.stringify({ 'message': 'backward' }));
    });
    $("#turnleft").click(function(){
        ws.send(JSON.stringify({ 'message': 'turnleft' }));
    });
    $("#turnright").click(function(){
        ws.send(JSON.stringify({ 'message': 'turnright' }));
    });
    $("#pickball").click(function(){
        ws.send(JSON.stringify({ 'message': 'pickball' }));
    });
    $("#hand").click(function(){
        ws.send(JSON.stringify({ 'message': 'hand' }));
    });
    $("#auto").click(function(){
        ws.send(JSON.stringify({ 'message': 'auto' }));
    });
});
ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};