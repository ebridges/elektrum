function renderThumbnails(images, locations) {
  for (let loc of locations) {
    let i = images.shift()
    loadImage(
      i.src,
      function(img) {
        img.style.width = i.w;
        img.style.height = i.h;
        img.style.maxWidth = '90vw';
        loc.appendChild(img);
      },
      {
        orientation: true
      }
    );
  }
}

function renderImage(image, loc) {
  loadImage(
    image.src,
    function(img) {
      img.style.width = image.w;
      img.style.height = image.h;
      img.style.maxWidth = '90vw';
      loc.appendChild(img);
    },
    {
      orientation: true
    }
  );
}
