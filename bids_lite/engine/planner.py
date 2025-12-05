# bids_lite/engine/planner.py
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import pandas as pd
import numpy as np
import re

def _extract_id_from_text(text: str, target_id: str, is_session_id: bool = False) -> bool:
    """
    Intelligently extract and match participant/session ID from text (filename or folder name).
    Handles various formats:
    - Numeric: 001, 01, 1, patient_001, patient-001, patient 001
    - Alphanumeric: Smith2023A, smith-2023-A, Smith_2023_A, etc.
    Uses precise matching to avoid false positives (e.g., 001 matching 002).
    
    Special characters in user-defined IDs are normalized to 'u' for matching.
    BIDS format separators (- and _) are only used in BIDS structure, not in participant_id.
    
    Args:
        text: Text to search in (filename or folder name)
        target_id: Target ID to match (should be normalized, with special chars replaced by 'u')
    
    Returns:
        True if target_id matches any variant found in text
    """
    if not text or not target_id:
        return False
    
    # Normalize both to lowercase for case-insensitive matching
    text_normalized = text.lower()
    target_normalized = target_id.lower().strip()
    
    # Normalize text: replace special characters with 'u' to match normalized target_id
    # This allows matching original formats (Smith_2023_A) with normalized IDs (smithu2023ua)
    text_normalized = re.sub(r'[^a-z0-9]', 'u', text_normalized)
    
    # Check if target_id is purely numeric
    is_numeric = target_normalized.isdigit()
    
    if is_numeric:
        # Handle numeric IDs (001, 01, 1, etc.)
        # Generate all possible variants (with/without zero-padding)
        target_clean = target_normalized.lstrip('0') or '0'
        target_variants = list(set([
            target_normalized,  # Original: 001
            target_clean,       # Without leading zeros: 1
            target_normalized.zfill(3),  # Ensure 3 digits: 001
            target_normalized.zfill(2),  # Ensure 2 digits: 01
            target_clean.zfill(3),      # Clean with 3 digits: 001
            target_clean.zfill(2),      # Clean with 2 digits: 01
        ]))
        
        # Use precise matching to avoid false positives
        # Note: 'u' is used to replace special chars, so it acts as a boundary
        # For BIDS format files, participant_id should be after 'sub-' prefix
        # Check if text contains 'sub' pattern to identify BIDS format
        is_bids_format = 'sub' in text_normalized
        
        for variant in target_variants:
            # Check if variant exists in text
            if variant in text_normalized:
                # Find all occurrences
                start = 0
                while True:
                    idx = text_normalized.find(variant, start)
                    if idx == -1:
                        break
                    
                    # For BIDS format, participant_id should be after 'sub', session_id should be after 'ses'
                    if is_bids_format:
                        if is_session_id:
                            # For session_id, only match in session section (after 'ses')
                            ses_pos = text_normalized.find('ses')
                            if ses_pos == -1 or idx < ses_pos:
                                # No session section or match is before session section - skip
                                start = idx + 1
                                continue
                        else:
                            # For participant_id, only match in participant section (before 'ses')
                            sub_pos = text_normalized.find('sub')
                            if sub_pos != -1:
                                ses_pos = text_normalized.find('ses', sub_pos)
                                if ses_pos != -1 and idx >= ses_pos:
                                    # This match is in session section, not participant section - skip
                                    start = idx + 1
                                    continue
                    
                    # Check left boundary: allow 'u' (from special chars) or start of string
                    left_ok = (idx == 0 or text_normalized[idx-1] == 'u' or not text_normalized[idx-1].isalnum())
                    
                    # Check right boundary: allow 'u' (from special chars) or end of string
                    right_pos = idx + len(variant)
                    if right_pos < len(text_normalized):
                        right_char = text_normalized[right_pos]
                        right_ok = (right_char == 'u' or not right_char.isalnum())
                    else:
                        right_ok = True
                    
                    # For single-digit variants, additional check: ensure it's not part of a larger number
                    # e.g., '1' should not match in 't1w' or '002'
                    if len(variant) == 1 and variant.isdigit():
                        # Check if it's part of a larger number
                        if idx > 0 and text_normalized[idx-1].isdigit():
                            # Preceded by a digit - likely part of larger number
                            start = idx + 1
                            continue
                        if right_pos < len(text_normalized) and text_normalized[right_pos].isdigit():
                            # Followed by a digit - likely part of larger number
                            start = idx + 1
                            continue
                    
                    if left_ok and right_ok:
                        return True
                    
                    start = idx + 1
    else:
        # Handle alphanumeric IDs (smithu2023ua, ahmed, ross1981case2, etc.)
        # For derivatives datasets, participant IDs can be:
        # - Simple author names: Ahmed, Hirel, Shatzman
        # - Author+year+case: Ross1981-case2, Abdullah2015Case07
        # - Complex formats: Anhedonia_LesionTracing_Abdullah_2015_Case07_f
        
        # Strategy: Try multiple matching approaches
        # 1. Direct match (exact normalized form)
        # 2. Match without 'u' separators (for files without separators)
        # 3. Extract author name from complex filenames and match
        
        # First, try direct match with normalized forms
        if target_normalized in text_normalized:
            idx = text_normalized.find(target_normalized)
            left_ok = (idx == 0 or not text_normalized[idx-1].isalnum())
            right_pos = idx + len(target_normalized)
            if right_pos < len(text_normalized):
                right_char = text_normalized[right_pos]
                # Allow 'u' (from separator) or end of string, but not alphanumeric
                # However, if target is a prefix of a longer ID (e.g., ross1981ucase2 vs ross1981ucase3),
                # we need to ensure the next character is not part of a continuation
                right_ok = (right_char == 'u' or not right_char.isalnum())
                
                # Additional check: if target ends with a digit and next char is also a digit,
                # this might be a longer number (e.g., case2 vs case3)
                # We need to check if the target is a prefix of a longer ID
                if target_normalized[-1].isdigit() and right_char.isdigit():
                    # This is a prefix match - target ends with digit, text continues with digit
                    # Check if the continuation forms a valid longer ID
                    # For example: ross1981ucase2 vs ross1981ucase3
                    # We should only match if the next character after the digit is 'u' or end
                    # But if it's another digit, it's a different case number - don't match
                    right_ok = False
                elif target_normalized[-1].isdigit() and right_char == 'u':
                    # Target ends with digit, next is 'u' - this is OK (end of ID)
                    right_ok = True
                elif not target_normalized[-1].isdigit():
                    # Target doesn't end with digit - normal check applies
                    pass
            else:
                right_ok = True
            
            if left_ok and right_ok:
                return True
        
        # Second, try removing 'u' from target to match files without separators
        # e.g., target "smithu2023ua" should match "smith2023a" in filename
        target_without_u = target_normalized.replace('u', '')
        if target_without_u and target_without_u in text_normalized:
            idx = text_normalized.find(target_without_u)
            left_ok = (idx == 0 or not text_normalized[idx-1].isalnum())
            right_pos = idx + len(target_without_u)
            if right_pos < len(text_normalized):
                right_char = text_normalized[right_pos]
                right_ok = (right_char == 'u' or not right_char.isalnum())
            else:
                right_ok = True
            
            if left_ok and right_ok:
                return True
        
        # Also try matching target against text with flexible 'u' separators
        # e.g., "abdullah2015case07" should match "abdullahu2015ucase07"
        # Build pattern that allows optional 'u' at letter-digit and digit-letter transitions
        if len(target_normalized) > 3:
            pattern_parts = []
            for i, char in enumerate(target_normalized):
                if i > 0:
                    prev_char = target_normalized[i-1]
                    # Allow optional 'u' at transitions between letters and digits
                    if (prev_char.isalpha() and char.isdigit()) or (prev_char.isdigit() and char.isalpha()):
                        pattern_parts.append(r'u?')  # Optional 'u' at transition
                pattern_parts.append(re.escape(char))
            
            flexible_pattern = ''.join(pattern_parts)
            match = re.search(flexible_pattern, text_normalized)
            if match:
                start, end = match.span()
                # Check boundaries
                left_ok = (start == 0 or text_normalized[start-1] == 'u' or not text_normalized[start-1].isalnum())
                if end < len(text_normalized):
                    right_char = text_normalized[end]
                    right_ok = (right_char == 'u' or not right_char.isalnum())
                else:
                    right_ok = True
                
                if left_ok and right_ok:
                    return True
        
        # Third, for derivatives with complex filenames, try to extract and match author name
        # e.g., "Anhedonia_LesionTracing_Abdullah_2015_Case07_f" -> match "Abdullah"
        # Extract potential author name from target (first word before digits or 'u')
        # For "ahmed" -> "ahmed" (simple name, use full match)
        # For "ross1981case2" -> "ross" (but need to be careful about case numbers)
        # For "abdullahu2015ucase07" -> "abdullah"
        target_author_match = re.match(r'^([a-z]+)', target_normalized)
        if target_author_match:
            target_author = target_author_match.group(1)
            
            # Only use author name matching if target is just the author name (no digits after)
            # If target has digits/case numbers, we should have matched in step 1 or 2
            # This prevents "ross" from matching both "ross1981case2" and "ross1981case3"
            target_after_author = target_normalized[len(target_author):]
            is_simple_author_name = (not target_after_author or 
                                    target_after_author.startswith('u') and 
                                    not any(c.isdigit() for c in target_after_author[:5]))  # Allow some text after, but not digits immediately
            
            if is_simple_author_name and target_author in text_normalized:
                # Find all occurrences
                start = 0
                while True:
                    idx = text_normalized.find(target_author, start)
                    if idx == -1:
                        break
                    
                    # Check left boundary: should be start or 'u' or non-alphanumeric
                    left_ok = (idx == 0 or text_normalized[idx-1] == 'u' or not text_normalized[idx-1].isalnum())
                    
                    # Check right boundary: should be followed by 'u', digit, or end
                    right_pos = idx + len(target_author)
                    if right_pos < len(text_normalized):
                        right_char = text_normalized[right_pos]
                        right_ok = (right_char == 'u' or right_char.isdigit() or not right_char.isalnum())
                    else:
                        right_ok = True
                    
                    if left_ok and right_ok:
                        return True
                    
                    start = idx + 1
        
        # Also try exact match
        if target_normalized == text_normalized:
            return True
    
    return False


def _extract_id_from_path(file_path: Path, target_id: str, is_session_id: bool = False) -> bool:
    """
    Check if target_id matches in file path (filename or any parent folder name).
    Supports one-patient-per-folder structure.
    
    Args:
        file_path: Full path to file
        target_id: Target ID to match
        is_session_id: If True, allow matching in session section (for session_id matching)
    
    Returns:
        True if target_id is found in filename or any parent folder
    """
    # Check filename
    if _extract_id_from_text(file_path.name, target_id, is_session_id=is_session_id):
        return True
    
    # Check parent folders (one patient per folder structure)
    # Get parents as a list to safely check for root
    parents_list = list(file_path.parents)
    if not parents_list:
        return False
    
    root_parent = parents_list[-1]  # Last parent is typically the root
    for parent in parents_list:
        if parent == root_parent:  # Skip root
            continue
        if _extract_id_from_text(parent.name, target_id, is_session_id=is_session_id):
            return True
    
    return False


def _dst_for_modality(out_dir: Path, pid: str, sid: str, modality: str, 
                      dataset_type: str = "raw", pipeline_name: Optional[str] = None,
                      has_session: bool = True) -> Path:
    """
    Generate destination path for a file based on modality and dataset type.
    
    Args:
        out_dir: Base output directory
        pid: Participant ID
        sid: Session ID (may be default "01" if not in metadata)
        modality: Modality (T1w, T2w, FLAIR, bold, lesion, connectivity, etc.)
        dataset_type: "raw" or "derivatives"
        pipeline_name: Pipeline name for derivatives (required if dataset_type is "derivatives")
        has_session: Whether session_id exists in metadata (False for derivatives without sessions)
    """
    modality = modality.strip().lower()
    if modality in ["t1w", "t2w", "flair"]:
        subdir = "anat"
        suffix = modality
    elif modality == "bold":
        subdir = "func"
        suffix = "bold"
    elif modality in ["lesion", "connectivity"] or modality.startswith("conn"):
        # For lesion/connectivity data, put in anat or create custom subdir
        # Connectivity can be "connectivity", "conn", "conn_matrix", "conn_results", etc.
        subdir = "anat"  # or could be "lesion", "connectivity" depending on BIDS extension
        suffix = modality
    else:
        # fallback: put in 'anat'
        subdir = "anat"
        suffix = modality

    # Build filename - handle cases without session
    if has_session:
        filename = f"sub-{pid}_ses-{sid}_{suffix}.nii.gz"
    else:
        # For derivatives without sessions, omit ses- prefix
        filename = f"sub-{pid}_{suffix}.nii.gz"
    
    # Handle derivatives structure
    if dataset_type == "derivatives":
        if pipeline_name is None:
            raise ValueError("pipeline_name is required for derivatives dataset type")
        # Derivatives go in: derivatives/pipeline_name/sub-XXX/...
        if has_session:
            return out_dir / "derivatives" / pipeline_name / f"sub-{pid}" / f"ses-{sid}" / subdir / filename
        else:
            # No session: derivatives/pipeline_name/sub-XXX/subdir/
            return out_dir / "derivatives" / pipeline_name / f"sub-{pid}" / subdir / filename
    else:
        # Raw data goes directly: sub-XXX/ses-XXX/... (always has session)
        return out_dir / f"sub-{pid}" / f"ses-{sid}" / subdir / filename


def plan_transforms(in_dir: Path, out_dir: Path, meta: pd.DataFrame, 
                   dataset_type: str = "raw", pipeline_name: Optional[str] = None,
                   match_all_modalities: bool = True) -> List[Dict]:
    """
    Plan file transformations from input directory to BIDS structure.
    
    Args:
        in_dir: Input directory with source files
        out_dir: Output BIDS directory
        meta: Metadata DataFrame with participant_id, session_id, and optionally modality
        dataset_type: "raw" or "derivatives"
        pipeline_name: Pipeline name for derivatives
        match_all_modalities: If True, one metadata row can match multiple files with different modalities.
                            If False, only match files with the specified modality (if provided).
    
    Returns:
        List of operations: [{"src": str, "dst": str, "action": str}, ...]
    """
    ops: List[Dict] = []
    all_files = [p for p in in_dir.rglob("*") if p.is_file() and p.name.endswith((".nii", ".nii.gz"))]
    used_files = set()  # Track which files have been matched to avoid duplicates
    
    # Check if metadata has session_id column
    has_session_in_meta = "session_id" in meta.columns

    for _, row in meta.iterrows():
        pid = str(row["participant_id"])
        # session_id may be missing for derivatives (lesion/connectivity data)
        # For raw data, if session_id is missing, use default "01" (BIDS standard requires session for raw)
        # For derivatives, if session_id is missing, set sid to None (no session folders)
        if has_session_in_meta and pd.notna(row.get("session_id")) and str(row.get("session_id", "")).strip():
            sid = str(row.get("session_id"))
        else:
            # For raw data: default to "01" (BIDS standard requires session for raw)
            # For derivatives: set to None (sessions are optional, no session folders)
            if dataset_type == "raw":
                sid = "01"  # Default session if missing (used for raw data)
            else:
                sid = None  # Explicitly None for derivatives without session_id
        specified_modality = str(row.get("modality", "")).strip() if "modality" in row else ""

        # pid is already normalized (special chars -> 'u') from normalize_ids()
        # We need to match it against files that may have original formats (with special chars)
        pid_normalized = str(pid).strip().lower()
        sid_normalized = str(sid).strip().lower() if sid is not None else ""
        
        # Find all matching files for this participant/session
        # Use intelligent matching that handles messy filenames and folder structures
        # The matching function will normalize file/folder names to match normalized participant_id
        candidates = []
        for p in all_files:
            if str(p) in used_files:
                continue
            
            # Check if participant_id matches in filename or folder structure
            # _extract_id_from_path will normalize file/folder names (special chars -> 'u') for matching
            pid_match = _extract_id_from_path(p, pid_normalized)
            if not pid_match:
                continue
            
            # For derivatives without session_id, match by participant only
            # Otherwise, check session_id if it exists in metadata
            # But be flexible: if filename doesn't contain session_id, still allow match
            # (many users don't include session_id in filenames)
            if has_session_in_meta and pd.notna(row.get("session_id")) and str(row.get("session_id", "")).strip():
                # Check if filename/folder contains session_id
                # If it does, require match; if it doesn't, allow match (flexible)
                sid_in_path = _extract_id_from_path(p, sid_normalized, is_session_id=True)
                # Also check if any session-like pattern exists in the path
                # If session pattern exists but doesn't match, skip this file
                # If no session pattern exists, allow match (user didn't include session in filename)
                path_text = (str(p.parent) + " " + p.name).lower()
                # Look for common session patterns (ses-01, session01, etc.)
                # Generate variants for zero-padding (001, 01, 1)
                sid_clean = sid_normalized.lstrip('0') or '0'
                sid_variants = [
                    sid_normalized,  # 001
                    sid_clean,       # 1
                    sid_normalized.zfill(3),  # 001
                    sid_normalized.zfill(2),  # 01
                    sid_clean.zfill(3),       # 001
                    sid_clean.zfill(2),       # 01
                ]
                sid_variants = list(set(sid_variants))  # Remove duplicates
                
                # Check if any session pattern exists with any variant
                has_session_pattern = False
                for variant in sid_variants:
                    if any([
                        f"ses-{variant}" in path_text,
                        f"session{variant}" in path_text,
                        f"session-{variant}" in path_text,
                        f"ses{variant}" in path_text,
                    ]):
                        has_session_pattern = True
                        break
                
                # Also check with regex for any session pattern
                if not has_session_pattern:
                    has_session_pattern = (re.search(r'ses[_-]?\d+|session[_-]?\d+', path_text) is not None)
                
                if has_session_pattern and not sid_in_path:
                    # Session pattern exists but doesn't match - skip
                    continue
                # Otherwise allow match (either matches, or no session pattern exists)
            # If no session_id in metadata, match any file with this participant
            
            # Auto-detect modality from filename (modality is never in metadata for derivatives)
            modality = "T1w"  # default
            p_name_upper = p.name.upper()
            if "T1W" in p_name_upper or "T1-W" in p_name_upper:
                modality = "T1w"
            elif "T2W" in p_name_upper or "T2-W" in p_name_upper:
                modality = "T2w"
            elif "FLAIR" in p_name_upper:
                modality = "FLAIR"
            elif "BOLD" in p_name_upper:
                modality = "bold"
            elif "LESION" in p_name_upper or "LES" in p_name_upper:
                modality = "lesion"  # For lesion data
            elif "CONNECTIVITY" in p_name_upper or "FC" in p_name_upper or "CONN" in p_name_upper:
                modality = "connectivity"  # For connectivity data
            else:
                # Try to extract from filename or use default
                modality = specified_modality if specified_modality else "T1w"
            
            candidates.append((p, modality))

        if not candidates:
            continue

        # Process all matching files for this participant/session
        # Prefer .nii.gz over .nii if both exist
        candidates_sorted = sorted(candidates, key=lambda x: (x[0].suffix != '.gz', x[0].name))
        
        for src, modality in candidates_sorted:
            if str(src) in used_files:
                continue
            
            used_files.add(str(src))
            # Pass has_session flag to handle derivatives without sessions
            # For raw data: always use session (even if default "01")
            # For derivatives: only use session if session_id was actually in metadata (and not None)
            if dataset_type == "raw":
                # Raw data always has session (BIDS standard requirement)
                use_session = True
            else:
                # Derivatives: only use session if it was in metadata and is not None
                use_session = has_session_in_meta and sid is not None
            
            dst = _dst_for_modality(out_dir, pid, sid or "", modality, dataset_type, pipeline_name, has_session=use_session)
            ops.append({"src": str(src), "dst": str(dst), "action": "copy"})

    return ops
