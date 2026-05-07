import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
from streamlit_extras.metric_cards import style_metric_cards

st.set_page_config(page_title="Football Player Stats Dashboard", page_icon="⚽", layout="wide")
st.header("⚽ FOOTBALL PLAYER STATISTICS ANALYSIS")

# Load data
df_gabungan_2324 = pd.read_csv('df_gabungan_2425_x.csv', header=[0, 1])

# Utility functions
def simplify_position(pos):
    if 'GK' in pos:
        return 'GK'
    elif any(x in pos for x in ['CB', 'RB', 'LB', 'FB', 'DF']):
        return 'DF'
    elif any(x in pos for x in ['DM', 'CM', 'LM', 'RM', 'WM', 'MF']):
        return 'MF'
    elif any(x in pos for x in ['AM', 'LW', 'RW', 'FW']):
        return 'FW'
    else:
        return 'Other'

# Preprocess data
def preprocess_data(df):
    df['Position'] = df['Pos'].apply(simplify_position)
    df['G+A_per90'] = df['G+A'] / (df['Min'] / 90)
    return df

# Sidebar filters
with st.sidebar:
    st.markdown("""
    <h3 style='color: #0e123e;'>FC Barcelona</h3>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title="Main Menu",
        options=["Overview", "Top Scorers", "Position Stats", "Cards & Discipline", "Data Frame"],
        icons=["house", "trophy", "bar-chart", "grid", "table"],
        default_index=0
    )

    competition_selected = st.selectbox(
    "Select Competition",
    options=[
        col for col in df_gabungan_2324.columns.levels[0] 
        if col not in ['Player', 'Unnamed: 0_level_0']
    ]
)

    # Ambil semua kolom level 1 di bawah competition_selected
    df_comp = df_gabungan_2324.loc[:, competition_selected].copy()

    # Jika kolom masih MultiIndex, drop level 0 agar kolom datar
    if isinstance(df_comp.columns, pd.MultiIndex):
        df_comp.columns = df_comp.columns.droplevel(0)

    # Preprocess data
    df_comp = preprocess_data(df_comp)

    with st.expander("🔎 FILTER DATA", expanded=True):
        selected_positions = st.multiselect(
            "📍 Select Position Group",
            options=df_comp["Position"].unique(),
            default=df_comp["Position"].unique()
        )

# Filter dataframe sesuai posisi yg dipilih
df_filtered = df_comp[df_comp["Position"].isin(selected_positions)]

# ----- Dashboard Functions -----
def overview():
    st.subheader("📊 Overview Statistics")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    col1.metric("Total Players", len(df_filtered))
    col2.metric("Total Goals", int(df_filtered['Gls'].sum()))
    col3.metric("Total Assists", int(df_filtered['Ast'].sum()))
    col4.metric("Average Age", f"{df_filtered['Age'].mean():.1f} years")
    col5.metric("Avg Minutes Played", f"{int(df_filtered['Min'].mean())} min")
    col6.metric("Total Yellow Cards", int(df_filtered['CrdY'].sum()))
    col7.metric("Total Red Cards", int(df_filtered['CrdR'].sum()))

    style_metric_cards()

    # Distribution of Players by Position
    st.markdown("### 🔄 Distribution of Players by Position")
    fig = px.histogram(df_filtered, x='Position', color='Position',
                       category_orders={'Position': ['GK', 'DF', 'MF', 'FW', 'Other']},
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
    # Tambahan keterangan
    st.markdown("#### ℹ️ Position Group Explanation")
    st.markdown("""
    - **GK**: Goalkeeper  
    - **DF**: Defender (CB, RB, LB, FB, DF)  
    - **MF**: Midfielder (DM, CM, LM, RM, WM, MF)  
    - **FW**: Forward (AM, LW, RW, FW)  
    - **Other**: Unclassified or Special Roles  
    """)
    # Age Distribution
    st.markdown("### 🎯 Age Distribution")
    fig2 = px.histogram(
        df_filtered,
        x='Age',
        nbins=20,
        color_discrete_sequence=['#0083B8'],
        title="Distribution of Player Ages"
    )

    # Enhance layout for professional appearance
    fig2.update_layout(
        xaxis_title="Age",
        yaxis_title="Number of Players",
        bargap=0.1,
        plot_bgcolor='white',
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(size=14)
    )

    # Add borders to the histogram bars
    fig2.update_traces(marker_line_color='black', marker_line_width=1)

    st.plotly_chart(fig2, use_container_width=True)


def top_scorers():
    st.subheader("🏆 Top 10 Goal Scorers (Non-Penalty)")
    top10 = df_filtered.sort_values('G-PK', ascending=False).head(10)
    fig = px.bar(top10, x='Player', y='G-PK', color='Position',
                 title="Top Scorers", color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

def top_scorers_detail():
    st.subheader("📋 Top Scorer Detail Table")

    default_cols = ['Player', 'Gls', 'Ast', 'G+A', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR']
    selected_cols = st.multiselect(
        "📌 Select Columns to Display",
        options=df_filtered.columns.tolist(),
        default=default_cols
    )

    st.markdown("#### 🔽 Player Stats Table")
    st.dataframe(df_filtered[selected_cols].sort_values('Gls', ascending=False), use_container_width=True)

def position_stats():
    st.subheader("📈 Average Goals & Assists by Position")
    avg_stats = df_filtered.groupby('Position')[['Gls', 'Ast']].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Goals', x=avg_stats['Position'], y=avg_stats['Gls'], marker_color='red'))
    fig.add_trace(go.Bar(name='Assists', x=avg_stats['Position'], y=avg_stats['Ast'], marker_color='green'))
    fig.update_layout(barmode='group', xaxis_title='Position Group', yaxis_title='Average')
    st.plotly_chart(fig, use_container_width=True)

def top_contributors_by_position():
    st.subheader("🌟 Top Contributors by Position")

    # Pilih grup posisi yang ingin dilihat
    selected_position_group = st.selectbox(
        "Select Position Group",
        options=df_filtered['Position'].unique(),
        index=0
    )

    # Filter data berdasarkan grup posisi yang dipilih
    position_group_df = df_filtered[df_filtered['Position'] == selected_position_group]

    # Urutkan berdasarkan jumlah gol dan assist
    position_group_df = position_group_df.sort_values(['Gls', 'Ast'], ascending=False)

    # Kolom untuk ditampilkan
    columns_to_display = ['Player', 'Pos', 'Gls', 'Ast', 'G+A']
    if 'Squad' in position_group_df.columns:
        columns_to_display.insert(1, 'Squad')

    # Tampilkan tabel pemain top
    st.markdown(f"### Top Players in {selected_position_group}")
    st.dataframe(position_group_df[columns_to_display], use_container_width=True)

    # Visualisasi kontribusi pemain dalam posisi tertentu
    st.markdown(f"### Contribution Visualization for {selected_position_group}")
    fig = px.bar(
        position_group_df.head(10),
        x='Player',
        y=['Gls', 'Ast'],
        title=f"Top 10 Contributors in {selected_position_group}",
        labels={'value': 'Contribution', 'variable': 'Metric'},
        barmode='group',
        text_auto=True,
        color_discrete_map={'Gls': 'red', 'Ast': 'green'}
    )
    fig.update_layout(
        xaxis_title="Player",
        yaxis_title="Contribution",
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(size=14)
    )
    st.plotly_chart(fig, use_container_width=True)


def cards_discipline():
    st.subheader("🟥 Cards by Position")
    cards = df_filtered.groupby('Position')[['CrdY', 'CrdR']].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Yellow Cards', x=cards['Position'], y=cards['CrdY'], text=cards['CrdY'], textposition='outside', marker_color='gold'))
    fig.add_trace(go.Bar(name='Red Cards', x=cards['Position'], y=cards['CrdR'], text=cards['CrdR'], textposition='outside', marker_color='crimson'))
    fig.update_layout(barmode='group', xaxis_title='Position Group', yaxis_title='Number of Cards', title='Card Distribution by Position')
    st.plotly_chart(fig, use_container_width=True)

def data_frame():
    st.subheader("📂 Full Dataset")
    show_cols = st.multiselect("Select Columns", options=df_filtered.columns.tolist(),
                               default=['Player', 'Pos', 'Age', 'MP', 'Min', 'Gls', 'Ast', 'G+A'])
    st.dataframe(df_filtered[show_cols], use_container_width=True)

def card_recipients():
    st.subheader("🧾 List of Players Who Received Cards")

    # Multiselect untuk memilih jenis kartu
    selected_cards = st.multiselect(
        "Select Card Type", 
        options=["Yellow Cards", "Red Cards"],
        default=["Yellow Cards", "Red Cards"]
    )

    if not selected_cards:
        st.warning("Please select at least one card type to display data.")
        return

    # Filter dataframe berdasarkan kartu yang dipilih
    if selected_cards == ["Yellow Cards"]:
        cards_df = df_filtered[df_filtered['CrdY'] > 0].copy()
    elif selected_cards == ["Red Cards"]:
        cards_df = df_filtered[df_filtered['CrdR'] > 0].copy()
    else:  # Kedua kartu
        cards_df = df_filtered[(df_filtered['CrdY'] > 0) | (df_filtered['CrdR'] > 0)].copy()

    # Urutkan dataframe sesuai kartu yang dipilih
    if selected_cards == ["Yellow Cards"]:
        cards_df = cards_df.sort_values(by='CrdY', ascending=False)
    elif selected_cards == ["Red Cards"]:
        cards_df = cards_df.sort_values(by='CrdR', ascending=False)
    else:
        cards_df['TotalCards'] = cards_df['CrdY'] + cards_df['CrdR']
        cards_df = cards_df.sort_values(by='TotalCards', ascending=False)

    # Kolom yang akan ditampilkan
    display_cols = ['Player', 'Position', 'Pos']
    if 'Squad' in cards_df.columns:
        display_cols.append('Squad')
    if "Yellow Cards" in selected_cards:
        display_cols.append('CrdY')
    if "Red Cards" in selected_cards:
        display_cols.append('CrdR')

    st.dataframe(cards_df[display_cols], use_container_width=True)

# --- Menu Routing ---
if selected == "Overview":
    overview()
elif selected == "Top Scorers":
    top_scorers()
    top_scorers_detail()
elif selected == "Position Stats":
    position_stats()
    top_contributors_by_position()
elif selected == "Cards & Discipline":
    cards_discipline()
    card_recipients()
elif selected == "Data Frame":
    data_frame()
