import streamlit as st
from datetime import datetime
import pytz
from pytz import all_timezones
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="🕐 Digital Clock - Multi TimeZone",
    page_icon="🕐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for digital clock styling
st.markdown("""
    <style>
    .digital-clock {
        font-family: 'Courier New', monospace;
        font-size: 72px;
        font-weight: bold;
        text-align: center;
        padding: 30px;
        border-radius: 15px;
        background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
        color: #00ff00;
        text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0, 255, 0, 0.2);
    }
    
    .timezone-clock {
        font-family: 'Courier New', monospace;
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a3d 100%);
        color: #00ff00;
        text-shadow: 0 0 8px #00ff00;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 255, 0, 0.15);
    }
    
    .timezone-label {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        margin-top: 10px;
    }
    
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 15px 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🕐 Digital Clock - Multi TimeZone Viewer")
st.markdown("*Real-time clock displaying current time across different time zones around the world*")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Time format selection
    time_format = st.radio(
        "Select time format:",
        ["12-hour (HH:MM:SS AM/PM)", "24-hour (HH:MM:SS)"],
        index=1
    )
    
    # Clock update frequency
    update_frequency = st.slider(
        "Update frequency (seconds):",
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )
    
    st.markdown("---")
    
    # Timezone selection
    st.header("📍 Select Time Zones")
    
    # Popular timezones
    popular_timezones = {
        "🌍 UTC": "UTC",
        "🌎 New York": "America/New_York",
        "🌎 Los Angeles": "America/Los_Angeles",
        "🌎 Chicago": "America/Chicago",
        "🌏 London": "Europe/London",
        "🌏 Paris": "Europe/Paris",
        "🌏 Dubai": "Asia/Dubai",
        "🌏 Tokyo": "Asia/Tokyo",
        "🌏 Hong Kong": "Asia/Hong_Kong",
        "🌏 Singapore": "Asia/Singapore",
        "🌏 Sydney": "Australia/Sydney",
        "🌏 Mumbai": "Asia/Kolkata",
        "🌏 Bangkok": "Asia/Bangkok",
        "🌏 Seoul": "Asia/Seoul",
        "🌏 Shanghai": "Asia/Shanghai",
    }
    
    selected_zones = st.multiselect(
        "Choose time zones:",
        options=list(popular_timezones.keys()),
        default=[
            "🌍 UTC",
            "🌎 New York",
            "🌏 London",
            "🌏 Tokyo",
            "🌏 Sydney"
        ]
    )
    
    # Convert selected keys back to timezone strings
    selected_timezones = [popular_timezones[zone] for zone in selected_zones]
    
    st.markdown("---")
    
    # Additional options
    show_date = st.checkbox("Show date", value=True)
    show_12hour = st.checkbox("Show 12-hour format", value=True)
    show_utc_offset = st.checkbox("Show UTC offset", value=True)

# Main content area
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.header("🕰️ Current Time Now")
    
    # Initialize session state for auto-refresh
    if "refresh_counter" not in st.session_state:
        st.session_state.refresh_counter = 0
    
    # Display main UTC clock
    with st.container():
        utc_now = datetime.now(pytz.UTC)
        
        if time_format == "24-hour (HH:MM:SS)":
            time_str = utc_now.strftime("%H:%M:%S")
        else:
            time_str = utc_now.strftime("%I:%M:%S %p")
        
        st.markdown(f"<div class='digital-clock'>{time_str}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='timezone-label' style='text-align: center;'>UTC - Coordinated Universal Time</div>", unsafe_allow_html=True)
        
        if show_date:
            date_str = utc_now.strftime("%A, %B %d, %Y")
            st.markdown(f"<p style='text-align: center; font-size: 18px; color: #666;'>{date_str}</p>", unsafe_allow_html=True)

with col2:
    st.header("📊 Quick Stats")
    
    utc_now = datetime.now(pytz.UTC)
    
    # Hour of day
    hour = utc_now.hour
    period = "Day" if 6 <= hour < 18 else "Night"
    
    st.markdown(f"<div class='metric-card'><p style='margin: 0;'>Hour of Day</p><p style='font-size: 32px; margin: 10px 0;'>{hour:02d}:00</p></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-card'><p style='margin: 0;'>Period</p><p style='font-size: 32px; margin: 10px 0;'>{period}</p></div>", unsafe_allow_html=True)

st.markdown("---")

# Time zones section
st.header("🌐 Time Zones")

if not selected_timezones:
    st.info("👈 Select at least one time zone from the sidebar to display")
else:
    # Create columns for timezone display
    cols = st.columns(min(3, len(selected_timezones)))
    
    for idx, tz_name in enumerate(selected_timezones):
        col = cols[idx % len(cols)]
        
        with col:
            try:
                # Get current time in timezone
                tz = pytz.timezone(tz_name)
                local_time = datetime.now(tz)
                
                # Format time based on selection
                if time_format == "24-hour (HH:MM:SS)":
                    time_str = local_time.strftime("%H:%M:%S")
                else:
                    time_str = local_time.strftime("%I:%M:%S %p")
                
                # Display timezone clock
                st.markdown(f"<div class='timezone-clock'>{time_str}</div>", unsafe_allow_html=True)
                
                # Display timezone info
                tz_display_name = tz_name.replace("_", " ").replace("/", " - ")
                
                # Calculate UTC offset
                utc_offset = local_time.strftime("%z")
                utc_offset_formatted = f"UTC{utc_offset[:3]}:{utc_offset[3:]}"
                
                if show_date:
                    date_str = local_time.strftime("%a, %b %d")
                    st.markdown(f"<p style='text-align: center; font-size: 14px; color: #666;'>{date_str}</p>", unsafe_allow_html=True)
                
                if show_utc_offset:
                    st.markdown(f"<p style='text-align: center; font-size: 12px; color: #999;'>{utc_offset_formatted}</p>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='timezone-label'>{tz_display_name}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error displaying timezone {tz_name}: {str(e)}")

st.markdown("---")

# Comparison table
st.header("📋 Time Zone Comparison Table")

if selected_timezones:
    table_data = []
    
    for tz_name in selected_timezones:
        try:
            tz = pytz.timezone(tz_name)
            local_time = datetime.now(tz)
            
            # Format different representations
            time_24h = local_time.strftime("%H:%M:%S")
            time_12h = local_time.strftime("%I:%M:%S %p")
            date_str = local_time.strftime("%A, %B %d, %Y")
            utc_offset = local_time.strftime("%z")
            utc_offset_formatted = f"UTC{utc_offset[:3]}:{utc_offset[3:]}"
            
            table_data.append({
                "🌍 Time Zone": tz_name.replace("_", " ").replace("/", " - "),
                "24-Hour Format": time_24h,
                "12-Hour Format": time_12h,
                "Date": date_str,
                "UTC Offset": utc_offset_formatted,
                "Day of Week": local_time.strftime("%A")
            })
        except Exception as e:
            pass
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Select time zones to view the comparison table")

st.markdown("---")

# Footer with information
st.markdown("""
<div style='text-align: center; color: #999; margin-top: 30px;'>
<p>🕐 <strong>Digital Clock Application</strong></p>
<p><small>Displays current time across multiple time zones in real-time</small></p>
<p><small>Last updated: {}</small></p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")), unsafe_allow_html=True)

# Auto-refresh placeholder
st.empty()
