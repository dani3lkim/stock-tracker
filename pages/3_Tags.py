import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from db import get_tags, add_tag, remove_tag, update_tag

st.set_page_config(page_title="Tags", layout="wide")
st.title("Tags")
st.caption("Tags let you categorize watchlist stocks (e.g. 'Tech', 'Dividend', 'Speculative'). "
           "A stock can have many tags; a tag can apply to many stocks.")

# --- Add Tag ---
st.subheader("Add Tag")
with st.form("add_tag"):
    tag_name = st.text_input("Tag Name *", placeholder="e.g. Tech, Dividend, Growth")
    submitted = st.form_submit_button("Add Tag")

if submitted:
    errors = []
    if not tag_name.strip():
        errors.append("**Tag name** is required.")
    elif len(tag_name.strip()) > 50:
        errors.append("**Tag name** must be 50 characters or fewer.")
    if errors:
        for e in errors:
            st.error(e)
    else:
        add_tag(tag_name)
        st.success(f"Tag '{tag_name.strip()}' added.")
        st.rerun()

st.divider()

tags = get_tags()

if not tags:
    st.info("No tags yet. Add one above.")
else:
    st.subheader("All Tags")
    st.dataframe(
        pd.DataFrame([{"Tag": t["name"]} for t in tags]),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    tag_map = {t["name"]: t["id"] for t in tags}

    # --- Edit Tag ---
    st.subheader("Edit Tag")
    edit_tag_name = st.selectbox("Select tag to rename", list(tag_map.keys()), key="edit_sel")

    with st.form("edit_tag"):
        new_name = st.text_input("New name *", value=edit_tag_name)
        edit_submitted = st.form_submit_button("Rename")

    if edit_submitted:
        errors = []
        if not new_name.strip():
            errors.append("**Tag name** is required.")
        elif len(new_name.strip()) > 50:
            errors.append("**Tag name** must be 50 characters or fewer.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            update_tag(tag_map[edit_tag_name], new_name)
            st.success(f"Tag renamed to '{new_name.strip()}'.")
            st.rerun()

    st.divider()

    # --- Delete Tag ---
    st.subheader("Delete Tag")
    del_tag_name = st.selectbox("Select tag to delete", list(tag_map.keys()), key="del_sel")

    if "confirm_del_tag" not in st.session_state:
        st.session_state.confirm_del_tag = False

    if st.button("Delete Tag"):
        st.session_state.confirm_del_tag = True

    if st.session_state.confirm_del_tag:
        st.warning(f"Delete tag **'{del_tag_name}'**? It will be removed from all stocks.")
        c1, c2 = st.columns(2)
        if c1.button("Yes, delete it"):
            remove_tag(tag_map[del_tag_name])
            st.session_state.confirm_del_tag = False
            st.success(f"Tag '{del_tag_name}' deleted.")
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_del_tag = False
            st.rerun()
