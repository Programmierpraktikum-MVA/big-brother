$(document).ready(function(){
    const video = document.querySelector('video');
    const canvas = document.querySelector('canvas');
    canvas.width = 480;
    canvas.height = 360;

    setInterval(function(){
        /* set the canvas to the dimensions of the video feed */
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        /* make the snapshot */
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    }, 30);

    navigator.mediaDevices.getUserMedia( {audio: false, video: true })
    .then(stream => video.srcObject = stream)
    .catch(error => console.error(error));
});
