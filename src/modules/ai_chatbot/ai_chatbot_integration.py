#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import random
from ..tts.streaming_tts_module import StreamingTTSModule
from datetime import datetime
import threading
import time

class AIReceptionistChatbot:
    """AI Receptionist với khả năng phản hồi động và TTS streaming"""
    
    def __init__(self, tts_engine="auto"):
        self.tts = StreamingTTSModule(engine_type=tts_engine, cache_size=30)
        self.conversation_history = []
        self.user_context = {}
        self.knowledge_base = self._load_knowledge_base()
        
        print("AI Receptionist Chatbot initialized")
    
    def _load_knowledge_base(self):
        """Load knowledge base for responses"""
        return {
            "greetings": {
                "patterns": ["xin chào", "hello", "chào", "hi", "hey"],
                "responses": [
                    "Tôi có thể giúp gì cho bạn?",
                    "Chào mừng bạn đến với hệ thống AI Receptionist."
                ]
            },
            "thanks": {
                "patterns": ["cảm ơn", "thank", "thanks", "cám ơn"],
                "responses": [
                    "Không có gì! Tôi luôn sẵn sàng giúp đỡ bạn.",
                    "Rất vui được hỗ trợ bạn!",
                    "Cảm ơn bạn! Còn gì khác tôi có thể giúp không?"
                ]
            },
            "goodbye": {
                "patterns": ["tạm biệt", "bye", "goodbye", "chào", "see you"],
                "responses": [
                    "Tạm biệt! Hẹn gặp lại bạn!",
                    "Chào bạn! Chúc bạn một ngày tốt lành!",
                    "Tạm biệt! Cảm ơn bạn đã sử dụng dịch vụ."
                ]
            },
            "time": {
                "patterns": ["mấy giờ", "time", "thời gian", "giờ"],
                "responses": [
                    f"Bây giờ là {datetime.now().strftime('%H:%M, ngày %d/%m/%Y')}."
                ]
            },
            "weather": {
                "patterns": ["thời tiết", "weather", "trời", "nắng", "mưa"],
                "responses": [
                    "Tôi không thể kiểm tra thời tiết thực tế, nhưng hy vọng hôm nay là một ngày đẹp trời!",
                    "Để biết thời tiết chính xác, bạn có thể kiểm tra ứng dụng thời tiết trên điện thoại."
                ]
            },
            "help": {
                "patterns": ["giúp", "help", "hỗ trợ", "làm gì", "chức năng"],
                "responses": [
                    "Tôi có thể giúp bạn: trả lời câu hỏi, cung cấp thông tin, trò chuyện, và hướng dẫn sử dụng hệ thống.",
                    "Tôi là AI Receptionist, có thể hỗ trợ bạn với nhiều việc khác nhau. Bạn muốn biết gì cụ thể?"
                ]
            },
            "name": {
                "patterns": ["tên", "name", "bạn là ai", "who are you"],
                "responses": [
                    "Tôi là AI Receptionist, một trợ lý ảo thông minh với khả năng giao tiếp bằng tiếng Việt.",
                    "Tên tôi là AI Receptionist. Tôi được thiết kế để hỗ trợ và trò chuyện với bạn."
                ]
            },
            "compliment": {
                "patterns": ["giỏi", "tốt", "hay", "good", "great", "excellent"],
                "responses": [
                    "Cảm ơn bạn! Tôi luôn cố gắng hết sức để hỗ trợ bạn tốt nhất.",
                    "Rất vui khi được bạn khen ngợi! Tôi sẽ tiếp tục cải thiện."
                ]
            }
        }
    
    def _analyze_intent(self, user_input):
        """Analyze user intent from input"""
        user_input_lower = user_input.lower()
        
        for intent, data in self.knowledge_base.items():
            for pattern in data["patterns"]:
                if pattern in user_input_lower:
                    return intent
        
        return "general"
    
    def _generate_response(self, user_input, intent):
        """Generate appropriate response based on intent"""
        
        if intent in self.knowledge_base:
            responses = self.knowledge_base[intent]["responses"]
            response = random.choice(responses)
            
            # Special handling for time
            if intent == "time":
                response = f"Bây giờ là {datetime.now().strftime('%H:%M, ngày %d/%m/%Y')}."
        
        elif intent == "general":
            # General responses for unrecognized input
            general_responses = [
                f"Tôi hiểu bạn nói về '{user_input}'. Bạn có thể nói rõ hơn được không?",
                f"Về vấn đề '{user_input}', tôi cần thêm thông tin để hỗ trợ bạn tốt hơn.",
                f"Đây là một câu hỏi thú vị về '{user_input}'. Tôi sẽ cố gắng tìm hiểu thêm.",
                "Tôi đang học hỏi thêm để có thể trả lời câu hỏi này tốt hơn. Bạn có thể hỏi tôi điều gì khác không?"
            ]
            response = random.choice(general_responses)
        
        else:
            response = "Tôi không hiểu rõ ý bạn. Bạn có thể nói lại được không?"
        
        return response
    
    def _add_personality(self, response, user_input):
        """Add personality and context to response"""
        
        # Add emotional context
        if any(word in user_input.lower() for word in ['buồn', 'sad', 'khó khăn']):
            response += " Tôi hy vọng mọi thứ sẽ tốt hơn!"
        
        elif any(word in user_input.lower() for word in ['vui', 'happy', 'tốt']):
            response += " Thật tuyệt vời!"
        
        # Add time-based context
        current_hour = datetime.now().hour
        if current_hour < 12:
            if "xin chào" in response.lower():
                response = response.replace("Xin chào!", "Chào buổi sáng!")
        elif current_hour < 18:
            if "xin chào" in response.lower():
                response = response.replace("Xin chào!", "Chào buổi chiều!")
        else:
            if "xin chào" in response.lower():
                response = response.replace("Xin chào!", "Chào buổi tối!")
        
        return response
    
    def process_input(self, user_input):
        """Process user input and generate response"""
        
        if not user_input.strip():
            return "Tôi không nghe thấy gì. Bạn có thể nói lại không?"
        
        # Analyze intent
        intent = self._analyze_intent(user_input)
        
        # Generate base response
        response = self._generate_response(user_input, intent)
        
        # Add personality
        response = self._add_personality(response, user_input)
        
        # Store conversation
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent": intent,
            "response": response
        })
        
        return response
    
    def speak_response(self, user_input, priority="normal"):
        """Process input and speak response"""
        response = self.process_input(user_input)
        
        # Speak with appropriate priority
        if priority == "high":
            self.tts.speak_immediate(response)
        else:
            self.tts.speak_async(response, priority=priority)
        
        return response
    
    def speak_direct(self, message, priority="normal"):
        """Speak message directly without AI processing"""
        # Speak with appropriate priority
        if priority == "high":
            self.tts.speak_immediate(message)
        else:
            self.tts.speak_async(message, priority=priority)
        
        return message
    
    def interrupt_and_respond(self, urgent_message):
        """Interrupt current speech with urgent message"""
        self.tts.speak_immediate(urgent_message)
        return urgent_message
    
    def get_conversation_summary(self):
        """Get conversation summary"""
        if not self.conversation_history:
            return "Chưa có cuộc trò chuyện nào."
        
        total_exchanges = len(self.conversation_history)
        intents = [conv["intent"] for conv in self.conversation_history]
        most_common_intent = max(set(intents), key=intents.count)
        
        summary = f"Đã có {total_exchanges} lượt trao đổi. Chủ đề chính: {most_common_intent}."
        return summary
    
    def is_busy(self):
        """Check if chatbot is currently speaking"""
        return self.tts.is_busy()
    
    def stop(self):
        """Stop chatbot and cleanup"""
        self.tts.stop()
        print("AI Receptionist Chatbot stopped")

def demo_ai_chatbot():
    """Demo AI Chatbot với streaming TTS"""
    
    print("Demo AI Receptionist Chatbot")
    print("=" * 35)
    
    chatbot = AIReceptionistChatbot(tts_engine="auto")
    
    # Demo scenarios
    test_inputs = [
        "Xin chào!",
        "Bạn tên gì?",
        "Mấy giờ rồi?",
        "Thời tiết hôm nay thế nào?",
        "Bạn có thể giúp tôi gì?",
        "Tôi cảm thấy hơi buồn",
        "Cảm ơn bạn nhiều!",
        "Tạm biệt!"
    ]
    
    print("\n🎭 Bắt đầu demo tự động...\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"👤 Người dùng: {user_input}")
        
        # Process and respond
        response = chatbot.speak_response(user_input)
        print(f"AI Receptionist: {response}")
        
        # Wait for speech to complete
        while chatbot.is_busy():
            time.sleep(0.5)
        
        print(f"✅ Trao đổi {i} hoàn thành\n")
        time.sleep(1)
    
    # Demo interrupt feature
    print("🚨 Demo tính năng ngắt lời khẩn cấp...")
    chatbot.tts.speak_async("Đây là một thông báo dài để demo tính năng ngắt lời của hệ thống AI Receptionist")
    time.sleep(2)
    
    urgent_msg = "Xin lỗi! Có cuộc gọi khẩn cấp!"
    print(f"⚡ Thông báo khẩn: {urgent_msg}")
    chatbot.interrupt_and_respond(urgent_msg)
    
    while chatbot.is_busy():
        time.sleep(0.5)
    
    # Summary
    print(f"\n📊 Tóm tắt: {chatbot.get_conversation_summary()}")
    
    chatbot.stop()
    print("\n🎉 Demo hoàn thành!")

if __name__ == "__main__":
    demo_ai_chatbot()