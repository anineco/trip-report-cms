// tozan.js
import {install} from 'ga-gtag';
install(process.env.VITE_GTAG);
const YEAR = Number(import.meta.env.VITE_YEAR);
const LM_YEAR = Number(import.meta.env.VITE_LM_YEAR);

function routemap(url) {
  if (window.innerWidth < 670) {
    window.open(url, 'ROUTEMAP');
  } else {
    window.open(url, 'ROUTEMAP', 'width=670,height=510,resizable=yes');
  }
}

const passive = { passive: true };

window.addEventListener('DOMContentLoaded', function (_event) {
  for (const element of document.querySelectorAll('a[href^="routemap.html"],a[href^="https://map.jpn.org/mountain.html?"]')) {
    element.addEventListener('click', function (event) {
      event.preventDefault();
      routemap(event.target.href);
    });
  }

  const ma = location.pathname.match(/\/([^/]*)\.html/);
  const fn = ma ? ma[1] : 'index';

  const ch = document.getElementById('ch-year');
  if (ch) {
    for (let year = YEAR; year >= 1997; year--) {
      const option = document.createElement('option');
      option.setAttribute('value', year);
      if (fn == 'ch' + year) {
        option.setAttribute('selected', 'selected');
      }
      option.textContent = year + '年';
      ch.appendChild(option);
    }
    ch.addEventListener('change', function (event) {
      location.assign('ch' + event.target.value + '.html');
    }, passive);
  }

  const hist = document.getElementById('hist-year');
  if (hist) {
    for (let year = LM_YEAR; year >= 2004; year--) {
      const yy = String(year).slice(-2);
      const option = document.createElement('option');
      option.setAttribute('value', yy);
      if (fn == 'hist' + yy) {
        option.setAttribute('selected', 'selected');
      }
      option.textContent = year + '年';
      hist.appendChild(option);
    }
    hist.addEventListener('change', function (event) {
      location.assign('hist' + event.target.value + '.html');
    }, passive);
  }

  for (const element of document.querySelectorAll('footer')) {
    const img = document.createElement('img');
    img.setAttribute('src', (fn == 'index')
      ? 'report/report.cgi?' + escape(document.referrer)
      : 'lime/lime.cgi?' + fn
    );
    img.setAttribute('width', 1);
    img.setAttribute('height', 1);
    img.setAttribute('alt', '');
    element.appendChild(img);
  }

  if (sessionStorage.getItem('url') === location.href) {
    document.querySelector('main').scrollTop = Number(sessionStorage.getItem('pos'));
  }
});

window.addEventListener('beforeunload', function (_event) {
  sessionStorage.setItem('url', location.href);
  sessionStorage.setItem('pos', document.querySelector('main').scrollTop);
});
// end of tozan.js
