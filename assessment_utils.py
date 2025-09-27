import json
from typing import List, Dict, Tuple
from datetime import datetime

# PHQ-9 Questions (Depression screening)
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless", 
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead, or of hurting yourself"
]

# GAD-7 Questions (Anxiety screening)
GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it is hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid, as if something awful might happen"
]

def calculate_phq9_score(responses: List[int]) -> int:
    """Calculate total PHQ-9 score from responses"""
    if len(responses) != 9:
        raise ValueError("PHQ-9 requires exactly 9 responses")
    if any(score < 0 or score > 3 for score in responses):
        raise ValueError("PHQ-9 responses must be between 0-3")
    return sum(responses)

def calculate_gad7_score(responses: List[int]) -> int:
    """Calculate total GAD-7 score from responses"""
    if len(responses) != 7:
        raise ValueError("GAD-7 requires exactly 7 responses")
    if any(score < 0 or score > 3 for score in responses):
        raise ValueError("GAD-7 responses must be between 0-3")
    return sum(responses)

def get_phq9_severity_level(score: int) -> str:
    """Get severity level based on PHQ-9 score"""
    if score <= 4:
        return "minimal"
    elif score <= 9:
        return "mild"
    elif score <= 14:
        return "moderate"
    elif score <= 19:
        return "moderately_severe"
    else:
        return "severe"

def get_gad7_severity_level(score: int) -> str:
    """Get severity level based on GAD-7 score"""
    if score <= 4:
        return "minimal"
    elif score <= 9:
        return "mild"
    elif score <= 14:
        return "moderate"
    else:
        return "severe"

def get_phq9_recommendations(severity_level: str, score: int) -> List[str]:
    """Get recommendations based on PHQ-9 severity level"""
    recommendations = []
    
    if severity_level == "minimal":
        recommendations = [
            "Your results suggest minimal depression symptoms.",
            "Continue practicing self-care and stress management.",
            "Consider mindfulness exercises and regular physical activity.",
            "Maintain social connections and healthy sleep habits."
        ]
    elif severity_level == "mild":
        recommendations = [
            "Your results suggest mild depression symptoms.",
            "Consider implementing stress reduction techniques.",
            "Try journaling or talking with trusted friends/family.",
            "Explore campus wellness resources and support groups.",
            "If symptoms persist or worsen, consider speaking with a counselor."
        ]
    elif severity_level == "moderate":
        recommendations = [
            "Your results suggest moderate depression symptoms.",
            "Consider scheduling an appointment with a mental health professional.",
            "Reach out to campus counseling services for support.",
            "Implement structured daily routines and self-care practices.",
            "Consider joining a support group or peer support program."
        ]
    elif severity_level == "moderately_severe":
        recommendations = [
            "Your results suggest moderately severe depression symptoms.",
            "It's important to seek professional help from a mental health provider.",
            "Contact campus counseling services or your healthcare provider soon.",
            "Consider both therapy and possible medication evaluation.",
            "Reach out to trusted friends or family for support."
        ]
    else:  # severe
        recommendations = [
            "Your results suggest severe depression symptoms.",
            "Please seek immediate professional help.",
            "Contact campus counseling services, your healthcare provider, or crisis services.",
            "If you're having thoughts of self-harm, reach out for help immediately.",
            "Call 988 (Suicide & Crisis Lifeline) if you're in crisis."
        ]
    
    # Add crisis resources if score indicates significant depression
    if score >= 15:
        recommendations.extend([
            "",
            "Crisis Resources:",
            "• Campus Counseling: [Your campus counseling center]",
            "• Crisis Text Line: Text HOME to 741741",
            "• National Suicide Prevention Lifeline: 988"
        ])
    
    return recommendations

def get_gad7_recommendations(severity_level: str, score: int) -> List[str]:
    """Get recommendations based on GAD-7 severity level"""
    recommendations = []
    
    if severity_level == "minimal":
        recommendations = [
            "Your results suggest minimal anxiety symptoms.",
            "Continue practicing stress management and relaxation techniques.",
            "Consider regular exercise and adequate sleep.",
            "Practice mindfulness and deep breathing exercises."
        ]
    elif severity_level == "mild":
        recommendations = [
            "Your results suggest mild anxiety symptoms.",
            "Try relaxation techniques such as deep breathing or progressive muscle relaxation.",
            "Consider time management strategies to reduce stress.",
            "Explore campus wellness and mindfulness programs.",
            "If symptoms persist, consider speaking with a counselor."
        ]
    elif severity_level == "moderate":
        recommendations = [
            "Your results suggest moderate anxiety symptoms.",
            "Consider scheduling an appointment with a mental health professional.",
            "Explore cognitive-behavioral techniques for managing anxiety.",
            "Join anxiety support groups or workshops.",
            "Consider both therapy and possible medication evaluation."
        ]
    else:  # severe
        recommendations = [
            "Your results suggest severe anxiety symptoms.",
            "It's important to seek professional help from a mental health provider.",
            "Contact campus counseling services or your healthcare provider soon.",
            "Consider comprehensive treatment including therapy and possible medication.",
            "Reach out to trusted friends or family for support."
        ]
    
    # Add campus resources for all levels
    recommendations.extend([
        "",
        "Campus Resources:",
        "• Campus Counseling Center",
        "• Student Wellness Programs",
        "• Academic Support Services"
    ])
    
    return recommendations

def process_assessment(assessment_type: str, responses: List[int]) -> Dict:
    """Process assessment responses and return results"""
    if assessment_type == "PHQ-9":
        score = calculate_phq9_score(responses)
        severity = get_phq9_severity_level(score)
        recommendations = get_phq9_recommendations(severity, score)
        questions = PHQ9_QUESTIONS
    elif assessment_type == "GAD-7":
        score = calculate_gad7_score(responses)
        severity = get_gad7_severity_level(score)
        recommendations = get_gad7_recommendations(severity, score)
        questions = GAD7_QUESTIONS
    else:
        raise ValueError("Unsupported assessment type")
    
    return {
        "assessment_type": assessment_type,
        "total_score": score,
        "severity_level": severity,
        "recommendations": recommendations,
        "questions": questions,
        "responses": responses,
        "timestamp": datetime.now().isoformat()
    }