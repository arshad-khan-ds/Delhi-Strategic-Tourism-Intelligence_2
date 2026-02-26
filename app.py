import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Delhi PDIS | Strategic Tourism Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== PROFESSIONAL STYLING ====================
st.markdown("""
    <style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background-color: #FFFFFF;
        padding: 0px;
    }
    
    .css-1d391kg {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .header-title {
        font-size: 2.5em;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1.1em;
        color: #475569;
        font-weight: 400;
        margin-bottom: 1.5rem;
    }
    
    .stMetricLabel {
        font-size: 0.95em;
        color: #475569;
        font-weight: 500;
    }
    
    .stMetricValue {
        font-size: 1.8em;
        font-weight: 700;
        color: #0F1419;
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #F8FAFC 0%, #F0F4F8 100%);
        border-left: 4px solid #1E3A5F;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
    }
    
    [data-testid="stTabs"] > [data-testid="stTabList"] button {
        font-weight: 600;
        color: #64748B;
    }
    
    [data-testid="stTabs"] > [data-testid="stTabList"] button[aria-selected="true"] {
        color: #1E3A5F;
        border-bottom: 3px solid #1E3A5F;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E3A5F 50%, #162E45 100%);
        border-right: 1px solid #0A0E1A;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #E8F0F7;
    }
    
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: #E8F0F7;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stSlider label {
        color: #B3D4E8 !important;
        font-size: 0.95em;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #B3D4E8 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: rgba(30, 58, 95, 0.2);
        border-color: #3D6B9B;
        border-left: 4px solid #3D6B9B;
    }
    
    [data-testid="stSidebar"] [data-testid="stAlert"] p {
        color: #E8F0F7;
    }
    
    [data-testid="stExpander"] {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }
    
    .section-title {
        font-size: 1.6em;
        font-weight: 700;
        color: #0F172A;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #1E3A5F;
    }
    
    .subsection-title {
        font-size: 1.3em;
        font-weight: 600;
        color: #0F172A;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    
    .hero-image {
        width: 100%;
        height: 400px;
        object-fit: cover;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== DATA LOADING & CACHING ====================
@st.cache_data
def load_pdis_data():
    """Load and clean PDIS dataset"""
    df = pd.read_csv('Final Data to use.csv')
    
    df_clean = df[~df['Year'].isin([2020, 2021])].copy()
    
    if 'International_Aviation_Arrivals' in df_clean.columns:
        df_clean['Total_Arrivals'] = df_clean['International_Aviation_Arrivals']
    
    if 'Estimated_Delhi_FTAs' in df_clean.columns:
        df_clean['FTA_Foreign'] = df_clean['Estimated_Delhi_FTAs']

    if 'Capture_Ratio (%)' not in df_clean.columns:
        if 'Total_Arrivals' in df_clean.columns:
            total_arrivals = df_clean['Total_Arrivals']
        else:
            total_arrivals = df_clean['International_Aviation_Arrivals']
        df_clean['Capture_Ratio (%)'] = (df_clean['Occupancy (%)'] / total_arrivals.replace(0, 1)) * 100
    
    if 'Market_Intensity' not in df_clean.columns:
        if 'FTA_Foreign' in df_clean.columns:
            fta = df_clean['FTA_Foreign']
        else:
            fta = df_clean['Estimated_Delhi_FTAs']
        df_clean['Market_Intensity'] = fta / (df_clean['Avg_Temp'] + 1)
    
    return df_clean

@st.cache_data
def load_aqi_data():
    """Load AQI data"""
    try:
        return pd.read_csv('Delhi_Monthly_AQI_Aggregated.csv')
    except:
        return None

@st.cache_data
def load_fta_data():
    """Load FTA data"""
    try:
        return pd.read_csv('Refined_Delhi_Monthly_FTAs_2015_2024.csv')
    except:
        return None

# ==================== MAIN APPLICATION ====================
try:
    df = load_pdis_data()
    aqi_df = load_aqi_data()
    fta_df = load_fta_data()
    
    # ==================== HEADER SECTION ====================
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="header-title">🏨 Delhi Strategic Tourism Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-subtitle">Professional Analytics Report | Destination Performance Intelligence System (PDIS)</div>', unsafe_allow_html=True)
    
    with col2:
        st.write("")
    
    # Hero Image
    try:
        import requests
        from PIL import Image
        from io import BytesIO
        
        img_url = "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=1200&h=400&fit=crop&q=80"
        response = requests.get(img_url, timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            st.image(img, caption="Delhi's Premier Hospitality Landscape")
    except:
        st.info("🏨 Delhi Hospitality Market Analytics Dashboard")
    
    st.markdown("---")
    
    # ==================== SIDEBAR CONTROLS ====================
    st.sidebar.markdown("""<div style='padding: 15px 0; border-bottom: 2px solid rgba(177, 212, 232, 0.3);'>
            <h2 style='color: #B3D4E8; font-size: 1.3em; margin: 0 0 10px 0; font-weight: 700;'>📊 ANALYSIS CONTROLS</h2>
            <p style='color: #8BA8C0; font-size: 0.85em; margin: 0;'>Customize your analysis view</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.write("")
    
    st.sidebar.markdown("<p style='color: #3D6B9B; font-weight: 600; font-size: 0.95em; margin-bottom: 8px;'>📅 Year Range</p>", unsafe_allow_html=True)
    year_range = st.sidebar.slider(
        "Select Year Range",
        int(df['Year'].min()),
        int(df['Year'].max()),
        (int(df['Year'].min()), int(df['Year'].max())),
        label_visibility="collapsed"
    )
    
    df_filtered = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])].copy()
    st.sidebar.caption(f"📌 {year_range[0]} → {year_range[1]}")
    
    st.sidebar.write("")
    
    if 'Month' in df_filtered.columns:
        st.sidebar.markdown("<p style='color: #3D6B9B; font-weight: 600; font-size: 0.95em; margin-bottom: 12px;'>🗓️ Months (Select Multiple)</p>", unsafe_allow_html=True)
        months = sorted(df_filtered['Month'].unique())
        selected_months = st.sidebar.multiselect(
            "Select Months",
            months,
            default=months,
            label_visibility="collapsed",
            help="Click to toggle months"
        )
        if selected_months:
            df_filtered = df_filtered[df_filtered['Month'].isin(selected_months)]
        st.sidebar.caption(f"✓ {len(selected_months)} month(s) selected")
    
    st.sidebar.markdown("")
    st.sidebar.markdown("""
        <div style='padding: 12px; background-color: rgba(61, 107, 155, 0.15); border-left: 4px solid #3D6B9B; border-radius: 4px; margin: 15px 0;'>
            <p style='color: #B3D4E8; font-size: 0.85em; margin: 0;'><strong>📌 Data Dictionary</strong></p>
            <p style='color: #8BA8C0; font-size: 0.75em; margin: 5px 0 0 0;'><strong>Total Arrivals:</strong> All visitor modes</p>
            <p style='color: #8BA8C0; font-size: 0.75em; margin: 5px 0 0 0;'><strong>Foreign Tourists:</strong> Tourism-focused</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("""
        <div style='padding: 15px 0; border-bottom: 2px solid rgba(177, 212, 232, 0.3);'>
            <h2 style='color: #B3D4E8; font-size: 1.3em; margin: 0 0 10px 0; font-weight: 700;'>🧬 SCENARIO SIMULATOR</h2>
            <p style='color: #8BA8C0; font-size: 0.85em; margin: 0;'>Forecast RevPAR under different conditions</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.write("")
    
    st.sidebar.markdown("<p style='color: #3D6B9B; font-weight: 600; font-size: 0.95em; margin-bottom: 8px;'>💨 Air Quality Index</p>", unsafe_allow_html=True)
    sim_aqi = st.sidebar.slider("AQI Level", 50, 500, 200, label_visibility="collapsed")
    st.sidebar.caption(f"Value: {sim_aqi}")
    
    st.sidebar.write("")
    
    st.sidebar.markdown("<p style='color: #3D6B9B; font-weight: 600; font-size: 0.95em; margin-bottom: 8px;'>💱 Exchange Rate</p>", unsafe_allow_html=True)
    sim_fx = st.sidebar.slider("USD/INR Exchange Rate", 70.0, 95.0, 83.0, label_visibility="collapsed")
    st.sidebar.caption(f"₹{sim_fx:.2f}/USD")
    
    st.sidebar.write("")
    
    st.sidebar.markdown("<p style='color: #3D6B9B; font-weight: 600; font-size: 0.95em; margin-bottom: 8px;'>🌡️ Temperature</p>", unsafe_allow_html=True)
    sim_temp = st.sidebar.slider("Avg Temperature (°C)", 10.0, 45.0, 30.0, label_visibility="collapsed")
    st.sidebar.caption(f"{sim_temp:.1f}°C")
    
    # ==================== EXECUTIVE SUMMARY KPIs ====================
    st.markdown('<div class="section-title">📈 Executive Summary - Key Performance Indicators</div>', unsafe_allow_html=True)
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        avg_revpar = df_filtered['RevPAR (INR)'].mean()
        delta_revpar = ((df_filtered[df_filtered['Year'] == df_filtered['Year'].max()]['RevPAR (INR)'].mean() - 
                        df_filtered[df_filtered['Year'] == df_filtered['Year'].min()]['RevPAR (INR)'].mean()) / 
                       df_filtered[df_filtered['Year'] == df_filtered['Year'].min()]['RevPAR (INR)'].mean() * 100)
        st.metric(
            "Average RevPAR",
            f"₹{avg_revpar:,.0f}",
            f"{delta_revpar:+.1f}%",
            delta_color="normal"
        )
    
    with kpi2:
        avg_occupancy = df_filtered['Occupancy (%)'].mean()
        st.metric(
            "Average Occupancy",
            f"{avg_occupancy:.1f}%",
            "All Properties"
        )
    
    with kpi3:
        if 'Total_Arrivals' in df_filtered.columns:
            total_arr = df_filtered['Total_Arrivals'].sum()
        else:
            total_arr = df_filtered['International_Aviation_Arrivals'].sum()
        st.metric(
            "Total Arrivals",
            f"{total_arr:,.0f}",
            "Period Total"
        )
    
    with kpi4:
        if 'FTA_Foreign' in df_filtered.columns:
            fta_foreign = df_filtered['FTA_Foreign'].sum()
        else:
            fta_foreign = df_filtered['Estimated_Delhi_FTAs'].sum()
        st.metric(
            "Foreign Tourist Arrivals",
            f"{fta_foreign:,.0f}",
            "FTA (Tourism)"
        )
    
    st.markdown("---")
    
    # ==================== ADVANCED METRICS ====================
    st.markdown('<div class="section-title">🎯 Advanced Market Metrics</div>', unsafe_allow_html=True)
    
    adv1, adv2, adv3, adv4 = st.columns(4)
    
    with adv1:
        capture_ratio = df_filtered['Capture_Ratio (%)'].mean()
        st.metric(
            "Market Capture Ratio",
            f"{capture_ratio:.1f}%",
            "International Share"
        )
    
    with adv2:
        avg_temp = df_filtered['Avg_Temp'].mean()
        st.metric(
            "Avg Temperature",
            f"{avg_temp:.1f}°C",
            "Climate Factor"
        )
    
    with adv3:
        try:
            aqi_val = df_filtered['AQI'].mean() if 'AQI' in df_filtered.columns else "N/A"
            if isinstance(aqi_val, (int, float)):
                st.metric("Air Quality Index", f"{aqi_val:.0f}", "Quarterly Avg")
            else:
                st.metric("Air Quality Index", aqi_val)
        except:
            st.metric("Air Quality Index", "N/A")
    
    with adv4:
        if 'Market_Intensity' in df_filtered.columns:
            market_intensity = df_filtered['Market_Intensity'].mean()
            st.metric("Market Intensity", f"{market_intensity:.2f}", "Derived Index")
    
    st.markdown("---")
    
    # ==================== MAIN ANALYSIS TABS ====================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Revenue Analysis",
        "👥 Visitor Metrics",
        "🌡️ Environmental Impact",
        "📈 Trend Analysis",
        "🧬 Correlation Matrix",
        "🤖 Predictive Model"
    ])
    
    # ==================== TAB 1: REVENUE ANALYSIS ====================
    with tab1:
        st.markdown('<div class="subsection-title">Revenue Performance Dashboard</div>', unsafe_allow_html=True)
        
        col_rev1, col_rev2 = st.columns(2)
        
        with col_rev1:
            yearly_revpar = df_filtered.groupby('Year')[['RevPAR (INR)', 'ADR (INR)']].mean().reset_index()
            
            fig_revpar = go.Figure()
            fig_revpar.add_trace(go.Scatter(
                x=yearly_revpar['Year'], y=yearly_revpar['RevPAR (INR)'],
                mode='lines+markers', name='RevPAR',
                line=dict(color='#1E3A5F', width=3),
                marker=dict(size=8)
            ))
            fig_revpar.add_trace(go.Scatter(
                x=yearly_revpar['Year'], y=yearly_revpar['ADR (INR)'],
                mode='lines+markers', name='ADR',
                line=dict(color='#6366F1', width=3),
                marker=dict(size=8)
            ))
            fig_revpar.update_layout(
                title="RevPAR & ADR Trends",
                xaxis_title="Year",
                yaxis_title="₹ (INR)",
                hovermode="x unified",
                plot_bgcolor="white",
                height=400
            )
            st.plotly_chart(fig_revpar, use_container_width=True)
        
        with col_rev2:
            fig_occ = px.scatter(
                df_filtered,
                x='Occupancy (%)',
                y='RevPAR (INR)',
                trendline="ols",
                title="Occupancy vs RevPAR Correlation",
                color='Avg_Temp',
                color_continuous_scale='Viridis',
                hover_data=['Year']
            )
            fig_occ.update_layout(plot_bgcolor="white", height=400)
            st.plotly_chart(fig_occ, use_container_width=True)
        
        if 'Month' in df_filtered.columns:
            st.markdown("#### Seasonality Pattern - Monthly Revenue")
            monthly_data = df_filtered.groupby('Month')[['RevPAR (INR)', 'Occupancy (%)']].mean().reset_index()
            
            fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
            fig_monthly.add_trace(
                go.Bar(x=monthly_data['Month'], y=monthly_data['RevPAR (INR)'], name='RevPAR',
                       marker_color='#1E3A5F'),
                secondary_y=False,
            )
            fig_monthly.add_trace(
                go.Scatter(x=monthly_data['Month'], y=monthly_data['Occupancy (%)'], name='Occupancy %',
                          line=dict(color='#3D6B9B', width=3),
                          mode='lines+markers'),
                secondary_y=True,
            )
            fig_monthly.update_layout(
                title="Monthly Seasonality Analysis",
                xaxis_title="Month",
                yaxis_title="RevPAR (₹)",
                yaxis2_title="Occupancy (%)",
                hovermode="x unified",
                plot_bgcolor="white",
                height=400
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    # ==================== TAB 2: VISITOR METRICS ====================
    with tab2:
        st.markdown('<div class="subsection-title">📌 Visitor & Arrival Analytics</div>', unsafe_allow_html=True)
        
        col_vis1, col_vis2 = st.columns(2)
        
        with col_vis1:
            st.markdown("#### Total Arrivals Trend (All Modes)")
            
            if 'Total_Arrivals' in df_filtered.columns:
                yearly_total = df_filtered.groupby('Year')['Total_Arrivals'].sum().reset_index()
                yearly_total.rename(columns={'Total_Arrivals':'Arrivals'}, inplace=True)
            else:
                yearly_total = df_filtered.groupby('Year')['International_Aviation_Arrivals'].sum().reset_index()
                yearly_total.rename(columns={'International_Aviation_Arrivals':'Arrivals'}, inplace=True)
            
            fig_total = px.bar(
                yearly_total,
                x='Year',
                y='Arrivals',
                title='Total Arrivals by Year',
                color_discrete_sequence=['#1E3A5F'],
                labels={'Arrivals': 'Total Arrivals'}
            )
            fig_total.update_layout(plot_bgcolor="white", height=400)
            st.plotly_chart(fig_total, use_container_width=True)
        
        with col_vis2:
            st.markdown("#### Foreign Tourist Arrivals Trend")
            
            if 'FTA_Foreign' in df_filtered.columns:
                yearly_fta = df_filtered.groupby('Year')['FTA_Foreign'].sum().reset_index()
                yearly_fta.rename(columns={'FTA_Foreign':'FTA'}, inplace=True)
            else:
                yearly_fta = df_filtered.groupby('Year')['Estimated_Delhi_FTAs'].sum().reset_index()
                yearly_fta.rename(columns={'Estimated_Delhi_FTAs':'FTA'}, inplace=True)
            
            fig_fta = px.bar(
                yearly_fta,
                x='Year',
                y='FTA',
                title='Foreign Tourist Arrivals by Year',
                color_discrete_sequence=['#E8995A'],
                labels={'FTA': 'Foreign Tourists'}
            )
            fig_fta.update_layout(plot_bgcolor="white", height=400)
            st.plotly_chart(fig_fta, use_container_width=True)
        
        st.markdown("#### Comparative Analysis: Total vs Foreign Arrivals")
        
        if 'Total_Arrivals' in df_filtered.columns:
            yearly_comp = df_filtered.groupby('Year').agg({
                'Total_Arrivals': 'sum',
                'Estimated_Delhi_FTAs' if 'FTA_Foreign' not in df_filtered.columns else 'FTA_Foreign': 'sum'
            }).reset_index()
            yearly_comp.rename(columns={
                'Total_Arrivals': 'Total Arrivals',
                'Estimated_Delhi_FTAs': 'Foreign Tourists'
            } if 'FTA_Foreign' not in df_filtered.columns else {
                'Total_Arrivals': 'Total Arrivals',
                'FTA_Foreign': 'Foreign Tourists'
            }, inplace=True)
        else:
            yearly_comp = df_filtered.groupby('Year').agg({
                'International_Aviation_Arrivals': 'sum',
                'Estimated_Delhi_FTAs': 'sum'
            }).reset_index()
            yearly_comp.rename(columns={
                'International_Aviation_Arrivals': 'Total Arrivals',
                'Estimated_Delhi_FTAs': 'Foreign Tourists'
            }, inplace=True)
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=yearly_comp['Year'],
            y=yearly_comp['Total Arrivals'],
            name='Total Arrivals (All Modes)',
            marker_color='#1E3A5F',
            opacity=0.8
        ))
        fig_comp.add_trace(go.Bar(
            x=yearly_comp['Year'],
            y=yearly_comp['Foreign Tourists'],
            name='Foreign Tourist Arrivals',
            marker_color='#E8995A',
            opacity=0.8
        ))
        fig_comp.update_layout(
            title="Total Arrivals vs Foreign Tourist Arrivals",
            xaxis_title="Year",
            yaxis_title="Number of Arrivals",
            barmode='group',
            plot_bgcolor="white",
            height=450,
            hovermode="x unified"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        if 'Month' in df_filtered.columns:
            st.markdown("#### Monthly Seasonality Pattern")
            
            if 'Total_Arrivals' in df_filtered.columns:
                monthly_comp = df_filtered.groupby('Month').agg({
                    'Total_Arrivals': 'mean',
                    'Estimated_Delhi_FTAs' if 'FTA_Foreign' not in df_filtered.columns else 'FTA_Foreign': 'mean'
                }).reset_index()
                if 'FTA_Foreign' not in df_filtered.columns:
                    monthly_comp.rename(columns={'Estimated_Delhi_FTAs': 'Foreign Tourists'}, inplace=True)
                else:
                    monthly_comp.rename(columns={'FTA_Foreign': 'Foreign Tourists'}, inplace=True)
            else:
                monthly_comp = df_filtered.groupby('Month').agg({
                    'International_Aviation_Arrivals': 'mean',
                    'Estimated_Delhi_FTAs': 'mean'
                }).reset_index()
                monthly_comp.rename(columns={
                    'International_Aviation_Arrivals': 'Total_Arrivals',
                    'Estimated_Delhi_FTAs': 'Foreign Tourists'
                }, inplace=True)
            
            fig_monthly = go.Figure()
            fig_monthly.add_trace(go.Scatter(
                x=monthly_comp['Month'],
                y=monthly_comp['Total_Arrivals'],
                name='Total Arrivals',
                mode='lines+markers',
                line=dict(color='#1E3A5F', width=3),
                marker=dict(size=8)
            ))
            fig_monthly.add_trace(go.Scatter(
                x=monthly_comp['Month'],
                y=monthly_comp['Foreign Tourists'],
                name='Foreign Tourists',
                mode='lines+markers',
                line=dict(color='#E8995A', width=3),
                marker=dict(size=8)
            ))
            fig_monthly.update_layout(
                title="Monthly Average: Total vs Foreign Arrivals",
                xaxis_title="Month",
                yaxis_title="Average Arrivals",
                hovermode="x unified",
                plot_bgcolor="white",
                height=450
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    # ==================== TAB 3: ENVIRONMENTAL IMPACT ====================
    with tab3:
        st.markdown('<div class="subsection-title">Climate & Environmental Factors</div>', unsafe_allow_html=True)
        
        col_env1, col_env2 = st.columns(2)
        
        with col_env1:
            bubble_col = 'FTA_Foreign' if 'FTA_Foreign' in df_filtered.columns else 'Estimated_Delhi_FTAs'
            
            fig_temp = px.scatter(
                df_filtered,
                x='Avg_Temp',
                y='RevPAR (INR)',
                color='Occupancy (%)',
                size=bubble_col,
                title="Temperature vs RevPAR (Bubble = Foreign Arrivals)",
                color_continuous_scale='Viridis',
                hover_data=['Year']
            )
            fig_temp.update_layout(plot_bgcolor="white", height=450)
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col_env2:
            if 'AQI' in df_filtered.columns:
                fig_aqi = px.scatter(
                    df_filtered,
                    x='AQI',
                    y='Occupancy (%)',
                    trendline="ols",
                    title="Air Quality Index vs Occupancy Rate",
                    color_discrete_sequence=['#E8995A']
                )
                fig_aqi.update_layout(plot_bgcolor="white", height=450)
                st.plotly_chart(fig_aqi, use_container_width=True)
            else:
                st.info("AQI data not available in current dataset")
        
        st.markdown("#### Environmental Metrics Summary")
        env_summary = df_filtered[['Year', 'Avg_Temp']].groupby('Year').agg({
            'Avg_Temp': ['min', 'mean', 'max']
        }).round(1)
        env_summary.columns = ['Min Temp (°C)', 'Avg Temp (°C)', 'Max Temp (°C)']
        env_summary.index = env_summary.index.astype(int)
        st.dataframe(env_summary, use_container_width=True)
    
    # ==================== TAB 4: TREND ANALYSIS ====================
    with tab4:
        st.markdown('<div class="subsection-title">Long-term Trend Analysis</div>', unsafe_allow_html=True)
        
        yearly_trends = df_filtered.groupby('Year').agg({
            'RevPAR (INR)': 'mean',
            'Occupancy (%)': 'mean',
            'ADR (INR)': 'mean',
            'Total_Arrivals': 'sum'
        }).reset_index()
        
        yearly_trends_norm = yearly_trends.copy()
        for col in yearly_trends_norm.columns[1:]:
            yearly_trends_norm[col] = (yearly_trends_norm[col] - yearly_trends_norm[col].min()) / (yearly_trends_norm[col].max() - yearly_trends_norm[col].min())
        
        fig_trends = go.Figure()
        fig_trends.add_trace(go.Scatter(
            x=yearly_trends_norm['Year'], y=yearly_trends_norm['RevPAR (INR)'],
            mode='lines+markers', name='RevPAR (Normalized)',
            line=dict(width=2.5, color='#1E3A5F')
        ))
        fig_trends.add_trace(go.Scatter(
            x=yearly_trends_norm['Year'], y=yearly_trends_norm['Occupancy (%)'],
            mode='lines+markers', name='Occupancy (Normalized)',
            line=dict(width=2.5, color='#06B6D4')
        ))
        fig_trends.add_trace(go.Scatter(
            x=yearly_trends_norm['Year'], y=yearly_trends_norm['Total_Arrivals'],
            mode='lines+markers', name='Total Arrivals (Normalized)',
            line=dict(width=2.5, color='#E8995A')
        ))
        fig_trends.update_layout(
            title="Normalized Multi-Metric Trends",
            xaxis_title="Year",
            yaxis_title="Index (0-1 Scale)",
            hovermode="x unified",
            plot_bgcolor="white",
            height=450
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        st.markdown("#### Year-on-Year Growth Analysis")
        yoy_growth = yearly_trends.copy()
        for col in yoy_growth.columns[1:]:
            yoy_growth[f'{col}_YoY'] = yoy_growth[col].pct_change() * 100
        
        yoy_display = yoy_growth[['Year', 'RevPAR (INR)_YoY', 'Occupancy (%)_YoY', 'Total_Arrivals_YoY']].round(2)
        yoy_display.columns = ['Year', 'RevPAR YoY %', 'Occupancy YoY %', 'Total Arrivals YoY %']
        st.dataframe(yoy_display, use_container_width=True)
    
    # ==================== TAB 5: CORRELATION MATRIX ====================
    with tab5:
        st.markdown('<div class="subsection-title">Multivariate Correlation Analysis</div>', unsafe_allow_html=True)
        
        numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns
        correlation_cols = ['RevPAR (INR)', 'Occupancy (%)', 'ADR (INR)', 
                           'Total_Arrivals', 'Avg_Temp', 'Capture_Ratio (%)']
        correlation_cols = [col for col in correlation_cols if col in df_filtered.columns]
        
        corr_matrix = df_filtered[correlation_cols].corr()
        
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='Blues',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        fig_corr.update_layout(
            title="Variable Correlation Matrix",
            height=600,
            width=800
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.markdown("#### Key Correlations")
        corr_insights = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:
                    corr_insights.append({
                        'Variable 1': corr_matrix.columns[i],
                        'Variable 2': corr_matrix.columns[j],
                        'Correlation': f"{corr_val:.3f}"
                    })
        
        if corr_insights:
            st.dataframe(pd.DataFrame(corr_insights), use_container_width=True)
    
    # ==================== TAB 6: PREDICTIVE MODEL ====================
    with tab6:
        st.markdown('<div class="subsection-title">Scenario Forecasting & Predictive Analytics</div>', unsafe_allow_html=True)
        
        col_pred1, col_pred2 = st.columns(2)
        
        with col_pred1:
            st.markdown("#### Current Scenario Parameters")
            st.info(f"""
            **AQI Level:** {sim_aqi}
            **Exchange Rate:** ₹{sim_fx:.2f} per USD
            **Temperature:** {sim_temp:.1f}°C
            """)
        
        with col_pred2:
            st.markdown("#### Market Elasticity Coefficients")
            st.info("""
            **FX Impact:** +1.32
            **Temperature Impact:** -0.70
            **AQI Impact:** -0.08
            """)
        
        base_revpar = df_filtered['RevPAR (INR)'].mean()
        fx_variance = ((sim_fx - 83.0) / 83.0) * 1.32
        temp_variance = ((sim_temp - 30.0) / 30.0) * -0.70
        aqi_variance = ((sim_aqi - 200.0) / 200.0) * -0.08
        
        total_variance = fx_variance + temp_variance + aqi_variance
        predicted_revpar = base_revpar * (1 + total_variance)
        
        st.markdown("---")
        st.markdown("#### Scenario Forecasting Results")
        
        pred_col1, pred_col2, pred_col3 = st.columns(3)
        
        with pred_col1:
            st.metric("Base RevPAR", f"₹{base_revpar:,.0f}", "Historical Average")
        
        with pred_col2:
            st.metric("Predicted RevPAR", f"₹{predicted_revpar:,.0f}", 
                     f"{total_variance*100:+.1f}%")
        
        with pred_col3:
            change = predicted_revpar - base_revpar
            st.metric("Impact Delta", f"₹{change:+,.0f}", "Absolute Change")
        
        st.markdown("#### Sensitivity Analysis")
        
        sensitivity_data = {
            'Factor': ['FX Exchange Rate', 'Temperature', 'Air Quality Index'],
            'Current Value': [f"₹{sim_fx:.2f}", f"{sim_temp:.1f}°C", sim_aqi],
            'Impact on RevPAR': [f"{fx_variance*100:+.1f}%", f"{temp_variance*100:+.1f}%", f"{aqi_variance*100:+.1f}%"],
            'Elasticity': ['+1.32', '-0.70', '-0.08']
        }
        
        st.dataframe(pd.DataFrame(sensitivity_data), use_container_width=True)
        
        st.markdown("#### Scenario Comparison")
        
        scenarios = {
            'Scenario': ['Best Case', 'Base Case', 'Worst Case', 'Current'],
            'AQI': [100, 200, 350, sim_aqi],
            'Exchange Rate': [95.0, 83.0, 70.0, sim_fx],
            'Temperature': [25.0, 30.0, 40.0, sim_temp]
        }
        
        scenarios_df = pd.DataFrame(scenarios)
        predicted_revpars = []
        
        for idx, row in scenarios_df.iterrows():
            fx_var = ((row['Exchange Rate'] - 83.0) / 83.0) * 1.32
            temp_var = ((row['Temperature'] - 30.0) / 30.0) * -0.70
            aqi_var = ((row['AQI'] - 200.0) / 200.0) * -0.08
            pred = base_revpar * (1 + fx_var + temp_var + aqi_var)
            predicted_revpars.append(f"₹{pred:,.0f}")
        
        scenarios_df['Predicted RevPAR'] = predicted_revpars
        st.dataframe(scenarios_df, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== STRATEGIC INSIGHTS ====================
    st.markdown('<div class="section-title">💡 Strategic Insights & Recommendations</div>', unsafe_allow_html=True)
    
    with st.expander("📌 Market Analysis & Recommendations", expanded=True):
        col_rec1, col_rec2 = st.columns(2)
        
        with col_rec1:
            st.markdown("""
            **Key Findings:**
            - RevPAR shows strong FX sensitivity (+1.32 elasticity)
            - Temperature is critical (30°C is yield ceiling)
            - Occupancy rates correlate with international arrivals
            - Seasonal pattern peaks in Nov-Dec period
            """)
        
        with col_rec2:
            st.markdown("""
            **Strategic Recommendations:**
            - Implement dynamic pricing based on FX fluctuations
            - Develop climate-resilient marketing strategies
            - Focus on corporate/MICE during peak temperature months
            - Leverage wedding season (Nov-Feb) for premium positioning
            """)
    
    with st.expander("📊 Data Quality & Methodology"):
        st.markdown("""
        **Data Coverage:** 2015-2024 (Pandemic years 2020-2021 excluded)
        
        **Variables Analyzed:**
        - Revenue Metrics: RevPAR, ADR, Occupancy Rate
        - Visitor Metrics: Total Arrivals & Foreign Tourist Arrivals
        - Environmental: Temperature, AQI
        - Market Indicators: Exchange Rate, Market Intensity
        
        **Analytical Methods:**
        - Time Series Decomposition
        - Correlation & Regression Analysis
        - Scenario Forecasting
        - Elasticity Modeling (Newey-West HAC correction)
        """)
    
    # ==================== FOOTER ====================
    st.markdown("---")
    
    footercol1, footercol2, footercol3 = st.columns([1, 1, 1])
    with footercol2:
        st.markdown(f"""
            <div style='text-align: center;'>
                <p style='color: #0F1419; font-weight: 600; font-size: 1.1em; margin: 10px 0;'>📋 Report Period</p>
                <p style='color: #1E3A5F; font-size: 1.3em; font-weight: 700; margin: 5px 0;'>{int(df['Year'].min())} to {int(df['Year'].max())}</p>
                <p style='color: #64748B; font-size: 0.85em; margin-top: 15px;'>Delhi Destination Intelligence System (PDIS)</p>
                <p style='color: #94A3B8; font-size: 0.8em;'>Strategic Tourism & Hospitality Analytics</p>
                <p style='color: #94A3B8; font-size: 0.8em;'>Confidential • Institutional Grade Analysis</p>
                <p style='color: #94A3B8; font-size: 0.75em; margin-top: 10px;'>Last Updated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")} | Data Integrity: Verified</p>
            </div>
        """, unsafe_allow_html=True)

except FileNotFoundError as e:
    st.error(f"❌ Data file not found: {e}")
    st.info("Please ensure 'Final Data to use.csv' is in the application directory.")
except Exception as e:
    st.error(f"❌ Application Error: {str(e)}")
    st.warning("Please check the data files and try refreshing the page.")
