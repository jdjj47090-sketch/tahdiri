import { h, clear, btn } from './dom.js';
import { logo } from './shell.js';
export let currentUser = null;
export async function refreshUser() { const r = await fetch('/api/me', { credentials: 'same-origin', cache: 'no-store' }); currentUser = r.ok ? await r.json() : null; return currentUser; }
async function request(path, method, data) { const r = await fetch(path, { method, credentials: 'same-origin', cache: 'no-store', headers: { 'content-type': 'application/json' }, body: data ? JSON.stringify(data) : undefined }); const out = await r.json().catch(() => ({})); if (!r.ok) throw new Error(out.error || 'تعذّر تنفيذ الطلب'); return out; }
export function authScreen(root, onDone, forcePassword = false) {
  clear(root);
  root.className = 'view-inner auth-view';
  const panel = h('section', { class: 'card auth-card' });
  const message = h('p', { class: 'auth-message', role: 'alert', 'aria-live': 'polite' });
  panel.append(h('div', { class: 'auth-logo', 'aria-label': 'تحضيري' }, logo(), h('span', null, 'تحضيري')));
  if (forcePassword) {
    panel.append(h('h1', null, 'تغيير كلمة المرور'), h('p', { class: 'muted' }, 'يجب تعيين كلمة مرور جديدة قبل المتابعة.'));
    const old = h('input', { type: 'password', autocomplete: 'current-password', required: true });
    const next = h('input', { type: 'password', autocomplete: 'new-password', minlength: '10', required: true });
    const submit = btn('تحديث كلمة المرور', null, 'primary', { type: 'submit' });
    const form = h('form', null, field('كلمة المرور الحالية', old), field('كلمة المرور الجديدة (10 أحرف على الأقل)', next), message, submit);
    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      message.textContent = '';
      submit.disabled = true;
      submit.setAttribute('aria-busy', 'true');
      submit.textContent = 'جارٍ التحديث…';
      try {
        await request('/api/auth/change-password', 'POST', { old_password: old.value, new_password: next.value });
        await refreshUser();
        onDone();
      } catch (err) {
        message.textContent = err.message;
        submit.disabled = false;
        submit.removeAttribute('aria-busy');
        submit.textContent = 'تحديث كلمة المرور';
      }
    });
    panel.append(form);
    root.append(panel);
    return;
  }
  panel.append(h('h1', null, 'تسجيل الدخول'), h('p', { class: 'muted' }, 'أدخل بيانات الحساب التي زودتك بها الإدارة.'));
  const email = h('input', { type: 'email', autocomplete: 'username', dir: 'ltr', required: true, 'aria-label': 'البريد الإلكتروني' });
  const password = h('input', { type: 'password', autocomplete: 'current-password', required: true, 'aria-label': 'كلمة المرور' });
  const submit = btn('دخول', null, 'primary', { type: 'submit' });
  const form = h('form', null, field('البريد الإلكتروني', email), field('كلمة المرور', password), message, submit);
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (!form.reportValidity()) return;
    message.textContent = '';
    submit.disabled = true;
    submit.setAttribute('aria-busy', 'true');
    submit.textContent = 'جارٍ تسجيل الدخول…';
    try {
      currentUser = await request('/api/auth/login', 'POST', { email: email.value, password: password.value });
      onDone();
    } catch (err) {
      message.textContent = err.message;
      submit.disabled = false;
      submit.removeAttribute('aria-busy');
      submit.textContent = 'دخول';
      password.focus();
    }
  });
  panel.append(form);
  root.append(panel);
}
export function field(label, input) { return h('label', { class: 'field' }, h('span', null, label), input); }
export function subscriptionBanner() {
  const user = currentUser;
  if (!user) return null;
  const active = user.subscription_status === 'active' && user.subscription_end && new Date(user.subscription_end) > new Date();
  const end = user.subscription_end ? new Date(user.subscription_end).toLocaleDateString('ar-IQ', { day: 'numeric', month: 'long', year: 'numeric' }) : null;
  const status = active ? `اشتراكك فعّال حتى ${end}.` : 'اشتراكك غير فعّال؛ تواصل مع الإدارة للتجديد.';
  return h('div', { class: `subscription-banner ${active ? 'active' : 'inactive'}`, role: 'status' }, h('span', null, status), btn('تسجيل الخروج', async () => { await request('/api/auth/logout', 'POST'); currentUser = null; location.hash = '#/'; location.reload(); }, 'ghost'));
}
export const apiRequest = request;
