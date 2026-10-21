(function () {
  const root = document.getElementById('app');
  const KEY = 'bellie-wine-oclock';
  const STYLES = [
    'The day’s negotiations are concluded. The evening’s deliberations may now commence.',
    'Your daily invitation to pause has arrived. Attendance is entirely optional.',
    'Some questions are best considered slowly. Others can wait until after the music starts.'
  ];
  const MODES = [
    ['day', 'Follow today’s cue'],
    ['jazz-lounge', 'The Jazz Lounge'],
    ['golden-hour', 'Golden Hour'],
    ['fireside', 'Fireside Reflections'],
    ['dinner-party', 'The Dinner Party'],
    ['quiet', 'Quiet Contemplation']
  ];
  const defaults = {
    reminderOn: false,
    time: '17:00',
    quietStart: '21:00',
    quietEnd: '08:00',
    notice: 0,
    music: 'day',
    narration: 'both',
    education: true,
    styles: [],
    sfx: true,
    volume: 0.85,
    skippedDate: '',
    favorites: { days: [], quotes: [] },
    firedKey: ''
  };
  let data = null;
  let prefs = loadPrefs();
  let view = 'today';
  let current = null;
  let queue = [];
  let stage = 'idle';
  const audio = new Audio();
  audio.preload = 'none';

  function loadPrefs() {
    try {
      return Object.assign({}, defaults, JSON.parse(localStorage.getItem(KEY) || '{}'), {
        favorites: Object.assign({}, defaults.favorites, JSON.parse(localStorage.getItem(KEY) || '{}').favorites || {})
      });
    } catch (e) {
      return Object.assign({}, defaults);
    }
  }
  function savePrefs() {
    localStorage.setItem(KEY, JSON.stringify(prefs));
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function temeculaDate(date) {
    return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' }).format(date || new Date());
  }
  function localDate() {
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function todayItem() {
    const key = temeculaDate();
    const [y, m, d] = key.split('-').map(Number);
    const n = Math.floor((Date.UTC(y, m - 1, d) - Date.UTC(2026, 9, 21)) / 86400000);
    return data.days[((n % 30) + 30) % 30];
  }
  function standalone() {
    return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  }
  function ios() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
  }
  function cueFile(item) {
    const id = prefs.music === 'day' ? item.cue : prefs.music;
    return '/wine-oclock/audio/' + id + '.wav';
  }
  function saved(kind, id) {
    return prefs.favorites[kind].includes(id);
  }
  function toggleSave(kind, id) {
    const list = prefs.favorites[kind];
    const i = list.indexOf(id);
    if (i >= 0) list.splice(i, 1);
    else list.push(id);
    savePrefs();
    render();
  }

  audio.addEventListener('ended', () => {
    if (stage === 'done') return;
    playNext();
  });
  audio.addEventListener('error', () => {
    const cap = document.getElementById('caption');
    if (cap) cap.textContent = 'The sound file did not load. The words are still here.';
    showTranscript();
    stage = 'done';
    paintPlay();
  });

  function playNext() {
    const src = queue.shift();
    if (!src) {
      stage = 'done';
      const cap = document.getElementById('caption');
      if (cap) cap.textContent = 'That’s today’s moment.';
      paintPlay();
      return;
    }
    stage = src.endsWith('.mp3') ? 'voice' : 'cue';
    audio.src = src;
    audio.volume = stage === 'voice' ? Number(prefs.volume) : Number(prefs.volume) * 0.45;
    const cap = document.getElementById('caption');
    if (cap) cap.textContent = stage === 'voice' ? 'Listening.' : 'A short signature, then the words.';
    if (stage === 'voice') showTranscript();
    audio.play().catch(() => {
      if (cap) cap.textContent = 'The phone blocked the sound. You can still read the moment.';
      showTranscript();
      stage = 'done';
      paintPlay();
    });
    paintPlay();
  }
  function showTranscript() {
    const el = document.getElementById('transcript');
    if (el) el.hidden = false;
  }
  function startPlayback(item) {
    current = item;
    if (prefs.narration === 'text') {
      showTranscript();
      stage = 'done';
      const cap = document.getElementById('caption');
      if (cap) cap.textContent = 'Reading, with the sound off.';
      paintPlay();
      return;
    }
    queue = [];
    if (prefs.sfx) {
      queue.push('/wine-oclock/audio/cork.wav');
      queue.push(cueFile(item));
    }
    queue.push('/wine-oclock/audio/' + item.id + '.mp3');
    playNext();
  }
  function paintPlay() {
    const btn = document.getElementById('play');
    if (!btn) return;
    if (stage === 'cue' || stage === 'voice') btn.textContent = audio.paused ? 'Resume' : 'Pause';
    else btn.textContent = prefs.narration === 'text' ? 'Read today’s moment' : 'Play Today’s Moment';
  }

  function shell(title, body) {
    root.innerHTML = '<button class="textish back" type="button" data-go="today">Back to today’s moment</button><h2>' + esc(title) + '</h2>' + body;
    bind();
  }
  function renderToday() {
    const item = todayItem();
    current = item;
    const when = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', weekday: 'long', month: 'long', day: 'numeric' }).format(new Date());
    root.innerHTML = [
      '<img class="logo" src="/images/brand/logo-header-horizontal.png" alt="Bellie Acres Wine. Good wine. No whine.">',
      '<h1>Wine O’Clock</h1>',
      '<p class="by">by Bellie Acres Wine</p>',
      '<p class="tag">A little wisdom. A little wine. A little nonsense.</p>',
      '<hr class="rule">',
      '<p class="kicker">Temecula · ' + esc(when) + ' · Day ' + item.day + '</p>',
      '<blockquote>' + esc(item.narration.split('. ').slice(0, 2).join('. ') + '.') + '</blockquote>',
      '<button class="play" id="play" type="button">Play Today’s Moment</button>',
      '<div class="transport" aria-label="Player">',
      '<button type="button" id="skip">Skip</button>',
      '<button type="button" id="read">Read it</button>',
      '<label class="vol">Volume <input id="volume" type="range" min="0" max="1" step="0.05" value="' + prefs.volume + '"></label>',
      '</div>',
      '<p class="caption" id="caption" aria-live="polite"></p>',
      '<article class="transcript" id="transcript" hidden><p>' + esc(item.narration) + '</p>' + (item.wineNote ? '<p>' + esc(item.wineNote) + '</p>' : '') + '</article>',
      '<button class="textish" id="save" type="button">' + (saved('days', item.id) ? 'Saved' : 'Save this moment') + '</button>',
      '<div id="invite"></div>',
      '<nav class="links" aria-label="In the app">',
      '<button class="row" type="button" data-go="guide">The Wine Guide</button>',
      '<button class="row" type="button" data-go="pairings">Pairings for the Occasion</button>',
      '<button class="row" type="button" data-go="archive">Earlier moments</button>',
      '<button class="row" type="button" data-go="quotes">The Wine Philosopher</button>',
      prefs.education ? '<button class="row" type="button" data-go="lessons">Wine in 60 Seconds</button>' : '',
      '<button class="row" type="button" data-go="prefs">Preferences and reminders</button>',
      '<button class="row" type="button" data-go="install">Add to iPhone</button>',
      '</nav>',
      '<p class="fine">For adults. Nothing here requires a drink, a streak, or a drive.</p>',
      '<p class="fine">Cultivated taste. Uncultivated wit.</p>'
    ].join('');
    bind();
    paintPlay();
  }
  function renderArchive() {
    const today = todayItem();
    const cards = data.days.map((item) => {
      const mark = item.id === today.id ? ' <span class="today-mark">Today</span>' : '';
      return '<article class="card"><p class="meta">Day ' + item.day + mark + '</p><h3>' + esc(item.title) + '</h3><p>' + esc(item.narration) + '</p><button class="textish" type="button" data-play="' + item.id + '">Play</button><button class="textish" type="button" data-save-day="' + item.id + '">' + (saved('days', item.id) ? 'Saved' : 'Save') + '</button></article>';
    }).join('');
    shell('Earlier moments', '<p>All thirty days are here. Today is marked. Nothing is locked behind a streak.</p>' + cards);
  }
  function renderGuide() {
    let list = data.varietals.slice();
    if (prefs.styles.length) {
      list.sort((a, b) => Number(prefs.styles.includes(b.id)) - Number(prefs.styles.includes(a.id)));
    }
    const cards = list.map((v) => '<button class="row" type="button" data-varietal="' + v.id + '">' + esc(v.name) + '<span>' + esc(v.color) + '</span></button>').join('');
    shell('The Wine Guide', '<p>A beginner’s shelf, not a final exam. Every note below can change with the producer, the vintage, the place, and the cellar.</p>' + cards + '<a class="row" href="/guides/temecula-red-varietals/">More on the Bellie Acres Wine site</a>');
  }
  function renderVarietal(id) {
    const v = data.varietals.find((item) => item.id === id);
    if (!v) return renderGuide();
    shell(v.name, [
      v.pronunciation ? '<p class="meta">' + esc(v.pronunciation) + '</p>' : '',
      '<p>' + esc(v.intro) + '</p>',
      '<p><strong>Body.</strong> ' + esc(v.body) + '</p>',
      '<p><strong>Acidity.</strong> ' + esc(v.acidity) + '</p>',
      '<p><strong>Tannin.</strong> ' + esc(v.tannin) + '</p>',
      '<p><strong>Aromas.</strong> ' + esc(v.aromas) + '</p>',
      '<p><strong>How it changes.</strong> ' + esc(v.variations) + '</p>',
      '<p><strong>With food.</strong> ' + esc(v.pairings) + '</p>',
      '<p><strong>Serving.</strong> ' + esc(v.serving) + '</p>',
      '<p><strong>You might also enjoy.</strong> ' + esc(v.also) + '</p>',
      '<p><strong>One fact.</strong> ' + esc(v.fact) + '</p>',
      '<p class="note">These are tendencies, not a guarantee. The bottle in front of you can disagree, and it is allowed to.</p>'
    ].join(''));
  }
  function renderLessons() {
    const cards = data.lessons.map((lesson) => '<article class="card"><h3>' + esc(lesson.title) + '</h3><p>' + esc(lesson.narration) + '</p><button class="textish" type="button" data-lesson="' + lesson.id + '">Play this lesson</button></article>').join('');
    shell('Wine in 60 Seconds', cards);
  }
  function renderPairings() {
    const cards = data.pairings.map((item) => '<article class="card"><h3>' + esc(item.title) + '</h3><p><strong>Why it works.</strong> ' + esc(item.why) + '</p><p><strong>Try.</strong> ' + esc(item.try) + '</p><p><strong>Instead.</strong> ' + esc(item.alt) + '</p><p><strong>Often a poor fit.</strong> ' + esc(item.avoid) + '</p></article>').join('');
    shell('Pairings for the Occasion', '<p>There is rarely one correct wine. Here is why a match works, and what else you can pour, including something with no alcohol.</p>' + cards + '<a class="row" href="/pairings/">The Bellie Acres Wine pairing library</a>');
  }
  function renderQuotes() {
    const cards = data.quotes.map((q) => '<article class="quote"><p class="meta">' + esc(q.category) + '</p><p>' + esc(q.text) + '</p><button class="textish" type="button" data-save-quote="' + q.id + '">' + (saved('quotes', q.id) ? 'Saved' : 'Save') + '</button><button class="textish" type="button" data-share="' + q.id + '">Share card</button></article>').join('');
    shell('The Wine Philosopher', '<p>Original lines. Not quotations from anyone else. Save one, or make a card.</p>' + cards);
  }
  function renderInstall() {
    const installed = standalone();
    const steps = installed
      ? '<p>This copy is open from your Home Screen.</p>'
      : '<ol><li>Open this page in Safari. Another browser’s share menu may not offer Add to Home Screen.</li><li>Tap Share.</li><li>Tap Add to Home Screen.</li><li>Tap Add.</li></ol><p>This page cannot tell that you have installed it until you open that Home Screen icon.</p>';
    shell('Add to iPhone', steps + '<p>Notification support and what happens in the background depend on the iOS version, whether the app was added to the Home Screen, and the permission you give. A reminder, when the phone allows one, only invites you to open Wine O’Clock. It does not start the audio.</p><p>This is a web app, not an App Store app. It cannot promise a custom sound at an exact minute while it is closed. Ordinary web apps cannot reliably do that on iPhone. The Play button is always here.</p>');
  }
  function renderPrefs() {
    const styles = data.varietals.map((v) => '<label class="check"><input type="checkbox" data-style="' + v.id + '"' + (prefs.styles.includes(v.id) ? ' checked' : '') + '> ' + esc(v.name) + '</label>').join('');
    const modes = MODES.map((mode) => '<option value="' + mode[0] + '"' + (prefs.music === mode[0] ? ' selected' : '') + '>' + esc(mode[1]) + '</option>').join('');
    const notices = STYLES.map((line, i) => '<label class="check"><input type="radio" name="notice" value="' + i + '"' + (Number(prefs.notice) === i ? ' checked' : '') + '> ' + esc(line) + '</label>').join('');
    shell('Preferences', [
      '<p class="note">Reminders are optional. If you allow them, they invite you to open the app. They do not start the music, and they cannot be promised at an exact time while an iPhone app is closed.</p>',
      '<label class="check"><input id="reminder" type="checkbox"' + (prefs.reminderOn ? ' checked' : '') + '> Remind me</label>',
      '<label>Preferred time<input id="time" type="time" value="' + esc(prefs.time) + '"></label>',
      '<label>Quiet hours begin<input id="qstart" type="time" value="' + esc(prefs.quietStart) + '"></label>',
      '<label>Quiet hours end<input id="qend" type="time" value="' + esc(prefs.quietEnd) + '"></label>',
      '<fieldset><legend>Reminder wording</legend>' + notices + '</fieldset>',
      '<button class="solid" id="permit" type="button">Allow reminders on this device</button>',
      '<p class="note" id="permit-note"></p>',
      '<button class="ghost" id="skipday" type="button">Skip today. No guilt, no streak.</button>',
      '<label>Music signature<select id="music">' + modes + '</select></label>',
      '<p class="note">The signatures are original tones made for this app, not recordings of a band. Nothing plays until you press Play.</p>',
      '<label>Narration<select id="narration"><option value="both"' + (prefs.narration === 'both' ? ' selected' : '') + '>Audio and text</option><option value="audio"' + (prefs.narration === 'audio' ? ' selected' : '') + '>Audio, with the transcript available</option><option value="text"' + (prefs.narration === 'text' ? ' selected' : '') + '>Text only</option></select></label>',
      '<label class="check"><input id="sfx" type="checkbox"' + (prefs.sfx ? ' checked' : '') + '> Opening sound</label>',
      '<label class="check"><input id="education" type="checkbox"' + (prefs.education ? ' checked' : '') + '> Keep wine lessons easy to find</label>',
      '<fieldset><legend>Wine styles you like, if you want to say</legend>' + styles + '</fieldset>',
      '<button class="ghost" id="reset" type="button">Reset preferences and clear saved items</button>',
      '<p class="note">Nothing here is sent to an account. It stays on this device. The spoken voice is Andrew. If a line still sounds mechanical, refresh the page so the old voice is not stuck in the phone.</p>'
    ].join(''));
  }

  function render() {
    if (view === 'today') renderToday();
    else if (view === 'archive') renderArchive();
    else if (view === 'guide') renderGuide();
    else if (view === 'lessons') renderLessons();
    else if (view === 'pairings') renderPairings();
    else if (view === 'quotes') renderQuotes();
    else if (view === 'prefs') renderPrefs();
    else if (view === 'install') renderInstall();
    else if (view.indexOf('varietal:') === 0) renderVarietal(view.split(':')[1]);
    const main = document.querySelector('h1, h2');
    if (main) main.focus && view !== 'today' && main.setAttribute('tabindex', '-1');
  }

  function bind() {
    root.querySelectorAll('[data-go]').forEach((el) => el.addEventListener('click', () => { view = el.getAttribute('data-go'); render(); }));
    root.querySelectorAll('[data-varietal]').forEach((el) => el.addEventListener('click', () => { view = 'varietal:' + el.getAttribute('data-varietal'); render(); }));
    root.querySelectorAll('[data-save-day]').forEach((el) => el.addEventListener('click', () => toggleSave('days', el.getAttribute('data-save-day'))));
    root.querySelectorAll('[data-save-quote]').forEach((el) => el.addEventListener('click', () => toggleSave('quotes', el.getAttribute('data-save-quote'))));
    root.querySelectorAll('[data-share]').forEach((el) => el.addEventListener('click', () => shareQuote(el.getAttribute('data-share'))));
    root.querySelectorAll('[data-play]').forEach((el) => el.addEventListener('click', () => {
      audio.pause();
      const item = data.days.find((day) => day.id === el.getAttribute('data-play'));
      view = 'today';
      render();
      startPlayback(item);
    }));
    root.querySelectorAll('[data-lesson]').forEach((el) => el.addEventListener('click', () => {
      const lesson = data.lessons.find((item) => item.id === el.getAttribute('data-lesson'));
      queue = ['/wine-oclock/audio/lesson-' + lesson.id + '.mp3'];
      stage = 'voice';
      playNext();
    }));
    const play = document.getElementById('play');
    if (play) play.addEventListener('click', () => {
      if (stage === 'cue' || stage === 'voice') {
        if (audio.paused) audio.play();
        else audio.pause();
        paintPlay();
        return;
      }
      startPlayback(todayItem());
    });
    const skip = document.getElementById('skip');
    if (skip) skip.addEventListener('click', () => {
      if (stage === 'cue') {
        queue = queue.filter((src) => src.endsWith('.mp3'));
        audio.pause();
        playNext();
      } else if (stage === 'voice') {
        audio.pause();
        queue = [];
        stage = 'done';
        showTranscript();
        paintPlay();
      }
    });
    const read = document.getElementById('read');
    if (read) read.addEventListener('click', () => { audio.pause(); showTranscript(); });
    const save = document.getElementById('save');
    if (save) save.addEventListener('click', () => toggleSave('days', todayItem().id));
    const volume = document.getElementById('volume');
    if (volume) volume.addEventListener('input', () => {
      prefs.volume = Number(volume.value);
      audio.volume = stage === 'voice' ? prefs.volume : prefs.volume * 0.45;
      savePrefs();
    });
    const reminder = document.getElementById('reminder');
    if (reminder) reminder.addEventListener('change', () => { prefs.reminderOn = reminder.checked; savePrefs(); });
    ['time', 'qstart', 'qend'].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('change', () => {
        prefs[id === 'time' ? 'time' : id === 'qstart' ? 'quietStart' : 'quietEnd'] = el.value;
        savePrefs();
      });
    });
    root.querySelectorAll('input[name="notice"]').forEach((el) => el.addEventListener('change', () => { prefs.notice = Number(el.value); savePrefs(); }));
    const music = document.getElementById('music');
    if (music) music.addEventListener('change', () => { prefs.music = music.value; savePrefs(); });
    const narration = document.getElementById('narration');
    if (narration) narration.addEventListener('change', () => { prefs.narration = narration.value; savePrefs(); });
    const sfx = document.getElementById('sfx');
    if (sfx) sfx.addEventListener('change', () => { prefs.sfx = sfx.checked; savePrefs(); });
    const education = document.getElementById('education');
    if (education) education.addEventListener('change', () => { prefs.education = education.checked; savePrefs(); });
    root.querySelectorAll('[data-style]').forEach((el) => el.addEventListener('change', () => {
      const id = el.getAttribute('data-style');
      if (el.checked && !prefs.styles.includes(id)) prefs.styles.push(id);
      if (!el.checked) prefs.styles = prefs.styles.filter((item) => item !== id);
      savePrefs();
    }));
    const permit = document.getElementById('permit');
    if (permit) permit.addEventListener('click', askPermission);
    const skipday = document.getElementById('skipday');
    if (skipday) skipday.addEventListener('click', () => { prefs.skippedDate = localDate(); savePrefs(); skipday.textContent = 'Today is skipped.'; });
    const reset = document.getElementById('reset');
    if (reset) reset.addEventListener('click', () => {
      localStorage.removeItem(KEY);
      prefs = Object.assign({}, defaults, { favorites: { days: [], quotes: [] } });
      view = 'prefs';
      render();
    });
  }

  function askPermission() {
    const note = document.getElementById('permit-note');
    if (!('Notification' in window)) {
      if (note) note.textContent = 'This browser does not offer notifications. The Play button still works.';
      return;
    }
    Notification.requestPermission().then((result) => {
      if (note) note.textContent = result === 'granted' ? 'Reminders are allowed on this device. They invite you to open the app. They do not play audio.' : 'Reminders stay off. You can still open the app and press Play.';
    });
  }

  function minutes(value) {
    const [h, m] = value.split(':').map(Number);
    return h * 60 + m;
  }
  function inQuiet(now) {
    const start = minutes(prefs.quietStart);
    const end = minutes(prefs.quietEnd);
    if (start === end) return false;
    if (start < end) return now >= start && now < end;
    return now >= start || now < end;
  }
  function checkReminder() {
    if (!prefs.reminderOn || prefs.skippedDate === localDate()) return;
    const now = new Date();
    const nowMin = now.getHours() * 60 + now.getMinutes();
    if (inQuiet(nowMin) || nowMin !== minutes(prefs.time)) return;
    const key = localDate() + prefs.time;
    if (prefs.firedKey === key) return;
    prefs.firedKey = key;
    savePrefs();
    const body = STYLES[Number(prefs.notice)] || STYLES[0];
    const invite = document.getElementById('invite');
    if (invite) invite.innerHTML = '<article class="card"><p>' + esc(body) + '</p><button class="solid" id="invite-play" type="button">Play Today’s Moment</button></article>';
    const invitePlay = document.getElementById('invite-play');
    if (invitePlay) invitePlay.addEventListener('click', () => startPlayback(todayItem()));
    if ('Notification' in window && Notification.permission === 'granted') {
      const note = new Notification('Wine O’Clock', { body: body, icon: '/wine-oclock/apple-touch-icon.png' });
      note.onclick = () => { window.focus(); note.close(); };
    }
  }

  function shareQuote(id) {
    const quote = data.quotes.find((item) => item.id === id);
    const canvas = document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1350;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#26392F';
    ctx.fillRect(0, 0, 1080, 1350);
    ctx.fillStyle = '#C5A15B';
    ctx.fillRect(120, 180, 120, 2);
    ctx.fillStyle = '#F4F0DF';
    ctx.font = 'italic 54px Georgia, serif';
    wrap(ctx, quote.text, 120, 280, 840, 68);
    ctx.font = '28px Georgia, serif';
    ctx.fillText('Wine O’Clock by Bellie Acres Wine', 120, 1180);
    const finish = () => {
      canvas.toBlob((blob) => {
        const file = new File([blob], 'wine-oclock.png', { type: 'image/png' });
        if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
          navigator.share({ files: [file], title: 'Wine O’Clock by Bellie Acres Wine', text: quote.text }).catch(() => download(blob));
        } else download(blob);
      }, 'image/png');
    };
    const logo = new Image();
    logo.onload = () => { ctx.drawImage(logo, 120, 1220, 280, 90); finish(); };
    logo.onerror = finish;
    logo.src = '/images/brand/logo-header-horizontal.png';
  }
  function wrap(ctx, text, x, y, max, lh) {
    const words = text.split(' ');
    let line = '';
    words.forEach((word) => {
      const trial = line ? line + ' ' + word : word;
      if (ctx.measureText(trial).width > max) {
        ctx.fillText(line, x, y);
        y += lh;
        line = word;
      } else line = trial;
    });
    if (line) ctx.fillText(line, x, y);
  }
  function download(blob) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'wine-oclock.png';
    a.click();
  }

  Promise.all(['days', 'varietals', 'lessons', 'pairings', 'quotes'].map((name) => fetch('/wine-oclock/content/' + name + '.json').then((r) => {
    if (!r.ok) throw new Error(name);
    return r.json();
  }))).then((parts) => {
    data = { days: parts[0], varietals: parts[1], lessons: parts[2], pairings: parts[3], quotes: parts[4] };
    render();
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/wine-oclock/sw.js', { scope: '/wine-oclock/' }).catch(() => {});
    setInterval(checkReminder, 20000);
    document.addEventListener('visibilitychange', checkReminder);
  }).catch(() => {
    root.innerHTML = '<h1>Wine O’Clock</h1><p class="by">by Bellie Acres Wine</p><article class="card error"><p>Today’s library did not load. Check the connection, then try again. The rest of Bellie Acres Wine is unchanged.</p><button class="solid" type="button" onclick="location.reload()">Try again</button></article>';
  });
})();
