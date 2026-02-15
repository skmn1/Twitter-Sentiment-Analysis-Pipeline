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

sys.path.append('..')
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

# Page configuration - Mobile-first approach
st.set_page_config(
    page_title="🐦 Twitter Sentiment",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed by default for mobile
)

# Comprehensive Responsive CSS styling
st.markdown("""
<style>
    /* ========== BASE STYLES ========== */
    :root {
        --primary-color: #1DA1F2;
        --positive-color: #00CC96;
        --negative-color: #EF553B;
        --neutral-color: #636EFA;
    }
    
    /* Main header - responsive sizing */
    .main-header {
        font-size: clamp(1.5rem, 5vw, 3rem);
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1rem;
        padding: 0.5rem;
        line-height: 1.2;
    }
    
    /* Mobile-optimized metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
        min-height: 80px;
    }
    
    /* ========== MOBILE STYLES (320px - 768px) ========== */
    @media only screen and (max-width: 768px) {
        /* Reduce padding on main container */
        .block-container {
            padding: 1rem 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Stack metrics vertically on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* Increase font size for readability */
        .stMarkdown, .stText {
            font-size: 16px !important;
        }
        
        /* Make buttons touch-friendly (44x44px minimum) */
        .stButton button {
            min-height: 44px !important;
            min-width: 44px !important;
            font-size: 16px !important;
            padding: 12px 20px !important;
        }
        
        /* Optimize select boxes for mobile */
        .stSelectbox, .stMultiSelect {
            font-size: 16px !important;
        }
        
        /* Make sliders touch-friendly */
        .stSlider {
            padding: 10px 0 !important;
        }
        
        /* Reduce header sizes on mobile */
        h1 {
            font-size: 1.75rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
        }
        h3 {
            font-size: 1.25rem !important;
        }
        
        /* Mobile-optimized tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px !important;
            font-size: 14px !important;
            white-space: nowrap;
        }
        
        /* Optimize dataframe for mobile */
        .dataframe {
            font-size: 12px !important;
            overflow-x: auto !important;
        }
        
        /* Hide sidebar by default on mobile */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        [data-testid="stSidebar"][aria-expanded="true"] {
            display: block;
            width: 100% !important;
            max-width: 100% !important;
        }
    }
    
    /* ========== SMALL MOBILE (320px - 428px) ========== */
    @media only screen and (max-width: 428px) {
        .main-header {
            font-size: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Compact metric display */
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.875rem !important;
        }
        
        /* Single column layout for very small screens */
        .row-widget.stHorizontalBlock {
            flex-direction: column !important;
        }
        
        /* Optimize charts for small screens */
        .js-plotly-plot {
            min-height: 250px !important;
        }
    }
    
    /* ========== TABLET STYLES (769px - 1024px) ========== */
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding: 2rem 1rem !important;
        }
        
        /* 2-column layout for tablets */
        [data-testid="column"] {
            width: 48% !important;
        }
    }
    
    /* ========== DESKTOP STYLES (1025px+) ========== */
    @media only screen and (min-width: 1025px) {
        .block-container {
            padding: 3rem 1rem !important;
        }
    }
    
    /* ========== LOADING STATES ========== */
    .stSpinner > div {
        border-color: var(--primary-color) !important;
    }
    
    /* ========== TOUCH-FRIENDLY IMPROVEMENTS ========== */
    .stCheckbox {
        min-height: 44px;
    }
    
    /* Improve tap targets */
    a, button, [role="button"] {
        min-height: 44px;
        min-width: 44px;
    }
    
    /* ========== ACCESSIBILITY ========== */
    /* Ensure text contrast */
    .stMarkdown p {
        line-height: 1.6;
    }
    
    /* Focus indicators */
    button:focus, select:focus, input:focus {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px;
    }
</style>
""", unsafe_allow_html=True)

# MongoDB connection with timeout for mobile networks
@st.cache_resource
def get_mongo_client():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[MONGO_DB][MONGO_COLLECTION]

collection = get_mongo_client()

# ========== VIEWPORT DETECTION ==========
# Inject JavaScript to detect viewport width
viewport_script = """
<script>
    // Send viewport width to Streamlit
    const width = window.innerWidth;
    const height = window.innerHeight;
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        data: {width: width, height: height}
    }, '*');
</script>
"""

# Store viewport info in session state (approximation via user agent)
if 'is_mobile' not in st.session_state:
    st.session_state.is_mobile = False  # Default to desktop

# Mobile-optimized header
st.markdown('<h1 class="main-header">🐦 Twitter Sentiment Analysis</h1>', unsafe_allow_html=True)

# Mobile-friendly info banner
st.info("💡 **Tip**: Swipe through tabs to explore different views. Use the sidebar (☰) for filters.")
st.markdown("---")

# ========== RESPONSIVE SIDEBAR CONFIGURATION ==========
st.sidebar.header("⚙️ Configuration")

# Collapsible configuration sections for mobile
with st.sidebar.expander("📅 Time & Refresh Settings", expanded=True):
    time_range = st.selectbox(
        "Analysis Period",
        ["Last hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "All"],
        key="time_range"
    )
    
    refresh_rate = st.slider("🔄 Refresh rate (seconds)", 5, 60, 10)
    auto_refresh = st.checkbox("Auto-refresh enabled", value=True)

# Additional filters
with st.sidebar.expander("🔍 Advanced Filters", expanded=False):
    sentiment_filter = st.multiselect(
        "Sentiments",
        ["positive", "negative", "neutral"],
        default=["positive", "negative", "neutral"]
    )
    
    # Mobile-friendly display options
    show_wordcloud = st.checkbox("Show word cloud", value=True, 
                                  help="Disable on slow connections")
    
    # Data limit for mobile performance
    data_limit = st.select_slider(
        "Max tweets to load",
        options=[500, 1000, 2500, 5000, 10000],
        value=5000,
        help="Lower values improve mobile performance"
    )

st.sidebar.markdown("---")
st.sidebar.caption("📱 Mobile-optimized dashboard")
st.sidebar.caption("🔄 Pull to refresh on mobile")


# Convert period to filter
time_filters = {
    "Last hour": datetime.now() - timedelta(hours=1),
    "Last 6 hours": datetime.now() - timedelta(hours=6),
    "Last 24 hours": datetime.now() - timedelta(days=1),
    "Last 7 days": datetime.now() - timedelta(days=7),
    "All": datetime(2000, 1, 1)
}

# Function to load data with mobile optimization
@st.cache_data(ttl=refresh_rate)
def get_data(time_filter, sentiments, limit=5000):
    """Load tweet data with pagination for mobile performance"""
    query = {
        "processing_timestamp": {"$gte": time_filter},
        "sentiment": {"$in": sentiments}
    }
    tweets = list(collection.find(query).sort("processing_timestamp", -1).limit(limit))
    return pd.DataFrame(tweets)

# Load data with mobile-friendly loading indicator
with st.spinner("🔄 Loading data..."):
    df = get_data(time_filters[time_range], sentiment_filter, data_limit)

if len(df) > 0:
    # ========== RESPONSIVE KEY METRICS ==========
    st.subheader("📊 Key Metrics")
    
    # Calculate metrics
    total_tweets = len(df)
    positive_count = (df['sentiment'] == 'positive').sum()
    positive_pct = positive_count / total_tweets * 100
    negative_count = (df['sentiment'] == 'negative').sum()
    negative_pct = negative_count / total_tweets * 100
    neutral_count = (df['sentiment'] == 'neutral').sum()
    neutral_pct = neutral_count / total_tweets * 100
    avg_score = df['sentiment_score'].astype(float).mean()
    
    # Responsive layout: 2x2 grid on mobile, 5 columns on desktop
    # First row
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📨 Total Tweets", f"{total_tweets:,}")
    with col2:
        st.metric("📈 Avg Score", f"{avg_score:.3f}")
    
    # Second row  
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("😊 Positive", f"{positive_pct:.1f}%", 
                  delta=f"{positive_count}", delta_color="normal")
    with col4:
        st.metric("😠 Negative", f"{negative_pct:.1f}%", 
                  delta=f"{negative_count}", delta_color="inverse")
    with col5:
        st.metric("😐 Neutral", f"{neutral_pct:.1f}%", 
                  delta=f"{neutral_count}", delta_color="off")
    
    st.markdown("---")
    
    # ========== MOBILE-OPTIMIZED TABS ==========
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⏱️ Temporal", "🏷️ Hashtags", "📝 Details"])
    
    with tab1:
        st.subheader("Sentiment Distribution")
        
        # Mobile-responsive layout: stack vertically on mobile
        sentiment_counts = df['sentiment'].value_counts()
        
        # Pie chart with mobile optimizations
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
        
        # Mobile-friendly chart configuration
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont_size=14,  # Larger text for mobile
            marker=dict(line=dict(color='white', width=2))
        )
        
        fig_pie.update_layout(
            height=350,  # Optimized height for mobile
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            # Enable touch interactions
            dragmode=False
        )
        
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")
        
        st.markdown("---")
        
        st.subheader("Score Distribution")
        
        # Histogram with mobile optimizations
        fig_hist = px.histogram(
            df,
            x='sentiment_score',
            color='sentiment',
            nbins=30,  # Reduced bins for mobile clarity
            color_discrete_map={
                'positive': '#00CC96',
                'negative': '#EF553B',
                'neutral': '#636EFA'
            },
            labels={'sentiment_score': 'Sentiment Score', 'count': 'Count'}
        )
        
        fig_hist.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=40),
            bargap=0.1,
            xaxis_title="Sentiment Score",
            yaxis_title="Count",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            ),
            # Touch-friendly
            dragmode=False,
            # Larger fonts for mobile
            font=dict(size=12)
        )
        
        st.plotly_chart(fig_hist, use_container_width=True, key="hist_chart")
    
    with tab2:
        st.subheader("Temporal Evolution")
        
        # Prepare temporal data
        df['processing_timestamp'] = pd.to_datetime(df['processing_timestamp'])
        df_sorted = df.sort_values('processing_timestamp')
        
        # Line chart by sentiment with mobile optimizations
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
            labels={'processing_timestamp': 'Time', 'count': 'Tweets', 'sentiment': 'Sentiment'}
        )
        
        # Mobile-optimized layout
        fig_line.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=40),
            xaxis_title="Time",
            yaxis_title="Tweet Count",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            ),
            hovermode='x unified',  # Better for touch
            dragmode='pan',  # Enable swipe to pan on mobile
            font=dict(size=11)
        )
        
        # Enable touch interactions
        config = {
            'displayModeBar': False,  # Hide toolbar on mobile
            'scrollZoom': False,
            'doubleClick': False
        }
        
        st.plotly_chart(fig_line, use_container_width=True, config=config, key="line_chart")
        
        st.markdown("---")
        
        # Total volume with mobile optimizations
        df_volume = df_sorted.set_index('processing_timestamp').resample('5T').size()
        
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=df_volume.index,
            y=df_volume.values,
            fill='tozeroy',
            fillcolor='rgba(29, 161, 242, 0.3)',
            line=dict(color='#1DA1F2', width=2),
            name='Total Volume'
        ))
        
        fig_area.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=40),
            xaxis_title="Time",
            yaxis_title="Total Tweets",
            showlegend=False,
            hovermode='x',
            dragmode='pan',
            font=dict(size=11)
        )
        
        st.plotly_chart(fig_area, use_container_width=True, config=config, key="area_chart")
        
        # Mobile-friendly info
        st.info("💡 **Tip**: Charts show 5-minute intervals. Swipe horizontally to explore the timeline.")
    
    with tab3:
        st.subheader("Hashtag Analysis")
        
        # Extract all hashtags
        all_hashtags = []
        for hashtags in df['hashtags'].dropna():
            if isinstance(hashtags, list):
                all_hashtags.extend([h.lower() for h in hashtags])
        
        if all_hashtags:
            hashtag_counts = pd.Series(all_hashtags).value_counts().head(15)
            
            # Bar chart with mobile optimization
            st.markdown("#### Top 15 Hashtags")
            fig_bar = px.bar(
                x=hashtag_counts.values,
                y=hashtag_counts.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Hashtag'},
                color=hashtag_counts.values,
                color_continuous_scale='viridis'
            )
            
            fig_bar.update_layout(
                height=400,  # Taller for horizontal bars
                margin=dict(l=20, r=20, t=20, b=40),
                showlegend=False,
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Count",
                yaxis_title="",
                font=dict(size=11),
                coloraxis_showscale=False  # Hide color scale on mobile
            )
            
            st.plotly_chart(fig_bar, use_container_width=True, key="hashtag_bar")
            
            st.markdown("---")
            
            # Word cloud - optional on mobile for performance
            if show_wordcloud:
                st.markdown("#### Hashtag Word Cloud")
                try:
                    # Find available font
                    font_path = None
                    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                             '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                             '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf']:
                        if os.path.exists(f):
                            font_path = f
                            break
                    
                    if font_path:
                        # Mobile-optimized word cloud
                        wordcloud = WordCloud(
                            width=600,  # Smaller for mobile
                            height=300,
                            background_color='white',
                            colormap='viridis',
                            font_path=font_path,
                            max_words=50,  # Limit words for clarity on mobile
                            relative_scaling=0.5,
                            min_font_size=10
                        ).generate(' '.join(all_hashtags))
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig, use_container_width=True)
                        plt.close()
                    else:
                        st.warning("💡 Word cloud requires fonts. Install: `sudo apt-get install fonts-dejavu`")
                except Exception as e:
                    st.warning(f"⚠️ Could not generate word cloud: {str(e)}")
            else:
                st.info("💡 Word cloud disabled for better mobile performance. Enable in sidebar filters.")
                
                # Alternative: show top hashtags as styled list
                st.markdown("##### Top Hashtags")
                for i, (tag, count) in enumerate(hashtag_counts.head(10).items(), 1):
                    st.markdown(f"**{i}.** `#{tag}` - {count} tweets")
        else:
            st.info("📭 No hashtags found in this period")
    
    with tab4:
        st.subheader("Detailed Tweets")
        
        # Mobile-friendly filters in expanders
        with st.expander("⚙️ Display Options", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox(
                    "Sort by", 
                    ["Most recent", "Most positive", "Most negative"],
                    key="sort_select"
                )
            with col2:
                # Mobile-optimized pagination
                page_size = st.select_slider(
                    "Tweets per page",
                    options=[10, 20, 50, 100],
                    value=20,
                    key="page_size"
                )
        
        # Apply sorting
        if sort_by == "Most recent":
            df_display = df.sort_values('processing_timestamp', ascending=False)
        elif sort_by == "Most positive":
            df_display = df.sort_values('sentiment_score', ascending=False)
        else:
            df_display = df.sort_values('sentiment_score', ascending=True)
        
        # Pagination logic
        total_tweets = len(df_display)
        total_pages = (total_tweets - 1) // page_size + 1
        
        # Initialize page number in session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Previous", disabled=(st.session_state.current_page <= 1)):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 10px;'><b>Page {st.session_state.current_page} of {total_pages}</b></div>", 
                       unsafe_allow_html=True)
        
        with col3:
            if st.button("Next ➡️", disabled=(st.session_state.current_page >= total_pages)):
                st.session_state.current_page += 1
                st.rerun()
        
        # Calculate slice for current page
        start_idx = (st.session_state.current_page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Display paginated data
        df_page = df_display.iloc[start_idx:end_idx]
        
        # Mobile-optimized card view for small screens
        st.markdown("---")
        
        # Show as expandable cards on mobile for better readability
        for idx, row in df_page.iterrows():
            sentiment_emoji = {"positive": "😊", "negative": "😠", "neutral": "😐"}
            sentiment_color = {"positive": "#00CC96", "negative": "#EF553B", "neutral": "#636EFA"}
            
            emoji = sentiment_emoji.get(row['sentiment'], "😐")
            color = sentiment_color.get(row['sentiment'], "#636EFA")
            
            with st.expander(f"{emoji} {row['text'][:80]}...", expanded=False):
                st.markdown(f"**Full Text**: {row['text']}")
                st.markdown(f"**Sentiment**: <span style='color: {color};'>{row['sentiment'].upper()}</span>", 
                          unsafe_allow_html=True)
                st.markdown(f"**Score**: {row['sentiment_score']:.3f}")
                
                if row.get('hashtags') and isinstance(row['hashtags'], list) and len(row['hashtags']) > 0:
                    hashtags_str = ', '.join([f"#{tag}" for tag in row['hashtags']])
                    st.markdown(f"**Hashtags**: {hashtags_str}")
                
                if 'processing_timestamp' in row:
                    timestamp = pd.to_datetime(row['processing_timestamp'])
                    st.markdown(f"**Time**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
        
        # Alternative: Compact table view (togglable)
        if st.checkbox("Show table view", value=False, key="table_view"):
            st.dataframe(
                df_page[['text', 'sentiment', 'sentiment_score', 'hashtags', 'processing_timestamp']]
                .style.background_gradient(subset=['sentiment_score'], cmap='RdYlGn', vmin=-1, vmax=1),
                use_container_width=True,
                height=400
            )
        
        # Show count info
        st.caption(f"Showing {start_idx + 1}-{min(end_idx, total_tweets)} of {total_tweets} tweets")
    
    st.markdown("---")
    
    # ========== ADVANCED STATISTICS (Mobile-Optimized) ==========
    with st.expander("📈 Advanced Statistics", expanded=False):
        # Stack vertically on mobile instead of columns
        st.markdown("### Score Distribution")
        st.write(df['sentiment_score'].astype(float).describe())
        
        st.markdown("---")
        
        st.markdown("### Sentiment Breakdown")
        sentiment_breakdown = df['sentiment'].value_counts()
        st.dataframe(sentiment_breakdown, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### Most Frequent Mentions")
        all_mentions = []
        for mentions in df['mentions'].dropna():
            if isinstance(mentions, list):
                all_mentions.extend(mentions)
        
        if all_mentions:
            mentions_df = pd.Series(all_mentions).value_counts().head(10)
            st.dataframe(mentions_df, use_container_width=True)
        else:
            st.info("📭 No mentions found")

else:
    # No data state
    st.warning("⚠️ No data available for this period.")
    st.info("💡 Check that the producer and consumer are active.")
    
    # Helpful troubleshooting on mobile
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common issues:**
        1. Ensure Docker containers are running
        2. Check that the Kafka producer is sending data
        3. Verify the Spark consumer is processing tweets
        4. Adjust the time range filter in the sidebar
        """)

# ========== FOOTER WITH SYSTEM INFO ==========
st.markdown("---")

# Responsive footer layout
col1, col2 = st.columns(2)
with col1:
    st.caption(f"🕐 Last update: {datetime.now().strftime('%H:%M:%S')}")
    total_docs = collection.count_documents({})
    st.caption(f"💾 Database: {total_docs:,} tweets")

with col2:
    st.caption("⚡ Pipeline: Kafka → Spark → MongoDB")
    st.caption(f"📱 Viewing {len(df) if len(df) > 0 else 0:,} tweets")

# Mobile performance tip
if len(df) > 2500:
    st.info("💡 **Performance Tip**: For better mobile performance, try reducing the data limit in sidebar filters.")

# Auto-refresh with mobile consideration
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()