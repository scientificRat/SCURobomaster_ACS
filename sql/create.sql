CREATE TABLE system_admin (
  user_name VARCHAR(25),
  password  CHAR(32),
  PRIMARY KEY (user_name)
);

CREATE TABLE register_visitor (
  id            SERIAL,
  card_id       VARCHAR(25) UNIQUE,
  name          VARCHAR(25) NOT NULL,
  remark        TEXT DEFAULT '',
  register_time TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE raw_record (
  id      SERIAL,
  card_id VARCHAR(25),
  time    TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
);

-- 此表允许陌生访客
CREATE TABLE visitor_stat (
  id         SERIAL,
  card_id    VARCHAR(25),
  enter_time TIMESTAMP NOT NULL,
  leave_time TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
);

-- init user and password, should change after first login
INSERT INTO system_admin (user_name, password) VALUES ('admin', md5('admin'));