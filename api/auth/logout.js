import { send, clearCookie } from '../_lib/core.js';
export default function handler(req, res) { if (req.method !== 'POST') return send(res, 405, { error: 'Method not allowed' }); res.setHeader('Set-Cookie', clearCookie()); return send(res, 200, { ok: true }); }
