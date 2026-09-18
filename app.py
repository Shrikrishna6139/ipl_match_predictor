"""
IPL Match Predictor — full dashboard (v2: visual redesign).

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import joblib
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from team_data import TEAM_INFO, STADIUM_CAPACITY

# ---------------------------------------------------------------------------
# Page config + theme
# ---------------------------------------------------------------------------
st.set_page_config(page_title="IPL Match Predictor", page_icon="🏏", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Rajdhani:wght@600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    /* Hero banner */
    .hero {
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 22px;
        background: linear-gradient(120deg, var(--c1) 0%, #0b0b0b 48%, var(--c2) 100%);
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: "";
        position: absolute; inset: 0;
        background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.10), transparent 45%);
    }
    .hero-title {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 44px;
        color: #fff;
        letter-spacing: 1px;
        margin: 0;
        text-shadow: 0 2px 14px rgba(0,0,0,0.5);
        position: relative; z-index: 1;
    }
    .hero-sub {
        color: rgba(255,255,255,0.85);
        font-size: 15px;
        margin-top: 6px;
        position: relative; z-index: 1;
    }
    .hero-badges { margin-top: 14px; position: relative; z-index: 1; }
    .hero-chip {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.25);
        color: #fff;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 12px;
        margin-right: 8px;
        backdrop-filter: blur(6px);
    }

    /* VS banner */
    .vs-wrap { display: flex; align-items: center; justify-content: center; gap: 22px; margin: 6px 0 18px 0; }
    .vs-logo {
        width: 84px; height: 84px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 26px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.4);
        border: 3px solid rgba(255,255,255,0.35);
    }
    .vs-text {
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 30px;
        background: linear-gradient(90deg, #f9cd05, #ec1c24);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .vs-name { text-align: center; font-weight: 600; font-size: 15px; margin-top: 6px; }

    /* Glass team card */
    .team-card {
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 10px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 6px 22px rgba(0,0,0,0.30);
    }
    .team-card::before {
        content: "";
        position: absolute; inset: 0;
        background: linear-gradient(160deg, rgba(255,255,255,0.14), rgba(255,255,255,0) 55%);
    }
    .team-card h2 { margin: 0 0 6px 0; font-size: 24px; font-family: 'Rajdhani', sans-serif; font-weight: 700; position: relative; z-index:1;}
    .team-card .meta { font-size: 13.5px; opacity: 0.92; line-height: 1.7; position: relative; z-index:1; }

    /* Trophy row */
    .trophy-row { margin-top: 8px; position: relative; z-index: 1; }
    .trophy { display: inline-block; font-size: 15px; margin-right: 4px; }

    /* Stat box */
    .stat-box {
        border-radius: 14px;
        padding: 14px 10px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        text-align: center;
        transition: transform .15s ease;
    }
    .stat-box .big { font-size: 26px; font-weight: 800; font-family: 'Rajdhani', sans-serif; }
    .stat-box .label { font-size: 11px; opacity: 0.65; text-transform: uppercase; letter-spacing: .06em; margin-top: 2px;}

    /* Form pills */
    .form-pill {
        display: inline-block; width: 27px; height: 27px; border-radius: 8px;
        text-align: center; line-height: 27px; font-size: 12px; font-weight: 700;
        margin-right: 5px; color: white; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .win { background: linear-gradient(135deg,#22c55e,#16a34a); }
    .loss { background: linear-gradient(135deg,#f87171,#dc2626); }

    /* Prob bars */
    .prob-row { margin: 6px 0 16px 0; }
    .prob-label { display:flex; justify-content: space-between; font-size: 14px; font-weight: 600; margin-bottom: 4px; }
    .prob-track { height: 22px; border-radius: 11px; background: rgba(255,255,255,0.08); overflow: hidden; }
    .prob-fill { height: 100%; border-radius: 11px; display:flex; align-items:center; justify-content:flex-end; padding-right:10px; font-size:11px; font-weight:700; color:#fff; }

    /* Section header */
    .section-title {
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 24px;
        margin: 4px 0 14px 0; display:flex; align-items:center; gap:8px;
    }
    .divider {
        height: 2px; border: none; margin: 26px 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
    }

    /* Winner banner */
    .winner-banner {
        border-radius: 16px; padding: 18px 24px; text-align:center;
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 26px; color: #fff;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35); margin-bottom: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Load model + data artifacts
# ---------------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
    model = joblib.load("ipl_best_model.pkl")
    features = joblib.load("ipl_best_features.pkl")
    encoder = joblib.load("ipl_team_encoder.pkl")
    history = joblib.load("df_v2_full.pkl")
    try:
        model_name = joblib.load("ipl_best_model_name.pkl")
    except FileNotFoundError:
        model_name = type(model).__name__
    return model, features, encoder, history, model_name


best_model, best_features, team_encoder, df_v2, best_model_name = load_artifacts()
known_teams = sorted(team_encoder.classes_)


# ---------------------------------------------------------------------------
# Feature engineering / stats helpers
# ---------------------------------------------------------------------------
def get_recent_form(data, team, n=5):
    return data[(data["team1"] == team) | (data["team2"] == team)].tail(n)


def recent_form_rate(data, team, n=5):
    last_matches = get_recent_form(data, team, n)
    if len(last_matches) == 0:
        return 0.5
    return (last_matches["winner"] == team).sum() / len(last_matches)


def get_h2h_matches(data, team1, team2):
    return data[
        ((data["team1"] == team1) & (data["team2"] == team2))
        | ((data["team1"] == team2) & (data["team2"] == team1))
    ].sort_values("date")


def h2h_win_rate(data, team1, team2):
    h2h = get_h2h_matches(data, team1, team2)
    if len(h2h) == 0:
        return 0.5
    return (h2h["winner"] == team1).sum() / len(h2h)


def team_overall_record(data, team):
    played = data[(data["team1"] == team) | (data["team2"] == team)]
    wins = (played["winner"] == team).sum()
    losses = len(played) - wins
    win_pct = round(100 * wins / len(played), 1) if len(played) else 0.0
    return len(played), wins, losses, win_pct


def team_batting_first_rate(data, team):
    played = data[data["batting_first"] == team] if "batting_first" in data.columns else pd.DataFrame()
    if len(played) == 0:
        return 0.5
    return (played["winner"] == team).sum() / len(played)


def predict_match(team1, team2, toss_winner, history=df_v2):
    team1_encoded = team_encoder.transform([team1])[0]
    team2_encoded = team_encoder.transform([team2])[0]
    team1_won_toss = int(toss_winner == team1)
    t1_recent = recent_form_rate(history, team1)
    t2_recent = recent_form_rate(history, team2)
    t1_h2h = h2h_win_rate(history, team1, team2)

    row = pd.DataFrame(
        [
            {
                "team1_encoded": team1_encoded,
                "team2_encoded": team2_encoded,
                "team1_won_toss": team1_won_toss,
                "team1_recent_win_rate": t1_recent,
                "team2_recent_win_rate": t2_recent,
                "team1_h2h_win_rate": t1_h2h,
            }
        ]
    )[best_features]

    proba = best_model.predict_proba(row)[0]
    classes = list(best_model.classes_)
    team1_prob = float(proba[classes.index(1)])
    team2_prob = float(proba[classes.index(0)])
    predicted_winner = team1 if team1_prob >= team2_prob else team2

    return {
        "team1": team1,
        "team2": team2,
        "predicted_winner": predicted_winner,
        "team1_win_probability": round(team1_prob * 100, 2),
        "team2_win_probability": round(team2_prob * 100, 2),
        "team1_recent_form": round(t1_recent, 3),
        "team2_recent_form": round(t2_recent, 3),
        "head_to_head_team1_rate": round(t1_h2h, 3),
    }


def team_info_default(name):
    return TEAM_INFO.get(
        name,
        {
            "short": name[:3].upper(), "color": "#666666", "text_color": "#ffffff",
            "founded": None, "home_ground": "Unknown", "city": "Unknown",
            "titles": 0, "title_years": [],
        },
    )


def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def confidence_label(prob):
    if prob >= 80:
        return "Strong Favorite", "#22c55e"
    if prob >= 65:
        return "Clear Edge", "#84cc16"
    if prob >= 55:
        return "Slight Lean", "#eab308"
    return "Toss-up", "#94a3b8"


# ---------------------------------------------------------------------------
# Team selectors (top, always visible)
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    team1 = st.selectbox("Team 1", known_teams, index=known_teams.index("Mumbai Indians") if "Mumbai Indians" in known_teams else 0)
with col2:
    remaining = [t for t in known_teams if t != team1]
    default_t2 = "Chennai Super Kings" if "Chennai Super Kings" in remaining else remaining[0]
    team2 = st.selectbox("Team 2", remaining, index=remaining.index(default_t2) if default_t2 in remaining else 0)
with col3:
    toss_winner = st.selectbox("Toss winner", [team1, team2])

info1, info2 = team_info_default(team1), team_info_default(team2)

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------
total_matches = len(df_v2)
total_seasons = df_v2["season"].nunique()
st.markdown(
    f"""
    <div class="hero" style="--c1:{hex_to_rgba(info1['color'],0.55)}; --c2:{hex_to_rgba(info2['color'],0.55)};">
        <div class="hero-title">🏏 IPL Match Predictor</div>
        <div class="hero-sub">Live win prediction, franchise dossiers, stadium intel & full head-to-head history</div>
        <div class="hero-badges">
            <span class="hero-chip">🤖 Model: {best_model_name}</span>
            <span class="hero-chip">📅 {total_seasons} seasons analyzed</span>
            <span class="hero-chip">📊 {total_matches} matches in dataset</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# VS banner
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="vs-wrap">
        <div>
            <div class="vs-logo" style="background:{info1['color']}; color:{info1['text_color']};">{info1['short']}</div>
            <div class="vs-name">{team1}</div>
        </div>
        <div class="vs-text">VS</div>
        <div>
            <div class="vs-logo" style="background:{info2['color']}; color:{info2['text_color']};">{info2['short']}</div>
            <div class="vs-name">{team2}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

predict_clicked = st.button("🔮 Predict Winner", type="primary", width="stretch")

if predict_clicked:
    result = predict_match(team1, team2, toss_winner)
    label, label_color = confidence_label(max(result["team1_win_probability"], result["team2_win_probability"]))
    winner_info = info1 if result["predicted_winner"] == team1 else info2

    st.markdown(
        f"""
        <div class="winner-banner" style="background: linear-gradient(120deg, {winner_info['color']}, #111);">
            🏆 Predicted Winner: {result['predicted_winner']}
            <div style="font-size:14px; font-weight:600; margin-top:6px; color:{label_color};">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.balloons()

    for team_name, prob, info in [
        (team1, result["team1_win_probability"], info1),
        (team2, result["team2_win_probability"], info2),
    ]:
        st.markdown(
            f"""
            <div class="prob-row">
                <div class="prob-label"><span>{team_name}</span><span>{prob:.2f}%</span></div>
                <div class="prob-track">
                    <div class="prob-fill" style="width:{prob:.2f}%; background: linear-gradient(90deg, {info['color']}aa, {info['color']});">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🔍 What went into this prediction"):
        st.json(
            {
                f"Recent form (last 5), {team1}": result["team1_recent_form"],
                f"Recent form (last 5), {team2}": result["team2_recent_form"],
                f"Head-to-head win rate ({team1})": result["head_to_head_team1_rate"],
                "Toss winner": toss_winner,
            }
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_profiles, tab_h2h, tab_trends, tab_stadium, tab_standings = st.tabs(
    ["🪪 Franchise Dossiers", "⚔️ Head-to-Head", "📈 Form & Trends", "🏟️ Stadium Intel", "🏅 Standings"]
)

# --- Franchise Dossiers -----------------------------------------------------
with tab_profiles:
    c1, c2 = st.columns(2)
    for col, team, info in [(c1, team1, info1), (c2, team2, info2)]:
        played, wins, losses, pct = team_overall_record(df_v2, team)
        with col:
            titles_html = "".join(f'<span class="trophy">🏆{y}</span>' for y in info["title_years"]) or "<span class='trophy'>No titles yet</span>"
            st.markdown(
                f"""
                <div class="team-card" style="background: linear-gradient(135deg, {info['color']}, {hex_to_rgba(info['color'],0.55)} 70%, #101010); color:{info['text_color']};">
                    <h2>{team} <span style="opacity:.75; font-size:16px;">({info['short']})</span></h2>
                    <div class="meta">
                        🏟️ {info['home_ground']}<br>
                        📍 {info['city']} &nbsp;|&nbsp; 🗓️ Est. {info['founded']}
                    </div>
                    <div class="trophy-row">{titles_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            sc1, sc2, sc3 = st.columns(3)
            sc1.markdown(f'<div class="stat-box"><div class="big">{played}</div><div class="label">Matches</div></div>', unsafe_allow_html=True)
            sc2.markdown(f'<div class="stat-box"><div class="big">{wins}-{losses}</div><div class="label">W-L</div></div>', unsafe_allow_html=True)
            sc3.markdown(f'<div class="stat-box"><div class="big">{pct}%</div><div class="label">Win Rate</div></div>', unsafe_allow_html=True)

            recent = get_recent_form(df_v2, team, 5)
            pills = "".join(
                f'<span class="form-pill {"win" if m["winner"] == team else "loss"}">{"W" if m["winner"] == team else "L"}</span>'
                for _, m in recent.iterrows()
            )
            st.markdown(f"<br>**Recent form:** {pills}", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🕸️ Head-to-Head Profile Comparison</div>', unsafe_allow_html=True)

    categories = ["Overall Win %", "Recent Form", "H2H Win Rate", "Batting-First Win %"]
    _, w1_, l1_, pct1_ = team_overall_record(df_v2, team1)
    _, w2_, l2_, pct2_ = team_overall_record(df_v2, team2)
    t1_vals = [pct1_, recent_form_rate(df_v2, team1) * 100, h2h_win_rate(df_v2, team1, team2) * 100, team_batting_first_rate(df_v2, team1) * 100]
    t2_vals = [pct2_, recent_form_rate(df_v2, team2) * 100, (1 - h2h_win_rate(df_v2, team1, team2)) * 100, team_batting_first_rate(df_v2, team2) * 100]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=t1_vals + [t1_vals[0]], theta=categories + [categories[0]], fill="toself", name=team1, line=dict(color=info1["color"])))
    fig_radar.add_trace(go.Scatterpolar(r=t2_vals + [t2_vals[0]], theta=categories + [categories[0]], fill="toself", name=team2, line=dict(color=info2["color"])))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=440,
        margin=dict(t=30, b=30, l=60, r=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
    )
    rc1, rc2, rc3 = st.columns([1, 3, 1])
    with rc2:
        st.plotly_chart(fig_radar, width="stretch")

# --- Head-to-Head -----------------------------------------------------------
with tab_h2h:
    h2h = get_h2h_matches(df_v2, team1, team2)
    t1_wins = int((h2h["winner"] == team1).sum())
    t2_wins = int((h2h["winner"] == team2).sum())
    total_h2h = len(h2h)

    hc1, hc2 = st.columns([1, 1])
    with hc1:
        if total_h2h > 0:
            fig = go.Figure(data=[go.Pie(labels=[team1, team2], values=[t1_wins, t2_wins], hole=0.55, marker=dict(colors=[info1["color"], info2["color"]]))])
            fig.update_layout(
                title=f"{total_h2h} matches played",
                annotations=[dict(text=f"{total_h2h}", x=0.5, y=0.5, font_size=26, showarrow=False)],
                margin=dict(t=40, b=0, l=0, r=0), height=340,
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("These two teams haven't played each other in this dataset yet.")

    with hc2:
        if total_h2h > 0:
            st.markdown(f"**{team1}**: {t1_wins} wins &nbsp;&nbsp;|&nbsp;&nbsp; **{team2}**: {t2_wins} wins")
            show_cols = ["date", "season", "venue", "toss_winner", "toss_decision", "winner"]
            h2h_display = h2h[show_cols].rename(columns={"date": "Date", "season": "Season", "venue": "Venue", "toss_winner": "Toss Winner", "toss_decision": "Toss Decision", "winner": "Winner"})
            h2h_display["Date"] = pd.to_datetime(h2h_display["Date"]).dt.strftime("%d %b %Y")
            st.dataframe(h2h_display, hide_index=True, width="stretch", height=280)

# --- Form & Trends -----------------------------------------------------------
with tab_trends:
    st.markdown('<div class="section-title">📈 Season-by-Season Win Rate</div>', unsafe_allow_html=True)

    def season_win_rates(data, team):
        played = data[(data["team1"] == team) | (data["team2"] == team)].copy()
        played["won"] = (played["winner"] == team).astype(int)
        by_season = played.groupby("season")["won"].mean().reset_index()
        by_season["win_rate"] = (by_season["won"] * 100).round(1)
        return by_season

    sr1 = season_win_rates(df_v2, team1)
    sr2 = season_win_rates(df_v2, team2)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=sr1["season"], y=sr1["win_rate"], mode="lines+markers", name=team1, line=dict(color=info1["color"], width=4), marker=dict(size=9)))
    fig2.add_trace(go.Scatter(x=sr2["season"], y=sr2["win_rate"], mode="lines+markers", name=team2, line=dict(color=info2["color"], width=4), marker=dict(size=9)))
    fig2.update_layout(yaxis_title="Win rate (%)", xaxis_title="Season", yaxis_range=[0, 100], height=380, margin=dict(t=10, b=0))
    st.plotly_chart(fig2, width="stretch")

# --- Stadium Intel -----------------------------------------------------------
with tab_stadium:
    st.markdown('<div class="section-title">🏟️ Stadium Spotlight</div>', unsafe_allow_html=True)
    venue_options = sorted(df_v2["venue"].unique())
    default_venue_idx = 0
    h2h_for_venue = get_h2h_matches(df_v2, team1, team2)
    if len(h2h_for_venue) > 0:
        top_venue = h2h_for_venue["venue"].value_counts().idxmax()
        if top_venue in venue_options:
            default_venue_idx = venue_options.index(top_venue)

    selected_venue = st.selectbox("Choose a venue to inspect", venue_options, index=default_venue_idx)
    venue_matches = df_v2[df_v2["venue"] == selected_venue]

    vc1, vc2, vc3, vc4 = st.columns(4)
    vc1.markdown(f'<div class="stat-box"><div class="big">{len(venue_matches)}</div><div class="label">Matches hosted</div></div>', unsafe_allow_html=True)
    capacity = STADIUM_CAPACITY.get(selected_venue, None)
    vc2.markdown(f'<div class="stat-box"><div class="big">{capacity if capacity else "N/A"}</div><div class="label">Approx. capacity</div></div>', unsafe_allow_html=True)

    bat_first_wins = (venue_matches["winner"] == venue_matches["batting_first"]).sum() if "batting_first" in venue_matches.columns else 0
    bat_first_pct = round(100 * bat_first_wins / len(venue_matches), 1) if len(venue_matches) else 0
    vc3.markdown(f'<div class="stat-box"><div class="big">{bat_first_pct}%</div><div class="label">Batting-first win rate</div></div>', unsafe_allow_html=True)

    toss_win_match_win = (venue_matches["toss_winner"] == venue_matches["winner"]).sum()
    toss_pct = round(100 * toss_win_match_win / len(venue_matches), 1) if len(venue_matches) else 0
    vc4.markdown(f'<div class="stat-box"><div class="big">{toss_pct}%</div><div class="label">Toss winner also won</div></div>', unsafe_allow_html=True)

    def venue_record(data, team, venue):
        played = data[((data["team1"] == team) | (data["team2"] == team)) & (data["venue"] == venue)]
        wins = (played["winner"] == team).sum()
        return len(played), wins

    pv1, wv1 = venue_record(df_v2, team1, selected_venue)
    pv2, wv2 = venue_record(df_v2, team2, selected_venue)
    st.markdown(f"<br>**{team1}** at this venue: {wv1}/{pv1} wins &nbsp;&nbsp;|&nbsp;&nbsp; **{team2}** at this venue: {wv2}/{pv2} wins", unsafe_allow_html=True)

# --- Standings -----------------------------------------------------------
with tab_standings:
    st.markdown('<div class="section-title">🏅 League Standings</div>', unsafe_allow_html=True)
    season_options = sorted(df_v2["season"].unique(), reverse=True)
    selected_season = st.selectbox("Season", season_options, index=0)

    season_df = df_v2[df_v2["season"] == selected_season]
    records = []
    for team in known_teams:
        played = season_df[(season_df["team1"] == team) | (season_df["team2"] == team)]
        if len(played) == 0:
            continue
        wins = (played["winner"] == team).sum()
        losses = len(played) - wins
        win_pct = round(100 * wins / len(played), 1)
        records.append({"Team": team, "Played": len(played), "Won": wins, "Lost": losses, "Win %": win_pct})

    standings = pd.DataFrame(records).sort_values(["Win %", "Won"], ascending=False).reset_index(drop=True)
    standings.insert(0, "Rank", range(1, len(standings) + 1))
    st.dataframe(standings, hide_index=True, width="stretch")

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.caption(
    "⚠️ For entertainment/analysis purposes only. Model accuracy is measured on a single "
    "held-out season — treat predictions as a mild statistical lean, not a certainty."
)
