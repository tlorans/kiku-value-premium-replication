from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import tidyfinance as tf

from lrrcs._backend import to_pandas
from lrrcs.empirical.construction import apply_delisting_returns


class EmpiricalDataError(RuntimeError):
    pass


def _is_credentials_failure(exc: BaseException) -> bool:
    if not isinstance(exc, ValueError):
        return False
    msg = str(exc).lower()
    return any(tok in msg for tok in ("wrds_user", "wrds_password", "credential"))


def _wrds_connection():
    # tidyfinance's load_dotenv walks from the installed package, so a
    # parent .env would leak into tests that chdir away from the repo.
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(cwd_env)
        except ImportError:
            pass
    user = os.environ.get("WRDS_USER") or os.environ.get("WRDS_USERNAME")
    password = os.environ.get("WRDS_PASSWORD")
    if not user or not password:
        raise EmpiricalDataError(
            "WRDS credentials missing or rejected. "
            "Call tidyfinance.set_wrds_credentials()."
        )
    if os.environ.get("WRDS_USER") is None:
        os.environ["WRDS_USER"] = user
    try:
        return tf.get_wrds_connection()
    except Exception as exc:
        raise EmpiricalDataError(
            "WRDS credentials missing or rejected. "
            "Call tidyfinance.set_wrds_credentials()."
        ) from exc


def _read_sql(query: str, conn) -> pd.DataFrame:
    return pd.read_sql(query, conn)


def _download_crsp_monthly(
    start_date: str = "1925-12-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    try:
        raw = to_pandas(
            tf.download_data(
                domain="WRDS",
                dataset="crsp_monthly",
                start_date=start_date,
                end_date=end_date,
                version="v1",
                additional_columns=["retx", "prc"],
            )
        )
    except EmpiricalDataError:
        raise
    except Exception as exc:
        if _is_credentials_failure(exc):
            raise EmpiricalDataError(
                "WRDS credentials missing or rejected. "
                "Call tidyfinance.set_wrds_credentials()."
            ) from exc
        raise
    msf = _normalize_crsp_monthly(raw)
    delist = _download_crsp_msedelist(start_date, end_date)
    return apply_delisting_returns(msf, delist)


def _normalize_crsp_monthly(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).lower() for c in out.columns]
    if "calculation_date" in out.columns:
        out["date"] = pd.to_datetime(out["calculation_date"])
    elif "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"])
    if "prc" not in out.columns and "altprc" in out.columns:
        out["prc"] = out["altprc"]
    if "exchcd" not in out.columns and "exchange" in out.columns:
        out["exchcd"] = out["exchange"].map(
            {"NYSE": 1, "AMEX": 2, "NASDAQ": 3}
        )
    if "exchcd" in out.columns:
        # tidyfinance v1: 31/1 NYSE, 32/2 AMEX, 33/3 NASDAQ
        out["exchcd"] = pd.to_numeric(out["exchcd"], errors="coerce").replace(
            {31: 1, 32: 2, 33: 3}
        )
    need = ["permno", "date", "ret", "retx", "prc", "shrout", "exchcd"]
    missing = [c for c in need if c not in out.columns]
    if missing:
        raise EmpiricalDataError(
            f"CRSP extract missing columns {missing}; "
            "pass them via additional_columns"
        )
    if out["shrout"].median() > 1e5:
        out["shrout"] = out["shrout"] / 1000.0
    return out[need]


def _download_compustat_annual(
    start_date: str = "1925-01-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    return to_pandas(
        tf.download_data(
            domain="WRDS",
            dataset="compustat_annual",
            start_date=start_date,
            end_date=end_date,
            additional_columns=["seq", "txditc", "pstkrv", "pstkl", "pstk"],
        )
    )


def _download_ccm_links() -> pd.DataFrame:
    out = to_pandas(tf.download_data(domain="WRDS", dataset="ccm_links"))
    if "lpermno" not in out.columns and "permno" in out.columns:
        out = out.rename(columns={"permno": "lpermno"})
    return out


def _download_crsp_msedelist(
    start_date: str = "1925-12-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    conn = _wrds_connection()
    try:
        out = _read_sql(
            f"""
            SELECT permno, dlstdt, dlret, dlretx, dlstcd
            FROM crsp.msedelist
            WHERE dlstdt BETWEEN '{start_date}' AND '{end_date}'
            """,
            conn,
        )
    finally:
        tf.disconnect_connection(conn)
    out.columns = [str(c).lower() for c in out.columns]
    return out


def _download_crsp_msi(
    start_date: str = "1925-12-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    conn = _wrds_connection()
    try:
        return _read_sql(
            f"""
            SELECT date, vwretd, vwretx
            FROM crsp.msi
            WHERE date BETWEEN '{start_date}' AND '{end_date}'
            """,
            conn,
        )
    finally:
        tf.disconnect_connection(conn)


def _download_crsp_mcti(
    start_date: str = "1925-12-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    conn = _wrds_connection()
    try:
        return _read_sql(
            f"""
            SELECT caldt, t90ret, cpiind AS cpi
            FROM crsp.mcti
            WHERE caldt BETWEEN '{start_date}' AND '{end_date}'
            """,
            conn,
        )
    finally:
        tf.disconnect_connection(conn)
