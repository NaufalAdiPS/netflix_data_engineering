import pandas as pd


class DataValidator:
    @staticmethod
    def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    @staticmethod
    def null_check(df: pd.DataFrame, columns: list[str] | None = None) -> dict:
        if columns is None:
            columns = df.columns.tolist()
        return {col: int(df[col].isna().sum()) for col in columns if col in df.columns}

    @staticmethod
    def duplicate_check(df: pd.DataFrame, subset: list[str]) -> int:
        return int(df.duplicated(subset=subset).sum())

    @staticmethod
    def min_max_check(df: pd.DataFrame, columns: list[str]) -> dict:
        result = {}
        for col in columns:
            if col in df.columns:
                numeric_series = pd.to_numeric(df[col], errors="coerce")
                result[col] = {
                    "min": None if numeric_series.dropna().empty else float(numeric_series.min()),
                    "max": None if numeric_series.dropna().empty else float(numeric_series.max()),
                }
        return result

    @staticmethod
    def distinct_check(df: pd.DataFrame, column: str, top_n: int = 10) -> list:
        if column not in df.columns:
            return []
        return (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
            .value_counts()
            .head(top_n)
            .index
            .tolist()
        )

    @staticmethod
    def print_quality_report(
        table_name: str,
        df: pd.DataFrame,
        primary_key: str | None = None,
        required_columns: list[str] | None = None,
        numeric_columns: list[str] | None = None,
        categorical_columns: list[str] | None = None,
    ) -> None:
        print(f"\n{'=' * 70}")
        print(f"DATA QUALITY REPORT: {table_name}")
        print(f"{'=' * 70}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        if required_columns:
            print("\nNull checks:")
            nulls = DataValidator.null_check(df, required_columns)
            for col, count in nulls.items():
                print(f" - {col}: {count}")

        if primary_key and primary_key in df.columns:
            dup_count = DataValidator.duplicate_check(df, [primary_key])
            print(f"\nDuplicate count on [{primary_key}]: {dup_count}")

        if numeric_columns:
            print("\nMin/Max checks:")
            stats = DataValidator.min_max_check(df, numeric_columns)
            for col, val in stats.items():
                print(f" - {col}: min={val['min']}, max={val['max']}")

        if categorical_columns:
            print("\nDistinct values preview:")
            for col in categorical_columns:
                values = DataValidator.distinct_check(df, col)
                print(f" - {col}: {values}")

        print(f"{'=' * 70}\n")