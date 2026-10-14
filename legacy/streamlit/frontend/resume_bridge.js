export default function(component) {
  // Restore only a public appearance preference before the workbench mounts.
  try{const mode=localStorage.getItem('inquire.appearance');if(mode==='light'||mode==='dark')document.documentElement.dataset.inquireTheme=mode;}catch{}
  const {parentElement, data, setTriggerValue} = component;
  const root = parentElement.querySelector('.resume-bridge');
  const storageKey = 'inquire.tab.resume.v1';
  if (!root._booted) {
    root._booted = true;
    if (!data.token) {
      let prior = '';
      try { prior = sessionStorage.getItem(storageKey) || ''; } catch (_) {}
      if (/^[A-Za-z0-9_-]{32,128}$/.test(prior)) setTriggerValue('restore', prior);
      else setTriggerValue('ready', true);
    }
  }
  if (data.token && /^[A-Za-z0-9_-]{32,128}$/.test(data.token)) {
    try { sessionStorage.setItem(storageKey, data.token); } catch (_) {}
  }
}
