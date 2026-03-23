"""
地区工具类
数据来源: area.csv
"""
import csv
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Area:
    """区域节点"""
    id: int
    name: str
    type: int
    parent_id: int
    children: List['Area'] = field(default_factory=list)


class AreaUtils:
    """地区工具类"""

    ID_GLOBAL = 0
    ID_CHINA = 1

    _areas: Dict[int, Area] = {}
    _initialized = False

    @classmethod
    def _init(cls):
        """初始化加载地区数据"""
        if cls._initialized:
            return

        import os
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'area.csv')

        if not os.path.exists(csv_path):
            cls._initialized = True
            return

        # 先加载所有地区到字典
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过表头
            for row in reader:
                if len(row) >= 4:
                    area_id = int(row[0])
                    cls._areas[area_id] = Area(
                        id=area_id,
                        name=row[1],
                        type=int(row[2]),
                        parent_id=int(row[3]),
                    )

        # 构建树结构
        for area in cls._areas.values():
            if area.parent_id in cls._areas:
                cls._areas[area.parent_id].children.append(area)

        cls._initialized = True

    @classmethod
    def get_area(cls, area_id: int) -> Optional[Area]:
        """获取地区"""
        cls._init()
        return cls._areas.get(area_id)

    @classmethod
    def get_area_tree(cls, parent_id: int = None) -> List[dict]:
        """获取地区树"""
        cls._init()

        if parent_id is None:
            parent_id = cls.ID_CHINA

        parent = cls.get_area(parent_id)
        if not parent:
            return []

        return cls._build_tree(parent)

    @classmethod
    def _build_tree(cls, area: Area) -> List[dict]:
        """构建树结构"""
        result = []
        for child in area.children:
            node = {
                "id": child.id,
                "name": child.name,
            }
            if child.children:
                node["children"] = cls._build_tree(child)
            result.append(node)
        return result