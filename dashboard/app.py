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

sys.path.append('..')
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

# Page configuration
st.set_page_config(
    page_title="📊 Big Data Analysis - Twitter Sentiment",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1DA1F2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# MongoDB connection
@st.cache_resource
def get_mongo_client():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB][MONGO_COLLECTION]

collection = get_mongo_client()

# Header
st.markdown('<h1 class="main-header">🐦 Twitter Sentiment Analysis - Big Data Pipeline</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Configuration")
time_range = st.sidebar.selectbox(
    "📅 Analysis Period",
    ["Last hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "All"]
)

refresh_rate = st.sidebar.slider("🔄 Refresh rate (seconds)", 5, 60, 10)
auto_refresh = st.sidebar.checkbox("Auto-refresh enabled", value=True)

# Additional filters
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Advanced Filters")
sentiment_filter = st.sidebar.multiselect(
    "Sentiments",
    ["positive", "negative", "neutral"],
    default=["positive", "negative", "neutral"]
)

# Convert period to filter
time_filters = {
    "Last hour": datetime.now() - timedelta(hours=1),
    "Last 6 hours": datetime.now() - timedelta(hours=6),
    "Last 24 hours": datetime.now() - timedelta(days=1),
    "Last 7 days": datetime.now() - timedelta(days=7),
    "All": datetime(2000, 1, 1)
}

# Function to load data
@st.cache_data(ttl=refresh_rate)
def get_data(time_filter, sentiments):
    query = {
        "processing_timestamp": {"$gte": time_filter},
        "sentiment": {"$in": sentiments}
    }
    tweets = list(collection.find(query).sort("processing_timestamp", -1).limit(5000))
    return pd.DataFrame(tweets)

# Load data
with st.spinner("🔄 Loading data..."):
    df = get_data(time_filters[time_range], sentiment_filter)

if len(df) > 0:
    # === KEY METRICS ===
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📨 Total Tweets", f"{len(df):,}")
    
    with col2:
        positive_count = (df['sentiment'] == 'positive').sum()
        positive_pct = positive_count / len(df) * 100
        st.metric("😊 Positive", f"{positive_pct:.1f}%", delta=f"{positive_count}")
    
    with col3:
        negative_count = (df['sentiment'] == 'negative').sum()
        negative_pct = negative_count / len(df) * 100
        st.metric("😠 Negative", f"{negative_pct:.1f}%", delta=f"-{negative_count}", delta_color="inverse")
    
    with col4:
        neutral_count = (df['sentiment'] == 'neutral').sum()
        neutral_pct = neutral_count / len(df) * 100
        st.metric("😐 Neutral", f"{neutral_pct:.1f}%", delta=f"{neutral_count}")
    
    with col5:
        avg_score = df['sentiment_score'].astype(float).mean()
        st.metric("📈 Avg Score", f"{avg_score:.3f}")
    
    st.markdown("---")
    
    # === MAIN CHARTS ===
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⏱️ Temporal", "🏷️ Hashtags", "📝 Details"])
    
    with tab1:
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
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
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
            fig_hist.update_layout(bargap=0.1)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab2:
        st.subheader("Temporal Evolution")
        
        # Prepare temporal data
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
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Total volume
        df_volume = df_sorted.set_index('processing_timestamp').resample('5T').size()
        fig_area = px.area(
            x=df_volume.index,
            y=df_volume.values,
            title="Total tweet volume"
        )
        st.plotly_chart(fig_area, use_container_width=True)
    
    with tab3:
        st.subheader("Hashtag Analysis")
        
        # Extract all hashtags
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
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.markdown("#### Word Cloud")
                try:
                    # Try to create wordcloud with a common TrueType font
                    import os
                    font_path = None
                    # Common font paths on Linux systems
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
                        st.pyplot(fig)
                    else:
                        st.warning("Word cloud requires TrueType fonts. Please install fonts: sudo apt-get install fonts-dejavu")
                except Exception as e:
                    st.warning(f"Could not generate word cloud: {str(e)}")
        else:
            st.info("No hashtags found in this period")
    
    with tab4:
        st.subheader("Detailed Tweets")
        
        # Additional filters
        col1, col2 = st.columns(2)
        with col1:
            sort_by = st.selectbox("Sort by", ["Most recent", "Most positive", "Most negative"])
        with col2:
            show_count = st.slider("Number of tweets to display", 10, 100, 20)
        
        # Apply sorting
        if sort_by == "Most recent":
            df_display = df.sort_values('processing_timestamp', ascending=False)
        elif sort_by == "Most positive":
            df_display = df.sort_values('sentiment_score', ascending=False)
        else:
            df_display = df.sort_values('sentiment_score', ascending=True)
        
        # Display table
        st.dataframe(
            df_display[['text', 'sentiment', 'sentiment_score', 'hashtags', 'processing_timestamp']]
            .head(show_count)
            .style.background_gradient(subset=['sentiment_score'], cmap='RdYlGn', vmin=-1, vmax=1),
            use_container_width=True,
            height=400
        )
    
    st.markdown("---")
    
    # === ADVANCED STATISTICS ===
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

# Footer with system info
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🕐 Last update: {datetime.now().strftime('%H:%M:%S')}")
with col2:
    total_docs = collection.count_documents({})
    st.caption(f"💾 Total in database: {total_docs:,} tweets")
with col3:
    st.caption("⚡ Pipeline: Kafka → Spark → MongoDB")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()