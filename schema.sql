create table users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
password text NOT NULL,
expert boolean NOT NULL,
admin boolean NOT NULL
);

CREATE TABLE questions(
id integer PRIMARY KEY AUTOINCREMENT,
question_text text NOT NULL,
answer_text text,
asked_by_id integer not null,
expert_id integer not null
);