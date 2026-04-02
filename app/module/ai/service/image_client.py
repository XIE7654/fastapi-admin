"""
AI 绘图客户端
支持多平台的 AI 绘图 API 调用
"""
import base64
import httpx
from typing import Optional, Dict, Any
from enum import Enum

from app.module.ai.schema.ai_model import AiPlatformEnum


class ImageStatusEnum(int, Enum):
    """绘画状态枚举"""
    IN_PROGRESS = 10  # 进行中
    SUCCESS = 20  # 成功
    FAIL = 30  # 失败


class ImageClient:
    """AI 绘图客户端"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url

    async def generate_image(
        self,
        platform: str,
        model: str,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成图片

        Args:
            platform: 平台标识
            model: 模型标识
            prompt: 提示词
            width: 图片宽度
            height: 图片高度
            options: 其他参数

        Returns:
            {"b64_json": "...", "url": "..."} 或 {"error": "..."}
        """
        platform_enum = AiPlatformEnum(platform)

        if platform_enum == AiPlatformEnum.OPENAI:
            return await self._call_openai(model, prompt, width, height, options)
        elif platform_enum == AiPlatformEnum.TONG_YI:
            return await self._call_tongyi(model, prompt, width, height, options)
        elif platform_enum == AiPlatformEnum.ZHI_PU:
            return await self._call_zhipu(model, prompt, width, height, options)
        elif platform_enum == AiPlatformEnum.STABLE_DIFFUSION:
            return await self._call_stability(model, prompt, width, height, options)
        elif platform_enum == AiPlatformEnum.SILICON_FLOW:
            return await self._call_siliconflow(model, prompt, width, height, options)
        else:
            return {"error": f"不支持的平台: {platform}"}

    async def _call_openai(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """调用 OpenAI DALL-E API"""
        url = self.base_url or "https://api.openai.com/v1/images/generations"

        # OpenAI 支持的尺寸: 256x256, 512x512, 1024x1024, 1792x1024, 1024x1792
        size = self._get_openai_size(width, height)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "response_format": "b64_json",
                },
            )

            if response.status_code != 200:
                return {"error": f"OpenAI API 错误: {response.text}"}

            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                return {"b64_json": data["data"][0].get("b64_json"), "url": data["data"][0].get("url")}
            return {"error": "OpenAI API 返回数据为空"}

    def _get_openai_size(self, width: int, height: int) -> str:
        """获取 OpenAI 支持的尺寸"""
        # DALL-E 3 支持的尺寸
        if width == 1024 and height == 1024:
            return "1024x1024"
        elif width == 1792 and height == 1024:
            return "1792x1024"
        elif width == 1024 and height == 1792:
            return "1024x1792"
        # DALL-E 2 支持的尺寸
        elif width <= 256 and height <= 256:
            return "256x256"
        elif width <= 512 and height <= 512:
            return "512x512"
        else:
            return "1024x1024"

    async def _call_tongyi(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """调用通义万象 API"""
        import dashscope
        from dashscope import ImageSynthesis

        dashscope.api_key = self.api_key

        try:
            response = ImageSynthesis.call(
                model=model or "wanx-v1",
                prompt=prompt,
                n=1,
                size=f"{width}*{height}",
            )

            if response.status_code == 200:
                if response.output and response.output.results:
                    url = response.output.results[0].url
                    # 下载图片并转为 base64
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        img_response = await client.get(url)
                        if img_response.status_code == 200:
                            b64_json = base64.b64encode(img_response.content).decode('utf-8')
                            return {"b64_json": b64_json, "url": url}
                        return {"url": url}
                return {"error": "通义万象 API 返回数据为空"}
            else:
                return {"error": f"通义万象 API 错误: {response.message}"}
        except Exception as e:
            return {"error": f"通义万象 API 异常: {str(e)}"}

    async def _call_zhipu(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """调用智谱 CogView API"""
        url = self.base_url or "https://open.bigmodel.cn/api/paas/v4/images/generations"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or "cogview-3",
                    "prompt": prompt,
                },
            )

            if response.status_code != 200:
                return {"error": f"智谱 API 错误: {response.text}"}

            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                url = data["data"][0].get("url")
                # 下载图片并转为 base64
                if url:
                    async with httpx.AsyncClient(timeout=60.0) as img_client:
                        img_response = await img_client.get(url)
                        if img_response.status_code == 200:
                            b64_json = base64.b64encode(img_response.content).decode('utf-8')
                            return {"b64_json": b64_json, "url": url}
                return {"url": url}
            return {"error": "智谱 API 返回数据为空"}

    async def _call_stability(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """调用 Stability AI API"""
        url = self.base_url or f"https://api.stability.ai/v1/generation/{model or 'stable-diffusion-xl-1024-v1-0'}/text-to-image"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "text_prompts": [{"text": prompt}],
                    "cfg_scale": options.get("scale", 7) if options else 7,
                    "height": height,
                    "width": width,
                    "steps": options.get("steps", 30) if options else 30,
                    "samples": 1,
                },
            )

            if response.status_code != 200:
                return {"error": f"Stability AI API 错误: {response.text}"}

            data = response.json()
            if data.get("artifacts") and len(data["artifacts"]) > 0:
                return {"b64_json": data["artifacts"][0].get("base64")}
            return {"error": "Stability AI API 返回数据为空"}

    async def _call_siliconflow(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """调用硅基流动 API"""
        url = self.base_url or "https://api.siliconflow.cn/v1/images/generations"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or "stabilityai/stable-diffusion-xl-base-1.0",
                    "prompt": prompt,
                    "image_size": f"{width}x{height}",
                    "batch_size": 1,
                },
            )

            if response.status_code != 200:
                return {"error": f"硅基流动 API 错误: {response.text}"}

            data = response.json()
            if data.get("images") and len(data["images"]) > 0:
                url = data["images"][0].get("url")
                # 下载图片并转为 base64
                if url:
                    async with httpx.AsyncClient(timeout=60.0) as img_client:
                        img_response = await img_client.get(url)
                        if img_response.status_code == 200:
                            b64_json = base64.b64encode(img_response.content).decode('utf-8')
                            return {"b64_json": b64_json, "url": url}
                return {"url": url}
            return {"error": "硅基流动 API 返回数据为空"}

    @staticmethod
    async def download_image(url: str) -> Optional[bytes]:
        """下载图片"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.content
        return None