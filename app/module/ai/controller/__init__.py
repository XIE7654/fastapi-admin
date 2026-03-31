"""
AI 模块控制器
"""
from app.module.ai.controller.ai_model import router as ai_model_router
from app.module.ai.controller.api_key import router as api_key_router
from app.module.ai.controller.chat_role import router as chat_role_router
from app.module.ai.controller.chat_message import router as chat_message_router
from app.module.ai.controller.image import router as image_router
from app.module.ai.controller.tool import router as tool_router

__all__ = ["ai_model_router", "api_key_router", "chat_role_router", "chat_message_router", "image_router", "tool_router"]