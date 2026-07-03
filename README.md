# 🚀 Smart Data Intelligence Group

An AI-powered natural language query engine for community metrics. Convert natural language questions into SQL queries, execute them against a mock database, and receive AI-generated insights—all in one elegant Streamlit dashboard.

## ✨ Features

- **🤖 Natural Language Processing**: Ask questions in plain English, not SQL
- **🔒 Security-First**: SQL injection prevention with query validation and sanitization
- **📊 Real-Time Analytics**: Execute queries and visualize results instantly
- **💡 AI-Powered Insights**: Get deep insights from your data using Google GenAI
- **📈 Interactive Dashboard**: Beautiful metrics and visualizations at a glance
- **📥 Data Export**: Download query results as CSV

## 🛠 Tech Stack

- **Streamlit**: Interactive web dashboard
- **Pandas**: Data manipulation and analysis
- **SQLite**: Mock database with community metrics
- **Google GenAI**: Natural language to SQL conversion and insight generation
- **Python 3.8+**: Core language

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google API Key (get one at [Google AI Studio](https://aistudio.google.com/app/apikeys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/prabhnoors386-tech/Smart-Data-Intelligence-Group.git
   cd Smart-Data-Intelligence-Group
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

   Or create a `.env` file:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```

   Or configure Streamlit secrets (`~/.streamlit/secrets.toml`):
   ```toml
   google_api_key = "your-api-key-here"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:8501`

## 💬 Example Queries

Try these natural language questions:

- "How many active users do we have?"
- "Show me the top 5 posts by likes"
- "What are the most popular categories?"
- "How much time do users spend on the platform?"
- "List all posts from the last 7 days"
- "Who are our most engaged members?"

## 📊 Database Schema

The mock database includes:

### Users
- `user_id`: Unique identifier
- `username`: User handle
- `email`: User email
- `join_date`: Account creation date
- `role`: User role (member, moderator, admin)
- `status`: Account status (active, inactive)

### Posts
- `post_id`: Unique identifier
- `user_id`: Creator's ID
- `title`: Post title
- `content`: Post content
- `created_at`: Creation timestamp
- `views`: View count
- `likes`: Like count
- `shares`: Share count
- `category`: Post category

### Comments
- `comment_id`: Unique identifier
- `post_id`: Parent post ID
- `user_id`: Commenter's ID
- `content`: Comment text
- `created_at`: Creation timestamp
- `likes`: Like count

### Engagement
- `engagement_id`: Unique identifier
- `user_id`: User ID
- `action_type`: Type of action (login, post_view, comment, etc.)
- `action_date`: Date of action
- `duration_minutes`: Duration of engagement
- `platform`: Platform used (web, mobile)

## 🔒 Security Features

### SQL Injection Prevention
- ✅ Query validation using allowlist approach
- ✅ Only SELECT queries permitted
- ✅ Dangerous keywords blocked (DROP, DELETE, INSERT, etc.)
- ✅ Query length limit (max 1000 characters)
- ✅ Query sanitization before execution

### API Key Protection
- ✅ Secrets stored in environment variables or Streamlit secrets
- ✅ API keys never logged or displayed
- ✅ `.gitignore` prevents accidental commits

## 📝 Configuration

### Environment Variables
```bash
GOOGLE_API_KEY=your-api-key-here
```

### Streamlit Secrets (`~/.streamlit/secrets.toml`)
```toml
google_api_key = "your-api-key-here"
```

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push your repository to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your repository and branch
5. Add your `GOOGLE_API_KEY` in Secrets
6. Deploy!

### Deploy to Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
git push heroku main
```

## 📊 How It Works

```
User Input (Natural Language)
    ↓
Google GenAI (Convert to SQL)
    ↓
Security Validation & Sanitization
    ↓
SQLite Query Execution
    ↓
Result Processing & Visualization
    ↓
AI Insight Generation
    ↓
Dashboard Display
```

## 🛠 Development

### Project Structure
```
Smart-Data-Intelligence-Group/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── .env.example          # Example environment variables
```

### Adding New Features

1. Create a feature branch: `git checkout -b feature/new-feature`
2. Make your changes
3. Test thoroughly
4. Commit: `git commit -am 'Add new feature'`
5. Push: `git push origin feature/new-feature`
6. Create a Pull Request

## 🐛 Troubleshooting

### API Key Not Found
- Ensure `GOOGLE_API_KEY` is set in environment or Streamlit secrets
- Check for typos in the environment variable name

### Import Errors
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.8+

### Query Execution Errors
- Check the generated SQL in the "Show SQL" option
- Ensure your natural language query is clear and unambiguous
- Try simplifying your question

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Generative AI API](https://ai.google.dev/docs)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

**Prabhnoor Singh**
- GitHub: [@prabhnoors386-tech](https://github.com/prabhnoors386-tech)

## 🌟 Acknowledgments

- Google Generative AI for the powerful NLP capabilities
- Streamlit for the amazing web framework
- The open-source community for excellent tools and libraries

---

**Built with ❤️ for the Smart Data Intelligence Community**
