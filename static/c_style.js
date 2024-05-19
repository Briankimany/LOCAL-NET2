const video = document.getElementById('video');
const playPause = document.getElementById('play-pause');
const mute = document.getElementById('mute');
const fullscreen = document.getElementById('fullscreen');
const seekBar = document.getElementById('seek');
const currentTime = document.getElementById('current-time');
const duration = document.getElementById('duration');

// Play/Pause button toggle
playPause.addEventListener('click', () => {
    if (video.paused) {
        video.play();
    } else {
        video.pause();
    }
});

// Double tap on right to seek forward and left to seek backward
video.addEventListener('dblclick', (event) => {
    const rect = video.getBoundingClientRect();
    const x = event.clientX - rect.left;
    if (x > rect.width / 2) {
        video.currentTime += 10; // Seek forward 10 seconds
    } else {
        video.currentTime -= 10; // Seek backward 10 seconds
    }
});

// Video player resize based on device width
window.addEventListener('resize', () => {
    const videoWidth = document.body.offsetWidth;
    video.width = videoWidth;
});

// Initialize video player
video.addEventListener('loadedmetadata', () => {
    duration.textContent = formatTime(video.duration);
});

video.addEventListener('timeupdate', () => {
    currentTime.textContent = formatTime(video.currentTime);
    seekBar.value = video.currentTime / video.duration * 100;
});

function formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}