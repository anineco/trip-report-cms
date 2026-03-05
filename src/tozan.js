// tozan.js
import {install} from 'ga-gtag';
const GTAG_ID = import.meta.env.VITE_GTAG;
if (GTAG_ID) install(GTAG_ID);
const YEAR = Number(import.meta.env.VITE_YEAR);
const LM_YEAR = Number(import.meta.env.VITE_LM_YEAR);

const passive = { passive: true };

function init() {
  function routemap(url) {
    if (window.innerWidth < 670) {
      window.open(url, 'ROUTEMAP');
    } else {
      window.open(url, 'ROUTEMAP', 'width=670,height=510,resizable=yes');
    }
  }

  for (const element of document.querySelectorAll('a[href^="routemap.html"],a[href^="https://map.jpn.org/mountain.html?"]')) {
    element.addEventListener('click', function (event) {
      event.preventDefault();
      routemap(event.currentTarget.href);
    });
  }

  const fn = location.pathname.match(/\/([^/]*)\.html/)?.[1] || 'index';

  function setupYearSelect(id, currentYear, startYear, prefix, isShort) {
    const select = document.getElementById(id);
    if (!select) return;
    for (let year = currentYear; year >= startYear; year--) {
      const value = isShort ? String(year).slice(-2) : year;
      const option = new Option(year + '年', value);
      if (fn === prefix + value) option.selected = true;
      select.appendChild(option);
    }
    select.addEventListener('change', function (event) {
      location.assign(prefix + event.target.value + '.html');
    }, passive);
  }

  setupYearSelect('ch-year', YEAR, 1997, 'ch', false);
  setupYearSelect('hist-year', LM_YEAR, 2004, 'hist', true);

  const footer = document.querySelector('footer');
  if (footer) {
    const img = new Image(1, 1);
    img.src = (fn === 'index')
      ? 'report/report.cgi?' + encodeURIComponent(document.referrer)
      : 'lime/lime.cgi?' + fn;
    img.alt = '';
    footer.appendChild(img);
  }

  const mainElement = document.querySelector('main');
  if (mainElement && sessionStorage.getItem('url') === location.href) {
    mainElement.scrollTop = Number(sessionStorage.getItem('pos'));
  }
}

init();

window.addEventListener('beforeunload', function (_event) {
  sessionStorage.setItem('url', location.href);
  const mainElement = document.querySelector('main');
  if (mainElement) sessionStorage.setItem('pos', mainElement.scrollTop);
});
// end of tozan.js
