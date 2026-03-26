from dataclasses import dataclass, field

LEVEL_NAMES = {1: "슬라임", 2: "고블린", 3: "오크"}
LEVEL_HP    = {1: 100,     2: 150,     3: 200}

@dataclass
class Monster:
    word: str
    meaning: str
    level: int
    hp: int = field(init=False)
    max_hp: int = field(init=False)

    def __post_init__(self):
        self.max_hp = LEVEL_HP.get(self.level, 100)
        self.hp = self.max_hp

    @property
    def name(self) -> str:
        return LEVEL_NAMES.get(self.level, "몬스터")

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    def take_damage(self, score: float) -> dict:
        """발음 점수(0~100)를 데미지로 변환합니다."""
        if score >= 90:
            dmg = int(self.max_hp * 0.6)
            result = "critical"
        elif score >= 70:
            dmg = int(self.max_hp * 0.35)
            result = "hit"
        else:
            dmg = 0
            result = "miss"

        self.hp = max(0, self.hp - dmg)
        return {"result": result, "damage": dmg, "hp": self.hp}


@dataclass
class GameState:
    monsters: list[Monster] = field(default_factory=list)
    current_index: int = 0
    score_total: int = 0
    defeated: int = 0

    @property
    def current_monster(self) -> Monster | None:
        if self.current_index < len(self.monsters):
            return self.monsters[self.current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self.current_index >= len(self.monsters)

    def next_monster(self):
        self.current_index += 1

    def load_from_keywords(self, keywords: list[dict]):
        """openai_helper의 결과를 몬스터 리스트로 변환합니다."""
        self.monsters = [
            Monster(word=k["word"], meaning=k["meaning"], level=k["level"])
            for k in keywords
        ]
        self.current_index = 0
        self.score_total = 0
        self.defeated = 0