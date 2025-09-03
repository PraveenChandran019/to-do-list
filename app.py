import streamlit as st
from datetime import datetime, timedelta
import uuid
import time
import plotly.express as px
import pandas as pd

# Page configuration with a professional theme
st.set_page_config(
    page_title="Personal Productivity Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional UI with fixed text visibility
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        font-family: 'Arial', sans-serif;
        color: #333333;
    }
    .main .block-container {
        padding: 2rem;
        background-color: #ffffff;
        font-family: 'Arial', sans-serif;
        color: #333333;
    }
    .stMetric {
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #333333;
    }
    .stPlotlyChart {
        margin-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        font-size: 1em;
        font-weight: 500;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1em;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        color: #333333;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #3498db;
        color: white;
    }
    .hero-section {
        background-color: #3498db;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-section h1 {
        font-size: 2.5em;
        margin-bottom: 0.5rem;
    }
    .hero-section p {
        font-size: 1.2em;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        color: #333333;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        color: #333333 !important;
        background-color: #ffffff !important;
        border: 1px solid #ced4da;
        border-radius: 4px;
    }
    .stForm {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        color: #333333;
    }
    .stCaption {
        color: #666666 !important;
    }
    .custom-container {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        color: #333333;
    }
    @media (max-width: 600px) {
        .hero-section h1 {
            font-size: 1.8em;
        }
        .feature-card {
            padding: 0.75rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
def initialize_session_state():
    """Initialize all session state variables"""
    if 'users' not in st.session_state:
        st.session_state.users = {}
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if 'user_tasks' not in st.session_state:
        st.session_state.user_tasks = {}
    
    if 'user_notes' not in st.session_state:
        st.session_state.user_notes = {}
    
    if 'user_habits' not in st.session_state:
        st.session_state.user_habits = {}
    
    if 'user_goals' not in st.session_state:
        st.session_state.user_goals = {}
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}
    
    if 'pomodoro_state' not in st.session_state:
        st.session_state.pomodoro_state = {
            'is_running': False,
            'start_time': None,
            'duration': 25 * 60,
            'session_type': 'work',
            'sessions_completed': 0,
            'work_duration': 25,
            'short_break_duration': 5,
            'long_break_duration': 15
        }

# Enhanced authentication functions
def signup_user(username, password, email, full_name):
    """Register a new user with enhanced profile"""
    if username in st.session_state.users:
        return False, "Username already exists!"
    
    user_data = {
        'password': password,
        'email': email,
        'full_name': full_name,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'last_login': None,
        'theme': 'light',
        'productivity_streak': 0
    }
    
    st.session_state.users[username] = user_data
    st.session_state.user_tasks[username] = []
    st.session_state.user_notes[username] = []
    st.session_state.user_habits[username] = []
    st.session_state.user_goals[username] = []
    st.session_state.user_preferences[username] = {
        'daily_goal': 5,
        'notifications': True,
        'work_hours': {'start': '09:00', 'end': '17:00'}
    }
    
    return True, "Account created successfully!"

def login_user(username, password):
    """Authenticate user login with enhanced tracking"""
    if username not in st.session_state.users:
        return False, "Username not found! Please create an account first."
    
    if st.session_state.users[username]['password'] != password:
        return False, "Incorrect password!"
    
    st.session_state.users[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    st.session_state.logged_in = True
    st.session_state.current_user = username
    return True, f"Welcome back, {st.session_state.users[username]['full_name']}! "

def logout_user():
    """Log out the current user"""
    st.session_state.logged_in = False
    st.session_state.current_user = None

# Enhanced task management
def add_task(task_text, priority='Medium', category='General', due_date=None):
    """Add a new task with enhanced features"""
    if st.session_state.current_user:
        new_task = {
            'id': str(uuid.uuid4()),
            'text': task_text,
            'completed': False,
            'priority': priority,
            'category': category,
            'due_date': due_date.strftime("%Y-%m-%d") if due_date else None,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'completed_at': None,
            'time_spent': 0
        }
        st.session_state.user_tasks[st.session_state.current_user].append(new_task)

def toggle_task(task_id):
    """Toggle task completion status"""
    if st.session_state.current_user:
        tasks = st.session_state.user_tasks[st.session_state.current_user]
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = not task['completed']
                task['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M") if task['completed'] else None
                break

def delete_task(task_id):
    """Delete a task"""
    if st.session_state.current_user:
        tasks = st.session_state.user_tasks[st.session_state.current_user]
        st.session_state.user_tasks[st.session_state.current_user] = [
            task for task in tasks if task['id'] != task_id
        ]

# Habit tracking functions
def add_habit(habit_name, target_frequency):
    """Add a new habit to track"""
    if st.session_state.current_user:
        new_habit = {
            'id': str(uuid.uuid4()),
            'name': habit_name,
            'target_frequency': target_frequency,
            'created_at': datetime.now().strftime("%Y-%m-%d"),
            'completions': []
        }
        st.session_state.user_habits[st.session_state.current_user].append(new_habit)

def mark_habit_complete(habit_id, date=None):
    """Mark habit as complete for a specific date"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.current_user:
        habits = st.session_state.user_habits[st.session_state.current_user]
        for habit in habits:
            if habit['id'] == habit_id:
                if date not in habit['completions']:
                    habit['completions'].append(date)
                break

# Goal management functions
def add_goal(title, description, target_date, category):
    """Add a new goal"""
    if st.session_state.current_user:
        new_goal = {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': description,
            'category': category,
            'target_date': target_date.strftime("%Y-%m-%d"),
            'created_at': datetime.now().strftime("%Y-%m-%d"),
            'progress': 0,
            'status': 'active'
        }
        st.session_state.user_goals[st.session_state.current_user].append(new_goal)

# Analytics functions
def get_productivity_stats():
    """Calculate productivity statistics"""
    if not st.session_state.current_user:
        return {}
    
    tasks = st.session_state.user_tasks[st.session_state.current_user]
    habits = st.session_state.user_habits[st.session_state.current_user]
    goals = st.session_state.user_goals[st.session_state.current_user]
    
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Task stats
    today_tasks = [t for t in tasks if datetime.strptime(t['created_at'][:10], "%Y-%m-%d").date() == today]
    today_completed = [t for t in today_tasks if t['completed']]
    
    week_tasks = [t for t in tasks if datetime.strptime(t['created_at'][:10], "%Y-%m-%d").date() >= week_start]
    week_completed = [t for t in week_tasks if t['completed']]
    
    categories = {}
    for task in tasks:
        cat = task.get('category', 'General')
        categories[cat] = categories.get(cat, 0) + 1
    
    total_tasks = len(tasks)
    total_completed = len([t for t in tasks if t['completed']])
    
    weekly_completed = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        weekly_completed[day_str] = len([t for t in tasks if t['completed_at'] and t['completed_at'][:10] == day_str])
    
    num_habits = len(habits)
    today_habits_completed = sum(1 for h in habits if today.strftime("%Y-%m-%d") in h['completions'])
    habit_streaks = {}
    for habit in habits:
        completions = sorted(habit['completions'], reverse=True)
        current_streak = 0
        check_date = today
        for comp in completions:
            if comp == check_date.strftime("%Y-%m-%d"):
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        habit_streaks[habit['name']] = current_streak
    avg_habit_streak = sum(habit_streaks.values()) / num_habits if num_habits > 0 else 0
    
    num_goals = len(goals)
    num_completed_goals = sum(1 for g in goals if g['status'] == 'completed')
    avg_progress = sum(g['progress'] for g in goals) / num_goals if num_goals > 0 else 0
    goal_categories = {}
    for goal in goals:
        cat = goal.get('category', 'General')
        goal_categories[cat] = goal_categories.get(cat, 0) + 1
    
    return {
        'today_tasks': len(today_tasks),
        'today_completed': len(today_completed),
        'week_tasks': len(week_tasks),
        'week_completed': len(week_completed),
        'total_tasks': total_tasks,
        'total_completed': total_completed,
        'categories': categories,
        'weekly_completed': weekly_completed,
        'num_habits': num_habits,
        'today_habits_completed': today_habits_completed,
        'avg_habit_streak': avg_habit_streak,
        'habit_streaks': habit_streaks,
        'num_goals': num_goals,
        'num_completed_goals': num_completed_goals,
        'avg_progress': avg_progress,
        'goal_categories': goal_categories
    }

# Enhanced Notes functions
def add_note(note_title, note_content, category='General'):
    """Add a new note with category"""
    if st.session_state.current_user:
        new_note = {
            'id': str(uuid.uuid4()),
            'title': note_title,
            'content': note_content,
            'category': category,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.user_notes[st.session_state.current_user].append(new_note)

def update_note(note_id, title, content, category):
    """Update an existing note"""
    if st.session_state.current_user:
        notes = st.session_state.user_notes[st.session_state.current_user]
        for note in notes:
            if note['id'] == note_id:
                note['title'] = title
                note['content'] = content
                note['category'] = category
                note['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                break

def delete_note(note_id):
    """Delete a note"""
    if st.session_state.current_user:
        notes = st.session_state.user_notes[st.session_state.current_user]
        st.session_state.user_notes[st.session_state.current_user] = [
            note for note in notes if note['id'] != note_id
        ]

# Page functions
def welcome_page():
    """Display welcome page for new users"""
    st.markdown(
        """
        <div class="hero-section">
            <h1>Welcome to Personal Productivity Hub</h1>
            <p>Your all-in-one solution for smarter task management, habit tracking, and goal achievement.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Why Choose Productivity Hub?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📋 Smart Tasks</h3>
                <p>Organize tasks with priorities, categories, and due dates.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="feature-card">
                <h3>🔄 Habit Tracking</h3>
                <p>Build lasting habits with streak monitoring.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🎯 Goal Setting</h3>
                <p>Track progress towards your dreams with clear milestones.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="feature-card">
                <h3>📝 Smart Notes</h3>
                <p>Organize ideas with searchable, categorized notes.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>⏰ Pomodoro Timer</h3>
                <p>Boost focus with timed work sessions.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="feature-card">
                <h3>📊 Analytics</h3>
                <p>Visualize your productivity with insightful charts.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem; color: #333333;">
            <h3>Ready to boost your productivity?</h3>
            <p>Create your free account or sign in below to get started!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def login_signup_page():
    """Enhanced login and signup interface"""
    welcome_page()
    
    st.markdown("---")
    
    signup_tab, login_tab = st.tabs(["Create Account", "Login"])
    
    with signup_tab:
        st.subheader("Join the Productivity Revolution!")
        st.info("New here? Start with this tab to create your account!")
        
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name *", placeholder="e.g., John Doe")
                username = st.text_input("Choose Username *", placeholder="e.g., johndoe123")
                
            with col2:
                email = st.text_input("Email Address *", placeholder="e.g., john@example.com")
                new_password = st.text_input("Choose Password *", type="password", placeholder="Create a strong password")
                
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Repeat your password")
            
            st.markdown("By creating an account, you agree to our terms of service and privacy policy.")
            signup_button = st.form_submit_button("Create My Account")
            
            if signup_button:
                if not all([full_name, username, email, new_password, confirm_password]):
                    st.error("Please fill in all required fields!")
                elif new_password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long!")
                else:
                    with st.spinner("Creating your account..."):
                        time.sleep(1)
                        success, message = signup_user(username, new_password, email, full_name)
                        if success:
                            st.success(message)
                            st.info("Account created! Now switch to the Login tab to sign in!")
                        else:
                            st.error(message)
    
    with login_tab:
        st.subheader("Welcome Back!")
        st.info("Already have an account? Sign in here!")
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                login_button = st.form_submit_button("Sign In")
            with col2:
                st.caption("Don't have an account? Use the 'Create Account' tab above!")
            
            if login_button:
                if username and password:
                    with st.spinner("Logging in..."):
                        time.sleep(1)
                        success, message = login_user(username, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please enter both username and password")

def dashboard_page():
    """Main dashboard with professional layout"""
    user_data = st.session_state.users[st.session_state.current_user]
    st.title(f"Dashboard - Welcome {user_data['full_name']}!")
    
    stats = get_productivity_stats()
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Today's Tasks", f"{stats['today_completed']}/{stats['today_tasks']}", "📋")
    with col2:
        st.metric("This Week", f"{stats['week_completed']}/{stats['week_tasks']}", "📅")
    with col3:
        completion_rate = (stats['total_completed'] / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%", "✅")
    with col4:
        st.metric("Habits Today", f"{stats['today_habits_completed']}/{stats['num_habits']}", "🔄")
    with col5:
        st.metric("Avg Streak", f"{stats['avg_habit_streak']:.1f} days", "🔥")
    with col6:
        st.metric("Goals Progress", f"{stats['avg_progress']:.1f}%", "🎯")
    
    st.subheader("Analytics Overview")
    vis_col1, vis_col2 = st.columns(2)
    
    with vis_col1:
        if stats['total_tasks'] > 0:
            task_data = pd.DataFrame({
                'Status': ['Completed', 'Pending'],
                'Count': [stats['total_completed'], stats['total_tasks'] - stats['total_completed']]
            })
            fig1 = px.pie(
                task_data,
                names='Status',
                values='Count',
                title='Task Completion Status',
                color='Status',
                color_discrete_map={'Completed': '#2ecc71', 'Pending': '#e74c3c'},
                hole=0.3
            )
            fig1.update_traces(textinfo='percent+label', textfont_size=14)
            fig1.update_layout(
                title_font_size=16,
                margin=dict(t=50, b=50, l=50, r=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333333')
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No tasks yet for pie chart.")
        
        if stats['num_goals'] > 0:
            goal_data = pd.DataFrame({
                'Category': list(stats['goal_categories'].keys()),
                'Count': list(stats['goal_categories'].values())
            })
            fig3 = px.pie(
                goal_data,
                names='Category',
                values='Count',
                title='Goal Categories',
                color_discrete_sequence=['#3498db', '#e67e22', '#9b59b6', '#f1c40f', '#1abc9c'],
                hole=0.3
            )
            fig3.update_traces(textinfo='percent+label', textfont_size=14)
            fig3.update_layout(
                title_font_size=16,
                margin=dict(t=50, b=50, l=50, r=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333333')
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No goals yet for pie chart.")
    
    with vis_col2:
        if stats['categories']:
            category_data = pd.DataFrame({
                'Category': list(stats['categories'].keys()),
                'Count': list(stats['categories'].values())
            })
            fig2 = px.bar(
                category_data,
                x='Category',
                y='Count',
                title='Task Categories',
                color_discrete_sequence=['#3498db']
            )
            fig2.update_layout(
                title_font_size=16,
                xaxis_title='',
                yaxis_title='Count',
                xaxis_tickangle=45,
                margin=dict(t=50, b=50, l=50, r=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333333')
            )
            fig2.update_traces(hovertemplate='Category: %{x}<br>Count: %{y}')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No categories yet for bar chart.")
        
        if stats['weekly_completed']:
            weekly_data = pd.DataFrame({
                'Date': list(stats['weekly_completed'].keys()),
                'Completed Tasks': list(stats['weekly_completed'].values())
            })
            fig4 = px.line(
                weekly_data,
                x='Date',
                y='Completed Tasks',
                title='Weekly Completed Tasks',
                markers=True,
                color_discrete_sequence=['#27ae60']
            )
            fig4.update_layout(
                title_font_size=16,
                xaxis_title='',
                yaxis_title='Completed Tasks',
                xaxis_tickangle=45,
                margin=dict(t=50, b=50, l=50, r=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333333')
            )
            fig4.update_traces(line=dict(width=2), marker=dict(size=8))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No weekly data yet for line chart.")
    
    if stats['habit_streaks']:
        st.subheader("Habit Streaks")
        habit_data = pd.DataFrame({
            'Habit': list(stats['habit_streaks'].keys()),
            'Streak Days': list(stats['habit_streaks'].values())
        })
        fig5 = px.bar(
            habit_data,
            y='Habit',
            x='Streak Days',
            title='Current Habit Streaks',
            orientation='h',
            color_discrete_sequence=['#f39c12']
        )
        fig5.update_layout(
            title_font_size=16,
            xaxis_title='Streak Days',
            yaxis_title='',
            margin=dict(t=50, b=50, l=50, r=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333')
        )
        fig5.update_traces(hovertemplate='Habit: %{y}<br>Streak Days: %{x}')
        st.plotly_chart(fig5, use_container_width=True)
    
    st.subheader("Quick Actions")
    qa_col1, qa_col2, qa_col3 = st.columns(3)
    
    with qa_col1:
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        with st.form("quick_task"):
            quick_task = st.text_input("Add Quick Task", placeholder="Enter task...")
            if st.form_submit_button("Add Task"):
                if quick_task:
                    add_task(quick_task.strip())
                    st.success("Task added!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with qa_col2:
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        with st.form("quick_note"):
            quick_note_title = st.text_input("Quick Note Title", placeholder="Title...")
            quick_note_content = st.text_area("Content", height=100, placeholder="Content...")
            if st.form_submit_button("Save Note"):
                if quick_note_title and quick_note_content:
                    add_note(quick_note_title.strip(), quick_note_content.strip())
                    st.success("Note saved!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with qa_col3:
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        st.subheader("Today's Focus")
        today_tasks = [t for t in st.session_state.user_tasks[st.session_state.current_user] 
                      if not t['completed'] and t.get('priority') == 'High'][:3]
        if today_tasks:
            for task in today_tasks:
                st.write(f"🔴 {task['text']}")
        else:
            st.write("No high-priority tasks for today!")
        st.markdown('</div>', unsafe_allow_html=True)

def enhanced_todo_page():
    """Enhanced to-do list with filters and categories"""
    st.title("Task Manager")
    
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_status = st.selectbox("Status", ["All", "Pending", "Completed"])
    with col2:
        filter_priority = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    with col3:
        filter_category = st.selectbox("Category", 
                                     ["All"] + list(set([t.get('category', 'General') 
                                     for t in st.session_state.user_tasks.get(st.session_state.current_user, [])])))
    with col4:
        sort_by = st.selectbox("Sort By", ["Created Date", "Priority", "Due Date"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("Create New Task")
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_task = st.text_input("Task Description*", placeholder="e.g., Complete project report")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
        
        with col2:
            category = st.text_input("Category", placeholder="e.g., Work, Personal, Health")
            due_date = st.date_input("Due Date (Optional)", value=None)
        
        add_button = st.form_submit_button("Add Task")
        
        if add_button and new_task.strip():
            add_task(new_task.strip(), priority, category or "General", due_date)
            st.success(f"Task added: {new_task}")
            st.rerun()
    
    st.subheader("Your Tasks")
    user_tasks = st.session_state.user_tasks.get(st.session_state.current_user, [])
    
    filtered_tasks = user_tasks
    if filter_status != "All":
        filtered_tasks = [t for t in filtered_tasks if 
                         (t['completed'] if filter_status == "Completed" else not t['completed'])]
    if filter_priority != "All":
        filtered_tasks = [t for t in filtered_tasks if t.get('priority') == filter_priority]
    if filter_category != "All":
        filtered_tasks = [t for t in filtered_tasks if t.get('category', 'General') == filter_category]
    
    if not filtered_tasks:
        st.info("No tasks match your current filters. Try adjusting them above!")
    else:
        for task in filtered_tasks:
            priority_colors = {"High": "#ff4d4d", "Medium": "#ffd700", "Low": "#90ee90"}
            priority_color = priority_colors.get(task.get('priority', 'Medium'), "#ffd700")
            
            st.markdown(f'<div class="custom-container" style="border-left: 5px solid {priority_color};">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
            
            with col1:
                if st.button("✅" if not task['completed'] else "🔄", 
                           key=f"toggle_{task['id']}", 
                           help="Toggle completion"):
                    toggle_task(task['id'])
                    st.rerun()
            
            with col2:
                task_style = "<s>" if task['completed'] else "<strong>"
                st.markdown(f"{task_style}{task['text']}</{task_style.split('>')[0][1:]}>", unsafe_allow_html=True)
                
                metadata = []
                metadata.append(f"📋 {task.get('category', 'General')}")
                metadata.append(f"📅 {task['created_at'][:10]}")
                if task.get('due_date'):
                    metadata.append(f"⏰ Due: {task['due_date']}")
                
                st.caption(" | ".join(metadata))
            
            with col3:
                if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                    delete_task(task['id'])
                    st.success("Task deleted!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def habits_page():
    """Habit tracking page"""
    st.title("Habit Tracker")
    
    st.subheader("Create New Habit")
    with st.form("add_habit_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            habit_name = st.text_input("Habit Name", placeholder="e.g., Drink 8 glasses of water")
        with col2:
            frequency = st.selectbox("Target Frequency", ["Daily", "Weekly", "Monthly"])
        
        if st.form_submit_button("Add Habit"):
            if habit_name:
                add_habit(habit_name.strip(), frequency.lower())
                st.success(f"Habit '{habit_name}' added!")
                st.rerun()
    
    st.subheader("Your Habits")
    user_habits = st.session_state.user_habits.get(st.session_state.current_user, [])
    
    if not user_habits:
        st.info("No habits yet! Create your first habit above to start building positive routines.")
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        
        for habit in user_habits:
            st.markdown('<div class="custom-container">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"<strong>{habit['name']}</strong>", unsafe_allow_html=True)
                st.caption(f"Target: {habit['target_frequency'].title()} | Created: {habit['created_at']}")
            
            with col2:
                completions = sorted(habit['completions'], reverse=True)
                current_streak = 0
                check_date = datetime.now().date()
                for completion_date in completions:
                    if completion_date == check_date.strftime("%Y-%m-%d"):
                        current_streak += 1
                        check_date -= timedelta(days=1)
                    else:
                        break
                
                st.metric("Streak", f"{current_streak} days")
            
            with col3:
                if today not in habit['completions']:
                    if st.button("✅ Mark Done", key=f"habit_{habit['id']}"):
                        mark_habit_complete(habit['id'])
                        st.success("Great job!")
                        st.rerun()
                else:
                    st.success("Done Today!")
            st.markdown('</div>', unsafe_allow_html=True)

def goals_page():
    """Goal tracking page"""
    st.title("Goal Tracker")
    
    st.subheader("Set New Goal")
    with st.form("add_goal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal_title = st.text_input("Goal Title*", placeholder="e.g., Learn Python Programming")
            category = st.selectbox("Category", ["Personal", "Professional", "Health", "Financial", "Learning"])
        
        with col2:
            target_date = st.date_input("Target Date")
            
        goal_description = st.text_area("Description", placeholder="Describe your goal in detail...")
        
        if st.form_submit_button("Set Goal"):
            if goal_title and goal_description:
                add_goal(goal_title.strip(), goal_description.strip(), target_date, category)
                st.success(f"Goal '{goal_title}' set!")
                st.rerun()
    
    st.subheader("Your Goals")
    user_goals = st.session_state.user_goals.get(st.session_state.current_user, [])
    
    if not user_goals:
        st.info("No goals yet! Set your first goal above to start achieving your dreams.")
    else:
        for goal in user_goals:
            with st.expander(f"{goal['title']} - {goal['category']}"):
                st.markdown('<div class="custom-container">', unsafe_allow_html=True)
                st.write(f"Description: {goal['description']}")
                st.write(f"Target Date: {goal['target_date']}")
                st.write(f"Created: {goal['created_at']}")
                
                progress_color = "#2ecc71" if goal['progress'] == 100 else "#3498db"
                st.progress(goal['progress'] / 100)
                st.markdown(f'<p style="text-align: center; color: {progress_color};">{goal["progress"]}% Complete</p>', unsafe_allow_html=True)
                
                progress = st.slider("Update Progress", 0, 100, goal['progress'], 
                                   key=f"progress_{goal['id']}")
                
                if st.button("Update", key=f"update_{goal['id']}"):
                    goals = st.session_state.user_goals[st.session_state.current_user]
                    for g in goals:
                        if g['id'] == goal['id']:
                            g['progress'] = progress
                            if progress == 100:
                                g['status'] = 'completed'
                            break
                    st.success("Progress updated!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

def enhanced_notes_page():
    """Enhanced notes with categories and search"""
    st.title("Smart Notes")
    
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("Search Notes", placeholder="Search by title or content...")
    with col2:
        user_notes = st.session_state.user_notes.get(st.session_state.current_user, [])
        categories = list(set([n.get('category', 'General') for n in user_notes]))
        filter_category = st.selectbox("Filter by Category", ["All"] + categories)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("Create New Note")
    with st.form("add_note_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            note_title = st.text_input("Note Title*", placeholder="Enter note title...")
        with col2:
            note_category = st.text_input("Category", placeholder="e.g., Ideas, Meeting Notes")
            
        note_content = st.text_area("Note Content*", placeholder="Write your note here...", height=150)
        
        add_note_button = st.form_submit_button("Save Note")
        
        if add_note_button and note_title.strip() and note_content.strip():
            add_note(note_title.strip(), note_content.strip(), note_category or "General")
            st.success(f"Note '{note_title}' saved!")
            st.rerun()
    
    st.subheader("Your Notes")
    filtered_notes = user_notes
    if search_term:
        filtered_notes = [n for n in filtered_notes if 
                         search_term.lower() in n['title'].lower() or 
                         search_term.lower() in n['content'].lower()]
    if filter_category != "All":
        filtered_notes = [n for n in filtered_notes if n.get('category', 'General') == filter_category]
    
    if not filtered_notes:
        if search_term or filter_category != "All":
            st.info("No notes match your search criteria. Try different keywords or categories.")
        else:
            st.info("No notes yet! Create your first note above.")
    else:
        for note in reversed(filtered_notes):
            with st.expander(f"{note['title']} - {note.get('category', 'General')}"):
                st.markdown('<div class="custom-container">', unsafe_allow_html=True)
                st.write(note['content'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Created: {note['created_at']}")
                    if note['updated_at'] != note['created_at']:
                        st.caption(f"Updated: {note['updated_at']}")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_note_{note['id']}"):
                        delete_note(note['id'])
                        st.success("Note deleted!")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

def pomodoro_page():
    """Pomodoro timer for focused work sessions"""
    st.title("Pomodoro Timer")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Focus Timer")
        
        if st.session_state.pomodoro_state['is_running']:
            elapsed = time.time() - st.session_state.pomodoro_state['start_time']
            remaining = max(0, st.session_state.pomodoro_state['duration'] - elapsed)
        else:
            remaining = st.session_state.pomodoro_state['duration']
        
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        timer_color = "#e74c3c" if st.session_state.pomodoro_state['session_type'] == 'work' else "#27ae60"
        st.markdown(f"""
        <div style="text-align: center; font-size: 3em; font-weight: bold; 
                    color: {timer_color}; margin: 1rem 0; background-color: #e9ecef; 
                    padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            {minutes:02d}:{seconds:02d}
        </div>
        """, unsafe_allow_html=True)
        
        session_type = st.session_state.pomodoro_state['session_type'].replace('_', ' ').title()
        st.markdown(f"<p style='text-align: center; color: #333333; font-size: 1.2em;'><strong>{session_type} Session</strong></p>", unsafe_allow_html=True)
        
        st.markdown('<div style="display: flex; justify-content: center; gap: 1rem;">', unsafe_allow_html=True)
        if st.button("▶ Start", key="pomodoro_start"):
            if not st.session_state.pomodoro_state['is_running']:
                st.session_state.pomodoro_state['is_running'] = True
                st.session_state.pomodoro_state['start_time'] = time.time()
                st.rerun()
        
        if st.button("⏸ Pause", key="pomodoro_pause"):
            if st.session_state.pomodoro_state['is_running']:
                elapsed = time.time() - st.session_state.pomodoro_state['start_time']
                st.session_state.pomodoro_state['duration'] -= elapsed
                st.session_state.pomodoro_state['is_running'] = False
                st.session_state.pomodoro_state['start_time'] = None
                st.rerun()
        
        if st.button("🔄 Reset", key="pomodoro_reset"):
            st.session_state.pomodoro_state['is_running'] = False
            st.session_state.pomodoro_state['start_time'] = None
            st.session_state.pomodoro_state['duration'] = st.session_state.pomodoro_state['work_duration'] * 60
            st.session_state.pomodoro_state['session_type'] = 'work'
            st.session_state.pomodoro_state['sessions_completed'] = 0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.pomodoro_state['is_running']:
            if remaining > 0:
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.pomodoro_state['is_running'] = False
                st.session_state.pomodoro_state['start_time'] = None
                current_session = st.session_state.pomodoro_state['session_type']
                sessions_completed = st.session_state.pomodoro_state['sessions_completed']
                
                if current_session == 'work':
                    st.session_state.pomodoro_state['sessions_completed'] += 1
                    if st.session_state.pomodoro_state['sessions_completed'] % 4 == 0:
                        st.session_state.pomodoro_state['session_type'] = 'long_break'
                        st.session_state.pomodoro_state['duration'] = st.session_state.pomodoro_state['long_break_duration'] * 60
                    else:
                        st.session_state.pomodoro_state['session_type'] = 'short_break'
                        st.session_state.pomodoro_state['duration'] = st.session_state.pomodoro_state['short_break_duration'] * 60
                    st.success("Work session completed! Time for a break!")
                else:
                    st.session_state.pomodoro_state['session_type'] = 'work'
                    st.session_state.pomodoro_state['duration'] = st.session_state.pomodoro_state['work_duration'] * 60
                    st.success("Break's over! Back to work!")
                st.rerun()
    
    with col2:
        st.subheader("Timer Settings")
        
        work_duration = st.number_input(
            "Work Session (min)",
            min_value=1,
            max_value=60,
            value=st.session_state.pomodoro_state['work_duration'],
            key="work_duration"
        )
        short_break_duration = st.number_input(
            "Short Break (min)",
            min_value=1,
            max_value=30,
            value=st.session_state.pomodoro_state['short_break_duration'],
            key="short_break_duration"
        )
        long_break_duration = st.number_input(
            "Long Break (min)",
            min_value=1,
            max_value=60,
            value=st.session_state.pomodoro_state['long_break_duration'],
            key="long_break_duration"
        )
        
        if st.button("Apply Settings", key="apply_settings"):
            if not st.session_state.pomodoro_state['is_running']:
                st.session_state.pomodoro_state['work_duration'] = work_duration
                st.session_state.pomodoro_state['short_break_duration'] = short_break_duration
                st.session_state.pomodoro_state['long_break_duration'] = long_break_duration
                if st.session_state.pomodoro_state['session_type'] == 'work':
                    st.session_state.pomodoro_state['duration'] = work_duration * 60
                elif st.session_state.pomodoro_state['session_type'] == 'short_break':
                    st.session_state.pomodoro_state['duration'] = short_break_duration * 60
                elif st.session_state.pomodoro_state['session_type'] == 'long_break':
                    st.session_state.pomodoro_state['duration'] = long_break_duration * 60
                st.success("Settings updated!")
                st.rerun()
            else:
                st.warning("Pause the timer first!")
        
        st.metric("Sessions Completed", st.session_state.pomodoro_state['sessions_completed'])
        
        st.subheader("Productivity Tip")
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        st.write("Use the Pomodoro Technique to break your work into focused intervals. "
                "After every 4 work sessions, take a longer break to recharge!")
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    initialize_session_state()
    if not st.session_state.logged_in:
        login_signup_page()
    else:
        st.sidebar.title(f"Hello, {st.session_state.users[st.session_state.current_user]['full_name']}!")
        page = st.sidebar.selectbox(
            "Navigate",
            ["Dashboard", "Tasks", "Habits", "Goals", "Notes", "Pomodoro"],
            format_func=lambda x: f"🚀 {x}" if x == "Dashboard" else 
                                f"📋 {x}" if x == "Tasks" else 
                                f"🔄 {x}" if x == "Habits" else 
                                f"🎯 {x}" if x == "Goals" else 
                                f"📝 {x}" if x == "Notes" else 
                                f"⏰ {x}" if x == "Pomodoro" else x
        )
        if page == "Dashboard":
            dashboard_page()
        elif page == "Tasks":
            enhanced_todo_page()
        elif page == "Habits":
            habits_page()
        elif page == "Goals":
            goals_page()
        elif page == "Notes":
            enhanced_notes_page()
        elif page == "Pomodoro":
            pomodoro_page()
        if st.sidebar.button("🚪 Logout"):
            logout_user()
            st.rerun()

if __name__ == "__main__":
    main()