// Streamlit v2 calls this again when data changes and calls the returned
// cleanup on unmount. Keep one live listener, including across remounts.
export default function(component) {
  const {parentElement, data, setTriggerValue} = component;
  const root = parentElement.querySelector('.command-palette');
  const registryKey = Symbol.for('inquire.commandPalette');
  const allowed = new Set(['model', 'scenario', 'conversation', 'notebook', 'briefing', 'write']);
  const make = (tag, cls, text) => {
    const element = document.createElement(tag);
    element.className = cls;
    if (text !== undefined) element.textContent = text;
    return element;
  };
  let ui = root._palette;
  if (!ui || ui.disposed) {
    document[registryKey]?.dispose();
    const launcher = make('button', 'palette-launcher');
    launcher.type = 'button';
    launcher.setAttribute('aria-haspopup', 'dialog');
    const label = make('span', 'palette-launcher-label');
    const keys = make('kbd', 'palette-keys', '⌘ / Ctrl K');
    const glyph = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    glyph.classList.add('palette-glyph');
    glyph.setAttribute('viewBox', '0 0 24 24');
    glyph.setAttribute('width', '16');
    glyph.setAttribute('height', '16');
    glyph.setAttribute('aria-hidden', 'true');
    glyph.setAttribute('focusable', 'false');
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', '10.5');
    circle.setAttribute('cy', '10.5');
    circle.setAttribute('r', '6.5');
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', '15.5');
    line.setAttribute('y1', '15.5');
    line.setAttribute('x2', '21');
    line.setAttribute('y2', '21');
    glyph.append(circle, line);
    launcher.append(glyph, label, keys);
    const dialog = make('dialog', 'palette-dialog');
    dialog.setAttribute('aria-labelledby', 'palette-heading');
    const heading = make('h2', 'palette-heading');
    heading.id = 'palette-heading';
    const search = make('input', 'palette-search');
    search.type = 'search';
    search.autocomplete = 'off';
    search.setAttribute('role', 'combobox');
    search.setAttribute('aria-autocomplete', 'list');
    search.setAttribute('aria-controls', 'palette-options');
    search.setAttribute('aria-expanded', 'true');
    const list = make('div', 'palette-list');
    list.id = 'palette-options';
    list.setAttribute('role', 'listbox');
    const empty = make('p', 'palette-empty');
    const footer = make('div', 'palette-footer');
    dialog.append(heading, search, list, empty, footer);
    root.replaceChildren(launcher, dialog);
    ui = {launcher, label, dialog, heading, search, list, empty, footer,
          commands: [], rows: [], active: null, open: false, disposed: false};
    root._palette = ui;
    document[registryKey] = ui;

    const restore = () => {
      const prior = ui.priorFocus;
      ui.priorFocus = null;
      if (prior?.isConnected) prior.focus({preventScroll: true});
      else if (launcher.isConnected) launcher.focus({preventScroll: true});
    };
    ui.close = () => {
      if (!ui.open) return;
      ui.open = false;
      launcher.setAttribute('aria-expanded', 'false');
      if (dialog.open) dialog.close();
      restore();
    };
    ui.highlight = (id) => {
      ui.active = id;
      ui.rows.forEach(row => row.button.setAttribute('aria-selected', String(row.command.id === id)));
      const selected = ui.rows.find(row => row.command.id === id);
      if (selected) {
        search.setAttribute('aria-activedescendant', selected.button.id);
        selected.button.scrollIntoView({block: 'nearest'});
      } else search.removeAttribute('aria-activedescendant');
    };
    ui.choose = (id) => {
      if (!ui.commands.some(command => command.id === id && command.enabled)) return;
      // A repeated click/key event cannot select again after the dialog closes.
      ui.close();
      ui.emit(id);
    };
    ui.filter = () => {
      const query = search.value.trim().toLocaleLowerCase();
      const matches = ui.commands.filter(command => `${command.title} ${command.hint} ${command.id}`.toLocaleLowerCase().includes(query));
      ui.rows = matches.map(command => {
        const button = make('button', 'palette-option');
        button.type = 'button';
        button.id = `palette-option-${command.id}`;
        button.tabIndex = -1;
        button.disabled = !command.enabled;
        button.setAttribute('role', 'option');
        button.setAttribute('aria-disabled', String(!command.enabled));
        const text = make('span', 'palette-option-text');
        text.append(make('span', 'palette-option-title', command.title), make('span', 'palette-option-hint', command.hint));
        button.append(text, make('span', 'palette-option-arrow', command.enabled ? '↗' : '—'));
        button.onclick = () => { if (ui.open) ui.choose(command.id); };
        button.onpointerenter = () => { if (command.enabled) ui.highlight(command.id); };
        return {command, button};
      });
      list.replaceChildren(...ui.rows.map(row => row.button));
      empty.hidden = matches.length > 0;
      const active = ui.rows.find(row => row.command.id === ui.active && row.command.enabled)
        || ui.rows.find(row => row.command.enabled);
      ui.highlight(active?.command.id || null);
    };
    ui.show = (focus) => {
      if (ui.open || ui.disposed) return;
      ui.priorFocus = focus || document.activeElement;
      ui.open = true;
      search.value = '';
      ui.filter();
      launcher.setAttribute('aria-expanded', 'true');
      dialog.showModal();
      search.focus({preventScroll: true});
    };
    launcher.onclick = () => ui.show(launcher);
    launcher.setAttribute('aria-expanded', 'false');
    search.oninput = () => ui.filter();
    dialog.oncancel = event => { event.preventDefault(); ui.close(); };
    dialog.onclose = () => { if (ui.open) ui.close(); };
    dialog.onclick = event => {
      if (event.target !== dialog) return;
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) ui.close();
    };
    const keyboard = event => {
      if (ui.disposed || event.isComposing || event.keyCode === 229 || event.defaultPrevented) return;
      // Inspect focus metadata only. Never inspect another widget's value.
      const focus = event.composedPath().find(node => typeof node.tagName === 'string') || document.activeElement;
      const password = focus?.tagName === 'INPUT' && focus.type === 'password';
      const typing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(focus?.tagName) || focus?.isContentEditable;
      const commandK = (event.metaKey || event.ctrlKey) && !event.altKey && event.key.toLowerCase() === 'k';
      if (commandK && !password) {
        event.preventDefault();
        if (!event.repeat) ui.open ? ui.close() : ui.show(focus);
        return;
      }
      if (ui.open) {
        if (event.key === 'Escape') { event.preventDefault(); ui.close(); }
        else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
          event.preventDefault();
          const enabled = ui.rows.filter(row => row.command.enabled);
          if (!enabled.length) return;
          const index = enabled.findIndex(row => row.command.id === ui.active);
          const direction = event.key === 'ArrowDown' ? 1 : -1;
          ui.highlight(enabled[(index + direction + enabled.length) % enabled.length].command.id);
        } else if (event.key === 'Enter' && !event.repeat) {
          event.preventDefault();
          if (ui.active) ui.choose(ui.active);
        }
        return;
      }
      if (event.key === '/' && !typing && !event.repeat && !event.metaKey && !event.ctrlKey && !event.altKey
          && ui.commands.some(command => command.id === 'write' && command.enabled)) {
        event.preventDefault();
        ui.choose('write');
      }
    };
    document.addEventListener('keydown', keyboard);
    ui.dispose = () => {
      if (ui.disposed) return;
      ui.close();
      ui.disposed = true;
      document.removeEventListener('keydown', keyboard);
      if (document[registryKey] === ui) delete document[registryKey];
    };
  }
  // Streamlit rerenders replace the data/trigger closure without installing
  // another listener or retaining enabled commands from a previous render.
  const seen = new Set();
  ui.commands = (Array.isArray(data.commands) ? data.commands : []).filter(command => {
    if (!allowed.has(command.id) || seen.has(command.id)) return false;
    seen.add(command.id);
    return true;
  }).map(command => ({id: command.id, title: String(command.title || ''), hint: String(command.hint || ''), enabled: command.enabled === true}));
  ui.emit = id => setTriggerValue('action', id);
  const zh = Boolean(data.zh);
  ui.label.textContent = zh ? '快捷导航' : 'Jump to…';
  ui.heading.textContent = zh ? '前往练习空间' : 'Go to your practice space';
  ui.search.placeholder = zh ? '搜索页面或操作…' : 'Search pages or actions…';
  ui.search.setAttribute('aria-label', zh ? '搜索快捷指令' : 'Search commands');
  ui.list.setAttribute('aria-label', zh ? '快捷指令' : 'Commands');
  ui.empty.textContent = zh ? '没有匹配的指令' : 'No matching commands';
  ui.footer.textContent = zh ? '↑ ↓ 选择    Enter 前往    Esc 关闭' : '↑ ↓ choose    Enter go    Esc close';
  if (ui.open) ui.filter();
  return () => ui.dispose();
}
