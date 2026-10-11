(() => {
  const body = document.body;
  const notice = document.getElementById('notice');
  const editorPanel = document.getElementById('editor-panel');
  const editor = document.getElementById('markdown-editor');
  const previewPanel = document.getElementById('preview-panel');
  const frame = document.getElementById('prototype-frame');
  const stateSelect = document.getElementById('prototype-state-select');
  const mapping = document.getElementById('prototype-mapping');
  const token = body.dataset.sessionToken;
  const setNotice = (message) => { notice.textContent = message; };
  let zoom = 1;

  // Scale the complete prototype canvas inside each table cell. This keeps
  // the canonical screen proportions instead of letting the iframe reflow to
  // the narrow table width.
  const fitInlinePrototypes = () => {
    document.querySelectorAll('.prd-inline-prototype').forEach(wrapper => {
      const viewport = wrapper.querySelector('.prd-inline-prototype-viewport');
      const iframe = wrapper.querySelector('iframe');
      if (!viewport || !iframe) return;
      const [canvasWidth, canvasHeight] = (wrapper.dataset.prototypeViewport || '520x900')
        .split('x').map(Number);
      if (!canvasWidth || !canvasHeight) return;
      const availableWidth = Math.max(120, viewport.clientWidth);
      const scale = Math.min(1, availableWidth / canvasWidth);
      iframe.style.width = `${canvasWidth}px`;
      iframe.style.height = `${canvasHeight}px`;
      iframe.style.transform = `scale(${scale})`;
      viewport.style.height = `${Math.ceil(canvasHeight * scale)}px`;
    });
  };
  window.addEventListener('resize', fitInlinePrototypes);
  requestAnimationFrame(fitInlinePrototypes);

  const stateData = (() => {
    try { return JSON.parse(body.dataset.stateMap || '{"states":[]}'); }
    catch { return { states: [], by_prd: {}, by_state: {} }; }
  })();
  const states = Array.isArray(stateData.states) ? stateData.states : [];
  const stateById = new Map(states.map(state => [state['State ID'], state]));
  // Use document headings/feature rows as scroll anchors. Inline prototype
  // frames remain interactive and can send their own state message, but they
  // should not compete with the owning feature section while the user reads.
  const prdElements = [...document.querySelectorAll('[data-prototype-state]:not(.prd-inline-prototype)')];
  let selectedState = '';

  if (stateSelect) {
    for (const state of states) {
      const option = document.createElement('option');
      option.value = state['State ID'];
      option.textContent = `${state['State ID']} · ${state['Visible state'] || '原型状态'}`;
      stateSelect.append(option);
    }
  }

  const setPrototypeState = (stateId, { locate = false } = {}) => {
    if (!stateId || !body.dataset.preview || !stateById.has(stateId)) return;
    selectedState = stateId;
    if (stateSelect) stateSelect.value = stateId;
    const state = stateById.get(stateId);
    const hash = state['Prototype anchor/frame'] || state['Asset link'] || `#${stateId}`;
    const suffix = hash.startsWith('#') ? hash : `#${stateId}`;
    const base = body.dataset.preview.split('#')[0];
    if (!frame.getAttribute('src')) frame.src = `${base}${suffix}`;
    else frame.src = `${base}${suffix}`;
    if (mapping) mapping.textContent = `${stateId} · ${state['PRD behavior ID'] || '未关联 PRD'}${state['Data status'] ? ` · ${state['Data status']}` : ''}`;
    if (locate) {
      const target = prdElements.find(element => element.dataset.prototypeState === stateId);
      if (target) target.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
  };

  if (stateSelect) stateSelect.addEventListener('change', () => setPrototypeState(stateSelect.value, { locate: true }));
  if (body.dataset.preview && states.length) {
    previewPanel.hidden = false;
    setPrototypeState(states[0]['State ID']);
  }

  document.querySelectorAll('#document a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const target = document.getElementById(decodeURIComponent(link.getAttribute('href').slice(1)));
      if (target) { event.preventDefault(); target.scrollIntoView(); }
    });
  });

  const tocLinks = [...document.querySelectorAll('.toc-link')];
  const tocTargets = tocLinks
    .map(link => document.getElementById(link.dataset.tocTarget))
    .filter(Boolean);
  tocLinks.forEach(link => link.addEventListener('click', event => {
    const target = document.getElementById(link.dataset.tocTarget);
    if (target) { event.preventDefault(); target.scrollIntoView({ block: 'start', behavior: 'smooth' }); }
  }));
  if ('IntersectionObserver' in window && tocTargets.length) {
    const tocObserver = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      tocLinks.forEach(link => link.classList.toggle('active', link.dataset.tocTarget === visible.target.id));
    }, { rootMargin: '-8% 0px -72% 0px', threshold: [0, .3, .8] });
    tocTargets.forEach(target => tocObserver.observe(target));
  }

  prdElements.forEach(element => {
    element.addEventListener('click', () => setPrototypeState(element.dataset.prototypeState));
  });
  if ('IntersectionObserver' in window && prdElements.length) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) setPrototypeState(visible.target.dataset.prototypeState);
    }, { root: null, threshold: [0.2, 0.5, 0.8] });
    prdElements.forEach(element => observer.observe(element));
  }
  window.addEventListener('message', event => {
    const data = event.data;
    const allowedSources = [frame, ...document.querySelectorAll('.flow-embed iframe, .prd-inline-prototype iframe')]
      .map(item => item.contentWindow).filter(Boolean);
    if (event.source && allowedSources.length && !allowedSources.includes(event.source)) return;
    if (data && data.type === 'intentflow-state' && typeof data.stateId === 'string') {
      setPrototypeState(data.stateId);
    }
  });

  document.getElementById('edit-toggle').addEventListener('click', () => {
    editorPanel.hidden = !editorPanel.hidden;
  });
  document.getElementById('preview-toggle').addEventListener('click', () => {
    previewPanel.hidden = !previewPanel.hidden;
    if (!previewPanel.hidden && !frame.getAttribute('src')) setPrototypeState(selectedState || (states[0] && states[0]['State ID']));
  });
  const updateZoom = () => {
    frame.style.transform = `scale(${zoom})`;
    frame.style.width = `${100 / zoom}%`;
    document.getElementById('zoom-level').textContent = `${Math.round(zoom * 100)}%`;
  };
  document.getElementById('zoom-in').addEventListener('click', () => { zoom = Math.min(2, zoom + .1); updateZoom(); });
  document.getElementById('zoom-out').addEventListener('click', () => { zoom = Math.max(.5, zoom - .1); updateZoom(); });

  const download = () => {
    const blob = new Blob([editor.value], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = body.dataset.source.split('/').pop();
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setNotice('已下载修改稿；正式文件尚未更新。');
  };
  document.getElementById('download-markdown').addEventListener('click', download);
  document.getElementById('save-markdown').addEventListener('click', async () => {
    if (!token || location.protocol === 'file:') { download(); return; }
    try {
      const response = await fetch('/api/save-markdown', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-IntentFlow-Token': token },
        body: JSON.stringify({ path: body.dataset.source, expected_hash: body.dataset.revision, content: editor.value })
      });
      const result = await response.json();
      if (!response.ok) { setNotice(result.error || '保存失败'); return; }
      body.dataset.revision = result.revision;
      setNotice('已保存正式 Markdown；刷新页面查看更新后的排版。');
    } catch (error) { setNotice(`保存失败：${error.message}`); }
  });

  document.getElementById('copy-content').addEventListener('click', async () => {
    const content = document.getElementById('document');
    try {
      if (navigator.clipboard && window.ClipboardItem) {
        const copy = content.cloneNode(true);
        const images = [...copy.querySelectorAll('img')];
        let missingImages = 0;
        for (const img of images) {
          try {
            const url = new URL(img.getAttribute('src'), document.baseURI);
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const blob = await response.blob();
            if (!blob.type.startsWith('image/')) throw new Error('not an image');
            const dataUrl = await new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () => resolve(reader.result);
              reader.onerror = () => reject(reader.error);
              reader.readAsDataURL(blob);
            });
            img.setAttribute('src', dataUrl);
          } catch { missingImages += 1; img.remove(); }
        }
        const html = new Blob([copy.outerHTML], { type: 'text/html' });
        const plain = new Blob([content.innerText], { type: 'text/plain' });
        await navigator.clipboard.write([new ClipboardItem({ 'text/html': html, 'text/plain': plain })]);
        setNotice(missingImages
          ? `已复制正文；${missingImages} 张图片无法嵌入，已从复制内容移除。`
          : '已复制正文和图片；原型 iframe 不在正文中。');
      } else {
        await navigator.clipboard.writeText(content.innerText);
        setNotice('已复制纯文本；当前环境不支持富文本复制。');
      }
    } catch (error) { setNotice(`复制失败：${error.message}`); }
  });

  if (body.dataset.kind === 'acceptance') {
    const statuses = ['未测', '通过', '失败', '跳过'];
    const rows = [...document.querySelectorAll('#document tbody tr')]
      .map(row => ({ row, id: row.cells[0]?.textContent.trim() }))
      .filter(item => /^AC-[A-Za-z0-9-]+$/.test(item.id));
    const headers = [...document.querySelectorAll('#document thead tr:first-child th')]
      .map(cell => cell.textContent.trim());
    const statusIndex = Math.max(0, headers.findIndex(header => header.includes('状态')));
    const noteIndex = headers.findIndex(header => header.includes('备注'));
    const filter = document.getElementById('acceptance-filter');
    const progress = document.getElementById('acceptance-progress');
    const progressBar = document.getElementById('acceptance-progress-bar');
    const localResults = (() => {
      try { return JSON.parse(localStorage.getItem(`intentflow-acceptance-${body.dataset.source}-${body.dataset.revision}`) || '{}'); }
      catch { return {}; }
    })();
    let resultsRevision = '';

    const currentEntry = (id) => localResults[id] || {
      status: '未测', build: '', notes: ''
    };
    const updateAcceptanceView = () => {
      const entries = rows.map(({ id }) => currentEntry(id));
      const passed = entries.filter(entry => entry.status === '通过').length;
      const done = entries.filter(entry => entry.status !== '未测').length;
      if (progressBar) { progressBar.max = rows.length; progressBar.value = passed; }
      if (progress) progress.textContent = `通过 ${passed}/${rows.length} · 已处理 ${done}/${rows.length}`;
      for (const { row, id } of rows) {
        const entry = currentEntry(id);
        row.hidden = filter.value !== '全部' && entry.status !== filter.value;
        row.querySelectorAll('.acceptance-status-button').forEach(button => {
          const active = button.dataset.status === entry.status;
          button.classList.toggle('active', active);
          button.setAttribute('aria-pressed', String(active));
        });
        const note = row.querySelector('.acceptance-note');
        if (note && document.activeElement !== note) note.value = entry.notes || '';
      }
    };
    const runContext = () => ({
      build: document.getElementById('review-build').value.trim(),
    });
    const persistCase = async (id, patch) => {
      const entry = { ...currentEntry(id), ...patch };
      if (!token || location.protocol === 'file:') {
        localResults[id] = entry;
        try { localStorage.setItem(`intentflow-acceptance-${body.dataset.source}-${body.dataset.revision}`, JSON.stringify(localResults)); } catch {}
        updateAcceptanceView();
        setNotice(`${id} 已暂存在浏览器；导出或启动本地服务后写入正式记录。`);
        return true;
      }
      try {
        const response = await fetch('/api/acceptance-status', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-IntentFlow-Token': token },
          body: JSON.stringify({ case_id: id, ...entry, expected_hash: resultsRevision })
        });
        const result = await response.json();
        if (!response.ok) { setNotice(result.error || '状态保存失败'); return false; }
        resultsRevision = result.revision;
        localResults[id] = entry;
        updateAcceptanceView();
        setNotice(`${id} 已写入正式验收执行记录。`);
        return true;
      } catch (error) { setNotice(`状态保存失败：${error.message}`); return false; }
    };

    for (const { row, id } of rows) {
      const statusCell = row.cells[statusIndex];
      if (statusCell) {
        statusCell.replaceChildren();
        const buttons = document.createElement('div');
        buttons.className = 'acceptance-status-buttons';
        for (const status of statuses) {
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'acceptance-status-button';
          button.dataset.status = status;
          button.textContent = status;
          button.setAttribute('aria-label', `${id} 状态 ${status}`);
          button.addEventListener('click', () => {
            const entry = { ...currentEntry(id), status, ...runContext() };
            persistCase(id, entry);
          });
          buttons.append(button);
        }
        statusCell.append(buttons);
      }
      const noteCell = noteIndex >= 0 && noteIndex !== statusIndex ? row.cells[noteIndex] : null;
      if (noteCell) {
        noteCell.replaceChildren();
        const note = document.createElement('textarea');
        note.className = 'acceptance-note';
        note.rows = 2;
        note.placeholder = '填写备注';
        note.setAttribute('aria-label', `${id} 备注`);
        note.addEventListener('blur', () => persistCase(id, { notes: note.value.trim() }));
        noteCell.append(note);
      }
    }
    filter.addEventListener('change', updateAcceptanceView);
    updateAcceptanceView();

    if (token && location.protocol !== 'file:') {
      fetch('/api/acceptance-results').then(response => response.json()).then(data => {
        resultsRevision = data.revision;
        for (const [id, entry] of Object.entries(data.results || {})) localResults[id] = entry;
        updateAcceptanceView();
      }).catch(error => setNotice(`读取验收结果失败：${error.message}`));
    }
    const openPrd = document.getElementById('open-prd');
    if (openPrd && body.dataset.prdReview) {
      openPrd.addEventListener('click', () => window.open(body.dataset.prdReview, '_blank', 'noopener'));
    }
    document.getElementById('export-status').addEventListener('click', () => {
      const lines = ['# 验收状态导出（待核对正式记录）', '', '| Case ID | 状态 | 构建版本（选填） | 备注 |', '| --- | --- | --- | --- |'];
      for (const { id } of rows) {
        const entry = currentEntry(id);
        const cells = [id, entry.status, entry.build, entry.notes]
          .map(value => String(value || '').replaceAll('|', '/').replaceAll('\n', ' '));
        lines.push(`| ${cells.join(' | ')} |`);
      }
      const blob = new Blob([lines.join('\n') + '\n'], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a'); link.href = url; link.download = 'acceptance-status-export.md'; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice('已导出状态和备注；请以正式验收执行记录为准。');
    });
  }
})();
