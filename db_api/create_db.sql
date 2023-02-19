CREATE EXTENSION if not exists pgcrypto;

create table if not exists users
(
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    url text UNIQUE,
    username text,
    nickname text,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    follow boolean default false,
    unfollow boolean default false
);