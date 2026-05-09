from supabase import create_client, Client
import datetime
import streamlit as st

# --- SUPABASE CONFIG ---
SUPABASE_URL = "https://eipcycffputlaevzbbyt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpcGN5Y2ZmcHV0bGFldnpiYnl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyNjM4MTYsImV4cCI6MjA5MzgzOTgxNn0.HRXtU9vfbIJ0er1OyCfzTObaxC4tbbZ3kwnkU9KuLZc"

# --- CLIENT INIT ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# 1. PATIENT FUNCTIONS
# ============================================================

def save_patient(patient_id: str, full_name: str, age: int, gender: str) -> bool:
    """
    Patient info Supabase mein save karo.
    Agar patient already exists toh update karo.
    """
    try:
        existing = supabase.table("patients")\
            .select("patient_id")\
            .eq("patient_id", patient_id)\
            .execute()

        if existing.data:
            # Patient exists — update karo
            supabase.table("patients").update({
                "full_name": full_name,
                "age": int(age),
                "gender": gender
            }).eq("patient_id", patient_id).execute()
        else:
            # Naya patient — insert karo
            supabase.table("patients").insert({
                "patient_id": patient_id,
                "full_name": full_name,
                "age": int(age),
                "gender": gender
            }).execute()

        return True

    except Exception as e:
        st.warning(f"⚠️ Patient save error: {e}")
        return False


def get_all_patients() -> list:
    """
    Saare patients ki list fetch karo.
    """
    try:
        result = supabase.table("patients")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        return result.data
    except Exception as e:
        st.warning(f"⚠️ Fetch patients error: {e}")
        return []


# ============================================================
# 2. SCAN RESULT FUNCTIONS
# ============================================================

def save_scan_result(patient_id: str, scan_mode: str, result: str, confidence: float) -> bool:
    """
    Scan result Supabase mein save karo.
    """
    try:
        supabase.table("scan_results").insert({
            "patient_id": patient_id,
            "scan_mode": scan_mode,
            "result": result,
            "confidence": round(float(confidence), 2)
        }).execute()
        return True

    except Exception as e:
        st.warning(f"⚠️ Scan result save error: {e}")
        return False


def get_patient_history(patient_id: str) -> list:
    """
    Kisi ek patient ki saari pichli scans fetch karo.
    """
    try:
        result = supabase.table("scan_results")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .order("scanned_at", desc=True)\
            .execute()
        return result.data
    except Exception as e:
        st.warning(f"⚠️ Fetch history error: {e}")
        return []


def get_all_scan_results() -> list:
    """
    Saare scan results fetch karo (admin view ke liye).
    """
    try:
        result = supabase.table("scan_results")\
            .select("*")\
            .order("scanned_at", desc=True)\
            .execute()
        return result.data
    except Exception as e:
        st.warning(f"⚠️ Fetch all scans error: {e}")
        return []


# ============================================================
# 3. PDF / STORAGE FUNCTIONS
# ============================================================

def upload_pdf(file_path: str, patient_id: str) -> str | None:
    """
    PDF ko Supabase Storage 'reports' bucket mein upload karo.
    Returns: Public URL of uploaded PDF, ya None if failed.
    """
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"{patient_id}_{timestamp}.pdf"

        with open(file_path, "rb") as f:
            supabase.storage.from_("reports").upload(
                file_name,
                f,
                file_options={"content-type": "application/pdf"}
            )

        url = supabase.storage.from_("reports").get_public_url(file_name)
        return url

    except Exception as e:
        st.warning(f"⚠️ PDF upload error: {e}")
        return None


def get_all_pdfs() -> list:
    """
    Storage mein saari PDF files ki list fetch karo.
    """
    try:
        files = supabase.storage.from_("reports").list()
        return files
    except Exception as e:
        st.warning(f"⚠️ Fetch PDFs error: {e}")
        return []


# ============================================================
# 4. STATS FUNCTIONS (Dashboard ke liye)
# ============================================================

def get_total_patients() -> int:
    """Total patients count"""
    try:
        result = supabase.table("patients").select("id", count="exact").execute()
        return result.count or 0
    except:
        return 0


def get_total_scans() -> int:
    """Total scans count"""
    try:
        result = supabase.table("scan_results").select("id", count="exact").execute()
        return result.count or 0
    except:
        return 0


def get_positive_cases() -> int:
    """Total positive cases (Pneumonia + Tumor detected)"""
    try:
        result = supabase.table("scan_results")\
            .select("id", count="exact")\
            .neq("result", "NORMAL")\
            .neq("result", "No Tumor")\
            .execute()
        return result.count or 0
    except:
        return 0