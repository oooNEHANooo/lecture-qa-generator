"""
Difficulty adjustment service for QA generation
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class DifficultyLevel(str, Enum):
    """難易度レベル"""
    EASY = "easy"
    MEDIUM = "medium" 
    HARD = "hard"


@dataclass
class DifficultyParameters:
    """難易度調整パラメータ"""
    cognitive_level: str  # 認知レベル（記憶、理解、応用、分析、評価、創造）
    question_complexity: str  # 質問の複雑さ
    content_depth: str  # 内容の深さ
    thinking_time: str  # 推定思考時間
    vocabulary_level: str  # 語彙レベル
    concept_integration: str  # 概念統合の必要性


class DifficultyAdjuster:
    """難易度調整サービス"""
    
    def __init__(self):
        self.difficulty_parameters = self._initialize_difficulty_parameters()
    
    def _initialize_difficulty_parameters(self) -> Dict[DifficultyLevel, DifficultyParameters]:
        """難易度パラメータを初期化"""
        return {
            DifficultyLevel.EASY: DifficultyParameters(
                cognitive_level="記憶・理解",
                question_complexity="単純な事実確認",
                content_depth="表面的な内容",
                thinking_time="30秒以内",
                vocabulary_level="基本的な専門用語",
                concept_integration="単一概念"
            ),
            DifficultyLevel.MEDIUM: DifficultyParameters(
                cognitive_level="応用・分析",
                question_complexity="概念の関連付け",
                content_depth="中程度の理解",
                thinking_time="1-2分",
                vocabulary_level="標準的な専門用語",
                concept_integration="複数概念の関連"
            ),
            DifficultyLevel.HARD: DifficultyParameters(
                cognitive_level="評価・創造",
                question_complexity="批判的思考",
                content_depth="深い理解と応用",
                thinking_time="3分以上",
                vocabulary_level="高度な専門用語",
                concept_integration="複雑な概念統合"
            )
        }
    
    def get_prompt_instructions(self, difficulty: DifficultyLevel) -> str:
        """難易度に応じたプロンプト指示を生成"""
        params = self.difficulty_parameters[difficulty]
        
        instructions = {
            DifficultyLevel.EASY: f"""
## 難易度: 易しい
**認知レベル**: {params.cognitive_level}
**質問の特徴**: 
- 講義で直接説明された事実や定義を確認
- 単純な用語の意味や基本概念を問う
- 暗記や単純な理解で回答可能
- 一つの概念に焦点を当てる

**指示**:
- 講義資料に明確に記載されている内容から出題
- 専門用語は基本的なもののみ使用
- 選択肢は明確に区別できるものにする
- {params.thinking_time}で回答できる内容
""",
            
            DifficultyLevel.MEDIUM: f"""
## 難易度: 普通
**認知レベル**: {params.cognitive_level}
**質問の特徴**:
- 概念の理解と簡単な応用を問う
- 複数の概念間の関係を理解する必要がある
- 具体例や応用場面を考えさせる
- 推論や判断が必要

**指示**:
- 講義内容の概念を実際の状況に適用
- 複数の概念を関連付けて考える必要がある
- 紛らわしい選択肢を含める
- {params.thinking_time}程度の思考時間を要する
""",
            
            DifficultyLevel.HARD: f"""
## 難易度: 難しい  
**認知レベル**: {params.cognitive_level}
**質問の特徴**:
- 深い理解と批判的思考を要求
- 複数の概念を統合して新しい結論を導く
- 問題解決や創造的思考が必要
- 応用範囲が広く、抽象的思考を求める

**指示**:
- 講義内容を基に新しい状況を分析・評価
- 複雑な概念の相互関係を理解する必要
- 推論過程が重要で、単純な暗記では解けない
- {params.thinking_time}以上の深い思考を要求
- 高度な専門用語や概念を含む
"""
        }
        
        return instructions[difficulty]
    
    def adjust_question_complexity(
        self, 
        slide_content: Dict[str, Any], 
        difficulty: DifficultyLevel
    ) -> Dict[str, Any]:
        """スライド内容に基づいて質問の複雑さを調整"""
        
        adjusted_content = slide_content.copy()
        params = self.difficulty_parameters[difficulty]
        
        # 難易度に応じて焦点を当てる内容を調整
        if difficulty == DifficultyLevel.EASY:
            # 基本的な事実と定義に焦点
            adjusted_content["focus_areas"] = [
                "基本用語の定義",
                "明確に記載された事実",
                "単純な概念"
            ]
            adjusted_content["question_patterns"] = [
                "〜とは何ですか？",
                "〜の定義として正しいものは？",
                "〜について正しい記述は？"
            ]
        
        elif difficulty == DifficultyLevel.MEDIUM:
            # 概念の関連性と応用に焦点
            adjusted_content["focus_areas"] = [
                "概念間の関係",
                "実際の応用例",
                "比較と対比"
            ]
            adjusted_content["question_patterns"] = [
                "〜と〜の関係として正しいものは？",
                "〜を実際に適用する場合、どのようになりますか？",
                "〜の例として適切なものは？"
            ]
        
        else:  # HARD
            # 批判的思考と統合に焦点
            adjusted_content["focus_areas"] = [
                "複雑な概念統合",
                "批判的分析",
                "創造的問題解決"
            ]
            adjusted_content["question_patterns"] = [
                "〜について批判的に分析すると？",
                "〜の問題点と改善案は？",
                "〜を別の観点から見た場合、どのように評価できますか？"
            ]
        
        return adjusted_content
    
    def calculate_difficulty_distribution(
        self, 
        total_questions: int,
        target_distribution: Dict[str, float] = None
    ) -> Dict[DifficultyLevel, int]:
        """難易度配分を計算"""
        
        if target_distribution is None:
            target_distribution = {
                "easy": 0.4,      # 40%
                "medium": 0.4,    # 40%  
                "hard": 0.2       # 20%
            }
        
        distribution = {}
        remaining_questions = total_questions
        
        # 易しい問題の配分
        easy_count = int(total_questions * target_distribution["easy"])
        distribution[DifficultyLevel.EASY] = easy_count
        remaining_questions -= easy_count
        
        # 普通の問題の配分
        medium_count = int(total_questions * target_distribution["medium"])
        distribution[DifficultyLevel.MEDIUM] = medium_count
        remaining_questions -= medium_count
        
        # 残りを難しい問題に割り当て
        distribution[DifficultyLevel.HARD] = remaining_questions
        
        logger.info(f"難易度配分: 易 {easy_count}, 普通 {medium_count}, 難 {remaining_questions}")
        
        return distribution
    
    def validate_difficulty_balance(
        self, 
        generated_questions: List[Any]
    ) -> Dict[str, Any]:
        """生成された質問の難易度バランスを検証"""
        
        difficulty_counts = {
            DifficultyLevel.EASY: 0,
            DifficultyLevel.MEDIUM: 0,
            DifficultyLevel.HARD: 0
        }
        
        total_questions = len(generated_questions)
        
        for question in generated_questions:
            difficulty = question.difficulty if hasattr(question, 'difficulty') else DifficultyLevel.MEDIUM
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1
        
        # 割合を計算
        difficulty_ratios = {
            level: count / total_questions if total_questions > 0 else 0
            for level, count in difficulty_counts.items()
        }
        
        # バランス評価
        balance_score = self._calculate_balance_score(difficulty_ratios)
        
        return {
            "total_questions": total_questions,
            "difficulty_counts": difficulty_counts,
            "difficulty_ratios": difficulty_ratios,
            "balance_score": balance_score,
            "is_balanced": balance_score >= 0.7
        }
    
    def _calculate_balance_score(self, ratios: Dict[DifficultyLevel, float]) -> float:
        """バランススコアを計算（0-1の範囲）"""
        
        # 理想的な配分
        ideal_ratios = {
            DifficultyLevel.EASY: 0.4,
            DifficultyLevel.MEDIUM: 0.4,
            DifficultyLevel.HARD: 0.2
        }
        
        # 各難易度の差分を計算
        differences = []
        for level in DifficultyLevel:
            diff = abs(ratios.get(level, 0) - ideal_ratios[level])
            differences.append(diff)
        
        # 平均差分からスコアを計算（差分が小さいほど高スコア）
        avg_difference = sum(differences) / len(differences)
        balance_score = max(0, 1 - (avg_difference * 2))  # 2倍して感度を上げる
        
        return balance_score
    
    def suggest_difficulty_adjustments(
        self, 
        current_distribution: Dict[DifficultyLevel, int],
        target_distribution: Dict[DifficultyLevel, int]
    ) -> List[str]:
        """難易度調整の提案を生成"""
        
        suggestions = []
        
        for level in DifficultyLevel:
            current = current_distribution.get(level, 0)
            target = target_distribution.get(level, 0)
            
            if current < target:
                suggestions.append(f"{level.value}の質問を{target - current}問追加することを推奨")
            elif current > target:
                suggestions.append(f"{level.value}の質問を{current - target}問削減することを推奨")
        
        return suggestions