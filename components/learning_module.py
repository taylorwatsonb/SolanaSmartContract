import streamlit as st
import plotly.express as px
from datetime import datetime

class Achievement:
    def __init__(self, name, description, badge_icon, points):
        self.name = name
        self.description = description
        self.badge_icon = badge_icon
        self.points = points
        self.earned = False
        self.earned_at = None

    def earn(self):
        if not self.earned:
            self.earned = True
            self.earned_at = datetime.now()

class LearningModule:
    def __init__(self):
        # Initialize achievements
        self.achievements = {
            'explorer': Achievement(
                'Block Explorer',
                'Viewed details of 5 different blocks',
                '🔍',
                100
            ),
            'analyst': Achievement(
                'Transaction Analyst',
                'Analyzed 10 different transactions',
                '📊',
                150
            ),
            'networker': Achievement(
                'Network Navigator',
                'Explored network statistics for 5 minutes',
                '🌐',
                200
            ),
            'validator': Achievement(
                'Validation Master',
                'Completed the validator node quiz',
                '✅',
                250
            ),
            'token_master': Achievement(
                'Token Master',
                'Tracked 5 different token transfers',
                '🪙',
                300
            )
        }
        
        # Initialize progress tracking
        if 'learning_progress' not in st.session_state:
            st.session_state.learning_progress = {
                'blocks_viewed': set(),
                'transactions_analyzed': set(),
                'network_stats_time': 0,
                'quiz_scores': {},
                'tokens_tracked': set()
            }

def show_learning_module():
    st.header("🎮 Blockchain Learning Center")
    
    # Initialize learning module
    module = LearningModule()
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["Lessons", "Achievements", "Progress"])
    
    with tab1:
        show_lessons()
    
    with tab2:
        show_achievements(module.achievements)
    
    with tab3:
        show_progress(module.achievements)

def show_lessons():
    st.subheader("📚 Interactive Lessons")
    
    lesson = st.selectbox(
        "Choose a lesson:",
        ["Blockchain Basics", "Transaction Flow", "Consensus Mechanisms", "Smart Contracts", "Token Standards"]
    )
    
    if lesson == "Blockchain Basics":
        show_blockchain_basics()
    elif lesson == "Transaction Flow":
        show_transaction_flow()
    elif lesson == "Consensus Mechanisms":
        show_consensus_mechanisms()
    elif lesson == "Smart Contracts":
        show_smart_contracts()
    else:
        show_token_standards()

def show_blockchain_basics():
    st.write("### Understanding Blockchain Technology")
    
    # Interactive content
    st.write("""
    A blockchain is a distributed ledger that records transactions across a network of computers.
    Let's explore the key components:
    """)
    
    # Interactive elements
    if st.button("1. What is a Block?"):
        st.info("""
        A block contains:
        - Transaction data
        - Timestamp
        - Previous block's hash
        - Nonce
        """)
        
    if st.button("2. How are Blocks Connected?"):
        st.info("""
        Blocks are connected through cryptographic hashes:
        - Each block contains the previous block's hash
        - This creates an immutable chain
        - Any change would break the chain
        """)
    
    # Simple quiz
    st.write("### Quick Quiz")
    answer = st.radio(
        "What makes blockchain immutable?",
        ["The size of blocks", "Cryptographic hash links", "Number of transactions", "Block timestamps"]
    )
    
    if st.button("Check Answer"):
        if answer == "Cryptographic hash links":
            st.success("Correct! The cryptographic links between blocks ensure immutability.")
            update_achievement_progress('quiz_scores', 'blockchain_basics', True)
        else:
            st.error("Try again! Think about how blocks are connected.")

def show_achievements(achievements):
    st.subheader("🏆 Your Achievements")
    
    col1, col2 = st.columns(2)
    
    for i, (key, achievement) in enumerate(achievements.items()):
        with col1 if i % 2 == 0 else col2:
            with st.container():
                st.write(f"{achievement.badge_icon} **{achievement.name}**")
                st.write(achievement.description)
                if achievement.earned:
                    st.success(f"Earned: {achievement.earned_at.strftime('%Y-%m-%d')}")
                    st.write(f"Points: {achievement.points}")
                else:
                    st.info("Not earned yet")

def show_progress(achievements):
    st.subheader("📈 Your Learning Progress")
    
    # Calculate total and earned points
    total_points = sum(a.points for a in achievements.values())
    earned_points = sum(a.points for a in achievements.values() if a.earned)
    
    # Progress bar
    progress = earned_points / total_points if total_points > 0 else 0
    st.progress(progress)
    st.write(f"Total Points: {earned_points}/{total_points}")
    
    # Progress chart
    if st.session_state.learning_progress['quiz_scores']:
        scores = list(st.session_state.learning_progress['quiz_scores'].values())
        topics = list(st.session_state.learning_progress['quiz_scores'].keys())
        
        fig = px.bar(
            x=topics,
            y=scores,
            title="Quiz Performance",
            labels={'x': 'Topic', 'y': 'Score'},
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

def update_achievement_progress(category, key, value):
    """Update progress tracking"""
    if category not in st.session_state.learning_progress:
        st.session_state.learning_progress[category] = {}
    
    if isinstance(st.session_state.learning_progress[category], dict):
        st.session_state.learning_progress[category][key] = value
    elif isinstance(st.session_state.learning_progress[category], set):
        st.session_state.learning_progress[category].add(key)
