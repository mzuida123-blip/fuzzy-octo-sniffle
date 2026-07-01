import streamlit as st
import re
import time
from datetime import datetime
from typing import List, Tuple

# Optional improved Chinese tokenizer
try:
    import jieba  # add jieba to requirements.txt if you want this behavior
    _JIEBA_AVAILABLE = True
except Exception:
    _JIEBA_AVAILABLE = False

# ==========================================
# 1. 页面极简美化配置
# ==========================================
st.set_page_config(
    page_title="万象时空文本数合计算引擎",
    page_icon="🌌",
    layout="centered"
)

# ==========================================
# 2. 底层核心万象数合算法引擎
# ==========================================
class UniversalWanXiangEngine:
    @staticmethod
    def segment_text(text: str, keep_non_chinese: bool = False, use_jieba: bool = False) -> Tuple[str, List[str]]:
        """
        全息文本语义词拆解：
        - keep_non_chinese: if True, preserves non-Chinese visible tokens for counting/segmentation.
        - use_jieba: if True and jieba is available, uses jieba.lcut for segmentation (recommended for better semantics).
        Returns (cleaned_for_counting, parsed_words)
        """
        if keep_non_chinese:
            # preserve visible non-control characters (keep Latin, digits, punctuation)
            cleaned = re.sub(r'[\t\r\n]', '', text).strip()
        else:
            # original behavior: keep only CJK unified ideographs
            cleaned = re.sub(r'[^\u4e00-\u9fa5]', '', text)

        if use_jieba and _JIEBA_AVAILABLE:
            words = [w for w in jieba.lcut(cleaned) if w.strip()]
            return cleaned, words

        # Fallback lightweight segmentation (your original particle+2-char logic)
        particles = set(list("下个到在与和或的时我你他她它去上里外是否要来问算"))
        parsed_words: List[str] = []
        temp = cleaned
        i = 0
        while i < len(temp):
            if temp[i] in particles or i == len(temp) - 1:
                parsed_words.append(temp[i])
                i += 1
            else:
                parsed_words.append(temp[i:i+2])
                i += 2
        return cleaned, parsed_words

# Cache segmentation results for responsiveness
@st.cache_data(max_entries=128)
def segment_cached(text: str, keep_non_chinese: bool = False, use_jieba: bool = False):
    return UniversalWanXiangEngine.segment_text(text, keep_non_chinese=keep_non_chinese, use_jieba=use_jieba)

def get_solar_term_and_five_elements(month: int) -> str:
    """简易流体五行季节映射"""
    if month in [3, 4, 5]:
        return "【木】(生发、破局、管道拓宽状态)"
    elif month in [6, 7, 8]:
        return "【火】(高频做功、极限淬炼状态)"
    elif month in [9, 10, 11]:
        return "【金】(收敛、边界防御、法则锁死状态)"
    else:
        return "【水】(底层蓄能、流动、因果沉淀状态)"

# ==========================================
# 3. Streamlit 前端交互展示
# ==========================================
st.title("🌌 万象时空 · 全息文本语义数合引擎")
st.caption("基于流体动力学反演、尺度倒置律与越冲越合定律的通用逻辑结算台")
st.markdown("---")

# 侧边栏：部署与环境动态载荷
st.sidebar.header("📡 实时物理时空载荷")
current_time = datetime.now()
st.sidebar.metric("当前物理时间", current_time.strftime("%Y-%m-%d %H:%M"))

# 用户自主填写的通用时空底盘
user_direction = st.sidebar.selectbox("🧭 当前所面朝向", ["东", "南", "西", "北", "中"], index=4)
user_bazi = st.sidebar.text_input("🧬 测算主体标识 (如八字/名字/代号)", value="通用本盘")
user_location = st.sidebar.text_input("📍 当前物理坐标点", value="未测距物理空间")

direction_elements = {"东": "木", "南": "火", "西": "金", "北": "水", "中": "土"}
activated_element = direction_elements[user_direction]

# Use a form so the calculation runs only when the user submits the form.
with st.form("wanxiang_form"):
    question = st.text_input(
        "🔮 注入你要测算的核心因果问题（按 Enter 键或点击下方按钮结算）：",
        placeholder="例如：我在这项项目里该如何破局突破死锁"
    )
    # optional toggles
    cola, colb = st.columns([1, 1])
    with cola:
        use_jieba = st.checkbox("使用 jieba 分词（可选）", value=False, help="需要在 requirements.txt 中添加 jieba")
    with colb:
        keep_non_chinese = st.checkbox("保留非中文字符用于计数（可选）", value=False)
    submitted = st.form_submit_button("🚀 启动万象矩阵结算")

if submitted:
    if not question.strip():
        st.warning("⚠️ 请先注入有效的问题文本。")
    else:
        with st.spinner("⏳ 正在抽取文本密度，叠合���层时空流体矩阵..."):
            # Small UI delay for perception only (avoid long sleeps)
            time.sleep(0.25)

            # 调用通用引擎 (cached)
            cleaned_text, parsed_words = segment_cached(question, keep_non_chinese=keep_non_chinese, use_jieba=use_jieba)
            total_chars = len(cleaned_text)

            # 1. 判定数合级别
            if total_chars == 0:
                harmony_level, harm_desc = "无气", "未捕捉到有效信息"
            elif total_chars < 6:
                harmony_level, harm_desc = "未成数合", "基础因果面较为浅薄"
            elif total_chars < 10:
                harmony_level, harm_desc = "小合", "局部微观节点开始咬合"
            elif total_chars < 100:
                harmony_level, harm_desc = "中合", "破十见骨，因果牵引力极强"
            else:
                harmony_level, harm_desc = "大合", "破百化象，宏观大势并轨"

            # 2. 提取微观冲克因子
            clash_factors = [w for w in parsed_words if len(w) == 1]
            clash_count = len(clash_factors)
            tail_word = parsed_words[-1] if parsed_words else "无"
            current_season_element = get_solar_term_and_five_elements(current_time.month)

            # ==================== 渲染报告 ====================
            st.success("✅ 矩阵收敛完成！生成万象终态决策报告：")

            # 第一板块：文本全息扫描
            st.subheader("🔮 1. 文本全息数合定量")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("问题净字数", f"{total_chars} 字", delta="")
                st.markdown(f"**数合定性：** {harmony_level} — {harm_desc}")
            with col2:
                st.metric("微观冲克因子", f"{clash_count} 处", delta="")
                st.markdown(f"**句尾中和锚点：** `[{tail_word}]`")

            st.markdown("**语义全息拆解序列：**")
            st.code(" + ".join([f"[{w}]({len(w)})" for w in parsed_words]), language="text")

            st.markdown("---")

            # 第二板块：流体动力学环境
            st.subheader("⚙️ 2. 跨层时空流体动力学")
            st.markdown(f"- **计算主体：** `{user_bazi}` @ `{user_location}`")
            st.markdown(f"- **空间超导：** 面朝【{user_direction}】方，定向激活本盘 **【{activated_element}】** 属性能量。")
            st.markdown(f"- **时间步进：** 当前月份正处于时空流体 {current_season_element} 的淬炼周期。")

            # 第三板块：核心死逻辑结算
            st.subheader("🏁 3. 万象决策收敛输出")

            # 越冲越合律判定逻辑
            if clash_count > 0:
                st.info("💡 **【定律激活】**：检测到结构非绝对对称。触发**越冲越合原理**！微观单字打破了常规平庸的能量死锁，转化为了高维超导通道。")
                decision_text = (
                    f"👑 **【高维超导 · 绿灯亮起】**\n\n"
                    f"评估结论：当前时空管道整体顺畅。微观层面的‘战术小冲’已经成功将宏观压强转化为稳态推背感。\n"
                    f"句尾目标核心项 **[{tail_word}]** 已完成中和。无需顾虑表面的干扰与拉锯阻力，卡准你当下的直接决断，放手前行，物理死锁将在瞬间被击穿！"
                )
            else:
                st.warning("⏳ **【状态判定】**：问题文本结构过于绝对对称，缺乏负反馈冲克因子，系统流体容易陷入平庸死锁。")
                decision_text = (
                    f"⏳ **【程序拉锯 · 局部卡死】**\n\n"
                    f"评估结论：由于缺乏微观的靶向小冲爆破，目标核心项 **[{tail_word}]** 容易在宏观大盘的交战中陷入长期的泥潭化硬对冲。\n"
                    f"建议改变切入问题的直观初心，或者人为制造一些变数（引入微观冲突因子），静待下一个时空步进的切换。"
                )

            st.markdown(f"> ### {decision_text}")
