CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'eve@123';

CREATE TABLE emails(
  id SERIAL PRIMARY KEY,
  email VARCHAR(255),
  telegram_user_id BIGINT,
  username VARCHAR(255),
  msg_date DATE default CURRENT_DATE
);

CREATE TABLE phones(
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR(32),
  telegram_user_id BIGINT,
  username VARCHAR(255),
  msg_date DATE default CURRENT_DATE
);

INSERT INTO emails(email, telegram_user_id, username, msg_date) VALUES ('user1@example.com', 123456789, 'Renkawa Cherino', '2024-05-06');
INSERT INTO emails(email, telegram_user_id, username, msg_date) VALUES ('user2@example.com', 987654321, 'Renkawa Cherino', '2024-05-06');

INSERT INTO phones (phone_number, telegram_user_id, username, msg_date) VALUES ('+7 917 414 15 21', 123456789, 'Renkawa Cherino', '2024-05-06');
INSERT INTO phones (phone_number, telegram_user_id, username, msg_date) VALUES ('8 (916)-999-60-20', 987654321, 'Renkawa Cherino', '2024-05-06');
