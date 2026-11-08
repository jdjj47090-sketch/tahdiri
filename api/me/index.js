import { send, requireUser, publicUser } from '../_lib/core.js';
export default async function handler(req, res) { if (req.method !== 'GET') return send(res, 405, { error: 'Method not allowed' }); const user = await requireUser(req, res); if (user) return send(res, 200, publicUser(user)); }
