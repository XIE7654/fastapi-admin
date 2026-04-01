"""
AI 模块控制器
"""
from app.module.ai.controller.ai_model import router as ai_model_router
from app.module.ai.controller.api_key import router as api_key_router
from app.module.ai.controller.chat_role import router as chat_role_router
from app.module.ai.controller.chat_message import router as chat_message_router
from app.module.ai.controller.chat_conversation import router as chat_conversation_router
from app.module.ai.controller.image import router as image_router
from app.module.ai.controller.tool import router as tool_router
from app.module.ai.controller.music import router as music_router
from app.module.ai.controller.write import router as write_router
from app.module.ai.controller.mind_map import router as mind_map_router
from app.module.ai.controller.knowledge import router as knowledge_router
from app.module.ai.controller.workflow import router as workflow_router

__all__ = ["ai_model_router", "api_key_router", "chat_role_router", "chat_message_router", "chat_conversation_router", "image_router", "tool_router", "music_router", "write_router", "mind_map_router", "knowledge_router", "workflow_router"]