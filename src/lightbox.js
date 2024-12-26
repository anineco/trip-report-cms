import { LuminousGallery } from 'luminous-lightbox';

window.addEventListener('DOMContentLoaded',
  function () {
    new LuminousGallery(
      document.querySelectorAll('.lightbox'),
      null,
      { sourceAttribute: 'data-src' }
    );
  }
);
