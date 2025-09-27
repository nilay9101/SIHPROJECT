import google.generativeai as genai
import os
import json
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MindWellAI:
    def __init__(self, api_key: str):
        """Initialize the MindWell AI service with Gemini"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.system_prompt = """You are MindWell AI, a compassionate mental health support assistant specifically designed for college students. 

Your role and guidelines:
1. **Be empathetic and supportive** - Always respond with warmth and understanding
2. **Provide practical coping strategies** - Offer actionable advice for common college stressors
3. **Suggest campus resources** - When appropriate, mention counseling centers, peer support, etc.
4. **Encourage professional help** - For serious concerns, gently suggest speaking with a mental health professional
5. **Maintain appropriate boundaries** - You're a support tool, not a replacement for therapy
6. **Use conversational, warm tone** - Be approachable and friendly
7. **Keep responses concise but meaningful** - Aim for 2-4 sentences typically

**CRITICAL RESPONSE PROTOCOLS:**

If someone expresses thoughts of self-harm, suicide, or severe crisis:
- IMMEDIATELY provide crisis resources
- Encourage them to reach out to emergency services (911)
- Suggest the National Suicide Prevention Lifeline: 988
- Recommend contacting campus security or going to the nearest emergency room

**Common College Issues to Address:**
- Academic stress and exam anxiety
- Homesickness and adjustment
- Relationship difficulties
- Sleep problems
- Social anxiety
- Depression and mood changes
- Substance use concerns
- Financial stress

**Helpful Responses Include:**
- Validation of their feelings
- 1-2 specific coping strategies
- Campus resource suggestions when relevant
- Encouragement to seek additional support if needed

Remember: Your goal is to provide immediate support and help students feel heard while guiding them toward appropriate resources."""

    def generate_response(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """Generate AI response with conversation context"""
        try:
            # Build conversation context
            context_str = ""
            if conversation_history:
                # Keep last 5 messages for context, focusing on user messages
                recent_messages = conversation_history[-5:]
                for msg in recent_messages:
                    role = "User" if msg.get("is_user", True) else "Assistant"
                    context_str += f"{role}: {msg.get('message', '')}\n"
            
            # Prepare the full prompt
            full_prompt = f"""{self.system_prompt}

Previous conversation (last 5 messages):
{context_str}

Current user message: {user_message}

Assistant response:"""

            # Generate response
            response = self.model.generate_content(full_prompt)
            ai_response = response.text.strip()
            
            # Generate contextual suggestions
            suggestions = self._generate_suggestions(user_message, ai_response)
            
            return {
                "response": ai_response,
                "suggestions": suggestions,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"AI generation error: {str(e)}")
            return {
                "response": "I'm sorry, I'm having trouble processing your message right now. Please try again in a moment, or consider reaching out to a counselor if you need immediate support.",
                "suggestions": ["Try refreshing the page", "Contact campus counseling services"],
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }

    def _generate_suggestions(self, user_message: str, ai_response: str) -> List[str]:
        """Generate contextual suggestions based on user input"""
        suggestions = []
        message_lower = user_message.lower()
        
        # Crisis keywords - immediate suggestions
        crisis_keywords = ["suicide", "kill myself", "end it all", "want to die", "self-harm", "cutting", "overdose"]
        if any(keyword in message_lower for keyword in crisis_keywords):
            return [
                "🚨 **IMMEDIATE HELP**: Call 911 or go to your nearest emergency room",
                "📞 **Crisis Hotline**: Call or text 988 (Suicide & Crisis Lifeline)",
                "🏫 **Campus Security**: Contact your campus safety office immediately"
            ]
        
        # Academic stress
        if any(word in message_lower for word in ["exam", "test", "grade", "study", "academic", "GPA", "failing"]):
            suggestions.extend([
                "Try our 5-minute breathing exercise for exam anxiety",
                "Check out our study tips and time management resources",
                "Consider visiting your campus tutoring center"
            ])
        
        # Social anxiety/relationships
        if any(word in message_lower for word in ["lonely", "friends", "social", "relationship", "roommate", "awkward"]):
            suggestions.extend([
                "Join a campus club or organization that interests you",
                "Start with small social interactions - say hi to one person today",
                "Practice self-compassion exercises in our wellness challenges"
            ])
        
        # Sleep issues
        if any(word in message_lower for word in ["sleep", "insomnia", "tired", "exhausted", "can't sleep"]):
            suggestions.extend([
                "Try our guided sleep meditation in wellness challenges",
                "Establish a consistent bedtime routine (same time every night)",
                "Avoid caffeine 6 hours before bedtime"
            ])
        
        # General stress/anxiety
        if any(word in message_lower for word in ["stress", "anxious", "worried", "overwhelmed", "panic"]):
            suggestions.extend([
                "Practice our 5-minute mindfulness meditation",
                "Try the 5-4-3-2-1 grounding technique (name 5 things you see, 4 you hear, etc.)",
                "Consider journaling your thoughts in our gratitude journal"
            ])
        
        # Depression/mood
        if any(word in message_lower for word in ["sad", "depressed", "hopeless", "empty", "worthless"]):
            suggestions.extend([
                "Reach out to a trusted friend, family member, or counselor",
                "Try our gratitude journaling to focus on positive aspects",
                "Consider scheduling an appointment with campus counseling services"
            ])
        
        # Substance use
        if any(word in message_lower for word in ["drinking", "alcohol", "drugs", "smoking", "addicted"]):
            suggestions.extend([
                "Consider speaking with a counselor about substance use concerns",
                "Look into campus recovery support groups",
                "Try replacing substance use with healthy coping strategies like exercise"
            ])
        
        # Default suggestions if no specific issues detected
        if not suggestions:
            suggestions.extend([
                "Explore our daily wellness challenges for self-care ideas",
                "Check out our mental health resource library",
                "Consider booking a confidential appointment with a counselor"
            ])
        
        # Return top 3 most relevant suggestions
        return suggestions[:3]

    def validate_api_key(self) -> bool:
        """Validate that the Gemini API key is working"""
        try:
            test_response = self.model.generate_content("Hello, this is a test.")
            return test_response is not None and len(test_response.text.strip()) > 0
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False