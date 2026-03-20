"""
验证码扩展
"""
import random
import string
from io import BytesIO
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from app.core.redis import get_redis, set_cache, RedisKeyPrefix


class CaptchaGenerator:
    """验证码生成器"""

    def __init__(
        self,
        width: int = 120,
        height: int = 40,
        font_size: int = 28,
        code_length: int = 4,
    ):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.code_length = code_length
        self._font = None

    @property
    def font(self):
        """懒加载字体"""
        if self._font is None:
            # 尝试加载系统字体
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                "Arial.ttf",
            ]
            for font_path in font_paths:
                try:
                    self._font = ImageFont.truetype(font_path, self.font_size)
                    break
                except Exception:
                    continue
            if self._font is None:
                self._font = ImageFont.load_default()
        return self._font

    def generate_code(self) -> str:
        """生成随机验证码"""
        chars = string.ascii_uppercase + string.digits
        # 排除容易混淆的字符
        chars = chars.replace("O", "").replace("0", "").replace("I", "").replace("1", "")
        return "".join(random.choice(chars) for _ in range(self.code_length))

    def generate_image(self, code: str) -> Image.Image:
        """生成验证码图片"""
        # 创建图片
        image = Image.new("RGB", (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 绘制背景噪点
        for _ in range(random.randint(100, 200)):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point((x, y), fill=self._random_color())

        # 绘制验证码文字
        for i, char in enumerate(code):
            x = 20 + i * 25
            y = random.randint(5, 10)
            draw.text((x, y), char, font=self.font, fill=self._random_color())

        # 绘制干扰线
        for _ in range(3):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line([(x1, y1), (x2, y2)], fill=self._random_color(), width=1)

        return image

    def _random_color(self) -> Tuple[int, int, int]:
        """生成随机颜色"""
        return (
            random.randint(0, 200),
            random.randint(0, 200),
            random.randint(0, 200),
        )

    def generate(self) -> Tuple[str, str]:
        """
        生成验证码

        Returns:
            (验证码文本, Base64编码的图片)
        """
        import base64

        code = self.generate_code()
        image = self.generate_image(code)

        # 转换为Base64
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return code, f"data:image/png;base64,{img_base64}"


async def create_captcha(uuid: str, expire_minutes: int = 5) -> str:
    """
    创建验证码并缓存

    Args:
        uuid: 验证码唯一标识
        expire_minutes: 过期时间(分钟)

    Returns:
        Base64编码的图片
    """
    generator = CaptchaGenerator()
    code, img_base64 = generator.generate()

    # 缓存验证码
    await set_cache(
        f"{RedisKeyPrefix.CAPTCHA}{uuid}",
        code,
        expire=expire_minutes * 60
    )

    return img_base64


async def verify_captcha(uuid: str, code: str) -> bool:
    """
    验证验证码

    Args:
        uuid: 验证码唯一标识
        code: 用户输入的验证码

    Returns:
        是否验证通过
    """
    from app.core.redis import get_cache, delete_cache

    cached = await get_cache(f"{RedisKeyPrefix.CAPTCHA}{uuid}")
    if not cached:
        return False

    # 验证后删除
    await delete_cache(f"{RedisKeyPrefix.CAPTCHA}{uuid}")

    return cached.lower() == code.lower()