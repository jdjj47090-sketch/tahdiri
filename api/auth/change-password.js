import { db, send, body, requireUser, passwordHash, verifyPassword } from '../_lib/core.js';
export default async function handler(req, res) {
  if (req.method !== 'POST') return send(res, 405, { error: 'Method not allowed' });
  const user = await requireUser(req, res); if (!user) return;
  const input = await body(req); if (typeof input.old_password !== 'string' || typeof input.new_password !== 'string' || input.new_password.length < 10) return send(res, 400, { error: 'كلمة المرور الجديدة يجب أن تكون 10 أحرف على الأقل' });
  if (!(await verifyPassword(input.old_password, user.password_hash))) return send(res, 401, { error: 'كلمة المرور الحالية غير صحيحة' });
  const { error } = await db().from('users').update({ password_hash: await passwordHash(input.new_password), must_change_password: false, updated_at: new Date().toISOString() }).eq('id', user.id);
  if (error) return send(res, 500, { error: 'تعذّر تحديث كلمة المرور' }); return send(res, 200, { ok: true });
}
