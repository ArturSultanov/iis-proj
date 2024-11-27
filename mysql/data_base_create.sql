create table animals
(
    id          int auto_increment
        primary key,
    name        varchar(256)                                            not null,
    age         int                                                     not null,
    species     varchar(256)                                            not null,
    photo       mediumblob                                              null,
    description varchar(2048)                                           not null,
    status      enum ('available', 'quarantine', 'adopted', 'deceased') not null,
    hidden      tinyint(1)                                              not null
);

create table medical_histories
(
    id          int auto_increment
        primary key,
    animal_id   int           not null,
    start_date  datetime      not null,
    description varchar(2048) not null,
    constraint medical_histories_ibfk_1
        foreign key (animal_id) references animals (id)
);

create index animal_id
    on medical_histories (animal_id);

create table treatments
(
    id                 int auto_increment
        primary key,
    medical_history_id int           not null,
    date               datetime      not null,
    description        varchar(2048) not null,
    constraint treatments_ibfk_1
        foreign key (medical_history_id) references medical_histories (id)
);

create index medical_history_id
    on treatments (medical_history_id);

create table users
(
    id       int auto_increment
        primary key,
    name     varchar(256)                                              not null,
    username varchar(256)                                              not null,
    password blob                                                      not null,
    role     enum ('admin', 'staff', 'vet', 'volunteer', 'registered') not null,
    disabled tinyint(1)                                                not null,
    constraint username
        unique (username)
);

create table adoption_requests
(
    id        int auto_increment
        primary key,
    user_id   int                                      not null,
    animal_id int                                      not null,
    date      datetime                                 not null,
    status    enum ('pending', 'accepted', 'rejected') not null,
    message   varchar(2048)                            null,
    constraint adoption_requests_ibfk_1
        foreign key (user_id) references users (id),
    constraint adoption_requests_ibfk_2
        foreign key (animal_id) references animals (id)
);

create index animal_id
    on adoption_requests (animal_id);

create index user_id
    on adoption_requests (user_id);

create table sessions
(
    id         int auto_increment
        primary key,
    user_id    int      not null,
    token      char(32) not null,
    expiration datetime not null,
    constraint token
        unique (token),
    constraint sessions_ibfk_1
        foreign key (user_id) references users (id)
);

create index user_id
    on sessions (user_id);

create table vaccinations
(
    id                 int auto_increment
        primary key,
    medical_history_id int           not null,
    date               datetime      not null,
    description        varchar(2048) not null,
    constraint vaccinations_ibfk_1
        foreign key (medical_history_id) references medical_histories (id)
);

create index medical_history_id
    on vaccinations (medical_history_id);

create table vet_requests
(
    id          int auto_increment
        primary key,
    animal_id   int                                      not null,
    user_id     int                                      not null,
    date        datetime                                 not null,
    description varchar(2048)                            not null,
    status      enum ('pending', 'accepted', 'rejected') not null,
    constraint vet_requests_ibfk_1
        foreign key (animal_id) references animals (id),
    constraint vet_requests_ibfk_2
        foreign key (user_id) references users (id)
);

create index animal_id
    on vet_requests (animal_id);

create index user_id
    on vet_requests (user_id);

create table volunteer_applications
(
    id      int auto_increment
        primary key,
    user_id int                                      not null,
    date    datetime                                 not null,
    status  enum ('pending', 'accepted', 'rejected') not null,
    message varchar(2048)                            not null,
    constraint volunteer_applications_ibfk_1
        foreign key (user_id) references users (id)
);

create index user_id
    on volunteer_applications (user_id);

create table walks
(
    id        int auto_increment
        primary key,
    animal_id int                                                                          not null,
    user_id   int                                                                          not null,
    date      datetime                                                                     not null,
    duration  int                                                                          not null,
    location  varchar(256)                                                                 not null,
    status    enum ('pending', 'accepted', 'rejected', 'started', 'finished', 'cancelled') not null,
    constraint walks_ibfk_1
        foreign key (animal_id) references animals (id),
    constraint walks_ibfk_2
        foreign key (user_id) references users (id)
);

create index animal_id
    on walks (animal_id);

create index user_id
    on walks (user_id);

