import gradio as gr
import time
from ocr import extract_text_from_image
from openai_helper import extract_keywords
from game import GameState
from speech import text_to_speech, assess_pronunciation
from leaderboard import save_score, render_leaderboard_html, reset_leaderboard

state = GameState()

MONSTER_PIXELS = {
    1: {"color": "#1D9E75", "pixels": ["00111100","01111110","11111111","11111111","01111110","00100100","01000010"]},
    2: {"color": "#BA7517", "pixels": ["01100110","11111111","10111101","11111111","01111110","00100100","01100110","11000011"]},
    3: {"color": "#E24B4A", "pixels": ["11000011","01111110","11111111","10111101","11111111","01111110","01100110","11000011","10000001"]},
}

def render_monster_html(monster, flash="", fadein=False):
    if monster is None:
        return "<div style='text-align:center;padding:16px;font-size:32px'>🏆</div>"

    px = MONSTER_PIXELS.get(monster.level, MONSTER_PIXELS[1])
    color = px["color"]
    cell = 13

    grid_rows = ""
    for row in px["pixels"]:
        cells = "".join(
            f"<div style='width:{cell}px;height:{cell}px;background:{'transparent' if b=='0' else color};display:inline-block'></div>"
            for b in row
        )
        grid_rows += f"<div style='display:flex'>{cells}</div>"

    hp_pct = int((monster.hp / monster.max_hp) * 100)
    hp_color = "#1D9E75" if hp_pct > 60 else "#BA7517" if hp_pct > 30 else "#E24B4A"
    lv_color = {1: "#1D9E75", 2: "#BA7517", 3: "#E24B4A"}.get(monster.level, "#888")

    flash_map = {
        "critical": "<div style='color:#EF9F27;font-size:14px;font-weight:500'>치명타!</div>",
        "hit":      "<div style='color:#1D9E75;font-size:13px'>공격 성공!</div>",
        "miss":     "<div style='color:#E24B4A;font-size:13px'>빗나감...</div>",
    }
    flash_html = flash_map.get(flash, "")

    anim = ("animation:shake .4s ease;" if flash in ("hit","critical")
            else "animation:idle .6s ease;" if flash == "miss"
            else "animation:bounce 1.2s ease-in-out infinite;")

    container_style = "animation:fadein .8s ease;" if fadein else ""

    return f"""
<style>
  @keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
  @keyframes shake{{0%,100%{{transform:translateX(0)}}20%{{transform:translateX(-5px)}}40%{{transform:translateX(5px)}}60%{{transform:translateX(-3px)}}80%{{transform:translateX(3px)}}}}
  @keyframes idle{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-2px)}}}}
  @keyframes fadein{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
<div style='text-align:center;padding:8px 10px;font-family:monospace;{container_style}'>
  <div style='margin-bottom:4px'>
    <span style='background:{lv_color};color:#fff;font-size:10px;padding:2px 7px;border-radius:99px'>Lv.{monster.level}</span>
    &nbsp;<span style='font-size:12px;font-weight:500'>{monster.name}</span>
  </div>
  <div style='display:inline-block;image-rendering:pixelated;{anim}'>{grid_rows}</div>
  {flash_html}
  <div style='margin:4px auto;max-width:160px'>
    <div style='font-size:10px;color:#888;margin-bottom:2px'>HP {monster.hp} / {monster.max_hp}</div>
    <div style='background:#eee;border-radius:4px;height:6px;overflow:hidden'>
      <div style='width:{hp_pct}%;height:100%;background:{hp_color};border-radius:4px;transition:width .4s'></div>
    </div>
  </div>
  <div style='font-size:15px;font-weight:500;margin-top:6px;letter-spacing:2px'>{monster.word}</div>
  <div style='font-size:11px;color:#888;margin-top:2px'>{monster.meaning}</div>
</div>"""

def victory_html(defeated_word, defeated_meaning, next_m):
    next_hint = f"다음: {next_m.name} ({next_m.word} / {next_m.meaning})" if next_m else "던전 클리어!"
    return f"""
<style>
  @keyframes fadein{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
<div style='text-align:center;padding:20px 10px;font-family:monospace;animation:fadein .4s ease'>
  <div style='font-size:28px'>✨</div>
  <div style='font-size:16px;font-weight:500;color:#7F77DD;margin-top:6px'>처치 성공!</div>
  <div style='font-size:14px;color:#0F6E56;margin-top:4px;font-weight:500;letter-spacing:1px'>{defeated_word}</div>
  <div style='font-size:11px;color:#888;margin-top:3px'>{defeated_meaning}</div>
  <div style='font-size:11px;color:#aaa;margin-top:8px'>{next_hint}</div>
</div>"""

def score_color(s):
    return "#1D9E75" if s >= 90 else "#BA7517" if s >= 70 else "#E24B4A"

def make_score_html(scores):
    return f"""
<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:5px;font-family:sans-serif'>
  {"".join(f'''<div style='text-align:center;background:#f7f7f5;border-radius:7px;padding:6px 3px'>
    <div style='font-size:16px;font-weight:500;color:{score_color(scores[k])}'>{scores[k]}</div>
    <div style='font-size:10px;color:#888'>{label}</div>
  </div>''' for k,label in [("overall","종합"),("accuracy","정확도"),("fluency","유창성"),("completeness","완성도")])}
</div>"""

def build_dungeon(keywords, player_name="익명"):
    state.load_from_keywords(keywords)
    state.player_name = player_name
    word_list = "\n".join(f"Lv.{k['level']}  {k['word']}  ({k['meaning']})" for k in keywords)
    log = f"몬스터 {len(keywords)}마리 소환!\n\n{word_list}"
    return render_monster_html(state.current_monster), log, gr.update(visible=True)

def load_dungeon_from_image(player_name, image):
    if image is None:
        return "<div style='text-align:center;padding:20px;color:#aaa'>이미지를 업로드해 주세요</div>", "", gr.update(visible=False)
    if not player_name or not player_name.strip():
        player_name = "익명"
    return build_dungeon(extract_keywords(extract_text_from_image(image)), player_name)

def load_dungeon_from_text(player_name, text):
    if not text or not text.strip():
        return "<div style='text-align:center;padding:20px;color:#aaa'>텍스트를 입력해 주세요</div>", "", gr.update(visible=False)
    if not player_name or not player_name.strip():
        player_name = "익명"
    return build_dungeon(extract_keywords(text.strip()), player_name)

def hear_pronunciation():
    m = state.current_monster
    if m is None:
        return None
    return text_to_speech(m.word)

def attack_monster(audio_path):
    m = state.current_monster
    if m is None or audio_path is None:
        return render_monster_html(m), "", None

    scores = assess_pronunciation(audio_path, m.word)
    result = m.take_damage(scores["overall"])
    flash = result["result"]

    if m.is_dead:
        state.defeated += 1
        defeated_word = m.word
        defeated_meaning = m.meaning
        state.next_monster()
        next_m = state.current_monster

        if state.is_finished:
            player = getattr(state, 'player_name', '익명')
            save_score(player, state.defeated)
            clear_html = f"""
<style>
  @keyframes fadein{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
<div style='text-align:center;padding:24px 10px;font-family:monospace;animation:fadein .8s ease'>
  <div style='font-size:30px'>🏆</div>
  <div style='font-size:17px;font-weight:500;color:#7F77DD;margin-top:8px'>던전 클리어!</div>
  <div style='font-size:13px;color:#1D9E75;margin-top:4px;font-weight:500'>{state.defeated}마리 처치 완료</div>
  <div style='font-size:11px;color:#888;margin-top:4px'>{player} 님의 기록이 저장됐어요!</div>
  <div style='margin-top:14px;padding:8px 14px;background:#EEEDFE;border-radius:8px;display:inline-block'>
    <div style='font-size:11px;color:#534AB7'>다시 도전하려면 새 이미지를 업로드하세요!</div>
  </div>
</div>"""
            return clear_html, make_score_html(scores), None

        return (
            victory_html(defeated_word, defeated_meaning, next_m),
            make_score_html(scores),
            None
        )

    return render_monster_html(m, flash=flash), make_score_html(scores), None

def next_monster_delayed():
    time.sleep(1.5)
    if state.is_finished:
        return gr.update()
    return render_monster_html(state.current_monster, fadein=True)

def reset_and_refresh():
    reset_leaderboard()
    return render_leaderboard_html()

# ── CSS ───────────────────────────────────────────────
CSS = """
footer { display:none !important }
.gradio-container { max-width:1060px !important; margin:0 auto !important; padding-top:0 !important; }
.main-row {
  display: grid !important;
  grid-template-columns: 380px 1fr !important;
  gap: 16px !important;
  align-items: start !important;
}
.monster-panel {
  border: 1px solid #e5e5e3;
  border-radius: 10px;
  overflow: hidden;
  min-height: 180px;
}
.gradio-container .gap { gap: 8px !important; }
.gradio-container .block { padding: 10px !important; }
.gradio-container .form { gap: 6px !important; }
.tabitem { padding-top: 6px !important; }
button.lg { min-height: 36px !important; font-size: 13px !important; }
button.sm { min-height: 30px !important; font-size: 12px !important; }
.wrap.svelte-1vmd51o {
  height: 70px !important; min-height: 70px !important;
  padding: 8px !important; flex-direction: row !important;
  gap: 8px !important; font-size: 12px !important;
}
.icon-wrap.svelte-1vmd51o { width:24px !important; height:24px !important; flex-shrink:0 !important; }
.or.svelte-1vmd51o { display:none !important; }
.battle-cols {
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 12px !important;
  align-items: start !important;
}
.battle-cols > div:first-child { padding-top: 28px !important; }
"""

# ── UI ────────────────────────────────────────────────
with gr.Blocks(title="Study Snap Quest") as demo:

    gr.HTML("""
    <div style='text-align:center;padding:10px 0 2px;font-family:monospace'>
      <span style='font-size:18px;font-weight:500;letter-spacing:3px'>STUDY SNAP QUEST</span>
      <span style='font-size:11px;color:#888;margin-left:12px'>발음으로 몬스터를 처치하세요!</span>
    </div>
    """)

    with gr.Row(elem_classes="main-row"):

        # 왼쪽 패널
        with gr.Column(min_width=360):
            player_input = gr.Textbox(
                label="플레이어 이름",
                placeholder="이름을 입력하세요",
                max_lines=1
            )
            with gr.Tabs():
                with gr.Tab("이미지 업로드"):
                    image_input = gr.Image(type="filepath", label="교과서 / 필기 사진", height=120)
                    image_btn   = gr.Button("던전 생성", variant="primary", size="sm")
                with gr.Tab("텍스트 붙여넣기"):
                    text_input  = gr.Textbox(placeholder="교과서 내용, 단어장 등...", lines=3, show_label=False)
                    text_btn    = gr.Button("던전 생성", variant="primary", size="sm")
            dungeon_log = gr.Textbox(label="소환 목록", lines=5, interactive=False)

        # 오른쪽 패널
        with gr.Column():
            with gr.Tabs():
                with gr.Tab("전투"):
                    monster_display = gr.HTML(
                        "<div style='text-align:center;padding:30px;color:#aaa'>던전을 생성해 주세요</div>",
                        elem_classes="monster-panel"
                    )
                    with gr.Column(visible=False) as battle_area:
                        with gr.Row(elem_classes="battle-cols"):
                            with gr.Column(scale=1, min_width=0):
                                hear_btn  = gr.Button("발음 듣기", variant="secondary", size="lg")
                                tts_audio = gr.Audio(label="원어민 발음", interactive=False, autoplay=True)
                            with gr.Column(scale=1, min_width=0):
                                mic_input = gr.Audio(
                                    sources=["microphone"],
                                    type="filepath",
                                    label="따라 말하기 (녹음 종료 시 자동 공격!)",
                                    streaming=False
                                )
                        score_display = gr.HTML("")

                with gr.Tab("🏆 리더보드"):
                    leaderboard_display = gr.HTML(render_leaderboard_html())
                    with gr.Row():
                        refresh_btn = gr.Button("새로고침", size="sm")
                        reset_btn   = gr.Button("초기화", size="sm", variant="stop")

    # ── 이벤트 ────────────────────────────────────────
    dungeon_outputs = [monster_display, dungeon_log, battle_area]

    image_btn.click(load_dungeon_from_image, inputs=[player_input, image_input], outputs=dungeon_outputs)
    image_input.change(load_dungeon_from_image, inputs=[player_input, image_input], outputs=dungeon_outputs)
    text_btn.click(load_dungeon_from_text, inputs=[player_input, text_input], outputs=dungeon_outputs)
    hear_btn.click(hear_pronunciation, outputs=tts_audio)

    mic_input.stop_recording(
        attack_monster,
        inputs=mic_input,
        outputs=[monster_display, score_display, mic_input]
    ).then(next_monster_delayed, outputs=monster_display)

    refresh_btn.click(render_leaderboard_html, outputs=leaderboard_display)
    reset_btn.click(reset_and_refresh, outputs=leaderboard_display)

from pyngrok import ngrok
tunnel = ngrok.connect(7860)
print(f"\n★ 공개 URL: {tunnel.public_url}\n")

demo.launch(share=False, css=CSS, theme=gr.themes.Soft())