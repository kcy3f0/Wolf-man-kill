import asyncio
import uuid
import discord
from collections import deque
from typing import Dict, List, Set, Optional, Any, Union

class AIPlayer:
    """
    代表一個 AI 玩家物件。

    這個類別模擬了 Discord Member 的部分行為，使得 AI 玩家可以像真人一樣參與遊戲邏輯。
    包含基本的屬性如 id, name, mention 等。
    """
    def __init__(self, name: str):
        # 使用 UUID 生成唯一的整數 ID，並右移 96 位以縮短長度，避免 ID 碰撞
        self.id = uuid.uuid4().int >> 96
        self.name = name
        self.mention = f"**{name}**" # 在 Discord 訊息中顯示粗體名稱
        self.bot = True # 標記為 Bot，用於邏輯判斷
        self.discriminator = "0000" # 模擬 Discord Discriminator

    async def send(self, content: str):
        """
        模擬發送私訊給 AI。

        由於 AI 的回應是透過 AIManager 根據上下文生成的，
        此處不需要實際發送網路請求，僅作為介面相容性存在。
        實際的 AI 思考與回應邏輯由 bot.py 中的 ai_manager 處理。
        """
        pass

    async def edit(self, mute: bool = False):
        """
        模擬修改成員屬性 (如靜音)。

        AI 玩家無法真正進入語音頻道，因此此方法僅為空實作，
        防止在批量操作玩家靜音時發生錯誤。
        """
        pass

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        """
        判斷兩個玩家是否相同。

        主要用於集合 (Set) 操作和列表查找。
        """
        return hasattr(other, 'id') and self.id == other.id

    def __hash__(self) -> int:
        """
        計算雜湊值，用於將物件放入字典或集合中。
        """
        return hash(self.id)

class GameState:
    """
    儲存單個 Discord Guild (伺服器) 的遊戲狀態。

    這個類別包含了遊戲進行所需的所有資訊，包括玩家列表、角色分配、
    投票狀態、以及遊戲階段控制。
    """
    def __init__(self):
        # 玩家列表 (包含真人 Member 和 AIPlayer)
        self.players: List[Union[discord.Member, AIPlayer]] = []

        # 角色分配表: Player -> Role Name (e.g., "狼人")
        self.roles: Dict[Union[discord.Member, AIPlayer], str] = {}

        # 反向角色查找表: Role Name -> List of Players
        # 用於優化查找特定角色 (如 "誰是預言家") 的速度
        self.role_to_players: Dict[str, List[Union[discord.Member, AIPlayer]]] = {}

        # 天神 (旁觀者/主持人) 列表
        self.gods: List[Union[discord.Member, AIPlayer]] = []

        # 當前投票狀況: Player (Target) -> Vote Count
        self.votes: Dict[Union[discord.Member, AIPlayer], int] = {}

        # 已投票的玩家集合 (避免重複投票)
        self.voted_players: Set[Union[discord.Member, AIPlayer]] = set()

        # 遊戲是否正在進行中
        self.game_active: bool = False

        # 玩家 ID 映射表 (用於處理輸入 ID 轉換)
        # ID (int) -> Player Object
        self.player_ids: Dict[int, Union[discord.Member, AIPlayer]] = {}

        # Player Object -> ID (int)
        self.player_id_map: Dict[Union[discord.Member, AIPlayer], int] = {}

        # 女巫藥水狀態: True 表示可用
        self.witch_potions: Dict[str, bool] = {'antidote': True, 'poison': True}

        # 房主/創建者 (用於權限控制，如開始遊戲、強制結束)
        self.creator: Optional[Union[discord.Member, discord.User]] = None

        # 並發控制鎖 (Async Lock)
        # 用於保護共享資源 (如 votes, speech_history) 在多個非同步任務中被安全存取
        self.lock = asyncio.Lock()

        # --- 發言階段狀態 ---

        # 發言佇列 (Deque)，依序儲存等待發言的玩家
        self.speaking_queue: deque = deque()

        # 當前正在發言的玩家
        self.current_speaker: Optional[Union[discord.Member, AIPlayer]] = None

        # 是否處於依序發言階段
        self.speaking_active: bool = False

        # --- 其他屬性 ---

        # 遊戲模式: "online" (AI 主持) 或 "offline" (AI 場控)
        self.game_mode: str = "online"

        # AI 玩家列表 (方便單獨處理 AI 邏輯)
        self.ai_players: List[AIPlayer] = []

        # 本輪發言紀錄 (List of strings)
        # 用於提供給 AI 作為上下文，以生成回應
        self.speech_history: List[str] = []

        # 當前天數 (第幾天)
        self.day_count: int = 0

        # 昨晚死亡的玩家名稱列表 (用於天亮廣播)
        self.last_dead_players: List[str] = []

    def reset(self):
        """
        重置遊戲狀態，準備開始新的一局。

        清除所有玩家數據、角色分配、投票紀錄和歷史訊息。
        保留 creator (房主) 和 game_mode (模式設定) 以便於連續開局。
        """
        self.players = []
        self.roles = {}
        self.role_to_players = {}
        self.gods = []
        self.votes = {}
        self.voted_players = set()
        self.game_active = False
        self.player_ids = {}
        self.player_id_map = {}
        self.witch_potions = {'antidote': True, 'poison': True}
        self.creator = None # 註: 原始代碼中這裡重置了 creator，這意味著新局需要重新加入

        self.speaking_queue = deque()
        self.current_speaker = None
        self.speaking_active = False
        self.speech_history = []

        self.game_mode = "online"
        self.ai_players = []
        self.day_count = 0
        self.last_dead_players = []

# 全域遊戲字典: Guild ID -> GameState
# 每個 Discord 伺服器擁有獨立的遊戲實例
games: Dict[int, GameState] = {}

def get_game(guild_id: int) -> GameState:
    """
    獲取指定 Guild 的遊戲狀態實例。
    如果不存在，則創建一個新的實例。
    """
    if guild_id not in games:
        games[guild_id] = GameState()
    return games[guild_id]
