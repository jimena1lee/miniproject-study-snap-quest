import json, os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"

def load_scores() -> list[dict]:
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_score(name: str, defeated: int):
    scores = load_scores()
    scores.append({
        "name": name,
        "defeated": defeated,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    # 처치 수 내림차순 정렬
    scores.sort(key=lambda x: x["defeated"], reverse=True)
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

def reset_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        os.remove(LEADERBOARD_FILE)

def render_leaderboard_html() -> str:
    scores = load_scores()
    if not scores:
        return "<div style='text-align:center;padding:20px;color:#aaa;font-family:monospace'>아직 기록이 없어요</div>"

    medals = ["🥇", "🥈", "🥉"]
    rows = ""
    for i, s in enumerate(scores[:10]):
        medal = medals[i] if i < 3 else f"{i+1}"
        bg = ["#FAEEDA","#F1EFE8","#FAECE7"][i] if i < 3 else "transparent"
        rows += f"""
<div style='display:grid;grid-template-columns:36px 1fr 60px 60px;
            align-items:center;gap:8px;padding:7px 12px;
            background:{bg};border-radius:7px;margin-bottom:4px;font-family:monospace'>
  <div style='text-align:center;font-size:14px'>{medal}</div>
  <div style='font-size:13px;font-weight:500;color:var(--color-text-primary)'>{s['name']}</div>
  <div style='text-align:center;font-size:13px;color:#1D9E75;font-weight:500'>{s['defeated']}마리</div>
  <div style='text-align:right;font-size:11px;color:#aaa'>{s['time']}</div>
</div>"""

    return f"""
<div style='padding:8px'>
  <div style='display:grid;grid-template-columns:36px 1fr 60px 60px;
              gap:8px;padding:4px 12px;margin-bottom:6px'>
    <div></div>
    <div style='font-size:10px;color:#aaa'>플레이어</div>
    <div style='font-size:10px;color:#aaa;text-align:center'>처치 수</div>
    <div style='font-size:10px;color:#aaa;text-align:right'>시간</div>
  </div>
  {rows}
</div>"""