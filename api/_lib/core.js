import { createClient } from '@supabase/supabase-js';
import bcrypt from 'bcryptjs';
import { SignJWT, jwtVerify } from 'jose';
import { randomBytes } from 'node:crypto';

let client;
export function db() {
  if (!client) client = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });
  return client;
}
export const json = (res, status, body, headers = {}) => res.status(status).setHeader('Cache-Control', 'no-store').setHeader('Content-Type', 'application/json; charset=utf-8').setHeader('X-Content-Type-Options', 'nosniff').setHeader('Referrer-Policy', 'same-origin').setHeader('SameSite', 'Lax').setHeader('X-Frame-Options', 'DENY').setHeader('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'").setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()').setHeader('Vary', 'Cookie').setHeader('Set-Cookie', headers.cookie ?? '').json(body);
export function send(res, status, body) { res.setHeader('Cache-Control', 'no-store'); res.setHeader('Content-Type', 'application/json; charset=utf-8'); return res.status(status).json(body); }
export function cookie(token, maxAge = 604800) { return `tahdiri_session=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`; }
export function clearCookie() { return 'tahdiri_session=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0'; }
export function readCookie(req) { const raw = req.headers.cookie ?? ''; return raw.split(';').map(x => x.trim()).find(x => x.startsWith('tahdiri_session='))?.slice(16); }
const secret = () => { const s = process.env.SESSION_SECRET; if (!s || s.length < 32) throw new Error('SESSION_SECRET must be at least 32 characters'); return new TextEncoder().encode(s); };
export async function signSession(user) { return new SignJWT({ sub: user.id }).setProtectedHeader({ alg: 'HS256' }).setIssuedAt().setExpirationTime('7d').sign(secret()); }
export async function sessionUser(req) {
  const token = readCookie(req); if (!token) return null;
  try { const { payload } = await jwtVerify(token, secret(), { algorithms: ['HS256'] }); const { data } = await db().from('users').select('*').eq('id', payload.sub).maybeSingle(); return data ?? null; } catch { return null; }
}
export async function requireUser(req, res) { const user = await sessionUser(req); if (!user) { send(res, 401, { error: 'يرجى تسجيل الدخول' }); return null; } return user; }
export async function requireAdmin(req, res) { const user = await requireUser(req, res); if (!user) return null; if (user.role !== 'admin') { send(res, 403, { error: 'غير مصرح' }); return null; } return user; }
export function isSubscriptionActive(user, now = new Date()) { return user?.subscription_status === 'active' && Boolean(user.subscription_end) && new Date(user.subscription_end) > now; }
export async function requireActiveSubscription(req, res, resolveUser = requireUser) {
  const user = await resolveUser(req, res); if (!user) return null;
  if (!isSubscriptionActive(user)) { send(res, 402, { error: 'انتهى اشتراكك، تواصل مع الإدارة للتجديد' }); return null; }
  return user;
}
export const passwordHash = password => bcrypt.hash(password, 12);
export const verifyPassword = (password, hash) => bcrypt.compare(password, hash);
export function generatePassword(length = 16) { if (!Number.isInteger(length) || length < 12) throw new Error('length must be at least 12'); const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789'; let out; do { const bytes = randomBytes(length); out = [...bytes].map(b => alphabet[b % alphabet.length]).join(''); } while (!/[A-Z]/.test(out) || !/[a-z]/.test(out) || !/[0-9]/.test(out)); return out; }
export function nextRenewal(currentEnd, now = new Date()) { const base = currentEnd && new Date(currentEnd) > now ? new Date(currentEnd) : now; return new Date(base.getTime() + 30 * 86400000).toISOString(); }
export const publicUser = u => ({ email: u.email, display_name: u.display_name, role: u.role, subscription_status: u.subscription_status, subscription_end: u.subscription_end, must_change_password: u.must_change_password });
export const validEmail = e => typeof e === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e) && e.length <= 254;
export async function body(req) { return req.body && typeof req.body === 'object' ? req.body : {}; }
