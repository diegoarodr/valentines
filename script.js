const scene1 = document.getElementById('scene1');
const scene2 = document.getElementById('scene2');
const enterButton = document.getElementById('enterButton');
const backgroundVideo = document.getElementById('backgroundVideo');
const yesButton = document.getElementById('yesButton');
const menu = document.getElementById('menu');
const heartContainer = document.getElementById('heartContainer');
const banner = document.getElementById('banner');

let generateHearts = true;
let buttonShown = false;

enterButton.addEventListener('click', () => {
  scene1.style.display = 'none';
  scene2.style.display = 'block';
  backgroundVideo.play();
  heartContainer.style.display = 'none';
  generateHearts = false;
});

backgroundVideo.addEventListener('timeupdate', () => {
  if (backgroundVideo.currentTime >= 29 &&!buttonShown) {
    backgroundVideo.pause();
    yesButton.style.display = 'block';
    buttonShown = true;
  }
});

yesButton.addEventListener('click', () => {
  yesButton.style.display = 'none';
  menu.style.display = 'block';
  banner.style.display = 'block';
  backgroundVideo.play();
});

backgroundVideo.addEventListener('ended', () => {
  backgroundVideo.pause();
});

function createHeart() {
  if (generateHearts) {
    const heart = document.createElement('div');
    heart.classList.add('heart');
    heart.style.left = Math.random() * (window.innerWidth - 50) + 'px';
    heart.style.top = Math.random() * (window.innerHeight - 30) + 'px';
    heart.style.setProperty('--hue', Math.random() * 360 + 'deg');
    document.body.appendChild(heart);

    setTimeout(() => {
      heart.remove();
    }, 7000);
  }
  requestAnimationFrame(createHeart);
}

requestAnimationFrame(createHeart);