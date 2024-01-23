PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Views;
DROP TABLE IF EXISTS HasTag;
DROP TABLE IF EXISTS Tag;
DROP TABLE IF EXISTS Stream;
DROP TABLE IF EXISTS StreamCategory;
DROP TABLE IF EXISTS Contains;
DROP TABLE IF EXISTS Message;
DROP TABLE IF EXISTS Emoticon;
DROP TABLE IF EXISTS ChatRoom;
DROP TABLE IF EXISTS Subscription;
DROP TABLE IF EXISTS Tier;
DROP TABLE IF EXISTS Follows;
DROP TABLE IF EXISTS Streamer;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Account;

CREATE TABLE Account(
    username    VARCHAR(30) CONSTRAINT UsernameNotNull NOT NULL,
    email       VARCHAR(50) CONSTRAINT EmailNotNull NOT NULL CONSTRAINT EmailUnique UNIQUE,
    password    VARCHAR(30) CONSTRAINT PasswordNotNull NOT NULL,
    createdAt   DATE CONSTRAINT CreatedAtNotNull NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE User(
    account     VARCHAR(30) CONSTRAINT AccountNotNull NOT NULL,
    PRIMARY KEY (account),
    FOREIGN KEY (account) REFERENCES Account (username) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Streamer(
    account             VARCHAR(30) CONSTRAINT AccountNotNull NOT NULL,
    profilePicture      VARCHAR(150),
    description         VARCHAR(255),
    numFollowers        NUMERIC(10,0) CONSTRAINT NumFollowersNotNegative CHECK (numFollowers >= 0),
    PRIMARY KEY (account),
    FOREIGN KEY (account) REFERENCES Account (username) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Follows(
    user        VARCHAR(30) CONSTRAINT UserNotNull NOT NULL,
    streamer    VARCHAR(30) CONSTRAINT StreamerNotNull NOT NULL,
    PRIMARY KEY (user, streamer),
    FOREIGN KEY (user) REFERENCES User (account) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (streamer) REFERENCES Streamer (account) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT NotFollowingItself CHECK (user != streamer)
);

CREATE TABLE Tier(
    tier    NUMERIC(1,0) CONSTRAINT TierNotNull NOT NULL CONSTRAINT ValidTier CHECK (tier >= 1 and tier <= 3),
    value   NUMERIC(2,2) CONSTRAINT ValuePositive CHECK (value > 0),
    PRIMARY KEY (tier)
);

CREATE TABLE Subscription(
    user        VARCHAR(30) CONSTRAINT UserNotNull NOT NULL,
    streamer    VARCHAR(30) CONSTRAINT StreamerNotNull NOT NULL,
    tier        NUMERIC(1,0) CONSTRAINT TierNotNull NOT NULL CONSTRAINT ValidTier CHECK (tier >= 1 and tier <= 3),
    start       DATETIME CONSTRAINT StartNotNull NOT NULL,
    end         DATETIME CONSTRAINT EndNotNull NOT NULL,
    PRIMARY KEY (user, streamer),
    FOREIGN KEY (user) REFERENCES User (account) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (streamer) REFERENCES Streamer (account) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (tier) REFERENCES Tier (tier) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT NotSubscribingItself CHECK (user != streamer),
    CONSTRAINT StartBeforeEnd CHECK (start < end)
);

CREATE TABLE ChatRoom(
    id              INTEGER CONSTRAINT IdNotNull NOT NULL,
    mode            VARCHAR(6) CONSTRAINT ValidMode CHECK (mode IN('normal', 'slow')),
    messageCooldown NUMERIC(3,0) CONSTRAINT MessageCooldownPositive CHECK (messageCooldown > 0),
    streamer        VARCHAR(30) CONSTRAINT StreamerNotNull NOT NULL CONSTRAINT StreamerUnique UNIQUE,      
    PRIMARY KEY (id),
    FOREIGN KEY (streamer) REFERENCES Streamer (account) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Emoticon(
    name    VARCHAR(20) CONSTRAINT NameNotNull NOT NULL,
    PRIMARY KEY (name)
);

CREATE TABLE Message(
    id          INTEGER CONSTRAINT IdNotNull NOT NULL,
    user        VARCHAR(30) CONSTRAINT UserNotNull NOT NULL,
    chatRoom    INTEGER CONSTRAINT ChatRoomNotNull NOT NULL,
    content     VARCHAR(255) CONSTRAINT ContentNotNull NOT NULL,
    timestamp   DATETIME CONSTRAINT TimestampNotNull NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user) REFERENCES User (account) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (chatRoom) REFERENCES Chatroom (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Contains(
    message     INTEGER CONSTRAINT MessageNotNull NOT NULL,
    emoticon    VARCHAR(20) CONSTRAINT EmoticonNotNull NOT NULL,
    PRIMARY KEY (message, emoticon),
    FOREIGN KEY (emoticon) REFERENCES Emoticon (name) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (message) REFERENCES Message (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE StreamCategory(
    name        VARCHAR(30) CONSTRAINT NameNotNull NOT NULL,
    ranking     NUMERIC(3,0) CONSTRAINT RankingPositive CHECK (ranking > 0),
    numViewers  NUMERIC(10,0) CONSTRAINT NumViewersNotNegative CHECK (numViewers >= 0),
    PRIMARY KEY (name)
);     

CREATE TABLE Stream(
    id              INTEGER CONSTRAINT IdNotNull NOT NULL,
    streamer        VARCHAR(30) CONSTRAINT StreamerNotNull NOT NULL,  
    streamCategory  VARCHAR(30) CONSTRAINT StreamCategoryNotNull NOT NULL,
    title           VARCHAR(100) CONSTRAINT TitleNotNull NOT NULL,
    startTime       DATETIME CONSTRAINT StartTimeNotNull NOT NULL,
    language        VARCHAR(2) CONSTRAINT LanguageNotNull NOT NULL,
    numViewers      NUMERIC(10,0) CONSTRAINT NumViewersNotNull NOT NULL CONSTRAINT NumViewersNotNegative CHECK (numViewers >= 0),
    PRIMARY KEY (id),
    FOREIGN KEY (streamer) REFERENCES Streamer (account) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (streamCategory) REFERENCES StreamCategory (name) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Tag(
    name    VARCHAR(20) CONSTRAINT NameNotNull NOT NULL,
    PRIMARY KEY (name)
);

CREATE TABLE HasTag(
    stream  INTEGER CONSTRAINT StreamNotNull NOT NULL,
    tag     VARCHAR(20) CONSTRAINT TagNotNull NOT NULL,
    PRIMARY KEY (stream, tag),
    FOREIGN KEY (stream) REFERENCES Stream (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (tag) REFERENCES Tag (name) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Views(
    user        VARCHAR(30) CONSTRAINT UserNotNull NOT NULL,
    stream      INTEGER CONSTRAINT StreamNotNull NOT NULL,
    PRIMARY KEY (user, stream),
    FOREIGN KEY (user) REFERENCES User (account) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (stream) REFERENCES Stream (id) ON DELETE CASCADE ON UPDATE CASCADE
);
