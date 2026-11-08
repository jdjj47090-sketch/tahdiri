import { db, send, body, validEmail, passwordHash, verifyPassword, signSession, cookie, publicUser } from '../_lib/core.js';
export default async function handler(req, res) {
  if (req.method !== 'POST') return send(res, 405, { error: 'Method not allowed' });
  const input = await body(req); const email = typeof input.email === 'string' ? input.email.trim().toLowerCase() : ''; const password = input.password;
  if (!validEmail(email) || typeof password !== 'string') return send(res, 400, { error: 'بيانات غير صالحة' });
  const supabase = db(); const cutoff = new Date(Date.now() - 15 * 60_000).toISOString();
  const { count } = await supabase.from('login_attempts').select('id', { count: 'exact', head: true }).eq('email', email).gte('created_at', cutoff);
  if ((count ?? 0) >= 5) return send(res, 429, { error: 'محاولات كثيرة، حاول بعد 15 دقيقة' });
  let { data: user } = await supabase.from('users').select('*').eq('email', email).maybeSingle();
  if (process.env.ADMIN_EMAIL && email === process.env.ADMIN_EMAIL.trim().toLowerCase()) {
    const { data: admin } = await supabase.from('users').select('*').eq('role', 'admin').limit(1).maybeSingle();
    if (!admin) {
      if (!process.env.ADMIN_PASSWORD) return send(res, 500, { error: 'إعداد حساب الإدارة غير مكتمل' });
      const hash = await passwordHash(process.env.ADMIN_PASSWORD);
      const created = await supabase.from('users').insert({ email, password_hash: hash, role: 'admin' }).select('*').single();
      if (!created.error) user = created.data;
    }
  }
  if (!user || !(await verifyPassword(password, user.password_hash))) {
    await supabase.from('login_attempts').insert({ email, ip: req.headers['x-forwarded-for']?.split(',')[0]?.trim() ?? null });
    return send(res, 401, { error: 'البريد أو كلمة المرور غير صحيحة' });
  }
  await supabase.from('login_attempts').delete().eq('email', email);
  res.setHeader('Set-Cookie', cookie(await signSession(user)));
  return send(res, 200, publicUser(user));
}
