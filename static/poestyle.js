



const container = document.querySelector('.container-grid');
const containerWidth = container.offsetWidth;
const imageWidth = 200; // width of the image element
const numImages = Math.floor(containerWidth / imageWidth);

for (let i = 0; i < numImages; i++) {
  const container = document.createElement('div');
  container.classList.add('container');
  container.innerHTML = `
    <a href="/specific_series/${i}">
      <img src="image/${i}.jpg" alt="Content ${i}">
    </a>
    <p>Content ${i}</p>
  `;
  containerGrid.appendChild(container);
}