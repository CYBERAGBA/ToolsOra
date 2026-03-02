document.addEventListener('DOMContentLoaded', function(){
  // Nav toggle for small screens
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      nav.classList.toggle('open');
    });
  }

  // Auto-dismiss flash messages after 4s with fade
  const flashes = document.querySelectorAll('.flashes li');
  if (flashes.length) {
    setTimeout(() => {
      flashes.forEach(li => {
        li.style.transition = 'opacity 360ms, transform 360ms, height 360ms';
        li.style.opacity = '0';
        li.style.transform = 'translateY(-8px)';
        setTimeout(() => li.remove(), 420);
      });
    }, 4000);
  }

  // Make .card elements with data-href clickable
  document.querySelectorAll('.card[data-href]').forEach(card => {
    card.style.cursor = 'pointer';
    card.addEventListener('click', () => {
      const href = card.dataset.href;
      if (href) window.location.href = href;
    });
  });

  // Prevent double-submit and show sending state
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (btn) {
        btn.disabled = true;
        if (btn.tagName.toLowerCase() === 'button') {
          btn.dataset._text = btn.innerText;
          btn.innerText = 'Envoi...';
        }
      }
    });
  });

  // Close nav on outside click (mobile)
  document.addEventListener('click', (e) => {
    if (nav && nav.classList.contains('open')) {
      const keep = e.target.closest('.nav') || e.target.closest('.nav-toggle');
      if (!keep) nav.classList.remove('open');
    }
  });

  /* Toast notifications system */
  function makeToast(type = 'info', title = '', msg = '', timeout = 4500) {
    const container = document.getElementById('toasts');
    if (!container) return;
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<div class="content"><div class="title">${title}</div><div class="msg">${msg}</div></div>`;
    container.appendChild(t);
    setTimeout(() => t.classList.add('visible'), 50);
    const tid = setTimeout(() => {
      t.style.opacity = '0';
      t.style.transform = 'translateY(18px)';
      setTimeout(() => t.remove(), 420);
    }, timeout);
    t.addEventListener('click', () => {
      clearTimeout(tid);
      t.remove();
    });
    return t;
  }

  // Expose a simple method for inline triggers
  document.querySelectorAll('[data-toast]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const cfg = btn.dataset.toast.split('|');
      makeToast(cfg[0] || 'info', cfg[1] || '', cfg[2] || '');
    });
  });

  // Dashboard: filter modules list
  const search = document.getElementById('search-modules');
  if (search) {
    search.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      document.querySelectorAll('.module-item').forEach(item => {
        const t = item.querySelector('.module-title')?.innerText.toLowerCase() || '';
        item.style.display = t.indexOf(q) === -1 ? 'none' : '';
      });
    });
  }

  // Widget collapse toggles
  document.querySelectorAll('.widget .widget-header .toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const widget = btn.closest('.widget');
      const body = widget.querySelector('.widget-body');
      if (body.style.maxHeight && body.style.maxHeight !== '0px') {
        body.style.maxHeight = '0px';
        btn.innerText = '+';
      } else {
        body.style.maxHeight = body.scrollHeight + 'px';
        btn.innerText = '–';
      }
    });
    // initialize collapsed
    const widget = btn.closest('.widget');
    const body = widget.querySelector('.widget-body');
    body.style.transition = 'max-height 320ms ease';
    body.style.maxHeight = '0px';
  });

  // Simulate subscription action (client-side) and show toast
  document.querySelectorAll('form[data-simulate="subscribe"]').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const plan = form.querySelector('select[name="plan"]')?.value || 'monthly';
      makeToast('success', 'Abonnement', `Plan ${plan} activé (simulation)`);
      // re-enable submit button after brief simulated delay
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.innerText = 'Enregistré';
      }
      setTimeout(() => {
        if (btn) { btn.disabled = false; btn.innerText = "S'abonner"; }
      }, 1500);
    });
  });

  // Simple client-side validation helper for auth forms
  document.querySelectorAll('form[data-validate="auth"]').forEach(form => {
    form.addEventListener('submit', (e) => {
      const email = form.querySelector('input[type="email"]');
      const pwd = form.querySelector('input[type="password"]');
      if (email && pwd && (!email.value || !pwd.value)) {
        e.preventDefault();
        makeToast('error', 'Erreur', 'Veuillez remplir tous les champs requis');
      }
    });
  });

  // Client-side validation for registration forms
  document.querySelectorAll('form[data-validate="register"]').forEach(form => {
    form.addEventListener('submit', (e) => {
      const username = form.querySelector('input[name="username"]');
      const email = form.querySelector('input[type="email"]');
      const pwd = form.querySelector('input[name="password"]');
      const pwd2 = form.querySelector('input[name="password2"]');
      if (!username || !username.value || !email || !email.value || !pwd || !pwd.value || !pwd2 || !pwd2.value) {
        e.preventDefault();
        makeToast('error', 'Erreur', 'Tous les champs sont requis');
        return;
      }
      if (pwd.value !== pwd2.value) {
        e.preventDefault();
        makeToast('error', 'Erreur', 'Les mots de passe ne correspondent pas');
        return;
      }
      if (pwd.value.length < 6) {
        e.preventDefault();
        makeToast('error', 'Erreur', 'Le mot de passe doit contenir au moins 6 caractères');
        return;
      }
      // allow submit to proceed
    });
  });

  // SaaS converter form handling (AJAX)
  const converter = document.getElementById('converter-form');
  if (converter) {
    converter.addEventListener('submit', async (e) => {
      e.preventDefault();
      const f = converter.querySelector('input[type=file]');
      if (!f || !f.files || f.files.length === 0) { makeToast('error','Erreur','Aucun fichier sélectionné'); return; }
      const formData = new FormData();
      formData.append('file', f.files[0]);
      formData.append('direction', converter.querySelector('select[name="direction"]').value);
      makeToast('info','Conversion','Envoi du fichier...');
      try {
        const res = await fetch('/modules/saas/convert', { method: 'POST', body: formData });
        const json = await res.json();
        if (res.ok && json.converted) {
          const msg = `Fichier ${json.original} traité (simulation)`;
          makeToast('success','Terminé', msg);
          const out = document.getElementById('convert-result');
          if (out) out.innerHTML = `<div class=\"small muted\">${msg}</div>`;
        } else {
          makeToast('error','Erreur', json.error || 'Échec de la conversion');
        }
      } catch (err) {
        makeToast('error','Erreur', 'Erreur réseau lors de l\'envoi');
      }
    });
    const clr = document.getElementById('clear-convert');
    if (clr) clr.addEventListener('click', () => {
      converter.reset();
      const out = document.getElementById('convert-result'); if (out) out.innerHTML = '';
    });
    // Drag & drop helper
    const drop = document.getElementById('drop-area');
    const fileInput = converter.querySelector('input[type=file]');
    if (drop && fileInput) {
      ['dragenter','dragover'].forEach(ev => drop.addEventListener(ev, (e)=>{ e.preventDefault(); drop.style.borderColor='var(--brand)'; drop.style.background='rgba(23,162,255,0.02)'}));
      ['dragleave','drop'].forEach(ev => drop.addEventListener(ev, (e)=>{ e.preventDefault(); drop.style.borderColor=''; drop.style.background=''; }));
      drop.addEventListener('drop', (e)=>{
        e.preventDefault();
        const f = e.dataTransfer.files && e.dataTransfer.files[0];
        if (f) fileInput.files = e.dataTransfer.files;
      });
    }

    // Load conversion history
    async function loadHistory(){
      const el = document.getElementById('conversion-history');
      if(!el) return;
      try{
        const res = await fetch('/modules/saas/history');
        const json = await res.json();
        if(json.history && json.history.length){
          el.innerHTML = '';
          json.history.forEach(h=>{
            const item = document.createElement('div');
            item.className = 'module-item';
            item.innerHTML = `<div><strong>${h.original}</strong><div class=\"small muted\">${h.direction} • ${h.created_at}</div></div><div><a href=\"/modules/saas/download/${h.output}\">Télécharger</a></div>`;
            el.appendChild(item);
          });
        } else {
          el.innerHTML = '<div class="empty">Aucune conversion récente</div>';
        }
      }catch(err){ el.innerHTML = '<div class="empty">Impossible de charger l\'historique</div>' }
    }
    loadHistory();
  }

  // PDF merge form
  const mergeForm = document.getElementById('merge-form');
  if (mergeForm) {
    mergeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const files = mergeForm.querySelector('input[name="files"]').files;
      if (!files || files.length < 2) { makeToast('error','Erreur','Sélectionnez au moins 2 fichiers'); return; }
      const fd = new FormData();
      for (let i=0;i<files.length;i++) fd.append('files', files[i]);
      makeToast('info','Fusion','Envoi des fichiers...');
      try {
        const res = await fetch('/modules/saas/pdf/merge', { method: 'POST', body: fd });
        const json = await res.json();
        if (res.ok && json.merged) {
          makeToast('success','Fusion réussie', json.output);
          const out = document.getElementById('merge-result'); if (out) out.innerHTML = `<a href="${json.download}">Télécharger ${json.output}</a>`;
          loadHistory && loadHistory();
        } else { makeToast('error','Erreur', json.error || 'Fusion échouée'); }
      } catch (err) { makeToast('error','Erreur','Erreur réseau'); }
    });
  }

  // PDF split form
  const splitForm = document.getElementById('split-form');
  if (splitForm) {
    splitForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const file = splitForm.querySelector('input[name="file"]').files[0];
      if (!file) { makeToast('error','Erreur','Sélectionnez un fichier'); return; }
      const fd = new FormData(); fd.append('file', file);
      makeToast('info','Split','Envoi du fichier...');
      try {
        const res = await fetch('/modules/saas/pdf/split', { method: 'POST', body: fd });
        const json = await res.json();
        if (res.ok && json.split) {
          makeToast('success','Split terminé', `${json.outputs.length} pages générées`);
          const out = document.getElementById('split-result'); if (out) out.innerHTML = json.outputs.map(o=>`<div><a href="/modules/saas/download/${o}">${o}</a></div>`).join('');
          loadHistory && loadHistory();
        } else { makeToast('error','Erreur', json.error || 'Split échoué'); }
      } catch (err) { makeToast('error','Erreur','Erreur réseau'); }
    });
  }

});