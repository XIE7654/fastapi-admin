"""
地区控制器
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.common.response import success

router = APIRouter()


# 地区数据（静态数据，实际应从数据库或缓存获取）
AREA_TREE = [
    {
        "id": 1,
        "name": "北京市",
        "children": [
            {"id": 11, "name": "东城区"},
            {"id": 12, "name": "西城区"},
            {"id": 13, "name": "朝阳区"},
            {"id": 14, "name": "丰台区"},
            {"id": 15, "name": "石景山区"},
            {"id": 16, "name": "海淀区"},
            {"id": 17, "name": "门头沟区"},
            {"id": 18, "name": "房山区"},
            {"id": 19, "name": "通州区"},
            {"id": 20, "name": "顺义区"},
            {"id": 21, "name": "昌平区"},
            {"id": 22, "name": "大兴区"},
            {"id": 23, "name": "怀柔区"},
            {"id": 24, "name": "平谷区"},
            {"id": 25, "name": "密云区"},
            {"id": 26, "name": "延庆区"},
        ]
    },
    {
        "id": 2,
        "name": "上海市",
        "children": [
            {"id": 31, "name": "黄浦区"},
            {"id": 32, "name": "徐汇区"},
            {"id": 33, "name": "长宁区"},
            {"id": 34, "name": "静安区"},
            {"id": 35, "name": "普陀区"},
            {"id": 36, "name": "虹口区"},
            {"id": 37, "name": "杨浦区"},
            {"id": 38, "name": "闵行区"},
            {"id": 39, "name": "宝山区"},
            {"id": 40, "name": "嘉定区"},
            {"id": 41, "name": "浦东新区"},
            {"id": 42, "name": "金山区"},
            {"id": 43, "name": "松江区"},
            {"id": 44, "name": "青浦区"},
            {"id": 45, "name": "奉贤区"},
            {"id": 46, "name": "崇明区"},
        ]
    },
    {
        "id": 3,
        "name": "广东省",
        "children": [
            {"id": 51, "name": "广州市", "children": [
                {"id": 511, "name": "荔湾区"},
                {"id": 512, "name": "越秀区"},
                {"id": 513, "name": "海珠区"},
                {"id": 514, "name": "天河区"},
                {"id": 515, "name": "白云区"},
                {"id": 516, "name": "黄埔区"},
                {"id": 517, "name": "番禺区"},
                {"id": 518, "name": "花都区"},
                {"id": 519, "name": "南沙区"},
                {"id": 520, "name": "从化区"},
                {"id": 521, "name": "增城区"},
            ]},
            {"id": 52, "name": "深圳市", "children": [
                {"id": 522, "name": "罗湖区"},
                {"id": 523, "name": "福田区"},
                {"id": 524, "name": "南山区"},
                {"id": 525, "name": "宝安区"},
                {"id": 526, "name": "龙岗区"},
                {"id": 527, "name": "盐田区"},
                {"id": 528, "name": "龙华区"},
                {"id": 529, "name": "坪山区"},
                {"id": 530, "name": "光明区"},
            ]},
            {"id": 53, "name": "珠海市"},
            {"id": 54, "name": "汕头市"},
            {"id": 55, "name": "佛山市"},
            {"id": 56, "name": "韶关市"},
            {"id": 57, "name": "湛江市"},
            {"id": 58, "name": "肇庆市"},
            {"id": 59, "name": "江门市"},
            {"id": 60, "name": "茂名市"},
            {"id": 61, "name": "惠州市"},
            {"id": 62, "name": "梅州市"},
            {"id": 63, "name": "汕尾市"},
            {"id": 64, "name": "河源市"},
            {"id": 65, "name": "阳江市"},
            {"id": 66, "name": "清远市"},
            {"id": 67, "name": "东莞市"},
            {"id": 68, "name": "中山市"},
            {"id": 69, "name": "潮州市"},
            {"id": 70, "name": "揭阳市"},
            {"id": 71, "name": "云浮市"},
        ]
    },
    {
        "id": 4,
        "name": "江苏省",
        "children": [
            {"id": 81, "name": "南京市"},
            {"id": 82, "name": "无锡市"},
            {"id": 83, "name": "徐州市"},
            {"id": 84, "name": "常州市"},
            {"id": 85, "name": "苏州市"},
            {"id": 86, "name": "南通市"},
            {"id": 87, "name": "连云港市"},
            {"id": 88, "name": "淮安市"},
            {"id": 89, "name": "盐城市"},
            {"id": 90, "name": "扬州市"},
            {"id": 91, "name": "镇江市"},
            {"id": 92, "name": "泰州市"},
            {"id": 93, "name": "宿迁市"},
        ]
    },
    {
        "id": 5,
        "name": "浙江省",
        "children": [
            {"id": 101, "name": "杭州市"},
            {"id": 102, "name": "宁波市"},
            {"id": 103, "name": "温州市"},
            {"id": 104, "name": "嘉兴市"},
            {"id": 105, "name": "湖州市"},
            {"id": 106, "name": "绍兴市"},
            {"id": 107, "name": "金华市"},
            {"id": 108, "name": "衢州市"},
            {"id": 109, "name": "舟山市"},
            {"id": 110, "name": "台州市"},
            {"id": 111, "name": "丽水市"},
        ]
    },
]


@router.get("/tree", summary="获得地区树")
async def get_area_tree(
    db: AsyncSession = Depends(get_db),
):
    """获得地区树"""
    return success(data=AREA_TREE)