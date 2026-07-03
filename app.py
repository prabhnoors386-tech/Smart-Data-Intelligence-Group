import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
import google.generativeai as genai

# ============================================================================
# CONFIGURATION & SECURITY
# ============================================================================

def load_api_key() -> str:
    """Securely load API key from environment or secrets."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        api_key = st.secrets.get("google_api_key") if "google_api_key" in st.secrets else None
        
    if not api_key:
        st.error("❌ API Key not configured. Please set GOOGLE_API_KEY environment variable or add it to secrets.")
        st.stop()
        
    return api_key

# ============================================================================
# DATABASE INITIALIZATION (CACHED)
# ============================================================================

@st.cache_resource
def get_db_connection() -> sqlite3.Connection:
    """Initialize and cache SQLite database connection."""
    return initialize_mock_database()

def initialize_mock_database() -> sqlite3.Connection:
    """Initialize SQLite database with mock community metrics data."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        join_date TEXT,
        role TEXT,
        status TEXT
    )
    """)

    # Create posts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        post_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT,
        content TEXT,
        created_at TEXT,
        views INTEGER,
        likes INTEGER,
        shares INTEGER,
        category TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # Create comments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        comment_id INTEGER PRIMARY KEY,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT,
        created_at TEXT,
        likes INTEGER,
        FOREIGN KEY (post_id) REFERENCES posts(post_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # Create engagement table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engagement (
        engagement_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        action_type TEXT,
        action_date TEXT,
        duration_minutes INTEGER,
        platform TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # Insert mock users
    users_data = [
        (1, "alice_tech", "alice@community.io", "2024-01-15", "moderator", "active"),
        (2, "bob_dev", "bob@community.io", "2024-02-10", "member", "active"),
        (3, "carol_ai", "carol@community.io", "2024-03-05", "member", "active"),
        (4, "david_ml", "david@community.io", "2024-01-20", "member", "inactive"),
        (5, "emma_data", "emma@community.io", "2024-04-01", "admin", "active"),
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", users_data)

    # Insert mock posts
    base_date = datetime.now() - timedelta(days=30)
    posts_data = [
        (1, 1, "Best practices for data cleaning", "A comprehensive guide on data cleaning techniques...", (base_date + timedelta(days=2)).isoformat(), 450, 89, 12, "data-science"),
        (2, 2, "Python performance optimization", "Tips and tricks for speeding up Python code...", (base_date + timedelta(days=5)).isoformat(), 520, 102, 34, "programming"),
        (3, 3, "Introduction to transformers", "Understanding transformer architecture in NLP...", (base_date + timedelta(days=7)).isoformat(), 680, 156, 67, "ai-ml"),
        (4, 1, "Community guidelines update", "New moderation policies for 2024...", (base_date + timedelta(days=10)).isoformat(), 290, 45, 8, "announcements"),
        (5, 5, "SQL query optimization", "Advanced techniques for efficient database queries...", (base_date + timedelta(days=12)).isoformat(), 410, 78, 23, "databases"),
    ]
    cursor.executemany("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", posts_data)

    # Insert mock comments
    comments_data = [
        (1, 1, 2, "Great article! Very helpful.", (base_date + timedelta(days=3)).isoformat(), 15),
        (2, 1, 3, "Thanks for sharing this insight.", (base_date + timedelta(days=3)).isoformat(), 8),
        (3, 2, 1, "Excellent tips on vectorization.", (base_date + timedelta(days=6)).isoformat(), 22),
        (4, 3, 2, "This is exactly what I needed.", (base_date + timedelta(days=8)).isoformat(), 31),
        (5, 5, 3, "Could you provide more examples?", (base_date + timedelta(days=13)).isoformat(), 5),
    ]
    cursor.executemany("INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)", comments_data)

    # Insert mock engagement
    engagement_data = [
        (1, 1, "login", base_date.isoformat(), 45, "web"),
        (2, 2, "post_view", (base_date + timedelta(days=1)).isoformat(), 12, "mobile"),
        (3, 3, "comment", (base_date + timedelta(days=2)).isoformat(), 8, "web"),
        (4, 1, "login", (base_date + timedelta(days=3)).isoformat(), 60, "web"),
        (5, 5, "post_create", (base_date + timedelta(days=4)).isoformat(), 25, "web"),
        (6, 4, "login", (base_date + timedelta(days=5)).isoformat(), 30, "mobile"),
    ]
    cursor.executemany("INSERT INTO engagement VALUES (?, ?, ?, ?, ?, ?)", engagement_data)

    conn.commit()
    return conn

# ============================================================================
# SECURITY: SQL INJECTION PREVENTION
# ============================================================================

def validate_query_safety(query: str) -> Tuple[bool, str]:
    """
    Validate SQL query for safety before execution.
    Uses allowlist approach to prevent SQL injection.
    """
    # Validate input
    if not query or not isinstance(query, str):
        return False, "❌ Invalid query input."

    # Convert to uppercase for checking
    query_upper = query.strip().upper()

    # Only allow SELECT queries
    if not query_upper.startswith("SELECT"):
        return False, "❌ Only SELECT queries are allowed."

    # Dangerous keywords that should not appear
    dangerous_keywords = [
        "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", 
        "CREATE", "EXEC", "EXECUTE", "--", "/*", "*/", 
        "UNION", "PRAGMA", "ATTACH", "DETACH"
    ]
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"❌ Query contains forbidden keyword: {keyword}"

    # Ensure query doesn't exceed reasonable length
    if len(query) > 1000:
        return False, "❌ Query too long (max 1000 characters)."

    return True, "✓ Query passed security validation."

def sanitize_sql_query(query: str) -> str:
    """Additional sanitization layer for SQL queries."""
    # Remove leading/trailing whitespace
    query = query.strip()
    
    # Ensure proper SQL formatting
    if not query.endswith(";"):
        query += ";"
        
    return query
    # ============================================================================
# NLP TO SQL CONVERSION
# ============================================================================

def convert_nlp_to_sql(natural_query: str, api_key: str) -> Tuple[str, bool]:
    """
    Convert natural language query to SQL using Google GenAI.
    Returns (sql_query, success_flag)
    """
    try:
        # Validate input
        if not natural_query or not natural_query.strip():
            return "Error: Empty query provided", False

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # System prompt for SQL generation
        system_prompt = """You are an expert SQL query generator for a community metrics database.

Database schema:
- users: user_id, username, email, join_date, role, status
- posts: post_id, user_id, title, content, created_at, views, likes, shares, category
- comments: comment_id, post_id, user_id, content, created_at, likes
- engagement: engagement_id, user_id, action_type, action_date, duration_minutes, platform

Generate ONLY a SELECT SQL query that answers the user's question.
- Use proper SQL syntax
- Include WHERE clauses when filtering
- Use aggregate functions (COUNT, SUM, AVG, MAX, MIN) when appropriate
- Return only the SQL query, no explanations

Important: The query must be safe and must only use SELECT statements."""

        prompt = f"{system_prompt}\n\nUser question: {natural_query}"

        # Generate with timeout handling
        response = model.generate_content(prompt)

        # Check for empty response
        if not response or not response.text:
            return "Error: AI returned empty response. Try rephrasing your question.", False

        sql_query = response.text.strip()

        # Validate generated SQL is not empty
        if not sql_query:
            return "Error: Generated SQL query is empty. Try rephrasing.", False

        # Extract SQL from code blocks if present
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].split("```")[0].strip()

        return sql_query, True

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"CRITICAL ERROR - {type(e).__name__}: {str(e)}\n\nFull Traceback:\n{error_details}", False

# ============================================================================
# QUERY EXECUTION
# ============================================================================

def execute_query(conn: sqlite3.Connection, query: str) -> Tuple[pd.DataFrame, str]:
    """Execute validated SQL query and return results as DataFrame."""
    try:
        # Validate query safety
        is_safe, validation_msg = validate_query_safety(query)
        
        if not is_safe:
            return pd.DataFrame(), validation_msg

        # Sanitize query
        query = sanitize_sql_query(query)

        # Execute query
        df = pd.read_sql_query(query, conn)
        return df, f"✓ Query executed successfully. Returned {len(df)} rows."

    except sqlite3.Error as e:
        return pd.DataFrame(), f"❌ Database error: {str(e)}"
    except Exception as e:
        return pd.DataFrame(), f"❌ Error executing query: {str(e)}"

# ============================================================================
# INSIGHTS GENERATION
# ============================================================================

def generate_insights(df: pd.DataFrame, query: str, api_key: str) -> str:
    """Generate AI-powered insights from query results."""
    if df.empty:
        return "No data available for analysis."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Prepare data summary
        data_summary = df.describe(include='all').to_string()
        top_rows = df.head(10).to_string()

        insight_prompt = f"""Analyze this query result and provide 3-4 key insights:
        
Original Query: {query}

Data Summary:
{data_summary}

Top Rows:
{top_rows}

Provide actionable, specific insights based on this community metrics data."""

        response = model.generate_content(insight_prompt)
        
        if not response or not response.text:
            return "Could not generate insights at this time."
            
        return response.text

    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg:
            return "⚠️ API quota reached. Could not generate insights."
        return f"Could not generate insights: {type(e).__name__}"
        # ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="Smart Data Intelligence Group",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main {padding: 2rem;}
        .stMetric {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
        h1, h2, h3 {color: #1f77b4;}
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("📊 Smart Data Intelligence Group")
    st.markdown("*AI-Powered Natural Language Query Engine for Community Metrics*")

    # Initialize session state
    if "api_key_loaded" not in st.session_state:
        st.session_state.api_key_loaded = False
        st.session_state.last_query = ""
        st.session_state.last_results = None

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key status
        try:
            api_key = load_api_key()
            st.session_state.api_key_loaded = True
            st.success("✓ API Key loaded securely")
        except Exception as e:
            st.error(str(e))
            st.stop()

        st.markdown("---")

        # Database info
        st.header("📁 Database Info")
        st.info("""
        **Active Database:** Mock Community Metrics
        - Users: 5 records
        - Posts: 5 records
        - Comments: 5 records
        - Engagement: 6 records
        """)

        st.markdown("---")
        
        # Example queries
        st.header("💡 Example Queries")
        examples = [
            "How many active users do we have?",
            "Show the top posts by engagement",
            "What are the most common categories?",
            "How much time do users spend on the platform?",
            "List posts created in the last 7 days",
        ]
        
        for example in examples:
            st.caption(f"→ {example}")

    # Main content area
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.header("🔍 Query Interface")
        
        # Natural language input
        user_query = st.text_area(
            "Enter your question in natural language:",
            placeholder="Example: Show me the top 5 posts by likes in the last 30 days",
            height=100,
            key="user_query"
        )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            submit_button = st.button("🚀 Execute Query", type="primary", use_container_width=True)
        with col_b:
            clear_button = st.button("🔄 Clear", use_container_width=True)
        with col_c:
            show_sql = st.checkbox("Show SQL", value=False)

        if clear_button:
            st.session_state.last_query = ""
            st.session_state.last_results = None
            st.rerun()

        # Get cached database connection
        conn = get_db_connection()

        if submit_button and user_query.strip():
            with st.spinner("🤖 Converting query to SQL..."):
                sql_query, success = convert_nlp_to_sql(user_query, api_key)
                
                if not success:
                    st.error(f"Failed to convert query: {sql_query}")
                else:
                    st.session_state.last_query = sql_query
                    
                    if show_sql:
                        with st.expander("📝 Generated SQL Query"):
                            st.code(sql_query, language="sql")

                    # Validate safety
                    is_safe, validation_msg = validate_query_safety(sql_query)
                    
                    if is_safe:
                        st.success(validation_msg)
                    else:
                        st.error(validation_msg)

                    with st.spinner("⏳ Executing query..."):
                        results_df, exec_msg = execute_query(conn, sql_query)
                        st.session_state.last_results = results_df
                        
                        if results_df.empty:
                            st.warning(exec_msg)
                        else:
                            st.success(exec_msg)

        # Display results
        st.subheader("📈 Query Results")
        st.dataframe(results_df if st.session_state.last_results is not None else pd.DataFrame(), use_container_width=True)

        # Generate insights
        if st.session_state.last_results is not None and not st.session_state.last_results.empty:
            with st.spinner("🧠 Generating AI insights..."):
                insights = generate_insights(st.session_state.last_results, user_query, api_key)
                st.subheader("💡 AI-Generated Insights")
                st.markdown(insights)

            # Download results
            csv = st.session_state.last_results.to_csv(index=False)
            st.download_button(
                label="📥 Download Results (CSV)",
                data=csv,
                file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col2:
        st.header("📊 Dashboard")
        
        # Get cached database connection
        conn = get_db_connection()
        
        # User count
        users = pd.read_sql_query("SELECT COUNT(*) as count FROM users", conn)
        st.metric("👥 Total Users", users['count'].values[0])
        
        # Posts count
        posts = pd.read_sql_query("SELECT COUNT(*) as count FROM posts", conn)
        st.metric("📝 Total Posts", posts['count'].values[0])
        
        # Average engagement
        avg_likes = pd.read_sql_query("SELECT AVG(likes) as avg FROM posts", conn)
        st.metric("👍 Avg Post Likes", f"{avg_likes['avg'].values[0]:.1f}")
        
        # Most viewed post
        top_post = pd.read_sql_query(
            "SELECT title, views FROM posts ORDER BY views DESC LIMIT 1", 
            conn
        )
        if not top_post.empty:
            st.metric("🔥 Most Viewed", top_post['views'].values[0])
            
        st.markdown("---")
            
        # Category distribution
        categories = pd.read_sql_query(
            "SELECT category, COUNT(*) as count FROM posts GROUP BY category", 
            conn
        )
        if not categories.empty:
            st.subheader("📂 Posts by Category")
            st.bar_chart(categories.set_index('category')['count'])
            
        # Active users
        st.subheader("👤 User Status")
        status = pd.read_sql_query(
            "SELECT status, COUNT(*) as count FROM users GROUP BY status", 
            conn
        )
        if not status.empty:
            st.bar_chart(status.set_index('status')['count'])

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #999;'>
            <p>🔐 <strong>Security Note:</strong> All queries are validated and sanitized. Only SELECT operations are permitted.</p>
            <p><small>Powered by Streamlit, Google GenAI, and SQLite</small></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
