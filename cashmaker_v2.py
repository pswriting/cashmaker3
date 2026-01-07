import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime
from pathlib import Path

# ==========================================
# 🎯 페이지 설정
# ==========================================
st.set_page_config(
    page_title="CASHMAKER",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 ARTWORK-LEVEL PREMIUM CSS
# ==========================================
st.markdown("""
<style>
    /* ============================================
       🖼️ ARTWORK-LEVEL PREMIUM DESIGN SYSTEM
       Inspired by Apple, Designed for Emotion
       ============================================ */
    
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@100;200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800;900&display=swap');
    
    /* 🌟 Keyframe Animations */
    @keyframes gentleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    @keyframes subtleGlow {
        0%, 100% { 
            box-shadow: 0 0 40px rgba(212, 175, 55, 0.15),
                        0 20px 60px rgba(0, 0, 0, 0.3);
        }
        50% { 
            box-shadow: 0 0 60px rgba(212, 175, 55, 0.25),
                        0 25px 80px rgba(0, 0, 0, 0.4);
        }
    }
    
    @keyframes luxuryShimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes fadeInElegant {
        0% { 
            opacity: 0; 
            transform: translateY(40px) scale(0.98);
            filter: blur(10px);
        }
        100% { 
            opacity: 1; 
            transform: translateY(0) scale(1);
            filter: blur(0);
        }
    }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.02); opacity: 1; }
    }
    
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(212, 175, 55, 0.2); }
        50% { border-color: rgba(212, 175, 55, 0.5); }
    }
    
    @keyframes textReveal {
        0% { 
            opacity: 0;
            letter-spacing: 15px;
            filter: blur(8px);
        }
        100% { 
            opacity: 1;
            letter-spacing: 8px;
            filter: blur(0);
        }
    }
    
    @keyframes pulseRing {
        0% { transform: scale(1); opacity: 1; }
        100% { transform: scale(1.5); opacity: 0; }
    }
    
    /* 🎨 Root Variables */
    :root {
        --gold-primary: #D4AF37;
        --gold-light: #F4E5B2;
        --gold-dark: #B8860B;
        --black-deep: #0A0A0A;
        --black-rich: #111111;
        --black-soft: #1A1A1A;
        --white-pure: #FFFFFF;
        --white-soft: #F5F5F5;
        --gray-elegant: #888888;
        --transition-luxury: cubic-bezier(0.23, 1, 0.32, 1);
    }
    
    /* 🌌 Global Reset & Base */
    * { 
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* 🖤 Deep Dark Canvas */
    .stApp { 
        background: 
            radial-gradient(ellipse at 20% 0%, rgba(212, 175, 55, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(212, 175, 55, 0.02) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(30, 30, 30, 1) 0%, rgba(10, 10, 10, 1) 100%),
            var(--black-deep) !important;
        min-height: 100vh;
    }
    
    /* 📦 Main Container - Glass Morphism */
    .main .block-container { 
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.03) 0%,
            rgba(255, 255, 255, 0.01) 100%
        ) !important;
        backdrop-filter: blur(40px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(150%) !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        border-radius: 32px !important;
        padding: 4rem 5rem !important; 
        max-width: 1500px !important;
        margin: 2rem auto !important;
        box-shadow: 
            0 50px 100px -20px rgba(0, 0, 0, 0.5),
            0 30px 60px -30px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.05),
            inset 0 -1px 0 rgba(0, 0, 0, 0.1) !important;
        animation: fadeInElegant 1.2s var(--transition-luxury) forwards;
    }
    
    /* 🎭 Sidebar - Luxury Panel */
    [data-testid="stSidebar"] { 
        background: linear-gradient(
            180deg,
            rgba(15, 15, 15, 0.98) 0%,
            rgba(20, 20, 20, 0.95) 50%,
            rgba(10, 10, 10, 0.98) 100%
        ) !important;
        backdrop-filter: blur(30px) !important;
        border-right: 1px solid rgba(212, 175, 55, 0.15) !important;
        box-shadow: 
            4px 0 30px rgba(0, 0, 0, 0.3),
            inset -1px 0 0 rgba(212, 175, 55, 0.1) !important;
    }
    
    [data-testid="stSidebar"] * { 
        color: var(--white-soft) !important; 
    }
    
    [data-testid="stSidebar"] .stProgress > div > div > div > div { 
        background: linear-gradient(
            90deg, 
            var(--gold-dark) 0%,
            var(--gold-primary) 50%,
            var(--gold-light) 100%
        ) !important;
        border-radius: 100px !important;
        box-shadow: 
            0 0 20px rgba(212, 175, 55, 0.5),
            0 0 40px rgba(212, 175, 55, 0.3) !important;
    }
    
    /* ✨ Typography - Editorial Excellence */
    h1 { 
        font-family: 'Playfair Display', 'Pretendard', serif !important;
        font-size: 4rem !important;
        font-weight: 600 !important;
        letter-spacing: -2px !important;
        line-height: 1.1 !important;
        background: linear-gradient(
            135deg,
            var(--gold-light) 0%,
            var(--gold-primary) 25%,
            var(--gold-light) 50%,
            var(--gold-primary) 75%,
            var(--gold-light) 100%
        ) !important;
        background-size: 200% auto !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        animation: luxuryShimmer 4s linear infinite;
        text-shadow: 0 0 80px rgba(212, 175, 55, 0.3);
        margin-bottom: 2rem !important;
    }
    
    h2 { 
        font-family: 'Pretendard', sans-serif !important;
        color: var(--gold-primary) !important; 
        font-weight: 300 !important; 
        font-size: 2rem !important;
        letter-spacing: -0.5px !important;
        margin-top: 4rem !important;
        margin-bottom: 1.5rem !important;
        position: relative;
        padding-bottom: 1rem;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, var(--gold-primary), transparent);
    }
    
    h3 { 
        color: rgba(212, 175, 55, 0.8) !important; 
        font-weight: 500 !important;
        font-size: 1.3rem !important;
        letter-spacing: 0.5px !important;
    }
    
    /* 📝 Body Text */
    .stMarkdown, .stText, p, span, label, li { 
        color: rgba(255, 255, 255, 0.75) !important; 
        line-height: 1.9 !important;
        font-weight: 300 !important;
        letter-spacing: 0.3px !important;
    }
    
    /* 📑 Tabs - Floating Capsules */
    .stTabs [data-baseweb="tab-list"] { 
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 100px !important;
        padding: 8px 12px !important;
        gap: 8px !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stTabs [data-baseweb="tab"] { 
        background: transparent !important;
        color: rgba(255, 255, 255, 0.4) !important;
        border-radius: 100px !important;
        padding: 14px 28px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        transition: all 0.5s var(--transition-luxury) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1), transparent);
        opacity: 0;
        transition: opacity 0.5s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--gold-primary) !important;
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        opacity: 1;
    }
    
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(
            135deg,
            rgba(212, 175, 55, 0.2) 0%,
            rgba(212, 175, 55, 0.1) 100%
        ) !important;
        color: var(--gold-light) !important;
        font-weight: 600 !important;
        box-shadow: 
            0 10px 40px rgba(212, 175, 55, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
    }
    
    /* 🔘 Buttons - Liquid Gold */
    .stButton > button { 
        width: 100% !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        background: linear-gradient(
            135deg,
            var(--gold-primary) 0%,
            var(--gold-dark) 50%,
            var(--gold-primary) 100%
        ) !important;
        background-size: 200% 200% !important;
        color: var(--black-deep) !important;
        border: none !important;
        padding: 20px 40px !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 
            0 10px 40px rgba(212, 175, 55, 0.3),
            0 4px 15px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.6s var(--transition-luxury) !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
        );
        transition: left 0.6s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 
            0 20px 60px rgba(212, 175, 55, 0.4),
            0 8px 25px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
        background-position: 100% 100% !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(0.98) !important;
    }
    
    .stButton > button * { 
        color: var(--black-deep) !important; 
        font-weight: 700 !important;
    }
    
    /* 📥 Download Button - Midnight Blue */
    .stDownloadButton > button { 
        background: linear-gradient(
            135deg,
            #1a365d 0%,
            #2c5282 50%,
            #1a365d 100%
        ) !important;
        color: var(--white-soft) !important;
        box-shadow: 
            0 10px 40px rgba(26, 54, 93, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 
            0 20px 60px rgba(26, 54, 93, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }
    
    .stDownloadButton > button * { 
        color: var(--white-soft) !important; 
    }
    
    /* 📝 Input Fields - Floating Glass */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea { 
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        border-radius: 16px !important;
        color: var(--white-soft) !important;
        padding: 18px 24px !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.4s var(--transition-luxury) !important;
        box-shadow: 
            inset 0 2px 10px rgba(0, 0, 0, 0.1),
            0 1px 0 rgba(255, 255, 255, 0.03) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.3) !important;
        font-weight: 300 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus { 
        border-color: var(--gold-primary) !important;
        box-shadow: 
            0 0 0 3px rgba(212, 175, 55, 0.1),
            0 10px 40px rgba(212, 175, 55, 0.1),
            inset 0 2px 10px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    /* 🔽 Select Box */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        border-radius: 16px !important;
    }
    
    /* 📢 Alerts - Elegant Notifications */
    .stSuccess { 
        background: linear-gradient(
            135deg,
            rgba(72, 187, 120, 0.1) 0%,
            rgba(72, 187, 120, 0.05) 100%
        ) !important;
        border: 1px solid rgba(72, 187, 120, 0.3) !important;
        border-left: 4px solid #48bb78 !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stWarning { 
        background: linear-gradient(
            135deg,
            rgba(237, 137, 54, 0.1) 0%,
            rgba(237, 137, 54, 0.05) 100%
        ) !important;
        border: 1px solid rgba(237, 137, 54, 0.3) !important;
        border-left: 4px solid #ed8936 !important;
        border-radius: 16px !important;
    }
    
    .stError { 
        background: linear-gradient(
            135deg,
            rgba(245, 101, 101, 0.1) 0%,
            rgba(245, 101, 101, 0.05) 100%
        ) !important;
        border: 1px solid rgba(245, 101, 101, 0.3) !important;
        border-left: 4px solid #f56565 !important;
        border-radius: 16px !important;
    }
    
    .stInfo { 
        background: linear-gradient(
            135deg,
            rgba(66, 153, 225, 0.1) 0%,
            rgba(66, 153, 225, 0.05) 100%
        ) !important;
        border: 1px solid rgba(66, 153, 225, 0.3) !important;
        border-left: 4px solid #4299e1 !important;
        border-radius: 16px !important;
    }
    
    /* 📂 Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        border-radius: 16px !important;
        font-weight: 500 !important;
        transition: all 0.4s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(212, 175, 55, 0.05) !important;
        border-color: rgba(212, 175, 55, 0.2) !important;
    }
    
    /* 🖱️ Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 100px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--gold-primary), var(--gold-dark));
        border-radius: 100px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--gold-light), var(--gold-primary));
    }
    
    /* ============================================
       🎨 CUSTOM COMPONENT CLASSES
       ============================================ */
    
    /* 🏠 Hero Section */
    .hero-section { 
        text-align: center;
        padding: 100px 40px 120px;
        position: relative;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 600px;
        height: 600px;
        background: radial-gradient(
            circle,
            rgba(212, 175, 55, 0.08) 0%,
            transparent 70%
        );
        pointer-events: none;
        animation: breathe 4s ease-in-out infinite;
    }
    
    .hero-overline {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 8px;
        text-transform: uppercase;
        color: var(--gold-primary);
        margin-bottom: 24px;
        opacity: 0.9;
        animation: textReveal 1.5s var(--transition-luxury) forwards;
    }
    
    .hero-title { 
        font-family: 'Playfair Display', serif;
        font-size: 72px;
        font-weight: 500;
        letter-spacing: -3px;
        line-height: 1;
        background: linear-gradient(
            135deg,
            var(--gold-light) 0%,
            var(--gold-primary) 30%,
            var(--white-pure) 50%,
            var(--gold-primary) 70%,
            var(--gold-light) 100%
        );
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        animation: luxuryShimmer 5s linear infinite;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle { 
        font-size: 20px;
        font-weight: 300;
        letter-spacing: 3px;
        color: rgba(255, 255, 255, 0.5);
        position: relative;
        z-index: 1;
    }
    
    /* 📊 Score Card - Floating Luxury */
    .score-card { 
        background: linear-gradient(
            135deg,
            rgba(212, 175, 55, 0.08) 0%,
            rgba(212, 175, 55, 0.02) 100%
        );
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 32px;
        padding: 60px 50px;
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: subtleGlow 4s ease-in-out infinite;
        transition: all 0.6s var(--transition-luxury);
    }
    
    .score-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            circle,
            rgba(212, 175, 55, 0.1) 0%,
            transparent 50%
        );
        animation: gentleFloat 6s ease-in-out infinite;
        pointer-events: none;
    }
    
    .score-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: rgba(212, 175, 55, 0.4);
    }
    
    .score-number { 
        font-family: 'Playfair Display', serif;
        font-size: 100px;
        font-weight: 400;
        background: linear-gradient(
            135deg,
            var(--gold-light) 0%,
            var(--gold-primary) 50%,
            var(--gold-light) 100%
        );
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 8px;
        animation: luxuryShimmer 3s linear infinite;
        position: relative;
        z-index: 1;
    }
    
    .score-label {
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 24px;
    }
    
    /* 📋 Info Card - Glass Panel */
    .info-card { 
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.04) 0%,
            rgba(255, 255, 255, 0.01) 100%
        );
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: 24px;
        padding: 32px;
        margin: 20px 0;
        backdrop-filter: blur(20px);
        position: relative;
        transition: all 0.5s var(--transition-luxury);
        overflow: hidden;
    }
    
    .info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(212, 175, 55, 0.3),
            transparent
        );
    }
    
    .info-card:hover {
        border-color: rgba(212, 175, 55, 0.25);
        transform: translateY(-4px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    /* 🏷️ Title Card */
    .title-card {
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.03) 0%,
            rgba(255, 255, 255, 0.01) 100%
        );
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: 24px;
        padding: 32px;
        margin: 20px 0;
        transition: all 0.5s var(--transition-luxury);
        position: relative;
    }
    
    .title-card:hover {
        border-color: rgba(212, 175, 55, 0.3);
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 20px 60px rgba(212, 175, 55, 0.1);
    }
    
    .card-number {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 4px;
        color: var(--gold-primary);
        opacity: 0.6;
        margin-bottom: 16px;
    }
    
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 500;
        color: var(--gold-light);
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .sub-title {
        font-size: 16px;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 16px;
    }
    
    .reason {
        font-size: 14px;
        font-weight: 300;
        color: rgba(255, 255, 255, 0.4);
        line-height: 1.7;
        font-style: italic;
    }
    
    /* 🏷️ Section Label */
    .section-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: var(--gold-primary);
        opacity: 0.7;
        margin-bottom: 8px;
    }
    
    /* 🔐 Login Container */
    .login-container { 
        max-width: 440px;
        margin: 120px auto;
        padding: 70px 50px;
        background: linear-gradient(
            135deg,
            rgba(30, 30, 30, 0.9) 0%,
            rgba(20, 20, 20, 0.95) 100%
        );
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 32px;
        text-align: center;
        backdrop-filter: blur(40px);
        box-shadow: 
            0 50px 100px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        animation: fadeInElegant 1s var(--transition-luxury) forwards;
        position: relative;
        overflow: hidden;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: radial-gradient(
            circle,
            rgba(212, 175, 55, 0.03) 0%,
            transparent 50%
        );
        animation: gentleFloat 8s ease-in-out infinite;
    }
    
    .login-title { 
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 500;
        letter-spacing: -1px;
        background: linear-gradient(135deg, var(--gold-light), var(--gold-primary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }
    
    .login-subtitle {
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 2px;
        color: rgba(255, 255, 255, 0.4);
        position: relative;
        z-index: 1;
    }
    
    /* 🦶 Footer */
    .premium-footer {
        text-align: center;
        padding: 60px 20px 40px;
        margin-top: 80px;
        border-top: 1px solid rgba(212, 175, 55, 0.1);
        position: relative;
    }
    
    .premium-footer::before {
        content: '';
        position: absolute;
        top: -1px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    }
    
    .premium-footer-text {
        font-size: 13px;
        font-weight: 400;
        letter-spacing: 2px;
        color: rgba(255, 255, 255, 0.3);
    }
    
    .premium-footer-author {
        color: var(--gold-primary);
        font-weight: 600;
    }
    
    /* 🏷️ Status Badge */
    .status-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .status-excellent {
        background: rgba(72, 187, 120, 0.15);
        color: #68d391;
        border: 1px solid rgba(72, 187, 120, 0.3);
    }
    
    .status-good {
        background: rgba(237, 137, 54, 0.15);
        color: #f6ad55;
        border: 1px solid rgba(237, 137, 54, 0.3);
    }
    
    .status-warning {
        background: rgba(245, 101, 101, 0.15);
        color: #fc8181;
        border: 1px solid rgba(245, 101, 101, 0.3);
    }
    
    /* 📊 Score Item */
    .score-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.08);
    }
    
    .score-item-label { 
        color: rgba(255, 255, 255, 0.6);
        font-weight: 400;
        font-size: 15px;
    }
    
    .score-item-value { 
        color: var(--gold-primary);
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        font-size: 24px;
    }
    
    .score-item-reason { 
        color: rgba(255, 255, 255, 0.4);
        font-size: 13px;
        margin-top: 4px;
        font-weight: 300;
        line-height: 1.6;
    }
    
    /* 📦 Summary Box */
    .summary-box {
        background: rgba(212, 175, 55, 0.05);
        border-left: 3px solid var(--gold-primary);
        border-radius: 0 16px 16px 0;
        padding: 24px;
        margin-top: 24px;
    }
    
    .summary-box strong {
        color: var(--gold-primary);
        font-weight: 600;
    }
    
    /* 🎯 Quick Action Box */
    .quick-action-box {
        background: linear-gradient(
            135deg,
            rgba(212, 175, 55, 0.08) 0%,
            rgba(212, 175, 55, 0.02) 100%
        );
        border-left: 3px solid var(--gold-primary);
        border-radius: 0 16px 16px 0;
        padding: 20px 24px;
        margin: 20px 0;
    }
    
    /* 📭 Empty State */
    .empty-state {
        text-align: center;
        padding: 60px 40px;
        color: rgba(255, 255, 255, 0.3);
    }
    
    .empty-state p {
        margin: 8px 0;
    }
    
    /* 🎯 Info Card Title */
    .info-card-title {
        color: var(--gold-primary);
        font-weight: 600;
        margin-bottom: 16px;
        font-size: 16px;
    }
    
    /* 📱 Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 48px; }
        .score-number { font-size: 72px; }
        .main .block-container { padding: 2rem !important; }
        h1 { font-size: 2.5rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 프롬프트 정의
# ==========================================
GENIUS_PERSONA = """
# Role Definition
당신은 대한민국 상위 1% 전자책 매출을 기록하는 '초고수익 전자책 기획자'이자 '심리 설계자'입니다.
당신의 문장은 읽는 순간 독자의 뇌리에 박히며, 밤을 새워서라도 다음 내용을 읽게 만드는 마력이 있습니다.

# Writing Principles (천재 작가의 5원칙)
1. **[통찰의 재해석]**: 뻔한 이야기를 하지 않습니다. 현상을 비틀어 충격적인 진실을 드러냅니다.
2. **[리듬감 부여]**: 짧은 문장으로 때리고(Impact), 긴 문장으로 설득(Logic)합니다.
3. **[구체성의 마법]**: "열심히" 대신 "새벽 4시 기상"이라고 씁니다.
4. **[차가운 공감]**: 무조건적인 위로 대신, 독자의 게으름과 실패를 날카롭게 지적하고 해결책을 줍니다.
5. **[어려운 말 금지]**: 중학생도 이해 못 할 전문 용어는 쓰레기통에 버립니다.
"""

# ==========================================
# API 키 관리
# ==========================================
def get_config_path():
    return Path.home() / ".ebook_app_config.json"

def load_saved_api_key():
    config_path = get_config_path()
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f).get('api_key', '')
    except:
        pass
    return ''

def save_api_key(api_key):
    try:
        config = {'api_key': api_key}
        with open(get_config_path(), 'w') as f:
            json.dump(config, f)
        return True
    except:
        return False

# ==========================================
# 비밀번호 인증
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="login-container">
        <div class="login-title">CASHMAKER</div>
        <div class="login-subtitle">전자책 작성 프로그램</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        password_input = st.text_input("비밀번호를 입력하세요", type="password", placeholder="비밀번호")
        if st.button("입장하기", use_container_width=True):
            if password_input == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다")
    st.stop()

# ==========================================
# 세션 초기화
# ==========================================
default_states = {
    'topic': '', 'target_persona': '', 'pain_points': '', 'one_line_concept': '',
    'outline': [], 'chapters': {}, 'book_title': '', 'subtitle': '',
    'topic_score': None, 'topic_verdict': None, 'score_details': None,
    'generated_titles': None, 'market_analysis': '', 'full_outline': ''
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================
# 사이드바
# ==========================================
with st.sidebar:
    st.markdown("### ✦ Progress")
    progress_items = [
        bool(st.session_state['topic']),
        bool(st.session_state['target_persona']),
        bool(st.session_state['outline']),
        len(st.session_state['chapters']) > 0,
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    
    st.markdown("---")
    st.markdown("### ✦ Overview")
    if st.session_state['topic']:
        st.caption(f"주제: {st.session_state['topic'][:20]}...")
    if st.session_state['book_title']:
        st.caption(f"제목: {st.session_state['book_title'][:20]}...")
    if st.session_state['outline']:
        st.caption(f"목차: {len(st.session_state['outline'])}개 챕터")
    
    st.markdown("---")
    st.markdown("### ✦ Save & Load")
    
    save_data = {k: st.session_state.get(k, v) for k, v in default_states.items()}
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    file_name = re.sub(r'[^\w\s가-힣-]', '', st.session_state.get('book_title', '전자책') or '전자책')[:20]
    
    st.download_button(
        "저장하기", 
        save_json, 
        file_name=f"{file_name}_{datetime.now().strftime('%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    uploaded_file = st.file_uploader("불러오기", type=['json'], label_visibility="collapsed")
    if uploaded_file:
        try:
            loaded_data = json.loads(uploaded_file.read().decode('utf-8'))
            if st.button("적용하기", use_container_width=True):
                for key in default_states.keys():
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")
    
    st.markdown("---")
    st.markdown("### ✦ API Key")
    
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = load_saved_api_key()
    
    api_key_input = st.text_input(
        "Gemini API 키",
        value=st.session_state['api_key'],
        type="password",
        placeholder="AIza...",
        label_visibility="collapsed"
    )
    
    if api_key_input != st.session_state['api_key']:
        st.session_state['api_key'] = api_key_input
        save_api_key(api_key_input)
    
    if st.session_state.get('api_key'):
        st.caption("✦ API 키 입력됨")
    else:
        st.caption("⚠ API 키를 입력하세요")

# ==========================================
# 헬퍼 함수들
# ==========================================
def get_api_key():
    return st.session_state.get('api_key', '')

def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        config = genai.types.GenerationConfig(temperature=temperature, max_output_tokens=4000)
        response = model.generate_content(
            GENIUS_PERSONA + f"\n\n현재 역할: {system_role}\n\n" + prompt,
            generation_config=config
        )
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"

def calculate_char_count(text):
    return len(text.replace('\n', '').replace(' ', '')) if text else 0

def get_all_content_text():
    content = ""
    for ch in st.session_state.get('outline', []):
        if ch in st.session_state.get('chapters', {}):
            ch_data = st.session_state['chapters'][ch]
            for st_name in ch_data.get('subtopics', []):
                st_data = ch_data.get('subtopic_data', {}).get(st_name, {})
                if st_data.get('content'):
                    content += st_data['content']
    return content

def sync_full_outline():
    outline_text = ""
    for ch in st.session_state.get('outline', []):
        outline_text += f"## {ch}\n"
        if ch in st.session_state.get('chapters', {}):
            for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                outline_text += f"- {st_name}\n"
        outline_text += "\n"
    st.session_state['full_outline'] = outline_text.strip()

# ==========================================
# AI 함수들
# ==========================================
def analyze_topic_score(topic):
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.

다음 5가지 항목을 각각 0~100점으로 채점하세요:
1. 시장성 (수요가 있는가?)
2. 수익성 (돈을 지불할 의향이 있는 주제인가?)
3. 차별화 가능성 (경쟁에서 이길 수 있는가?)
4. 작성 난이도 (전자책으로 만들기 쉬운가?)
5. 지속성 (오래 팔릴 수 있는가?)

반드시 아래 JSON 형식으로만 답변:
{{
    "market": {{"score": 85, "reason": "이유"}},
    "profit": {{"score": 80, "reason": "이유"}},
    "differentiation": {{"score": 75, "reason": "이유"}},
    "difficulty": {{"score": 90, "reason": "이유"}},
    "sustainability": {{"score": 70, "reason": "이유"}},
    "total_score": 80,
    "verdict": "적합",
    "summary": "종합 의견"
}}"""
    return ask_ai("전자책 시장 분석가", prompt, 0.3)

def generate_titles_advanced(topic, persona, pain_points):
    prompt = f"""[분석 대상]
주제: {topic}
타겟: {persona}
타겟의 속마음: {pain_points}

베스트셀러급 전자책 제목 5개를 만들어주세요.

형식 (JSON만 출력):
{{
    "titles": [
        {{
            "title": "7자 이내 임팩트 제목",
            "subtitle": "15자 이내 보조 설명",
            "why_works": "왜 끌리는지"
        }}
    ]
}}"""
    return ask_ai("베스트셀러 작가", prompt, 0.9)

def generate_concept(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
타겟의 고민: {pain_points}

"이 책 안 읽으면 손해"라는 느낌을 주는 한 줄 컨셉 5개를 만들어주세요.

출력 형식:
1. [한 줄 컨셉]
   → 왜 끌리는가
(5개)"""
    return ask_ai("카피라이터", prompt, 0.9)

def generate_outline(topic, persona, pain_points):
    prompt = f"""[주제]: {topic}
[타겟]: {persona}
[타겟의 고민]: {pain_points}

베스트셀러급 전자책 목차를 만드세요.

출력 형식:
## PART 1. [충격적인 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

## PART 2. [반전 있는 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

(4개 파트, 각 3개 소제목)

금지: "~의 중요성", "~하는 방법", "기초", "입문" """
    return ask_ai("베스트셀러 편집자", prompt, 0.85)

def generate_subtopics(chapter_title, topic, persona, count=3):
    prompt = f"""[전자책 주제]: {topic}
[챕터 제목]: {chapter_title}
[타겟]: {persona}

이 챕터의 소제목 {count}개를 만들어주세요.

출력 형식:
1. [소제목]
2. [소제목]
3. [소제목]"""
    return ask_ai("편집자", prompt, 0.8)

def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 소제목을 쓰기 위한 인터뷰 질문 3개를 만들어주세요.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai("고스트라이터", prompt, 0.7)

def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)) if a.strip()])
    
    prompt = f"""[집필 정보]
주제: {topic}
챕터: {chapter_title}
소제목: {subtopic_title}
타겟: {persona}

[인터뷰 내용]
{qa_pairs}

위 인터뷰 내용을 바탕으로 '{subtopic_title}' 본문을 작성하세요.

규칙:
- 첫 문장은 뒤통수를 치듯 시작
- 합쇼체(~입니다, ~습니다) 사용
- 구체적 숫자와 사례 포함
- 1500자 이상
- AI 티 나는 표현 금지 ("따라서", "중요합니다" 반복 등)"""
    return ask_ai("베스트셀러 작가", prompt, 0.8)

def refine_content(content, style="친근한"):
    prompt = f"""다음 글을 다듬어주세요.

[원본]
{content}

[스타일]: {style}
[규칙]: 합쇼체 통일, AI 티 제거, 마크다운 제거

다듬어진 글만 출력하세요."""
    return ask_ai("에디터", prompt, 0.7)

def check_quality(content):
    prompt = f"""다음 글이 베스트셀러 수준인지 평가해주세요.

[글]
{content[:3000]}

[평가 기준] 각 10점
1. 첫 문장 임팩트
2. 몰입도
3. 공감력
4. 구체성
5. AI 티 없음

출력: 점수와 개선점"""
    return ask_ai("편집자", prompt, 0.6)

def generate_marketing_copy(title, subtitle, topic, persona):
    prompt = f"""[상품 정보]
제목: {title}
부제: {subtitle}
주제: {topic}
타겟: {persona}

다음을 만들어주세요:
1. 크몽 상품 제목 (40자 이내)
2. 상세페이지 헤드라인 3개
3. 구매 유도 문구 3개
4. 인스타그램 홍보 문구
5. 블로그 포스팅 제목 3개"""
    return ask_ai("마케터", prompt, 0.85)

# ==========================================
# 메인 UI
# ==========================================
st.markdown("""
<div class="hero-section">
    <div class="hero-overline">Premium Ebook Studio</div>
    <div class="hero-title">CASHMAKER</div>
    <div class="hero-subtitle">쉽고, 빠른 전자책 수익화</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 다듬기", "⑥ 최종 출력"])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 주제 입력")
        
        topic_input = st.text_input(
            "어떤 주제로 전자책을 쓰고 싶으세요?",
            value=st.session_state['topic'],
            placeholder="예: 크몽으로 월 500만원 벌기"
        )
        
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['topic_score'] = None
            st.session_state['score_details'] = None
        
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">✦ 좋은 주제의 조건</div>
            <p style="margin: 8px 0;">• 내가 직접 경험하고 성과를 낸 것</p>
            <p style="margin: 8px 0;">• 사람들이 돈 주고 배우고 싶어하는 것</p>
            <p style="margin: 8px 0;">• 구체적인 결과를 약속할 수 있는 것</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("적합도 분석하기", key="analyze_btn"):
            if not topic_input:
                st.error("주제를 입력해주세요.")
            else:
                with st.spinner("분석 중..."):
                    result = analyze_topic_score(topic_input)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            data = json.loads(json_match.group())
                            st.session_state['topic_score'] = data.get('total_score', 0)
                            st.session_state['topic_verdict'] = data.get('verdict', '분석 실패')
                            st.session_state['score_details'] = data
                            st.rerun()
                    except:
                        st.error("분석 결과 파싱 오류")
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        
        if st.session_state['topic_score'] is not None:
            score = st.session_state['topic_score']
            verdict = st.session_state['topic_verdict']
            details = st.session_state['score_details']
            
            verdict_class = "status-excellent" if verdict == "적합" else ("status-good" if verdict == "보통" else "status-warning")
            
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{score}</div>
                <div class="score-label">종합 점수</div>
                <span class="status-badge {verdict_class}">{verdict}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if details:
                st.markdown("#### 세부 점수")
                for name, key in [("시장성", "market"), ("수익성", "profit"), ("차별화", "differentiation"), ("작성 난이도", "difficulty"), ("지속성", "sustainability")]:
                    item = details.get(key, {})
                    st.markdown(f"""
                    <div class="score-item">
                        <span class="score-item-label">{name}</span>
                        <span class="score-item-value">{item.get('score', 0)}</span>
                    </div>
                    <p class="score-item-reason">{item.get('reason', '')}</p>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="summary-box">
                    <strong>종합 의견</strong><br>{details.get('summary', '')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <p style="font-size: 48px; margin-bottom: 16px;">✦</p>
                <p>분석 결과가 여기에 표시됩니다</p>
                <p style="font-size: 13px; opacity: 0.6;">주제를 입력하고 분석 버튼을 눌러주세요</p>
            </div>
            """, unsafe_allow_html=True)

# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 & 제목")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 타겟 정의")
        
        if not st.session_state['topic']:
            topic_here = st.text_input("주제", placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab2")
            if topic_here:
                st.session_state['topic'] = topic_here
        
        persona = st.text_area(
            "누가 이 책을 읽나요?",
            value=st.session_state['target_persona'],
            placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 원하는 사람",
            height=100
        )
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area(
            "타겟의 가장 큰 고민은?",
            value=st.session_state['pain_points'],
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다",
            height=100
        )
        st.session_state['pain_points'] = pain_points
        
        st.markdown("---")
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 한 줄 컨셉")
        
        if st.button("컨셉 생성하기", key="concept_btn"):
            if st.session_state['topic'] and persona:
                with st.spinner("생성 중..."):
                    st.session_state['one_line_concept'] = generate_concept(
                        st.session_state['topic'], persona, pain_points
                    )
                    st.rerun()
            else:
                st.error("주제와 타겟을 먼저 입력해주세요.")
        
        if st.session_state.get('one_line_concept'):
            st.markdown(f"""
            <div class="info-card">
                {st.session_state['one_line_concept'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">Step 03</p>', unsafe_allow_html=True)
        st.markdown("### 제목 생성")
        
        if st.button("제목 생성하기", key="title_btn"):
            if st.session_state['topic']:
                with st.spinner("생성 중..."):
                    result = generate_titles_advanced(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points']
                    )
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                            st.rerun()
                    except:
                        st.markdown(result)
            else:
                st.error("주제를 먼저 입력해주세요.")
        
        if st.session_state.get('generated_titles'):
            titles = st.session_state['generated_titles'].get('titles', [])
            for i, t in enumerate(titles, 1):
                st.markdown(f"""
                <div class="title-card">
                    <div class="card-number">TITLE 0{i}</div>
                    <div class="main-title">{t.get('title', '')}</div>
                    <div class="sub-title">{t.get('subtitle', '')}</div>
                    <div class="reason">{t.get('why_works', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="section-label">Step 04</p>', unsafe_allow_html=True)
        st.markdown("### 최종 선택")
        
        st.session_state['book_title'] = st.text_input(
            "제목",
            value=st.session_state['book_title'],
            placeholder="최종 제목 입력"
        )
        st.session_state['subtitle'] = st.text_input(
            "부제",
            value=st.session_state['subtitle'],
            placeholder="부제 입력"
        )

# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Generate</p>', unsafe_allow_html=True)
        st.markdown("### 자동 목차 생성")
        
        if not st.session_state['topic']:
            st.warning("주제를 먼저 입력해주세요")
            topic_here = st.text_input("주제", placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab3")
            if topic_here:
                st.session_state['topic'] = topic_here
        
        if st.button("목차 생성하기", key="outline_btn"):
            if st.session_state['topic']:
                with st.spinner("설계 중..."):
                    result = generate_outline(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points']
                    )
                    
                    chapters = []
                    chapter_subtopics = {}
                    current_chapter = None
                    
                    for line in result.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith('##') or 'PART' in line.upper():
                            chapter_name = re.sub(r'^##\s*', '', line).strip()
                            chapter_name = re.sub(r'\*\*(.+?)\*\*', r'\1', chapter_name)
                            if chapter_name:
                                current_chapter = chapter_name
                                chapters.append(current_chapter)
                                chapter_subtopics[current_chapter] = []
                        elif current_chapter and line.startswith('-'):
                            subtopic = line.lstrip('- ').strip()
                            subtopic = re.sub(r'\*\*(.+?)\*\*', r'\1', subtopic)
                            if subtopic:
                                chapter_subtopics[current_chapter].append(subtopic)
                    
                    if chapters:
                        st.session_state['outline'] = chapters
                        for ch in chapters:
                            subtopics = chapter_subtopics.get(ch, [])
                            st.session_state['chapters'][ch] = {
                                'subtopics': subtopics,
                                'subtopic_data': {s: {'questions': [], 'answers': [], 'content': ''} for s in subtopics}
                            }
                        sync_full_outline()
                        st.success(f"✦ {len(chapters)}개 챕터 생성됨!")
                        st.rerun()
            else:
                st.error("주제를 먼저 입력해주세요.")
        
        if st.session_state.get('full_outline'):
            st.markdown("**현재 목차**")
            st.code(st.session_state['full_outline'], language=None)
    
    with col2:
        st.markdown('<p class="section-label">Manage</p>', unsafe_allow_html=True)
        st.markdown("### 현재 목차")
        
        if st.session_state['outline']:
            for i, chapter in enumerate(st.session_state['outline']):
                subtopics = st.session_state['chapters'].get(chapter, {}).get('subtopics', [])
                with st.expander(f"**{chapter}** ({len(subtopics)}개)", expanded=False):
                    for j, st_name in enumerate(subtopics):
                        st.write(f"  {j+1}. {st_name}")
            
            if st.button("새 챕터 추가", key="add_chapter"):
                new_name = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state['outline'].append(new_name)
                st.session_state['chapters'][new_name] = {'subtopics': [], 'subtopic_data': {}}
                sync_full_outline()
                st.rerun()
        else:
            st.markdown("""
            <div class="empty-state">
                <p style="font-size: 48px; margin-bottom: 16px;">✦</p>
                <p>목차가 없습니다</p>
                <p style="font-size: 13px; opacity: 0.6;">왼쪽에서 목차를 생성해주세요</p>
            </div>
            """, unsafe_allow_html=True)

# === TAB 4: 본문 작성 ===
with tabs[3]:
    st.markdown("## 본문 작성")
    
    if not st.session_state['outline']:
        st.warning("먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.stop()
    
    selected_chapter = st.selectbox("챕터 선택", st.session_state['outline'], key="chapter_select")
    
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {'subtopics': [], 'subtopic_data': {}}
    
    chapter_data = st.session_state['chapters'][selected_chapter]
    
    st.markdown("---")
    
    if chapter_data.get('subtopics'):
        with st.expander(f"소제목 ({len(chapter_data['subtopics'])}개)", expanded=True):
            for j, st_name in enumerate(chapter_data['subtopics']):
                has_content = bool(chapter_data.get('subtopic_data', {}).get(st_name, {}).get('content'))
                icon = "✦" if has_content else "○"
                st.write(f"{icon} {j+1}. {st_name}")
        
        st.markdown("### 본문 작성")
        
        selected_subtopic = st.selectbox(
            "작성할 소제목",
            chapter_data['subtopics'],
            format_func=lambda x: f"{'✦' if chapter_data.get('subtopic_data', {}).get(x, {}).get('content') else '○'} {x}"
        )
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data.get('subtopic_data', {}):
                chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
            
            st_data = chapter_data['subtopic_data'][selected_subtopic]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 인터뷰")
                
                if st.button("질문 생성하기", key="gen_q"):
                    with st.spinner("생성 중..."):
                        result = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state['topic'])
                        questions = re.findall(r'Q\d+:\s*(.+)', result)
                        if not questions:
                            questions = [q.strip() for q in result.split('\n') if '?' in q][:3]
                        st_data['questions'] = questions
                        st_data['answers'] = [''] * len(questions)
                        st.rerun()
                
                if st_data.get('questions'):
                    for i, q in enumerate(st_data['questions']):
                        st.markdown(f"**Q{i+1}.** {q}")
                        if i >= len(st_data.get('answers', [])):
                            st_data['answers'].append('')
                        st_data['answers'][i] = st.text_area(
                            f"A{i+1}",
                            value=st_data['answers'][i],
                            height=80,
                            key=f"ans_{selected_chapter}_{selected_subtopic}_{i}",
                            label_visibility="collapsed"
                        )
            
            with col2:
                st.markdown("#### 본문")
                
                has_answers = st_data.get('questions') and any(a.strip() for a in st_data.get('answers', []))
                
                if has_answers:
                    if st.button("본문 생성하기", key="gen_content"):
                        with st.spinner("집필 중..."):
                            content = generate_subtopic_content(
                                selected_subtopic, selected_chapter,
                                st_data['questions'], st_data['answers'],
                                st.session_state['topic'], st.session_state['target_persona']
                            )
                            st_data['content'] = content
                            st.rerun()
                else:
                    st.info("먼저 인터뷰 질문에 답변해주세요.")
                
                content = st.text_area(
                    "본문 내용",
                    value=st_data.get('content', ''),
                    height=400,
                    key=f"content_{selected_chapter}_{selected_subtopic}",
                    label_visibility="collapsed"
                )
                st_data['content'] = content
                
                if content:
                    st.caption(f"✦ {calculate_char_count(content):,}자")
    else:
        st.warning("소제목이 없습니다. 목차 탭에서 추가해주세요.")

# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기")
    
    content_options = []
    for ch in st.session_state['outline']:
        if ch in st.session_state['chapters']:
            for st_name, st_data in st.session_state['chapters'][ch].get('subtopic_data', {}).items():
                if st_data.get('content'):
                    content_options.append(f"{ch} > {st_name}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 문체 다듬기")
        
        if content_options:
            selected = st.selectbox("다듬을 콘텐츠", content_options, key="refine_select")
            style = st.selectbox("스타일", ["친근한", "전문적", "직설적", "스토리텔링"])
            
            if st.button("다듬기", key="refine_btn"):
                parts = selected.split(" > ")
                if len(parts) == 2:
                    content = st.session_state['chapters'][parts[0]]['subtopic_data'][parts[1]]['content']
                    with st.spinner("다듬는 중..."):
                        st.session_state['refined_content'] = refine_content(content, style)
                        st.rerun()
            
            if st.session_state.get('refined_content'):
                st.text_area("다듬어진 본문", st.session_state['refined_content'], height=400)
                if st.button("원본에 적용"):
                    parts = selected.split(" > ")
                    if len(parts) == 2:
                        st.session_state['chapters'][parts[0]]['subtopic_data'][parts[1]]['content'] = st.session_state['refined_content']
                        st.success("적용됨!")
                        st.rerun()
        else:
            st.info("먼저 본문을 작성해주세요.")
    
    with col2:
        st.markdown("### 품질 검사")
        
        if content_options:
            if st.button("베스트셀러 체크", key="quality_btn"):
                parts = selected.split(" > ")
                if len(parts) == 2:
                    content = st.session_state['chapters'][parts[0]]['subtopic_data'][parts[1]]['content']
                    with st.spinner("분석 중..."):
                        st.session_state['quality_result'] = check_quality(content)
                        st.rerun()
            
            if st.session_state.get('quality_result'):
                st.markdown(f"""
                <div class="info-card">
                    {st.session_state['quality_result'].replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 다운로드")
        
        book_title = st.text_input("전자책 제목", st.session_state.get('book_title', ''), key="final_title")
        subtitle = st.text_input("부제", st.session_state.get('subtitle', ''), key="final_subtitle")
        st.session_state['book_title'] = book_title
        st.session_state['subtitle'] = subtitle
        
        # 전체 책 내용 생성
        full_txt = f"{book_title}\n{subtitle}\n\n{'='*50}\n\n"
        full_html = f"<h1>{book_title}</h1><p>{subtitle}</p><hr>"
        
        for chapter in st.session_state['outline']:
            ch_data = st.session_state['chapters'].get(chapter, {})
            has_content = any(ch_data.get('subtopic_data', {}).get(s, {}).get('content') for s in ch_data.get('subtopics', []))
            if has_content:
                full_txt += f"\n{chapter}\n{'-'*40}\n"
                full_html += f"<h2>{chapter}</h2>"
                for st_name in ch_data.get('subtopics', []):
                    content = ch_data.get('subtopic_data', {}).get(st_name, {}).get('content', '')
                    if content:
                        full_txt += f"\n{st_name}\n\n{content}\n\n"
                        full_html += f"<h3>{st_name}</h3><p>{content}</p>"
        
        html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{book_title}</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:0 auto;padding:40px;line-height:1.8;}}</style>
</head><body>{full_html}</body></html>"""
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("TXT 다운로드", full_txt, f"{book_title or 'ebook'}.txt", "text/plain", use_container_width=True)
        with col_d2:
            st.download_button("HTML 다운로드", html_doc, f"{book_title or 'ebook'}.html", "text/html", use_container_width=True)
        
        st.markdown("---")
        all_content = get_all_content_text()
        if all_content:
            chars = calculate_char_count(all_content)
            st.success(f"✦ 총 {chars:,}자 | 약 {chars//500}페이지")
    
    with col2:
        st.markdown("### 마케팅 카피")
        
        if st.button("카피 생성하기", key="marketing_btn"):
            with st.spinner("생성 중..."):
                st.session_state['marketing_copy'] = generate_marketing_copy(
                    st.session_state.get('book_title', ''),
                    st.session_state.get('subtitle', ''),
                    st.session_state['topic'],
                    st.session_state['target_persona']
                )
                st.rerun()
        
        if st.session_state.get('marketing_copy'):
            st.markdown(f"""
            <div class="info-card">
                {st.session_state['marketing_copy'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

# 푸터
st.markdown("""
<div class="premium-footer">
    <span class="premium-footer-text">전자책 작성 프로그램 — </span>
    <span class="premium-footer-author">남현우 작가</span>
</div>
""", unsafe_allow_html=True)
