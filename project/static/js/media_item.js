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
