CREATE TABLE user_group
(
    id      BIGINT NOT NULL AUTO_INCREMENT,
    mode    ENUM ('recording','checking'),
    licence ENUM ('public','academic'),
    name    VARCHAR(100),
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
    sex        VARCHAR(45) DEFAULT NULL,
    password   VARCHAR(100) NOT NULL,
    canton     VARCHAR(45)  NOT NULL,
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
# TODO not sure how the upload should work => upload original or maybe already preformated text?
# extract sencences etc using spacy?
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
    skipped          INT     DEFAULT 0,
    private          BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id),
    FOREIGN KEY (original_text_id) REFERENCES original_text (id)
);
CREATE TABLE recording
(
    id         BIGINT NOT NULL AUTO_INCREMENT,
    excerpt_id BIGINT NOT NULL,
    user_id    BIGINT NOT NULL,
    audio      MEDIUMBLOB,
    time       TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (excerpt_id) REFERENCES excerpt (id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

# TODO old part => can be  replaced with new data structure once everything else is clear/done
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
    id            BIGINT NOT NULL AUTO_INCREMENT,
    user_id       BIGINT,
    text_audio_id INT,
    time          TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uni UNIQUE (user_id, text_audio_id)
) ENGINE = INNODB
  DEFAULT CHARSET = UTF8MB4;

# TODO remove test values once everything else is done
#  password admin
INSERT INTO user(id, first_name, last_name, email, username, password, canton)
VALUES (1, 'admin', 'admin', 'admin', 'admin', '$2a$10$nY/FB8OIhF55Iatu.Vf5Au/mRUnrjYsYU.3yamAxcxZPc4e3Dh1jm', 'ag');
INSERT INTO user_group(id, mode, licence, name)
VALUES (1, 'checking', 'public', 'public_test'),
       (2, 'recording', 'academic', 'academic_test');
INSERT INTO user_group_role(role, user_id, user_group_id)
VALUES ('admin', 1, 1),
       ('group_admin', 1, 1),
       ('group_admin', 1, 2);