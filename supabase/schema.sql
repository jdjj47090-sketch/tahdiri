create extension if not exists pgcrypto;

create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  display_name text,
  password_hash text not null,
  role text not null default 'user' check (role in ('user','admin')),
  subscription_status text not null default 'inactive' check (subscription_status in ('active','inactive')),
  subscription_end timestamptz,
  must_change_password boolean not null default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create table login_attempts (
  id bigserial primary key,
  email text not null,
  ip text,
  created_at timestamptz default now()
);
alter table users enable row level security;
alter table login_attempts enable row level security;
