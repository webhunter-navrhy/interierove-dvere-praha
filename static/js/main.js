// Interiérové dveře Praha – menu, filtr katalogu, náhled provedení/dekoru, galerie, sestavovač dveří, formuláře.
(function () {
  var d = document;

  // Menu: burger na mobilu, rozbalovací Sortiment
  var burger = d.querySelector('.burger');
  if (burger) burger.addEventListener('click', function () {
    var o = burger.getAttribute('aria-expanded') === 'true';
    burger.setAttribute('aria-expanded', String(!o));
    d.body.classList.toggle('menu-otevrene', !o);
  });
  d.querySelectorAll('.menu__rozbal').forEach(function (b) {
    b.addEventListener('click', function () {
      var o = b.getAttribute('aria-expanded') === 'true';
      b.setAttribute('aria-expanded', String(!o));
    });
  });
  d.addEventListener('click', function (e) {
    d.querySelectorAll('.menu__rozbal[aria-expanded="true"]').forEach(function (b) {
      if (!b.parentNode.contains(e.target)) b.setAttribute('aria-expanded', 'false');
    });
  });
  d.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') d.querySelectorAll('.menu__rozbal').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
  });

  // Filtr katalogu Fólie / CPL
  d.querySelectorAll('[data-filtr]').forEach(function (k) {
    k.querySelectorAll('button[data-f]').forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-f');
        k.querySelectorAll('button[data-f]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        k.querySelectorAll('[data-typ]').forEach(function (m) { m.hidden = f !== 'vse' && m.getAttribute('data-typ') !== f; });
      });
    });
  });

  // Detail modelu: provedení a dekor do náhledu
  function vymen(img, src, alt) {
    if (!img) return;
    img.removeAttribute('srcset'); img.src = src; if (alt) img.alt = alt;
  }
  var nahled = d.querySelector('[data-nahled] img');
  d.querySelectorAll('[data-varianta]').forEach(function (b) {
    b.addEventListener('click', function () {
      d.querySelectorAll('[data-varianta]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      vymen(nahled, b.getAttribute('data-varianta'), 'Interiérové dveře ' + b.getAttribute('data-nazev'));
      d.querySelector('[data-nahled]').style.setProperty('--r', b.getAttribute('data-r'));
      var top = d.querySelector('.model');
      if (top && top.getBoundingClientRect().bottom < 120) top.scrollIntoView({ behavior: 'smooth' });
    });
  });
  var vzorek = d.querySelector('.model__vzorek');
  d.querySelectorAll('[data-dekor]').forEach(function (b) {
    b.addEventListener('click', function () {
      d.querySelectorAll('[data-dekor]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      if (vzorek) { vymen(vzorek.querySelector('img'), b.getAttribute('data-dekor')); vzorek.querySelector('figcaption').textContent = b.getAttribute('data-nazev'); }
    });
  });

  // Galerie realizací
  var dlg = d.querySelector('.lightbox');
  if (dlg && dlg.showModal) {
    var odkazy = Array.prototype.slice.call(d.querySelectorAll('[data-lightbox]')), i = 0;
    var ukaz = function (n) { i = (n + odkazy.length) % odkazy.length; var a = odkazy[i]; var im = dlg.querySelector('img'); im.src = a.href; im.alt = a.querySelector('img').alt; };
    odkazy.forEach(function (a, n) { a.addEventListener('click', function (e) { e.preventDefault(); ukaz(n); dlg.showModal(); }); });
    dlg.querySelector('.lightbox__zavrit').addEventListener('click', function () { dlg.close(); });
    dlg.querySelector('.lightbox__dalsi:not(.lightbox__dalsi--zpet)').addEventListener('click', function () { ukaz(i + 1); });
    dlg.querySelector('.lightbox__dalsi--zpet').addEventListener('click', function () { ukaz(i - 1); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') ukaz(i + 1); if (e.key === 'ArrowLeft') ukaz(i - 1); });
  }

  // Sestavovač dveří
  var s = d.querySelector('[data-sestavovac]');
  if (s) {
    var M = JSON.parse(d.getElementById('modely-data').textContent);
    var kc = function (n) { return n ? n.toLocaleString('cs-CZ').replace(/\s/g, ' ') + ' Kč' : ''; };
    var $ = function (c) { return s.querySelector(c); };
    var esc = function (t) { var x = d.createElement('span'); x.textContent = t; return x.innerHTML; };
    var aktualni = null;
    var hodnota = function (n) { var x = s.querySelector('input[name="' + n + '"]:checked'); return x ? x.value : ''; };

    var souhrn = function () {
      var m = aktualni, vi = hodnota('varianta'), di = hodnota('dekor');
      $('.js-s-model').textContent = m ? m.nazev + ' (' + (m.typ === 'cpl' ? 'CPL' : 'fólie') + ')' : (hodnota('model') === 'poradit' ? 'poradíme' : '–');
      $('.js-s-var').textContent = m && vi !== '' ? m.varianty[vi] : '–';
      $('.js-s-dekor').textContent = m && di !== '' ? m.dekory[di] : (m && !m.dekory.length ? 'podle provedení' : '–');
      var pocet = Math.max(1, parseInt(s.pocet.value, 10) || 1);
      $('.js-s-typ').textContent = [hodnota('typ'), hodnota('sirka'), s.sila_zdi.value ? 'zeď ' + s.sila_zdi.value + ' mm' : '', pocet > 1 ? pocet + ' ks' : ''].filter(Boolean).join(', ');
      var cena = m ? (vi !== '' ? m.ceny[vi] : m.od) : null;
      $('.js-cena').textContent = cena ? (vi === '' ? 'od ' : '') + kc(cena) : 'po výběru modelu';
      $('.js-cena-pozn').textContent = cena ? (pocet > 1 ? 'za kus bez DPH, ' + pocet + ' ks = ' + kc(cena * pocet) : 'za kus bez DPH') : '';
      var v = s.querySelector('.sestavovac__nahled');
      var text = ['Model: ' + $('.js-s-model').textContent, 'Provedení: ' + $('.js-s-var').textContent, 'Dekor: ' + $('.js-s-dekor').textContent,
        'Typ a rozměr: ' + $('.js-s-typ').textContent, 'Montáž: ' + hodnota('montaz'), 'Doprava: ' + hodnota('doprava'), 'Cena křídla: ' + $('.js-cena').textContent];
      $('.js-souhrn').value = text.join('\n');
    };

    var vyberModel = function (slug) {
      aktualni = M.filter(function (x) { return x.slug === slug; })[0] || null;
      var vv = $('.js-varianty'), dd = $('.js-dekory');
      if (!aktualni) {
        vv.innerHTML = '<p class="krok__prazdne">Model s vámi vybereme při konzultaci.</p>';
        dd.innerHTML = '<p class="krok__prazdne">Dekor s vámi vybereme při konzultaci.</p>';
        $('.js-vzorek').hidden = true; souhrn(); return;
      }
      vv.innerHTML = aktualni.varianty.map(function (n, i) {
        return '<label class="volba volba--model"><input type="radio" name="varianta" value="' + i + '"' + (i === 0 ? ' checked' : '') + '><span class="volba__kridlo"><img src="' + aktualni.img[i] + '" alt="" width="60" height="159" loading="lazy"></span><b>' + esc(n) + '</b><small>' + kc(aktualni.ceny[i]) + '</small></label>';
      }).join('');
      dd.innerHTML = aktualni.dekory.length ? aktualni.dekory.map(function (n, i) {
        return '<label class="volba volba--dekor"><input type="radio" name="dekor" value="' + i + '"' + (i === 0 ? ' checked' : '') + '><img src="' + aktualni.dekory_img[i] + '" alt="" width="64" height="64" loading="lazy"><span>' + esc(n) + '</span></label>';
      }).join('') : '<p class="krok__prazdne">U modelu ' + esc(aktualni.nazev) + ' je dekor součástí provedení, vyberte ho v kroku 2.</p>';
      nastavNahled(); souhrn();
    };

    var nastavNahled = function () {
      if (!aktualni) return;
      var vi = hodnota('varianta') || aktualni.hlavni, di = hodnota('dekor');
      var im = $('.js-nahled'); im.src = aktualni.img[vi]; im.alt = 'Náhled: ' + aktualni.varianty[vi];
      $('.js-kridlo').style.setProperty('--r', aktualni.r[vi]);
      var vz = $('.js-vzorek');
      if (di !== '' && aktualni.dekory.length) { vz.hidden = false; vz.querySelector('img').src = aktualni.dekory_img[di]; vz.querySelector('figcaption').textContent = aktualni.dekory[di]; }
      else vz.hidden = true;
    };

    s.addEventListener('change', function (e) {
      if (e.target.name === 'model') vyberModel(e.target.value);
      else { nastavNahled(); souhrn(); }
    });
    s.addEventListener('input', function (e) { if (e.target.name === 'pocet' || e.target.name === 'sila_zdi') souhrn(); });

    var q = new URLSearchParams(location.search).get('model') || 'interierove-dvere-vasco-doors-leon';
    var start = s.querySelector('input[name="model"][value="' + (q || '') + '"]');
    if (start) { start.checked = true; vyberModel(q); } else souhrn();
  }

  // Formuláře (kontakt i sestavovač): v návrhu ukázkový režim, nic se neodesílá
  d.querySelectorAll('form.formular').forEach(function (f) {
    var stav = f.querySelector('.formular-stav');
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var past = f.querySelector('.past input');
      if (past && past.value) return;
      if (f.hasAttribute('data-sestavovac') && !f.telefon.value && !f.email.value) {
        stav.textContent = 'Vyplňte prosím telefon nebo e-mail, ať vám můžeme poslat nabídku.'; f.telefon.focus(); return;
      }
      var souhlas = f.querySelector('input[name="souhlas"]');
      if (souhlas && !souhlas.checked) { stav.textContent = 'Potvrďte prosím souhlas se zpracováním osobních údajů.'; return; }
      if (!f.hasAttribute('data-sestavovac') && !f.checkValidity()) { f.reportValidity(); return; }
      var endpoint = f.getAttribute('data-endpoint');
      if (f.getAttribute('data-demo') === '1' || !endpoint) {
        stav.textContent = 'Ukázka formuláře: v návrhu se nic neodesílá. Po spuštění webu přijde poptávka rovnou na e-mail vzorkovny.';
        return;
      }
      var fo = f.querySelector('input[type=file]');
      if (fo && fo.files[0] && fo.files[0].size > 9 * 1024 * 1024) { stav.textContent = 'Příloha je větší než 9 MB, pošlete ji prosím e-mailem.'; return; }
      // běžné odeslání (multipart): AJAX u FormSubmit přílohy zahazuje
      stav.textContent = 'Odesílám…';
      if (f.hasAttribute('data-sestavovac')) {
        // do e-mailu pošleme názvy místo čísel voleb (stejné jako v souhrnu)
        [['model', '.js-s-model'], ['varianta', '.js-s-var'], ['dekor', '.js-s-dekor']].forEach(function (p) {
          var r = f.querySelector('input[name="' + p[0] + '"]:checked'), t = f.querySelector(p[1]);
          if (r && t && t.textContent && t.textContent !== '–') r.value = t.textContent;
        });
      }
      f.action = endpoint;
      var nx = f.querySelector('input[name=_next]');
      if (!nx) { nx = d.createElement('input'); nx.type = 'hidden'; nx.name = '_next'; f.appendChild(nx); }
      nx.value = location.href.split('#')[0].split('?')[0] + '?odeslano=1';
      f.submit();
    });
  });

  // Po odeslání (návrat z FormSubmit) potvrdíme, že poptávka odešla
  if (/[?&]odeslano=1/.test(location.search)) {
    var ff = d.querySelector('form.formular'), st = ff && ff.querySelector('.formular-stav');
    if (st) {
      st.textContent = 'Děkujeme, Vaše zpráva byla odeslána. Brzy se Vám ozveme.';
      st.classList.add('formular-stav--ok');
      st.setAttribute('tabindex', '-1');
      var ok = function () { st.scrollIntoView({ block: 'center' }); };
      if (d.readyState === 'complete') ok(); else window.addEventListener('load', ok);
    }
    if (history.replaceState) history.replaceState(null, '', location.pathname + location.hash);
  }

  // Zvětšení obrázků v obsahu (tabulky a fotky): klepnutím na celou obrazovku
  d.addEventListener('click', function (e) {
    var f = e.target.closest ? e.target.closest('[data-zoom]') : null;
    if (!f) return;
    var o = d.createElement('div'); o.className = 'zoom'; o.setAttribute('role', 'dialog'); o.setAttribute('aria-label', 'Zvětšený obrázek');
    var im = d.createElement('img'); im.src = f.getAttribute('data-zoom'); im.alt = '';
    o.appendChild(im); o.addEventListener('click', function () { o.remove(); });
    d.addEventListener('keydown', function esc(k) { if (k.key === 'Escape') { o.remove(); d.removeEventListener('keydown', esc); } });
    d.body.appendChild(o);
  });

  // Sestavovač: typy dveří podle modelu (Ventura bez posuvných, Nero a Nero GT bez otočných)
  var typyPodleModelu = function (slug) {
    var skryt = /-ventura$/.test(slug || '') ? ['Posuvné do pouzdra', 'Posuvné na stěnu'] : (/-nero(-gt)?$/.test(slug || '') ? ['Interiérové otočné'] : []);
    var prvni = null;
    d.querySelectorAll('input[name="typ"]').forEach(function (r) {
      var lab = r.closest('label'), schovat = skryt.indexOf(r.value) > -1;
      lab.hidden = schovat; if (schovat && r.checked) r.checked = false;
      if (!schovat && !prvni) prvni = r;
    });
    if (prvni && !d.querySelector('input[name="typ"]:checked')) { prvni.checked = true; prvni.dispatchEvent(new Event('change', { bubbles: true })); }
  };
  d.addEventListener('change', function (e) { if (e.target.name === 'model') typyPodleModelu(e.target.value); });
  var q0 = new URLSearchParams(location.search).get('model'); if (q0) typyPodleModelu(q0);
})();

// Tlačítko Zpět nahoru (17. 10. 2026)
(function () {
  var b = document.querySelector('.totop'); if (!b) return;
  function upd() { b.hidden = window.scrollY < 600; }
  window.addEventListener('scroll', upd, { passive: true }); upd();
  b.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
})();
