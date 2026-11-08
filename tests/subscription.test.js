import test from 'node:test';
import assert from 'node:assert/strict';
import { generatePassword, isSubscriptionActive, nextRenewal, requireActiveSubscription } from '../api/_lib/core.js';

test('password generator returns 12+ characters with letters and digits', () => {
  const p = generatePassword(); assert.ok(p.length >= 12); assert.match(p, /[A-Z]/); assert.match(p, /[a-z]/); assert.match(p, /[0-9]/);
});
test('expiry logic rejects inactive and expired subscriptions', async () => {
  assert.equal(isSubscriptionActive({ subscription_status: 'active', subscription_end: '2025-12-31T00:00:00Z' }, new Date('2026-01-01T00:00:00Z')), false);
  const old = process.env.SESSION_SECRET; process.env.SESSION_SECRET = 'x'.repeat(32);
  const res = { statusCode: 0, status(n) { this.statusCode = n; return this; }, setHeader() { return this; }, json(v) { this.body = v; return this; } };
  const user = await requireActiveSubscription({}, res, async () => ({ subscription_status: 'inactive', subscription_end: '2027-01-01T00:00:00.000Z' })); assert.equal(user, null); assert.equal(res.statusCode, 402);
  process.env.SESSION_SECRET = old;
});
test('renewal starts from now for expired end and stacks 30 days for active end', () => {
  const now = new Date('2026-01-01T00:00:00.000Z');
  assert.equal(nextRenewal('2025-12-01T00:00:00.000Z', now), '2026-01-31T00:00:00.000Z');
  assert.equal(nextRenewal('2026-01-15T00:00:00.000Z', now), '2026-02-14T00:00:00.000Z');
});
