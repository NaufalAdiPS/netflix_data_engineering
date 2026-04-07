ALTER TABLE gold.dim_users ADD PRIMARY KEY (user_id);
ALTER TABLE gold.dim_movies ADD PRIMARY KEY (movie_id);
ALTER TABLE gold.dim_device ADD PRIMARY KEY (device_id);
ALTER TABLE gold.dim_date ADD PRIMARY KEY (date_id);

ALTER TABLE gold.fact_watch_history
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id)
REFERENCES gold.dim_users(user_id);

ALTER TABLE gold.fact_watch_history
ADD CONSTRAINT fk_movie
FOREIGN KEY (movie_id)
REFERENCES gold.dim_movies(movie_id);

ALTER TABLE gold.fact_watch_history
ADD CONSTRAINT fk_device
FOREIGN KEY (device_id)
REFERENCES gold.dim_device(device_id);

ALTER TABLE gold.fact_watch_history
ADD CONSTRAINT fk_date
FOREIGN KEY (date_id)
REFERENCES gold.dim_date(date_id);