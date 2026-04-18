import streamlit as st
import pandas as pd
import pdb
from utils.s3_utils import *
from utils.match_info_utils import *

st.set_page_config(layout="wide")

# st.title("Production-Grade Table (Sticky Header + Checkboxes)")

# Sample data
# df = pd.DataFrame({
#     "Name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"],
#     "Score": [85, 90, 78, 92, 88, 76]
# })
s3=S3()

def create_file(filename):
    # print(filename)
    # print(prev_session_state)
    # pdb.set_trace()
    
    jd=st.session_state.jd_text
    jd_file=st.session_state.jd_file

    if not jd_file:
        match_info_file_path=f"{filename.split("/")[-1].split('.')[0]}_match_info.pdf"
    else:
        match_info_file_path=f"{jd_file.name.split("/")[-1].split('.')[0]}_{filename.split("/")[-1].split('.')[0]}_match_info.pdf"
    

    if not s3.file_exists(match_info_file_path,default_folder=False) or not jd_file:
        # pdb.set_trace()
        if jd_file:
            match_info_file_path=getMatchInfo(s3,filename,jd,jd_file.name)
        else:
            match_info_file_path=getMatchInfo(s3,filename,jd,'')
        
        s3.upload_to_s3(match_info_file_path,default_folder=False)

    s3_url=s3.getS3Url(match_info_file_path.split("/")[-1],default_folder=False)

    st.session_state.generated_files[filename]=s3_url

    return match_info_file_path.split("/")[-1]
    

def update_table(df):

    # Session state for selections
    

    # if "generating" not in st.session_state:
    #     st.session_state.generating = set()

    # if "load_state" not in st.session_state:
    #     st.session_state.load_state=set()

    # -------------------------
    # CSS styling
    # -------------------------
    st.markdown("""
    <style>
    .table-container {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
    }

    /* Header */
    .header {
        position: sticky;
        top: 0;
        background: white;
        z-index: 10;
        border-bottom: 2px solid #ccc;
    }

    /* Row styling */
    .row {
        display: flex;
        border-bottom: 1px solid #eee;
        align-items: center;
    }

    /* Cells */
    .cell {
        padding: 10px;
        flex: 1;
        border-right: 1px solid #eee;
    }

    .cell:last-child {
        border-right: none;
    }

    /* Header cells */
    .header .cell {
        font-weight: bold;
        background-color: #f9fafb;
    }

    /* Hover effect */
    .row:hover {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)

    # -------------------------
    # Table container
    # -------------------------
    st.markdown('<div class="table-container">', unsafe_allow_html=True)

    # Header
    widths=[4]*(len(df.columns)+2)
    # header_cols = st.columns([1, 3, 2, 2])
    header_cols = st.columns(widths)

    for idx in range(len(df.columns)+2):

        if idx==len(df.columns):
            header_cols[idx].markdown(f'<div class="cell header">Get Match Info</div>', unsafe_allow_html=True)
        elif idx==len(df.columns)+1:
            header_cols[idx].markdown(f'<div class="cell header">Match Info File</div>', unsafe_allow_html=True)
        else:
            header_cols[idx].markdown(f'<div class="cell header">{df.columns[idx]}</div>', unsafe_allow_html=True)
    # header_cols[0].markdown('<div class="cell header">Select</div>', unsafe_allow_html=True)
    # header_cols[1].markdown('<div class="cell header">Name</div>', unsafe_allow_html=True)
    # header_cols[2].markdown('<div class="cell header">Score</div>', unsafe_allow_html=True)
    # header_cols[3].markdown('<div class="cell header">Get Match Info</div>', unsafe_allow_html=True)

    # Rows
    
    for i, row in df.iterrows():
        # cols = st.columns([1, 3, 2, 2])
        cols = st.columns(widths)
        filename=row["file name"].split(">")[1].split("<")[0]
        # checked = cols[-1].checkbox(
        #     "",
        #     key=f"chk_{i}",
        #     value=st.session_state.selected_rows.get(i, False)
        # )
        # st.session_state.selected_rows[i] = checked

        # try:
        #     if checked:
        #         # pdb.set_trace()
        #         if i not in st.session_state.generated_files:
        #             st.session_state.generated_files[i] = create_file(
        #                 row["file name"],
        #                 # row["Score"]
        #             )
        # except:
        #     pdb.set_trace()

        #     file_buffer = st.session_state.generated_files[i]
        #     st.write("file created")

            # Download icon/button
            # cols[3].download_button(
            #     label="📄",
            #     data=file_buffer,
            #     file_name=f"{row['Name']}_report.txt",
            #     mime="text/plain",
            #     key=f"dl_{i}"
            # )
        # else:
        #     st.write("file not created")
            # cols[3].write("-")

        for idx in range(len(df.columns)+2):
            if idx==len(df.columns):
            #     # cols[idx].button("Get Match Info", key=f"run_{i}")
                
            #     if cols[idx].button("Generate", key=f"gen_{i}"):

            #         # mark as "generating" (instant UI feedback)
            #         # st.session_state.generating.add(idx)

            #         # create file
            #         st.session_state.files[i] = create_file(
            #             row["file name"]
            #         )

                #     st.toast(f"File generated for {row['Name']}")
                
                if  cols[idx].button("Get Match Info", key=f"gmi_{i}") or i in st.session_state.selected_rows:
                    # st.session_state.load_state.append(i)
                    st.session_state.selected_rows.add(i)
                    match_info_file=create_file(
                        filename,
                        # prev_session_state
                    )
            elif idx==len(df.columns)+1:
                if filename in st.session_state.generated_files:
                    match_info_url=st.session_state.generated_files[filename]
                    display_text=f'<a href="{match_info_url}" target="_blank">{match_info_file}</a>'
                    cols[idx].markdown(display_text, unsafe_allow_html=True)
            else:
                col_name=df.columns[idx]
                cols[idx].markdown(f'<div class="cell">{row[col_name]}</div>', unsafe_allow_html=True)
        # cols[1].markdown(f'<div class="cell">{row["Name"]}</div>', unsafe_allow_html=True)
        # cols[2].markdown(f'<div class="cell">{row["Score"]}</div>', unsafe_allow_html=True)
        # cols[3].button("Run", key=f"run_{i}")

        # st.session_state.selected_rows[i] = checked

    st.markdown('</div>', unsafe_allow_html=True)

    # submitted = st.form_submit_button("Apply")

     # -------------------------
    # Selected rows output
    # -------------------------
    # selected_indices = [i for i, v in st.session_state.selected_rows.items() if v]
    # selected_df = df.loc[selected_indices]

    # st.write("### Selected Rows")
    # st.dataframe(selected_df, use_container_width=True)
# update_table(df)