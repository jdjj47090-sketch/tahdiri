import { send, body, requireActiveSubscription } from './_lib/core.js';
const model = 'claude-haiku-4-5-20251001';
export default async function handler(req, res) {
  if (req.method !== 'POST') return send(res, 405, { error: 'Method not allowed' });
  if (!(await requireActiveSubscription(req, res))) return;
  const input = await body(req); const task = input.task;
  if (!['summarize', 'questions'].includes(task) || typeof input.text !== 'string' || input.text.length > 30000) return send(res, 400, { error: 'طلب غير صالح' });
  const prompt = task === 'summarize'
    ? `لخص نص الكتاب باللغة العربية في JSON فقط بالشكل {"topic":"...","sections":[{"kind":"idea|explain|definitions|reasons|laws|comparisons|memorize|mistakes|unreadable","title":"...","items":["..."]}]}. نص الصفحة:\n${input.text}`
    : `أنشئ أسئلة تدريبية باللغة العربية من نص الكتاب وأعد JSON فقط بالشكل {"questions":[{"type":"mcq|true_false|fill_blank|definition|reason|compare|short|calc|explain","prompt":"...","options":["..."],"answer":"...","keywords":[],"explanation":"..."}]}. أنشئ 5 أسئلة. نص الصفحة:\n${input.text}`;
  const upstream = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', headers: { 'content-type': 'application/json', 'x-api-key': process.env.ANTHROPIC_API_KEY ?? '', 'anthropic-version': '2023-06-01' }, body: JSON.stringify({ model, max_tokens: 3000, messages: [{ role: 'user', content: prompt }] }) });
  const data = await upstream.json().catch(() => ({})); if (!upstream.ok) return send(res, 502, { error: 'تعذّر إكمال طلب الذكاء الاصطناعي' });
  const raw = data.content?.find(part => part.type === 'text')?.text ?? ''; let parsed;
  try { parsed = JSON.parse(raw.replace(/^```(?:json)?\s*|\s*```$/g, '')); } catch { return send(res, 502, { error: 'تعذّر قراءة رد الذكاء الاصطناعي' }); }
  return send(res, 200, task === 'summarize' ? { summary: parsed, model } : { questions: parsed.questions ?? [], model });
}
