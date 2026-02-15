import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
import time
from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="🐦 Twitter Sentiment Analysis",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="auto"
)

# ========== MONGODB CONNECTION (SHARED) ==========
@st.cache_resource
def get_mongo_client():
    """Get MongoDB client connection - shared by both views."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[MONGO_DB][MONGO_COLLECTION]

collection = get_mongo_client()

# ========== SHARED DATA FETCHING ==========


@st.cache_data(ttl=10)
def fetch_dashboard_data(time_filter, sentiments, limit=5000):
    """
    Fetch tweet data from MongoDB - shared by both Desktop and Mobile views.
    
    Args:
        time_filter (datetime): Filter tweets after this time
        sentiments (list): List of sentiment types to include
        limit (int): Maximum number of tweets to fetch
        
    Returns:
        pd.DataFrame: Tweet data
    """
    query = {
        "processing_timestamp": {"$gte": time_filter},
        "sentiment": {"$in": sentiments}
    }
    tweets = list(collection.find(query).sort("processing_timestamp", -1).limit(limit))
    return pd.DataFrame(tweets)

# ========== VIEW SWITCHER COMPONENT ==========
def render_view_switcher():
    """
    Render the view mode toggle - allows users to switch between Desktop and Mobile views.
    Desktop view is the DEFAULT.
    """
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 📊 Dashboard View")
        view = st.radio(
            "Select your preferred view:",
            options=['desktop', 'mobile'],
            format_func=lambda x: '🖥️ Desktop View (Default)' if x == 'desktop' else '📱 Mobile View',
            horizontal=True,
            index=0,  # Desktop is default (index 0)
            key='view_mode',
            help="Desktop view: Optimized for large screens with side-by-side layouts\nMobile view: Optimized for phones with vertical stacking and card-based display"
        )
    st.markdown("---")
    return view

# ========== MOBILE VIEW SPECIFIC CSS ==========
def apply_mobile_css():
    """Apply custom CSS styles for Mobile View mode with comprehensive overflow prevention."""
    st.markdown("""
        <style>
        /* ===== CRITICAL OVERFLOW PREVENTION ===== */
        
        /* Root level - prevent any horizontal scroll */
        html, body {
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }
        
        /* Mobile View Container - Foundation for overflow prevention */
        .mobile-view {
            max-width: 100vw !important;
            overflow-x: hidden !important;
            padding: 0 1rem !important;
            box-sizing: border-box !important;
            width: 100% !important;
        }
        
        /* Ensure all children respect viewport width */
        .mobile-view * {
            box-sizing: border-box !important;
            max-width: 100% !important;
        }
        
        /* Fix Streamlit container overflow */
        .mobile-view .stApp {
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }
        
        .mobile-view .main {
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }
        
        .mobile-view .stAppViewContainer {
            overflow-x: hidden !important;
        }
        
        .mobile-view [data-testid="stAppViewContainer"] {
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }
        
        .mobile-view [data-testid="block-container"] {
            max-width: 100vw !important;
            overflow-x: hidden !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Fix column overflow */
        .mobile-view [data-testid="column"] {
            min-width: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            overflow-x: hidden !important;
        }
        
        /* Fix row widget margins that cause overflow */
        .mobile-view .row-widget {
            margin-left: 0 !important;
            margin-right: 0 !important;
            max-width: 100% !important;
            flex-wrap: wrap !important;
        }
        
        /* ===== TEXT & CONTENT OVERFLOW PREVENTION ===== */
        
        /* Text overflow handling */
        .mobile-view p,
        .mobile-view div,
        .mobile-view span,
        .mobile-view label,
        .mobile-view li {
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            word-break: break-word !important;
            max-width: 100% !important;
            font-size: 16px;
            line-height: 1.6;
        }
        
        /* Code and pre blocks */
        .mobile-view pre,
        .mobile-view code {
            max-width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            font-size: 0.85rem !important;
        }
        
        /* Links don't overflow */
        .mobile-view a {
            word-break: break-all !important;
            max-width: 100% !important;
        }
        
        /* ===== IMAGE & MEDIA FIXES ===== */
        
        .mobile-view img {
            max-width: 100% !important;
            height: auto !important;
            display: block !important;
        }
        
        /* Matplotlib/Pyplot figures */
        .mobile-view .stPlotlyChart,
        .mobile-view .stPyplot {
            max-width: 100% !important;
            width: 100% !important;
            overflow-x: hidden !important;
        }
        
        /* Plotly chart container */
        .mobile-view .js-plotly-plot {
            max-width: 100% !important;
            width: 100% !important;
        }
        
        .mobile-view .plotly {
            max-width: 100% !important;
            width: 100% !important;
        }
        
        /* ===== TABLE & DATAFRAME FIXES ===== */
        
        /* Dataframe styling - internal scroll only */
        .mobile-view .stDataFrame {
            max-width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        
        .mobile-view .stDataFrame table {
            min-width: 100%;
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem !important;
        }
        
        .mobile-view .stDataFrame thead th,
        .mobile-view .stDataFrame tbody td {
            padding: 0.5rem !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .mobile-view table {
            display: block !important;
            max-width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        
        /* ===== METRIC CARDS ===== */
        
        .mobile-metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            text-align: center;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
            overflow: hidden;
        }
        
        .mobile-metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            margin: 0.5rem 0;
            color: white;
            word-break: break-word;
        }
        
        .mobile-metric-label {
            font-size: 0.8rem;
            color: #ddd;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            word-break: break-word;
        }
        
        /* ===== TWEET CARDS ===== */
        
        .mobile-tweet-card {
            background: #f8f9fa;
            border-left: 4px solid;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.75rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
            overflow: hidden;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        .mobile-tweet-card.positive {
            border-color: #00CC96;
        }
        
        .mobile-tweet-card.negative {
            border-color: #EF553B;
        }
        
        .mobile-tweet-card.neutral {
            border-color: #636EFA;
        }
        
        .mobile-tweet-text {
            font-size: 15px;
            line-height: 1.5;
            margin: 0.5rem 0;
            color: #333;
            word-wrap: break-word;
            overflow-wrap: break-word;
            word-break: break-word;
        }
        
        .mobile-tweet-meta {
            font-size: 0.8rem;
            color: #666;
            margin-top: 0.5rem;
            word-break: break-word;
        }
        
        .mobile-sentiment-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 16px;
            font-size: 0.78rem;
            font-weight: bold;
            margin-right: 0.25rem;
            white-space: normal;
            word-break: break-word;
        }
        
        .mobile-sentiment-badge.positive {
            background-color: #00CC96;
            color: white;
        }
        
        .mobile-sentiment-badge.negative {
            background-color: #EF553B;
            color: white;
        }
        
        .mobile-sentiment-badge.neutral {
            background-color: #636EFA;
            color: white;
        }
        
        /* ===== INPUT CONTROLS ===== */
        
        /* Touch-friendly buttons */
        .stButton > button {
            min-height: 44px;
            font-size: 16px;
            padding: 12px 16px;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }
        
        /* Radio buttons - stack vertically on mobile */
        .stRadio > div {
            flex-direction: column !important;
            gap: 0.5rem;
        }
        
        .stRadio [role="radiogroup"] {
            max-width: 100% !important;
            overflow-x: hidden !important;
        }
        
        /* Selectbox and inputs */
        .stSelectbox,
        .stTextInput,
        .stNumberInput,
        .stTextArea {
            width: 100% !important;
            max-width: 100% !important;
        }
        
        .stSelectbox select,
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        
        /* Slider fixes */
        .stSlider {
            padding: 0 !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Expanders */
        .stExpander {
            max-width: 100% !important;
        }
        
        .streamlit-expanderHeader {
            font-size: 0.95rem !important;
        }
        
        /* ===== SECTION HEADERS ===== */
        
        .mobile-section-header {
            font-size: 1.3rem;
            font-weight: bold;
            margin: 1rem 0 0.75rem 0;
            color: #1DA1F2;
            word-break: break-word;
            width: 100%;
            max-width: 100%;
        }
        
        /* ===== OVERRIDE ANY FIXED WIDTHS ===== */
        
        .mobile-view [style*="width: 500px"],
        .mobile-view [style*="width: 600px"],
        .mobile-view [style*="width: 800px"],
        .mobile-view [style*="width: 1000px"],
        .mobile-view [style*="width: 1200px"] {
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* ===== HORIZONTAL DIVIDERS ===== */
        
        .mobile-view hr {
            width: 100% !important;
            margin: 1rem 0 !important;
        }
        
        /* ===== WORD CLOUD CONTAINER ===== */
        
        .mobile-wordcloud-container {
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        
        .mobile-wordcloud-container img {
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
        }
        
        /* ===== END OVERFLOW PREVENTION ===== */
        </style>
    """, unsafe_allow_html=True)

# ========== DESKTOP VIEW FUNCTION ==========
def render_desktop_view(df, time_range, sentiment_filter, refresh_rate, auto_refresh, show_wordcloud):
    """
    Render the Desktop View - optimized for large screens.
    Preserves the original multi-column layout with side-by-side visualizations.
    """
    st.markdown('<h1 style="color: #1DA1F2; text-align: center;">🐦 Twitter Sentiment Analysis - Desktop View</h1>', unsafe_allow_html=True)
    st.info("💡 **Tip**: Switch to Mobile View for a phone-optimized experience with card-based tweet display.")
    st.markdown("---")
    
    if len(df) > 0:
        # ========== KEY METRICS (Desktop: 5-column layout) ==========
        st.subheader("📊 Key Metrics")
        
        total_tweets = len(df)
        positive_count = (df['sentiment'] == 'positive').sum()
        positive_pct = positive_count / total_tweets * 100
        negative_count = (df['sentiment'] == 'negative').sum()
        negative_pct = negative_count / total_tweets * 100
        neutral_count = (df['sentiment'] == 'neutral').sum()
        neutral_pct = neutral_count / total_tweets * 100
        avg_score = df['sentiment_score'].astype(float).mean()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📨 Total Tweets", f"{total_tweets:,}")
        with col2:
            st.metric("😊 Positive", f"{positive_pct:.1f}%", delta=f"{positive_count}", delta_color="normal")
        with col3:
            st.metric("😠 Negative", f"{negative_pct:.1f}%", delta=f"{negative_count}", delta_color="inverse")
        with col4:
            st.metric("😐 Neutral", f"{neutral_pct:.1f}%", delta=f"{neutral_count}", delta_color="off")
        with col5:
            st.metric("📈 Avg Score", f"{avg_score:.3f}")
        
        st.markdown("---")
        
        # ========== TABS FOR DIFFERENT VIEWS ==========
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⏱️ Temporal", "🏷️ Hashtags", "📝 Details"])
        
        with tab1:
            # Side-by-side charts (Desktop layout)
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sentiment Distribution")
                sentiment_counts = df['sentiment'].value_counts()
                fig_pie = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    color=sentiment_counts.index,
                    color_discrete_map={
                        'positive': '#00CC96',
                        'negative': '#EF553B',
                        'neutral': '#636EFA'
                    },
                    hole=0.4
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
                fig_pie.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_pie, use_container_width=True, key="desktop_pie")
            
            with col2:
                st.subheader("Score Distribution")
                fig_hist = px.histogram(
                    df,
                    x='sentiment_score',
                    color='sentiment',
                    nbins=50,
                    color_discrete_map={
                        'positive': '#00CC96',
                        'negative': '#EF553B',
                        'neutral': '#636EFA'
                    }
                )
                fig_hist.update_layout(height=400, bargap=0.1)
                st.plotly_chart(fig_hist, use_container_width=True, key="desktop_hist")
        
        with tab2:
            st.subheader("Temporal Evolution")
            
            df['processing_timestamp'] = pd.to_datetime(df['processing_timestamp'])
            df_sorted = df.sort_values('processing_timestamp')
            
            # Line chart by sentiment
            df_time = df_sorted.set_index('processing_timestamp')
            df_resampled = df_time.groupby([pd.Grouper(freq='5T'), 'sentiment']).size().reset_index(name='count')
            
            fig_line = px.line(
                df_resampled,
                x='processing_timestamp',
                y='count',
                color='sentiment',
                color_discrete_map={
                    'positive': '#00CC96',
                    'negative': '#EF553B',
                    'neutral': '#636EFA'
                },
                title="Tweets by sentiment (5-minute intervals)"
            )
            st.plotly_chart(fig_line, use_container_width=True, key="desktop_line")
            
            # Total volume
            df_volume = df_sorted.set_index('processing_timestamp').resample('5T').size()
            fig_area = px.area(
                x=df_volume.index,
                y=df_volume.values,
                title="Total tweet volume"
            )
            st.plotly_chart(fig_area, use_container_width=True, key="desktop_area")
        
        with tab3:
            st.subheader("Hashtag Analysis")
            
            all_hashtags = []
            for hashtags in df['hashtags'].dropna():
                if isinstance(hashtags, list):
                    all_hashtags.extend([h.lower() for h in hashtags])
            
            if all_hashtags:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Top 15 Hashtags")
                    hashtag_counts = pd.Series(all_hashtags).value_counts().head(15)
                    fig_bar = px.bar(
                        x=hashtag_counts.values,
                        y=hashtag_counts.index,
                        orientation='h',
                        labels={'x': 'Count', 'y': 'Hashtag'},
                        color=hashtag_counts.values,
                        color_continuous_scale='viridis'
                    )
                    fig_bar.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_bar, use_container_width=True, key="desktop_hashtag_bar")
                
                with col2:
                    if show_wordcloud:
                        st.markdown("#### Word Cloud")
                        try:
                            font_path = None
                            for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                                     '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                                     '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf']:
                                if os.path.exists(f):
                                    font_path = f
                                    break
                            
                            if font_path:
                                wordcloud = WordCloud(
                                    width=800,
                                    height=400,
                                    background_color='white',
                                    colormap='viridis',
                                    font_path=font_path
                                ).generate(' '.join(all_hashtags))
                                
                                fig, ax = plt.subplots(figsize=(10, 5))
                                ax.imshow(wordcloud, interpolation='bilinear')
                                ax.axis('off')
                                st.pyplot(fig, use_container_width=True)
                                plt.close()
                            else:
                                st.warning("Word cloud requires fonts.")
                        except Exception as e:
                            st.warning(f"Could not generate word cloud: {str(e)}")
                    else:
                        st.info("Word cloud disabled. Enable in sidebar.")
            else:
                st.info("No hashtags found")
        
        with tab4:
            st.subheader("Detailed Tweets")
            
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox("Sort by", ["Most recent", "Most positive", "Most negative"], key="desktop_sort")
            with col2:
                show_count = st.slider("Tweets to display", 10, 100, 20, key="desktop_count")
            
            if sort_by == "Most recent":
                df_display = df.sort_values('processing_timestamp', ascending=False)
            elif sort_by == "Most positive":
                df_display = df.sort_values('sentiment_score', ascending=False)
            else:
                df_display = df.sort_values('sentiment_score', ascending=True)
            
            st.dataframe(
                df_display[['text', 'sentiment', 'sentiment_score', 'hashtags', 'processing_timestamp']]
                .head(show_count)
                .style.background_gradient(subset=['sentiment_score'], cmap='RdYlGn', vmin=-1, vmax=1),
                use_container_width=True,
                height=400
            )
        
        # Advanced Statistics (Expander)
        with st.expander("📈 Advanced Statistics", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Score Distribution**")
                st.write(df['sentiment_score'].astype(float).describe())
            
            with col2:
                st.markdown("**Sentiment Breakdown**")
                st.write(df['sentiment'].value_counts())
            
            with col3:
                st.markdown("**Most Frequent Mentions**")
                all_mentions = []
                for mentions in df['mentions'].dropna():
                    if isinstance(mentions, list):
                        all_mentions.extend(mentions)
                if all_mentions:
                    st.write(pd.Series(all_mentions).value_counts().head(10))
                else:
                    st.info("No mentions")
    
    else:
        st.warning("⚠️ No data available for this period.")
        st.info("Check that the producer and consumer are active.")

# ========== MOBILE VIEW FUNCTION ==========
def render_mobile_view(df, time_range, sentiment_filter, refresh_rate, auto_refresh, show_wordcloud):
    """
    Render the Mobile View - optimized for phones with vertical stacking and card-based layout.
    """
    apply_mobile_css()  # Apply mobile-specific CSS
    
    st.markdown('<div class="mobile-view">', unsafe_allow_html=True)
    st.markdown('<h1 style="color: #1DA1F2; text-align: center; font-size: 1.75rem;">🐦 Twitter Sentiment</h1>', unsafe_allow_html=True)
    st.info("💡 **Mobile View**: Optimized for phones. Switch to Desktop View for side-by-side charts.")
    st.markdown("---")
    
    if len(df) > 0:
        # ========== KEY METRICS (Mobile: 2x2 grid with cards) ==========
        st.markdown('<div class="mobile-section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
        
        total_tweets = len(df)
        positive_count = (df['sentiment'] == 'positive').sum()
        positive_pct = positive_count / total_tweets * 100
        negative_count = (df['sentiment'] == 'negative').sum()
        negative_pct = negative_count / total_tweets * 100
        neutral_count = (df['sentiment'] == 'neutral').sum()
        neutral_pct = neutral_count / total_tweets * 100
        avg_score = df['sentiment_score'].astype(float).mean()
        
        # Row 1: Total and Avg Score
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="mobile-metric-card">
                    <div class="mobile-metric-label">Total Tweets</div>
                    <div class="mobile-metric-value">{total_tweets:,}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="mobile-metric-card">
                    <div class="mobile-metric-label">Avg Score</div>
                    <div class="mobile-metric-value">{avg_score:.3f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Row 2: Sentiments
        col3, col4, col5 = st.columns(3)
        with col3:
            st.markdown(f"""
                <div class="mobile-metric-card">
                    <div class="mobile-metric-label">😊 Positive</div>
                    <div class="mobile-metric-value">{positive_pct:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="mobile-metric-card">
                    <div class="mobile-metric-label">😠 Negative</div>
                    <div class="mobile-metric-value">{negative_pct:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
                <div class="mobile-metric-card">
                    <div class="mobile-metric-label">😐 Neutral</div>
                    <div class="mobile-metric-value">{neutral_pct:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ========== VISUALIZATIONS (Mobile: Vertical Stacking) ==========
        
        # Sentiment Distribution Pie Chart
        st.markdown('<div class="mobile-section-header">📊 Sentiment Distribution</div>', unsafe_allow_html=True)
        sentiment_counts = df['sentiment'].value_counts()
        fig_pie = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            color=sentiment_counts.index,
            color_discrete_map={
                'positive': '#00CC96',
                'negative': '#EF553B',
                'neutral': '#636EFA'
            },
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
        fig_pie.update_layout(
            height=320,
            width=None,  # Let container control width
            autosize=True,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False, 'responsive': True}, key="mobile_pie")
        
        st.markdown("---")
        
        # Score Distribution Histogram
        st.markdown('<div class="mobile-section-header">📈 Score Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            df,
            x='sentiment_score',
            color='sentiment',
            nbins=25,
            color_discrete_map={
                'positive': '#00CC96',
                'negative': '#EF553B',
                'neutral': '#636EFA'
            }
        )
        fig_hist.update_layout(
            height=280,
            width=None,  # Let container control width
            autosize=True,
            margin=dict(l=10, r=10, t=30, b=40),
            bargap=0.1,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=11)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False, 'responsive': True}, key="mobile_hist")
        
        st.markdown("---")
        
        # Hashtags
        st.markdown('<div class="mobile-section-header">🏷️ Top Hashtags</div>', unsafe_allow_html=True)
        
        all_hashtags = []
        for hashtags in df['hashtags'].dropna():
            if isinstance(hashtags, list):
                all_hashtags.extend([h.lower() for h in hashtags])
        
        if all_hashtags:
            hashtag_counts = pd.Series(all_hashtags).value_counts().head(10)
            fig_bar = px.bar(
                x=hashtag_counts.values,
                y=hashtag_counts.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Hashtag'},
                color=hashtag_counts.values,
                color_continuous_scale='viridis'
            )
            fig_bar.update_layout(
                height=320,
                width=None,  # Let container control width
                autosize=True,
                margin=dict(l=80, r=10, t=20, b=30),
                showlegend=False,
                yaxis={'categoryorder':'total ascending'},
                coloraxis_showscale=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=11)
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False, 'responsive': True}, key="mobile_hashtag")
            
            # Simple list instead of word cloud for mobile
            if not show_wordcloud:
                with st.expander("View top hashtags list"):
                    for i, (tag, count) in enumerate(hashtag_counts.head(10).items(), 1):
                        st.markdown(f"**{i}.** `#{tag}` - {count} tweets")
        else:
            st.info("No hashtags found")
        
        st.markdown("---")
        
        # ========== TWEETS (Mobile: Card-based Display) ==========
        st.markdown('<div class="mobile-section-header">📝 Latest Tweets</div>', unsafe_allow_html=True)
        
        with st.expander("⚙️ Display Options", expanded=False):
            sort_by = st.selectbox(
                "Sort by",
                ["Most recent", "Most positive", "Most negative"],
                key="mobile_sort"
            )
            page_size = st.select_slider(
                "Tweets per page",
                options=[10, 20, 30, 50],
                value=20,
                key="mobile_page_size"
            )
        
        # Apply sorting
        if sort_by == "Most recent":
            df_display = df.sort_values('processing_timestamp', ascending=False)
        elif sort_by == "Most positive":
            df_display = df.sort_values('sentiment_score', ascending=False)
        else:
            df_display = df.sort_values('sentiment_score', ascending=True)
        
        # Pagination
        total_tweets_display = len(df_display)
        total_pages = (total_tweets_display - 1) // page_size + 1
        
        if 'mobile_page' not in st.session_state:
            st.session_state.mobile_page = 1
        
        # Page controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Prev", disabled=(st.session_state.mobile_page <= 1), key="mobile_prev"):
                st.session_state.mobile_page -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 10px;'><b>Page {st.session_state.mobile_page} of {total_pages}</b></div>",
                       unsafe_allow_html=True)
        
        with col3:
            if st.button("Next ➡️", disabled=(st.session_state.mobile_page >= total_pages), key="mobile_next"):
                st.session_state.mobile_page += 1
                st.rerun()
        
        # Calculate slice
        start_idx = (st.session_state.mobile_page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df_display.iloc[start_idx:end_idx]
        
        # Display tweets as cards
        for idx, row in df_page.iterrows():
            sentiment = row['sentiment']
            score = float(row['sentiment_score'])
            text = row['text']
            timestamp = pd.to_datetime(row['processing_timestamp']).strftime('%Y-%m-%d %H:%M')
            
            sentiment_badge_html = f'<span class="mobile-sentiment-badge {sentiment}">{sentiment.upper()}</span>'
            
            card_html = f"""
                <div class="mobile-tweet-card {sentiment}">
                    <div>{sentiment_badge_html} <strong>Score: {score:.3f}</strong></div>
                    <div class="mobile-tweet-text">{text}</div>
                    <div class="mobile-tweet-meta">🕒 {timestamp}</div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.caption(f"Showing {start_idx + 1}-{min(end_idx, total_tweets_display)} of {total_tweets_display} tweets")
        
        st.markdown("---")
        
        # Advanced Stats (Collapsible)
        with st.expander("📈 Advanced Statistics"):
            st.markdown("### Score Distribution")
            st.write(df['sentiment_score'].astype(float).describe())
            
            st.markdown("---")
            
            st.markdown("### Sentiment Breakdown")
            st.dataframe(df['sentiment'].value_counts(), use_container_width=True)
    
    else:
        st.warning("⚠️ No data available for this period.")
        st.info("Check that the producer and consumer are active.")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close mobile-view div

# ========== MAIN APPLICATION ==========
def main():
    """Main application entry point with view switcher."""
    
    # Initialize session state for view mode (Desktop is DEFAULT)
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'desktop'
    
    # ========== SIDEBAR CONFIGURATION (Shared by both views) ==========
    st.sidebar.header("⚙️ Configuration")
    
    with st.sidebar.expander("📅 Time & Refresh Settings", expanded=True):
        time_range = st.selectbox(
            "Analysis Period",
            ["Last hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "All"],
            key="time_range_select"
        )
        
        refresh_rate = st.slider("🔄 Refresh rate (seconds)", 5, 60, 10)
        auto_refresh = st.checkbox("Auto-refresh enabled", value=True)
    
    with st.sidebar.expander("🔍 Advanced Filters", expanded=False):
        sentiment_filter = st.multiselect(
            "Sentiments",
            ["positive", "negative", "neutral"],
            default=["positive", "negative", "neutral"]
        )
        
        show_wordcloud = st.checkbox("Show word cloud", value=True,
                                      help="Disable on slow connections")
        
        data_limit = st.select_slider(
            "Max tweets to load",
            options=[500, 1000, 2500, 5000, 10000],
            value=5000,
            help="Lower values improve performance"
        )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("📱 Dual-view dashboard")
    st.sidebar.caption("🔄 Switch between Desktop & Mobile")
    
    # ========== TIME FILTERS ==========
    time_filters = {
        "Last hour": datetime.now() - timedelta(hours=1),
        "Last 6 hours": datetime.now() - timedelta(hours=6),
        "Last 24 hours": datetime.now() - timedelta(days=1),
        "Last 7 days": datetime.now() - timedelta(days=7),
        "All": datetime(2000, 1, 1)
    }
    
    # ========== RENDER VIEW SWITCHER ==========
    current_view = render_view_switcher()
    
    # ========== FETCH DATA (Shared by both views) ==========
    with st.spinner("🔄 Loading data..."):
        df = fetch_dashboard_data(time_filters[time_range], sentiment_filter, data_limit)
    
    # ========== RENDER APPROPRIATE VIEW ==========
    if current_view == 'desktop':
        render_desktop_view(df, time_range, sentiment_filter, refresh_rate, auto_refresh, show_wordcloud)
    else:
        render_mobile_view(df, time_range, sentiment_filter, refresh_rate, auto_refresh, show_wordcloud)
    
    # ========== FOOTER (Shared) ==========
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"🕐 Last update: {datetime.now().strftime('%H:%M:%S')}")
        total_docs = collection.count_documents({})
        st.caption(f"💾 Database: {total_docs:,} tweets")
    
    with col2:
        st.caption("⚡ Pipeline: Kafka → Spark → MongoDB")
        st.caption(f"👁️ Current View: {current_view.title()}")
    
    # ========== AUTO-REFRESH ==========
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    main()
