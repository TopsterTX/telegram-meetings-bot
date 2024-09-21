create type meeting_status as enum ('creating','editing','cancel','reject','processing','expired');

create table if not exists users (
    id uuid primary key not null default gen_random_uuid(),
    username varchar(255) not null,
    chat_id int not null,
    first_name varchar(255) not null
);

create table if not exists meetings (
    id uuid primary key not null default gen_random_uuid(),
    theme varchar(255),
    status meeting_status not null default 'creating',
    admin_user_id uuid,
    date varchar(255),
    foreign key (admin_user_id) references users(id)
);

create table if not exists user_meeting (
    meeting_id uuid not null,
    user_id uuid not null,
    foreign key (meeting_id) references meetings(id),
    foreign key (user_id) references users(id)
);

