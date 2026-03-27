"""
AI 模块模型
"""
from app.module.ai.model.api_key import ApiKey
from app.module.ai.model.chat_conversation import ChatConversation
from app.module.ai.model.chat_message import ChatMessage
from app.module.ai.model.chat_role import ChatRole
from app.module.ai.model.image import Image
from app.module.ai.model.knowledge import Knowledge
from app.module.ai.model.knowledge_document import KnowledgeDocument
from app.module.ai.model.knowledge_segment import KnowledgeSegment
from app.module.ai.model.mind_map import MindMap
from app.module.ai.model.ai_model import AiModel
from app.module.ai.model.music import Music
from app.module.ai.model.tool import Tool
from app.module.ai.model.workflow import Workflow
from app.module.ai.model.write import Write

# 导出所有模型类
__all__ = [
    "ApiKey",
    "ChatConversation",
    "ChatMessage",
    "ChatRole",
    "Image",
    "Knowledge",
    "KnowledgeDocument",
    "KnowledgeSegment",
    "MindMap",
    "AiModel",
    "Music",
    "Tool",
    "Workflow",
    "Write",
]