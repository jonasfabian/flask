CREATE TABLE user_group
(
    id   BIGINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100),
    PRIMARY KEY (id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

CREATE TABLE user
(
    id         BIGINT       NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL,
    username   VARCHAR(100) NOT NULL,
    password   VARCHAR(100) NOT NULL,
    canton     VARCHAR(45)  NOT NULL,
    sex        ENUM ('none','m','f')      DEFAULT 'none',
    licence    ENUM ('public','academic') DEFAULT 'academic',
    PRIMARY KEY (id),
    UNIQUE KEY email (email)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

CREATE TABLE user_group_role
(
    role          ENUM ('admin', 'group_admin', 'user'),
    user_id       BIGINT NOT NULL,
    user_group_id BIGINT NOT NULL,
    FOREIGN KEY (user_group_id) REFERENCES user_group (id),
    FOREIGN KEY (user_id) REFERENCES user (id)

) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

CREATE TABLE original_text
(
    id             BIGINT     NOT NULL AUTO_INCREMENT,
    user_group_id  BIGINT     NOT NULL,
    original_text  BLOB       NOT NULL,
    extracted_text MEDIUMTEXT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_group_id) REFERENCES user_group (id)
);
CREATE TABLE excerpt
(
    id               BIGINT NOT NULL AUTO_INCREMENT,
    original_text_id BIGINT NOT NULL,
    excerpt          TEXT   NOT NULL,
    isSkipped        INT     DEFAULT 0,
    isPrivate        BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id),
    FOREIGN KEY (original_text_id) REFERENCES original_text (id)
);
CREATE TABLE recording
(
    id         BIGINT   NOT NULL AUTO_INCREMENT,
    excerpt_id BIGINT   NOT NULL,
    user_id    BIGINT   NOT NULL,
    audio      MEDIUMBLOB,
    time       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (excerpt_id) REFERENCES excerpt (id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

CREATE TABLE checked_utterance
(
    id           BIGINT   NOT NULL AUTO_INCREMENT,
    utterance_id BIGINT   NOT NULL,
    user_id      BIGINT   NOT NULL,
    label        ENUM ('skipped', 'correct', 'wrong'),
    time         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

### TEST VALUES
# TODO remove test values once everything else is done

# password admin
INSERT INTO user(id, first_name, last_name, email, username, password, canton)
VALUES (1, 'admin', 'admin', 'admin', 'admin', '$2a$10$nY/FB8OIhF55Iatu.Vf5Au/mRUnrjYsYU.3yamAxcxZPc4e3Dh1jm', 'ag');
INSERT INTO user_group(id, name) VALUE (1, 'public test group');
INSERT INTO user_group_role(role, user_id, user_group_id)
VALUES ('admin', 1, 1),
       ('group_admin', 1, 1);
INSERT INTO original_text(id, original_text, extracted_text, user_group_id) VALUE (1, 'none', 'none', 1);
INSERT INTO excerpt(original_text_id, excerpt, isSkipped, isPrivate)
VALUES (1, 'Hallo Welt', 0, 0),
       (1, 'Guten Morgen', 0, 0),
       (1, 'Guten Abend', 0, 0);

### OLD TABLES
# TODO replace with new data structure once everything else is clear/done
CREATE TABLE speaker
(
    id            BIGINT NOT NULL AUTO_INCREMENT,
    speaker_id    VARCHAR(45),
    language_used VARCHAR(45),
    dialect       VARCHAR(45),
    PRIMARY KEY (id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

CREATE TABLE text_audio
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    audio_start FLOAT  NOT NULL,
    audio_end   FLOAT  NOT NULL,
    text        MEDIUMTEXT,
    fileId      INT    NOT NULL,
    speaker     VARCHAR(45),
    labeled     INT,
    correct     BIGINT,
    wrong       BIGINT,
    PRIMARY KEY (id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

CREATE TABLE user_and_text_audio
(
    id            BIGINT   NOT NULL AUTO_INCREMENT,
    user_id       BIGINT,
    text_audio_id INT,
    time          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uni UNIQUE (user_id, text_audio_id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;