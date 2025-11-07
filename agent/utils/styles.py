"""
Custom styling for Spotify-inspired dark purple theme
"""

def get_custom_css():
    return """
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main container */
    .main {
        background: linear-gradient(135deg, #0F0F0F 0%, #1A0F1F 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A0F1F 0%, #0F0F0F 100%);
        border-right: 1px solid #2A1A3F;
    }

    /* Headers */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Cards */
    .incident-card {
        background: linear-gradient(135deg, #1F1F1F 0%, #2A1A3F 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        border: 1px solid #3A2A4F;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .incident-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.3);
        border-color: #8B5CF6;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }

    .status-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }

    .status-high {
        background: rgba(251, 146, 60, 0.2);
        color: #FB923C;
        border: 1px solid #FB923C;
    }

    .status-medium {
        background: rgba(250, 204, 21, 0.2);
        color: #FACC15;
        border: 1px solid #FACC15;
    }

    .status-low {
        background: rgba(34, 197, 94, 0.2);
        color: #22C55E;
        border: 1px solid #22C55E;
    }

    /* Pipeline stages */
    .pipeline-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 32px;
        background: linear-gradient(135deg, #1F1F1F 0%, #2A1A3F 100%);
        border-radius: 20px;
        margin: 24px 0;
        border: 1px solid #3A2A4F;
    }

    .pipeline-stage {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }

    .pipeline-icon {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        margin-bottom: 12px;
        transition: all 0.4s ease;
        border: 2px solid transparent;
    }

    .pipeline-stage.inactive .pipeline-icon {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.3);
    }

    .pipeline-stage.active .pipeline-icon {
        background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
        color: white;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5);
        border-color: #8B5CF6;
        animation: pulse 2s infinite;
    }

    .pipeline-stage.completed .pipeline-icon {
        background: linear-gradient(135deg, #22C55E 0%, #4ADE80 100%);
        color: white;
        border-color: #22C55E;
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5);
        }
        50% {
            transform: scale(1.05);
            box-shadow: 0 12px 48px rgba(139, 92, 246, 0.8);
        }
    }

    .pipeline-connector {
        position: absolute;
        top: 32px;
        left: 50%;
        width: 100%;
        height: 2px;
        background: rgba(255, 255, 255, 0.1);
        z-index: -1;
    }

    .pipeline-connector.active {
        background: linear-gradient(90deg, #8B5CF6 0%, transparent 100%);
        animation: flow 2s infinite;
    }

    @keyframes flow {
        0% {
            background-position: 0% 50%;
        }
        100% {
            background-position: 100% 50%;
        }
    }

    .pipeline-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 13px;
        font-weight: 500;
        text-align: center;
    }

    .pipeline-stage.active .pipeline-label,
    .pipeline-stage.completed .pipeline-label {
        color: white;
        font-weight: 600;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1F1F1F 0%, #2A1A3F 100%);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #3A2A4F;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: #8B5CF6;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.2);
    }

    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #8B5CF6;
        margin: 8px 0;
    }

    .metric-label {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Modal */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(8px);
    }

    .modal-content {
        background: linear-gradient(135deg, #1F1F1F 0%, #2A1A3F 100%);
        border-radius: 20px;
        padding: 32px;
        max-width: 700px;
        width: 90%;
        max-height: 85vh;
        overflow-y: auto;
        border: 1px solid #3A2A4F;
        box-shadow: 0 20px 80px rgba(0, 0, 0, 0.8);
    }

    /* User info */
    .user-info {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 16px;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 24px;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }

    .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 14px;
    }

    .user-name {
        color: white;
        font-weight: 500;
        font-size: 14px;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
    }

    /* Tables */
    .dataframe {
        background: #1F1F1F !important;
        border-radius: 12px;
        border: 1px solid #3A2A4F !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1F1F1F;
    }

    ::-webkit-scrollbar-thumb {
        background: #8B5CF6;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #A78BFA;
    }

    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(139, 92, 246, 0.3);
        border-radius: 50%;
        border-top-color: #8B5CF6;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Timeline */
    .timeline-item {
        position: relative;
        padding-left: 32px;
        padding-bottom: 24px;
        border-left: 2px solid #3A2A4F;
    }

    .timeline-item:last-child {
        border-left: none;
    }

    .timeline-dot {
        position: absolute;
        left: -6px;
        top: 0;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #8B5CF6;
        border: 2px solid #1F1F1F;
    }

    .timeline-content {
        background: rgba(139, 92, 246, 0.05);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    </style>
    """