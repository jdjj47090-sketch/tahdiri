import { db, send, body, requireAdmin, validEmail, passwordHash, generatePassword, nextRenewal } from '../../_lib/core.js';
export default async function handler(req, res) {
  const admin = await requireAdmin(req, res); if (!admin) return; const supabase = db();
  if (req.method === 'GET') { const { data, error } = await supabase.from('users').select('id,email,display_name,role,subscription_status,subscription_end,created_at').order('created_at', { ascending: false }); if (error) return send(res, 500, { error: 'تعذّر تحميل المستخدمين' }); return send(res, 200, { users: data }); }
  if (req.method !== 'POST') return send(res, 405, { error: 'Method not allowed' });
  const input = await body(req); const email = typeof input.email === 'string' ? input.email.trim().toLowerCase() : ''; const display_name = typeof input.display_name === 'string' ? input.display_name.trim().slice(0, 80) : null;
  if (!validEmail(email)) return send(res, 400, { error: 'البريد الإلكتروني غير صالح' });
  const password = generatePassword(); const { data, error } = await supabase.from('users').insert({ email, display_name, password_hash: await passwordHash(password), must_change_password: true, subscription_status: 'active', subscription_end: nextRenewal(null) }).select('id,email,display_name,role,subscription_status,subscription_end,created_at').single();
  if (error) return send(res, error.code === '23505' ? 409 : 500, { error: error.code === '23505' ? 'هذا البريد مسجل مسبقًا' : 'تعذّر إنشاء الحساب' }); return send(res, 201, { user: data, password });
}
