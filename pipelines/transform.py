import logging
import pandas as pd
import numpy as np 

from validators.data_validator import DataValidator
from pipelines.load import load_to_postgres


logging.basicConfig(level=logging.INFO)


class SilverTransformer:
    def __init__(self, engine):
        self.engine = engine

    def read_table(self, schema, table):
        query = f'SELECT * FROM {schema}."{table}"'
        return pd.read_sql(query, self.engine)

    @staticmethod
    def _clean_text(series: pd.Series) -> pd.Series:
        return (
            series.astype("string")
            .str.strip()
            .replace({
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
                "<NA>": pd.NA
            })
        )

    @staticmethod
    def _normalize_country(series: pd.Series) -> pd.Series:
        cleaned = (
            series.astype("string")
            .str.strip()
            .str.lower()
            .replace({
                "": pd.NA,
                "nan": pd.NA,
                "none": pd.NA,
                "<na>": pd.NA
            })
        )

        country_map = {
            "usa": "USA",
            "us": "USA",
            "united states": "USA",
            "canada": "Canada",
            "uk": "UK",
            "united kingdom": "UK",
            "south korea": "South Korea",
            "korea": "South Korea",
            "japan": "Japan",
            "germany": "Germany",
            "france": "France",
            "india": "India",
        }

        return cleaned.map(country_map).fillna("Unknown")

    @staticmethod
    def _normalize_content_type(series: pd.Series) -> pd.Series:
        cleaned = (
            series.astype("string")
            .str.strip()
            .str.lower()
            .replace({
                "": pd.NA,
                "nan": pd.NA,
                "none": pd.NA,
                "<na>": pd.NA
            })
        )

        content_type_map = {
            "movie": "Movie",
            "tv series": "TV Series",
            "documentary": "Documentary",
            "stand-up comedy": "Stand-Up Comedy",
            "limited series": "Limited Series",
        }

        return cleaned.map(content_type_map).fillna("Unknown")

    @staticmethod
    def _normalize_device_type(series: pd.Series) -> pd.Series:
        cleaned = (
            series.astype("string")
            .str.strip()
            .str.lower()
            .replace({
                "": pd.NA,
                "nan": pd.NA,
                "none": pd.NA,
                "<na>": pd.NA
            })
        )

        device_map = {
            "mobile": "Smartphone",
            "phone": "Smartphone",
            "desktop": "Desktop",
            "laptop": "Laptop",
            "tablet": "Tablet",
            "tv": "Smart TV",
            "smart tv": "Smart TV",
            "gaming console": "Gaming Console",
        }

        return cleaned.map(device_map).fillna("Unknown")

    @staticmethod
    def _normalize_quality(series: pd.Series) -> pd.Series:
        cleaned = (
            series.astype("string")
            .str.strip()
            .str.lower()
            .replace({
                "": pd.NA,
                "nan": pd.NA,
                "none": pd.NA,
                "<na>": pd.NA
            })
        )

        quality_map = {
            "sd": "SD",
            "hd": "HD",
            "fhd": "FULL HD",
            "full hd": "FULL HD",
            "uhd": "4K",
            "ultra hd": "4K",
            "4k": "4K",
        }

        return cleaned.map(quality_map).fillna("UNKNOWN")

    # USERS

    def transform_users(self):
        df = self.read_table("bronze", "users").copy()

        DataValidator.print_quality_report(
            "bronze.users",
            df,
            primary_key="user_id",
            required_columns=["user_id"],
            numeric_columns=["age", "monthly_spend", "household_size"],
            categorical_columns=["gender", "country", "subscription_plan", "primary_device"],
        )

        df = df.drop_duplicates(subset=["user_id"]).copy()

        text_cols = [
            "email",
            "first_name",
            "last_name",
            "gender",
            "country",
            "state_province",
            "city",
            "subscription_plan",
            "primary_device",
        ]
        for col in text_cols:
            if col in df.columns:
                df[col] = self._clean_text(df[col])

        if "gender" in df.columns:
            gender_map = {
                "m": "Male",
                "male": "Male",
                "f": "Female",
                "female": "Female",
                "other": "Other",
                "prefer not to say": "Prefer not to say",
            }
            df["gender"] = (
                df["gender"]
                .str.lower()
                .map(gender_map)
                .fillna("Unknown")
            )

        if "country" in df.columns:
            df["country"] = self._normalize_country(df["country"])

        for col in ["state_province", "city", "subscription_plan", "primary_device"]:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown").str.title()

        if "email" in df.columns:
            df["email"] = df["email"].str.lower()

        if "age" in df.columns:
            df["age"] = pd.to_numeric(df["age"], errors="coerce")
            df.loc[(df["age"] < 10) | (df["age"] > 100), "age"] = pd.NA

        if "monthly_spend" in df.columns:
            df["monthly_spend"] = pd.to_numeric(df["monthly_spend"], errors="coerce")
            df.loc[df["monthly_spend"] < 0, "monthly_spend"] = pd.NA

        if "household_size" in df.columns:
            df["household_size"] = pd.to_numeric(df["household_size"], errors="coerce")
            df.loc[df["household_size"] < 1, "household_size"] = pd.NA

        if "subscription_start_date" in df.columns:
            df["subscription_start_date"] = pd.to_datetime(
                df["subscription_start_date"],
                errors="coerce"
            )

        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(
                df["created_at"],
                errors="coerce"
            )

        if "is_active" in df.columns:
            # Mengubah dari boolean (True/False) menjadi label String yang lebih informatif
            df["is_active"] = (
                df["is_active"]
                .astype("string")
                .str.lower()
                .map({
                    "true": "Active User",
                    "false": "Inactive User",
                    "1": "Active User",
                    "0": "Inactive User"
                })
                .fillna("Unknown Status")
            )

        DataValidator.print_quality_report(
            "silver.users_clean_preview",
            df,
            primary_key="user_id",
            required_columns=["user_id"],
            numeric_columns=["age", "monthly_spend", "household_size"],
            categorical_columns=["gender", "country", "subscription_plan", "primary_device"],
        )

        return df

    # MOVIES

    def transform_movies(self):
        df = self.read_table("bronze", "movies").copy()

        DataValidator.print_quality_report(
            "bronze.movies",
            df,
            primary_key="movie_id",
            required_columns=["movie_id"],
            numeric_columns=[
                "release_year",
                "duration_minutes",
                "imdb_rating",
                "production_budget",
                "box_office_revenue",
            ],
            categorical_columns=[
                "content_type",
                "genre_primary",
                "genre_secondary",
                "language",
                "country_of_origin",
            ],
        )

        df = df.drop_duplicates(subset=["movie_id"]).copy()

        text_cols = [
            "title",
            "content_type",
            "genre_primary",
            "genre_secondary",
            "rating",
            "language",
            "country_of_origin",
            "content_warning",
        ]
        for col in text_cols:
            if col in df.columns:
                df[col] = self._clean_text(df[col])

        if "title" in df.columns:
            df["title"] = df["title"].fillna("Unknown")

        if "content_type" in df.columns:
            df["content_type"] = self._normalize_content_type(df["content_type"])

        if "genre_primary" in df.columns:
            df["genre_primary"] = df["genre_primary"].fillna("Unknown").str.title()

        if "genre_secondary" in df.columns:
            df["genre_secondary"] = df["genre_secondary"].fillna("Unknown").str.title()

        if "language" in df.columns:
            df["language"] = df["language"].fillna("Unknown").str.title()

        if "country_of_origin" in df.columns:
            df["country_of_origin"] = self._normalize_country(df["country_of_origin"])

        numeric_cols = [
            "release_year",
            "duration_minutes",
            "imdb_rating",
            "production_budget",
            "box_office_revenue",
            "number_of_seasons",
            "number_of_episodes",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "release_year" in df.columns:
            df.loc[
                (df["release_year"] < 1900) | (df["release_year"] > 2030),
                "release_year"
            ] = pd.NA

        if "duration_minutes" in df.columns:
            df.loc[
                (df["duration_minutes"] <= 0) | (df["duration_minutes"] > 600),
                "duration_minutes"
            ] = pd.NA

        if "imdb_rating" in df.columns:
            df.loc[
                (df["imdb_rating"] < 0) | (df["imdb_rating"] > 10),
                "imdb_rating"
            ] = pd.NA

        if "production_budget" in df.columns:
            df.loc[df["production_budget"] < 0, "production_budget"] = pd.NA

        if "box_office_revenue" in df.columns:
            df.loc[df["box_office_revenue"] < 0, "box_office_revenue"] = pd.NA

        if "added_to_platform" in df.columns:
            df["added_to_platform"] = pd.to_datetime(
                df["added_to_platform"],
                errors="coerce"
            )

        if "is_netflix_original" in df.columns:
            # Mengubah dari boolean ke String deskriptif
            df["is_netflix_original"] = (
                df["is_netflix_original"]
                .astype("string")
                .str.lower()
                .map({
                    "true": "Netflix Original",
                    "false": "Licensed Content",
                    "1": "Netflix Original",
                    "0": "Licensed Content"
                })
                .fillna("Unknown Originality")
            )

        DataValidator.print_quality_report(
            "silver.movies_clean_preview",
            df,
            primary_key="movie_id",
            required_columns=["movie_id"],
            numeric_columns=[
                "release_year",
                "duration_minutes",
                "imdb_rating",
                "production_budget",
                "box_office_revenue",
            ],
            categorical_columns=[
                "content_type",
                "genre_primary",
                "genre_secondary",
                "language",
                "country_of_origin",
            ],
        )

        return df

    # WATCH HISTORY

    def transform_watch_history(self):
        df = self.read_table("bronze", "watch_history").copy()

        DataValidator.print_quality_report(
            "bronze.watch_history",
            df,
            primary_key="session_id",
            required_columns=["session_id", "user_id", "movie_id"],
            numeric_columns=["watch_duration_minutes", "progress_percentage", "user_rating"],
            categorical_columns=["device_type", "action", "quality", "location_country"],
        )

        df = df.drop_duplicates(subset=["session_id"]).copy()

        text_cols = ["device_type", "action", "quality", "location_country"]
        for col in text_cols:
            if col in df.columns:
                df[col] = self._clean_text(df[col])

        if "device_type" in df.columns:
            df["device_type"] = self._normalize_device_type(df["device_type"])

        if "action" in df.columns:
            df["action"] = df["action"].fillna("Unknown").str.title()

        if "quality" in df.columns:
            df["quality"] = self._normalize_quality(df["quality"])

        if "location_country" in df.columns:
            df["location_country"] = self._normalize_country(df["location_country"])

        if "watch_duration_minutes" in df.columns:
            df["watch_duration_minutes"] = pd.to_numeric(
                df["watch_duration_minutes"],
                errors="coerce"
            )
            df.loc[
                (df["watch_duration_minutes"] <= 0) | (df["watch_duration_minutes"] > 800),
                "watch_duration_minutes"
            ] = pd.NA
            # Membiarkan Null sebagai NA, jangan diisi 0

        if "progress_percentage" in df.columns:
            df["progress_percentage"] = pd.to_numeric(
                df["progress_percentage"],
                errors="coerce"
            )
            df.loc[
                (df["progress_percentage"] < 0) | (df["progress_percentage"] > 100),
                "progress_percentage"
            ] = pd.NA
            # Membiarkan Null sebagai NA

        if "user_rating" in df.columns:
            df["user_rating"] = pd.to_numeric(df["user_rating"], errors="coerce")
            df.loc[
                (df["user_rating"] < 1) | (df["user_rating"] > 5),
                "user_rating"
            ] = pd.NA

        if "watch_date" in df.columns:
            df["watch_date"] = pd.to_datetime(df["watch_date"], errors="coerce")

        if "is_download" in df.columns:
            # Mengubah dari boolean ke String deskriptif
            df["is_download"] = (
                df["is_download"]
                .astype("string")
                .str.lower()
                .map({
                    "true": "Downloaded",
                    "false": "Streamed",
                    "1": "Downloaded",
                    "0": "Streamed"
                })
                .fillna("Unknown Method")
            )

        DataValidator.print_quality_report(
            "silver.watch_history_clean_preview",
            df,
            primary_key="session_id",
            required_columns=["session_id", "user_id", "movie_id"],
            numeric_columns=["watch_duration_minutes", "progress_percentage", "user_rating"],
            categorical_columns=["device_type", "action", "quality", "location_country"],
        )

        return df


    # LOAD SILVER


    def load_silver(self):
        users = self.transform_users()
        movies = self.transform_movies()
        watch = self.transform_watch_history()

        load_to_postgres(users, "users_clean", "silver", self.engine)
        load_to_postgres(movies, "movies_clean", "silver", self.engine)
        load_to_postgres(watch, "watch_history_clean", "silver", self.engine)



# GOLD


class GoldBuilder:
    def __init__(self, engine):
        self.engine = engine

    def read(self, schema, table):
        return pd.read_sql(f'SELECT * FROM {schema}."{table}"', self.engine)


    # DIM USERS

    def dim_users(self):
        df = self.read("silver", "users_clean").copy()
        df = df.drop_duplicates(subset=["user_id"])
        load_to_postgres(df, "dim_users", "gold", self.engine)


    # DIM MOVIES


    def dim_movies(self):
        df = self.read("silver", "movies_clean").copy()
        df = df.drop_duplicates(subset=["movie_id"])
        load_to_postgres(df, "dim_movies", "gold", self.engine)


    # DIM DEVICE


    def dim_device(self):
        df = self.read("silver", "watch_history_clean").copy()

        dim = (
            df[["device_type"]]
            .dropna()
            .drop_duplicates()
            .sort_values("device_type")
            .reset_index(drop=True)
        )

        dim["device_id"] = range(1, len(dim) + 1)
        dim = dim[["device_id", "device_type"]]

        load_to_postgres(dim, "dim_device", "gold", self.engine)

  
    # DIM DATE
  

    def dim_date(self):
        df = self.read("silver", "watch_history_clean").copy()

        d = pd.DataFrame()
        d["full_date"] = pd.to_datetime(
            df["watch_date"],
            errors="coerce"
        ).dt.normalize()

        d = (
            d.dropna()
            .drop_duplicates()
            .sort_values("full_date")
            .reset_index(drop=True)
        )

        d["date_id"] = d["full_date"].dt.strftime("%Y%m%d").astype(int)
        d["year"] = d["full_date"].dt.year
        d["month"] = d["full_date"].dt.month
        d["day"] = d["full_date"].dt.day
        d["day_of_week"] = d["full_date"].dt.day_name()
        d["week_of_year"] = d["full_date"].dt.isocalendar().week.astype(int)
        d["is_weekend"] = d["day_of_week"].isin(["Saturday", "Sunday"])

        load_to_postgres(d, "dim_date", "gold", self.engine)

    
    # FACT
    

    def fact_watch(self):
        fact = self.read("silver", "watch_history_clean").copy()
        dim_device = self.read("gold", "dim_device").copy()

        fact["watch_date"] = pd.to_datetime(fact["watch_date"], errors="coerce")
        fact["date_id"] = fact["watch_date"].dt.strftime("%Y%m%d")
        fact.loc[fact["watch_date"].isna(), "date_id"] = pd.NA
        fact["date_id"] = pd.to_numeric(fact["date_id"], errors="coerce")

        fact = fact.merge(dim_device, on="device_type", how="left")

        
        # Derived columns for analytics (Menggunakan np.where untuk String Labels)
        
        # fact["completion_status"] = np.where(
        #     fact["progress_percentage"] >= 90, "Completed", "In Progress"
        # )

        # fact["progress_category"] = np.where(
        #     fact["progress_percentage"] >= 80, "High Progress",
        #     np.where(fact["progress_percentage"] >= 20, "Mid Progress", "Low Progress")
        # )

        # fact["watch_duration_category"] = np.where(
        #     fact["watch_duration_minutes"] >= 60, "Long Watch (>60m)",
        #     np.where(fact["watch_duration_minutes"] < 10, "Short Watch (<10m)", "Regular Watch")
        # )

        fact["completion_status"] = np.where(
            fact["progress_percentage"].isna(),
            "Unknown Progress",
            np.where(fact["progress_percentage"] >= 90, "Completed", "In Progress")
        )

        fact["progress_category"] = np.where(
            fact["progress_percentage"].isna(),
            "Unknown Progress",
            np.where(
                fact["progress_percentage"] >= 80,
                "High Progress",
                np.where(fact["progress_percentage"] >= 20, "Mid Progress", "Low Progress")
            )
        )

        fact["watch_duration_category"] = np.where(
            fact["watch_duration_minutes"].isna(),
            "Unknown Duration",
            np.where(
                fact["watch_duration_minutes"] >= 60,
                "Long Watch (>60m)",
                np.where(fact["watch_duration_minutes"] < 10, "Short Watch (<10m)", "Regular Watch")
            )
        )

        # optional: action-progress inconsistency flag
        is_inconsistent = (
            ((fact["action"] == "Completed") & (fact["progress_percentage"] < 80)) |
            ((fact["action"] == "Started") & (fact["progress_percentage"] >= 90))
        )
        fact["data_consistency_status"] = np.where(
            is_inconsistent, "Inconsistent Data", "Consistent Data"
        )
        
        # Incomplete session flag
        is_incomplete = (
            fact["progress_percentage"].isna() |
            fact["watch_duration_minutes"].isna()
        )
        fact["session_status"] = np.where(
            is_incomplete, "Incomplete/Missing Data", "Valid Session"
        )

        fact_cols = [
            "session_id",
            "watch_duration_minutes",
            "progress_percentage",
            "action",
            "quality",
            "is_download",
            "location_country",
            "user_rating",
            "user_id",
            "movie_id",
            "device_id",
            "date_id",
            "completion_status",
            "progress_category",
            "watch_duration_category",
            "data_consistency_status",
            "session_status",
        ]

        fact = fact[fact_cols].drop_duplicates(subset=["session_id"]).copy()

        load_to_postgres(fact, "fact_watch_history", "gold", self.engine)

    # -------------------

    def build_all(self):
        self.dim_users()
        self.dim_movies()
        self.dim_device()
        self.dim_date()
        self.fact_watch()