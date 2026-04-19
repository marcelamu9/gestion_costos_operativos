from pathlib import Path

import numpy as np
import pandas as pd

# Ruta base de los datos (relativa a la raíz del proyecto)
DATA_DIR = Path(__file__).parent.parent / "Prueba tecnica Senior" / "data"


def load_historico_equipos() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "historico_equipos.csv", parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def load_materia_x() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "X.csv", parse_dates=["Date"])
    df = df.rename(columns={"Price": "Price_X"})
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def load_materia_y() -> pd.DataFrame:
    df = pd.read_csv(
        DATA_DIR / "Y.csv",
        sep=";",
        decimal=",",
        parse_dates=["Date"],
        dayfirst=True,   # fecha en formato DD/MM/YYYY
    )
    df = df.rename(columns={"Price": "Price_Y"})
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def load_materia_z() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Z.csv")
    # Detectar y reordenar columnas si están invertidas
    if "Price" in df.columns and "Date" in df.columns:
        df = df[["Date", "Price"]]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.rename(columns={"Price": "Price_Z"})
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def load_all_raw() -> dict[str, pd.DataFrame]:
    return {
        "historico": load_historico_equipos(),
        "X": load_materia_x(),
        "Y": load_materia_y(),
        "Z": load_materia_z(),
    }


def build_analysis_dataset() -> pd.DataFrame:
    """
    Construye el dataset unificado para análisis y modelado.

    Usa `historico_equipos.csv` como fuente principal (ya contiene X, Y, Z
    sincronizadas con los precios de equipos). Las series individuales X, Y, Z
    se usan para extender el histórico si se requiere forecasting de materias primas.

    Retorna:
        DataFrame con columnas: Date, Price_X, Price_Y, Price_Z,
        Price_Equipo1, Price_Equipo2 — período 2010-01-04 a 2023-08-31.
    """
    df = load_historico_equipos()

    # Asegurar tipos correctos
    df["Date"] = pd.to_datetime(df["Date"])
    numeric_cols = ["Price_X", "Price_Y", "Price_Z", "Price_Equipo1", "Price_Equipo2"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Reporte de calidad
    n_nulls = df[numeric_cols].isnull().sum().sum()
    if n_nulls > 0:
        print(f"[data_loader] Advertencia: {n_nulls} valores nulos detectados — se imputarán con ffill.")
        df[numeric_cols] = df[numeric_cols].ffill()

    return df


def build_extended_series() -> dict[str, pd.DataFrame]:
    """
    Retorna las series individuales de cada materia prima en su rango completo.
    Útil para ajustar modelos ARIMA sobre el histórico más largo disponible.

    Retorna:
        Dict con DataFrames por variable: {'X': df_x, 'Y': df_y, 'Z': df_z}
    """
    return {
        "X": load_materia_x(),
        "Y": load_materia_y(),
        "Z": load_materia_z(),
    }


def summary_report(df: pd.DataFrame) -> None:
    """Imprime un resumen básico del dataset."""
    print("=" * 60)
    print(f"Registros: {len(df):,}")
    print(f"Periodo  : {df['Date'].min().date()} a {df['Date'].max().date()}")
    print(f"Columnas : {list(df.columns)}")
    print("\nEstadísticas descriptivas:")
    print(df.describe().round(2).to_string())
    print("\nValores nulos:")
    print(df.isnull().sum())
    print("=" * 60)


if __name__ == "__main__":
    df = build_analysis_dataset()
    summary_report(df)
