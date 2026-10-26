"""Explainer video for the project, in the style of 3Blue1Brown (made with Manim Community).

Needs video/data.json (from video/prepare_data.py). Render at 1080p, 30 fps:
    .venv-video/Scripts/manim.exe -r 1920,1080 --fps 30 --media_dir video/media video/explainer.py Explainer
"""

import json
from pathlib import Path

import numpy as np
from manim import *

DATA = json.loads((Path(__file__).parent / "data.json").read_text(encoding="utf-8"))
FONT = "Cambria"
CAPTION_Y = -2.85


def txt(s, size=32, color=WHITE):
    return Text(s, font=FONT, font_size=size, color=color)


def check_mark(color=GREEN):
    return VMobject(stroke_color=color, stroke_width=10).set_points_as_corners([[-0.3, 0, 0], [-0.08, -0.25, 0], [0.35, 0.3, 0]])


class Explainer(Scene):
    def construct(self):
        self.caption = None
        self.title_card()
        self.vwap_and_signal()
        self.universe_and_data()
        self.in_sample()
        self.out_of_sample()
        self.by_year()
        self.power()
        self.conclusion()

    # ---------- helpers ----------
    def say(self, s, size=28, color=GREY_A, run_time=0.8):
        """Replace the caption at the bottom of the screen."""
        new = txt(s, size, color).move_to([0, CAPTION_Y, 0])
        if new.width > 13.2:  # keep long captions inside the frame
            new.scale_to_fit_width(13.2)
        if self.caption is None:
            self.play(FadeIn(new, shift=UP * 0.15), run_time=run_time)
        else:
            self.play(FadeOut(self.caption, shift=UP * 0.15), FadeIn(new, shift=UP * 0.15), run_time=run_time)
        self.caption = new

    def clear(self, run_time=0.6):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self.caption = None

    def heading(self, s, size=36):
        return txt(s, size).to_edge(UP, buff=0.45)

    # ---------- 1. title ----------
    def title_card(self):
        t = txt("Buying the dip, measured", 60)
        s = txt("A 2σ VWAP strategy on 10 Spanish small caps, 2016–2026", 30, GREY_B).next_to(t, DOWN, buff=0.45)
        self.play(Write(t), run_time=1.5)
        self.play(FadeIn(s, shift=UP * 0.2), run_time=1)
        self.wait(1.2)
        self.clear(0.5)

    # ---------- 2-3. VWAP, the signal, the exits ----------
    def vwap_and_signal(self):
        ex = DATA["example"]
        close, vwap, band = (np.array(ex[k], dtype=float) for k in ("close", "vwap", "band"))
        vol = np.array(ex["volume"], dtype=float)
        n = len(close)
        y_min = float(np.floor((min(close.min(), np.nanmin(band)) - 0.05) * 10) / 10)
        y_max = float(np.ceil((max(close.max(), vwap.max()) + 0.05) * 10) / 10)

        ax = Axes(x_range=[0, n - 1, 10], y_range=[y_min, y_max, 0.5], x_length=11.6, y_length=4.2, tips=False,
                  axis_config={"include_numbers": False, "include_ticks": False, "color": GREY_C, "stroke_width": 2})
        ax.move_to([0.35, 0.75, 0])
        y_labels = VGroup(*[txt(f"€{v:.1f}", 20, GREY_B).next_to(ax.c2p(0, v), LEFT, buff=0.15)
                            for v in np.arange(np.ceil(y_min * 2) / 2, y_max, 0.5)])
        month_starts = {}
        for i, d in enumerate(ex["dates"]):
            month_starts.setdefault(d[:7], i)
        names = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May"}
        x_labels = VGroup(*[txt(names[m[5:]], 20, GREY_B).next_to(ax.c2p(i, y_min), DOWN, buff=0.15)
                            for m, i in month_starts.items()])
        title = txt("Tubacex, January to May 2020", 26, GREY_B).next_to(ax, UP, buff=0.25).align_to(ax, LEFT)

        def line(values, i0, i1, color, width=3.5):
            pts = [ax.c2p(i, values[i]) for i in range(i0, i1 + 1) if not np.isnan(values[i])]
            return VMobject(stroke_color=color, stroke_width=width).set_points_as_corners(pts)

        unit = ax.x_length / (n - 1)
        vmax = vol.max()

        def volume_bars(i0, i1):
            return VGroup(*[Rectangle(width=unit * 0.7, height=max(0.9 * vol[i] / vmax, 0.01), stroke_width=0,
                                      fill_color=GREY_D, fill_opacity=0.55).move_to(ax.c2p(i, y_min), aligned_edge=DOWN)
                            for i in range(i0, i1 + 1)])

        k = 31  # first part of the chart: up to just after the first trade
        price1, price2 = line(close, 0, k, BLUE), line(close, k, n - 1, BLUE)
        vwap1, vwap2 = line(vwap, 0, k, YELLOW), line(vwap, k, n - 1, YELLOW)
        band1 = DashedVMobject(line(band, 0, k, TEAL, 3), num_dashes=30)
        band2 = DashedVMobject(line(band, k, n - 1, TEAL, 3), num_dashes=60)
        vol1, vol2 = volume_bars(0, k), volume_bars(k + 1, n - 1)

        legend = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=BLUE, stroke_width=4), txt("price", 22)).arrange(RIGHT, buff=0.15),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=YELLOW, stroke_width=4), txt("VWAP, last 20 days", 22)).arrange(RIGHT, buff=0.15),
            VGroup(DashedLine(ORIGIN, RIGHT * 0.5, color=TEAL, stroke_width=4, dash_length=0.08), txt("VWAP − 2σ", 22)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(ax.c2p(0.8 * n, y_max - 0.05), aligned_edge=UP)

        self.play(Create(ax), FadeIn(y_labels), FadeIn(x_labels), FadeIn(title), run_time=1)
        self.say("The share price of Tubacex, early 2020")
        self.play(Create(price1), run_time=2.2)
        self.say("Grey bars: how many shares traded each day")
        self.play(FadeIn(vol1, lag_ratio=0.05), run_time=1)
        self.say("VWAP = Σ (price × volume) ÷ Σ volume, over the last 20 days")
        self.play(Create(vwap1), FadeIn(legend[:2]), run_time=2)
        self.wait(1.8)

        self.say("2σ below VWAP: unusually far, judged against the last 60 days")
        self.play(Create(band1), FadeIn(legend[2]), run_time=1.5)
        self.wait(1.3)

        t1 = DATA["example"]["trades"][0]
        buy1 = Dot(ax.c2p(t1["entry"], t1["entry_price"]), radius=0.09, color=GREEN)
        self.say("The close falls through the line: buy at the next open")
        self.play(FadeIn(buy1, scale=2), Flash(buy1, color=GREEN), run_time=1)
        self.wait(0.8)
        sell1 = Circle(radius=0.1, color=WHITE, stroke_width=4).move_to(ax.c2p(t1["exit"], t1["exit_price"]))
        lab1 = txt(f"+{t1['return']:.1f}%", 26, GREEN).next_to(sell1, UP, buff=0.12)
        self.say("Sell when it's back at VWAP, or after 10 days at most")
        self.play(Create(sell1), FadeIn(lab1, shift=UP * 0.1), run_time=1)
        self.wait(1.5)

        self.say("But some dips keep falling…")
        self.play(Create(price2), Create(vwap2), Create(band2), FadeIn(vol2, lag_ratio=0.02), run_time=3, rate_func=linear)
        marks, labels = VGroup(), VGroup()
        offsets = [None, LEFT * 0.85 + DOWN * 0.25, LEFT * 0.75 + DOWN * 0.3, UP * 0.32]
        for t, off in zip(DATA["example"]["trades"][1:], offsets[1:]):
            b = Dot(ax.c2p(t["entry"], t["entry_price"]), radius=0.09, color=GREEN)
            s = Circle(radius=0.1, color=WHITE, stroke_width=4).move_to(ax.c2p(t["exit"], t["exit_price"]))
            color = GREEN if t["return"] > 0 else RED
            sign = "+" if t["return"] > 0 else "−"
            lab = txt(f"{sign}{abs(t['return']):.1f}%", 26, color).move_to(s.get_center() + off)
            marks.add(b, s)
            labels.add(lab)
        self.play(FadeIn(marks[0:4], lag_ratio=0.3), FadeIn(labels[0:2], lag_ratio=0.5), run_time=1.5)
        self.say("…the falling knife: bought twice into the COVID crash", color=RED_B)
        self.wait(1.2)
        self.play(FadeIn(marks[4:6], lag_ratio=0.3), FadeIn(labels[2]), run_time=1)
        self.say("…then the rebound. Does it win more than it loses?")
        self.wait(1.5)
        self.clear()

    # ---------- 4. universe and the data trap ----------
    def universe_and_data(self):
        head = self.heading("The universe: chosen by a rule, before any results")
        names = ["OHLA", "eDreams", "Amper", "Oryzon", "Tubacex", "Ence", "Nextil", "Dominion", "San José", "Audax"]
        boxes = VGroup(*[VGroup(RoundedRectangle(width=2.25, height=0.85, corner_radius=0.15, stroke_color=GREY_B, stroke_width=2),
                                txt(nm, 28)) for nm in names]).arrange_in_grid(rows=2, cols=5, buff=0.3).move_to(UP * 0.4)
        self.play(FadeIn(head), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in boxes], lag_ratio=0.12), run_time=1.5)
        self.say("The 10 most-traded Spanish stocks under €1bn: no 0.2% transaction tax")
        self.wait(1.8)

        nxt = boxes[6]
        self.play(nxt[0].animate.set_stroke(YELLOW, 4), *[b.animate.set_opacity(0.25) for i, b in enumerate(boxes) if i != 6], run_time=0.8)
        self.play(FadeOut(boxes), FadeOut(head), run_time=0.5)

        nx = DATA["nextil"]
        raw, fixed = np.array(nx["raw"]), np.array(nx["fixed"])
        m = len(raw)
        ax = Axes(x_range=[0, m - 1, 10], y_range=[0, 4, 1], x_length=9, y_length=3.6, tips=False,
                  axis_config={"include_numbers": False, "include_ticks": False, "color": GREY_C}).move_to(UP * 0.5)
        y_labs = VGroup(*[txt(f"€{v}", 20, GREY_B).next_to(ax.c2p(0, v), LEFT, buff=0.15) for v in (1, 2, 3)])
        sub = txt("Nextil, summer 2018, as downloaded", 26, GREY_B).next_to(ax, UP, buff=0.3).align_to(ax, LEFT)

        def line(values, color):
            return VMobject(stroke_color=color, stroke_width=4).set_points_as_corners([ax.c2p(i, v) for i, v in enumerate(values)])

        raw_line, fixed_line = line(raw, RED), line(fixed, BLUE)
        cliff = txt("−73% overnight?", 30, RED).next_to(ax.c2p(nx["split_index"], 2.3), RIGHT, buff=0.2)
        self.play(Create(ax), FadeIn(y_labs), FadeIn(sub), run_time=0.8)
        self.play(Create(raw_line), run_time=1.5)
        self.play(FadeIn(cliff, shift=LEFT * 0.2), run_time=0.6)
        self.say("No: a 4-for-1 share split the data provider never applied")
        self.wait(1)
        self.play(Transform(raw_line, fixed_line), FadeOut(cliff), run_time=1.5)
        self.say("Fixed before any testing. A backtest believes every number.")
        self.wait(1.5)
        self.clear()

    # ---------- 5. in-sample ----------
    def in_sample(self):
        s = DATA["in_sample"]
        head = self.heading("2016–2023: the first seven years (in-sample)")
        l1 = txt("EV per trade = P(win) × average win + P(loss) × average loss", 32)
        p = s["win_rate"] / 100
        l2 = txt(f"= {p:.2f} × {s['avg_win']:.2f}%  −  {1 - p:.2f} × {abs(s['avg_loss']):.2f}%  ≈  −0.3%", 36, YELLOW)
        VGroup(l1, l2).arrange(DOWN, buff=0.45).move_to(UP * 0.6)
        self.play(FadeIn(head), Write(l1), run_time=1.5)
        self.say(f"{s['trades']} trades. Just over half win, but the losers lose more.")
        self.play(FadeIn(l2, shift=UP * 0.2), run_time=1)
        self.wait(2)

        twins = np.array(DATA["twins"])
        edges = np.arange(-1.6, 2.75, 0.1)
        counts, _ = np.histogram(twins, bins=edges)
        ax = Axes(x_range=[edges[0], edges[-1], 1], y_range=[0, counts.max() * 1.15, 50], x_length=10, y_length=2.8, tips=False,
                  axis_config={"include_numbers": False, "include_ticks": False, "color": GREY_C}).move_to(DOWN * 0.2)
        ax.y_axis.set_opacity(0)  # only the strategy's line should stand out
        bars = VGroup(*[Rectangle(width=ax.x_length / len(counts) * 0.85, height=max(c, 0.01) * ax.y_length / (counts.max() * 1.15),
                                  stroke_width=0, fill_color=BLUE, fill_opacity=0.8).move_to(ax.c2p((a + b) / 2, 0), aligned_edge=DOWN)
                        for a, b, c in zip(edges[:-1], edges[1:], counts)])
        x_labs = VGroup(*[txt(lab, 20, GREY_B).next_to(ax.c2p(v, 0), DOWN, buff=0.12) for v, lab in [(-1, "−1%"), (0, "0%"), (1, "+1%"), (2, "+2%")]])
        x_title = txt("average return per trade, buying on random days", 20, GREY_B).next_to(x_labs, DOWN, buff=0.1)
        strat = s["ev"]
        vline = Line(ax.c2p(strat, 0), ax.c2p(strat, counts.max() * 1.1), color=YELLOW, stroke_width=5)
        vlab = txt(f"the strategy: {strat:+.2f}%".replace("-", "−"), 24, YELLOW).next_to(vline, UP, buff=0.08)

        self.play(FadeOut(l1), l2.animate.scale(0.8).next_to(head, DOWN, buff=0.3), run_time=0.8)
        self.play(Create(ax), FadeIn(x_labs), FadeIn(x_title), run_time=0.6)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.03), run_time=1.5)
        self.play(Create(vline), FadeIn(vlab), run_time=0.8)
        self.say(f"Buying on random days instead: {s['random_as_good']}% of 2,000 runs did at least as well")
        self.wait(2.2)
        self.clear()

    # ---------- 6. the one out-of-sample test ----------
    def out_of_sample(self):
        o = DATA["out_of_sample"]
        head = self.heading("Then one test on the held-out years: Oct 2023 – Oct 2026")
        rule = txt("Rule fixed in advance:  pass if EV after costs > 0  and  t ≥ 2", 30, GREY_A)
        box = SurroundingRectangle(rule, color=GREY_B, buff=0.25, corner_radius=0.1)
        VGroup(rule, box).move_to(UP * 1.7)
        self.play(FadeIn(head), run_time=0.6)
        self.play(Write(rule), Create(box), run_time=1.5)
        self.wait(0.8)

        ev, tt = ValueTracker(0), ValueTracker(0)
        ev_lab = txt("EV per trade after costs", 26, GREY_B).move_to(LEFT * 3.2 + UP * 0.35)
        t_lab = txt("t-statistic", 26, GREY_B).move_to(RIGHT * 3.2 + UP * 0.35)
        ev_num = always_redraw(lambda: txt(f"+{ev.get_value():.2f}%", 64, GREEN).next_to(ev_lab, DOWN, buff=0.3))
        t_num = always_redraw(lambda: txt(f"{tt.get_value():.1f}", 64, GREEN).next_to(t_lab, DOWN, buff=0.3))
        self.play(FadeIn(ev_lab), FadeIn(t_lab), FadeIn(ev_num), FadeIn(t_num), run_time=0.5)
        self.play(ev.animate.set_value(o["ev_auction"]), tt.animate.set_value(o["t_month"]), run_time=2)
        verdict = VGroup(check_mark(), txt("PASS", 48, GREEN)).arrange(RIGHT, buff=0.3).move_to(DOWN * 1.65)
        self.play(Create(verdict[0]), FadeIn(verdict[1], scale=1.3), run_time=0.9)
        self.say(f"Sharpe ratio {o['sharpe']:.2f}, against {o['sharpe_buy_hold']:.2f} for simply holding the 10 stocks")
        self.wait(2.3)
        self.clear()

    # ---------- 7. results by year ----------
    def by_year(self):
        d = DATA["decade"]
        years = list(DATA["by_year"].items())
        head = self.heading("…but it depends on the market")
        ax = Axes(x_range=[0, len(years), 1], y_range=[-5, 5, 1], x_length=10.5, y_length=4.4, tips=False,
                  axis_config={"include_numbers": False, "include_ticks": False, "color": GREY_C}).move_to(UP * 0.15)
        ax.y_axis.set_opacity(0)
        unit = ax.x_length / len(years)
        held = Rectangle(width=unit * 3, height=ax.y_length, stroke_width=0, fill_color=GREY, fill_opacity=0.18).move_to(ax.c2p(len(years) - 1.5, 0))
        held_lab = txt("held-out years", 22, GREY_B).next_to(held, UP, buff=0.08)
        bars, vals, labs = VGroup(), VGroup(), VGroup()
        for i, (yr, v) in enumerate(years):
            color = GREEN if v > 0 else RED
            h = abs(v) * ax.y_length / 10
            bar = Rectangle(width=unit * 0.62, height=max(h, 0.02), stroke_width=0, fill_color=color, fill_opacity=0.9)
            bar.move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN if v > 0 else UP)
            bars.add(bar)
            sign = "+" if v > 0 else "−"
            vals.add(txt(f"{sign}{abs(v):.1f}%", 20, color).next_to(bar, UP if v > 0 else DOWN, buff=0.08))
            labs.add(txt(yr if yr != "2026" else "2026*", 20, GREY_B).move_to(ax.c2p(i + 0.5, -5) + DOWN * 0.2))
        y_title = txt("average trade, before costs, by year", 22, GREY_B).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)

        self.play(FadeIn(head), Create(ax.x_axis), FadeIn(labs), FadeIn(y_title), run_time=0.8)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN if v > 0 else UP) for b, (_, v) in zip(bars, years)], lag_ratio=0.15),
                  LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.15), run_time=2.5)
        self.play(FadeIn(held), FadeIn(held_lab), run_time=0.8)
        self.say("Wins when sell-offs reverse quickly; loses when they drag on (2018, 2020, 2022)")
        self.wait(2.2)
        self.say(f"Whole decade: +{d['ev']:.2f}% per trade, t = {d['t_month']:.1f}   ·   Sharpe {d['sharpe']:.2f} vs {d['sharpe_buy_hold']:.2f} for buy-and-hold",
                 color=YELLOW)
        self.wait(3)
        self.clear()

    # ---------- 8. statistical power ----------
    def power(self):
        pw = DATA["power"]
        head = self.heading("How much data would it take to be sure?")
        f = txt("trades needed:   n ≥ (2σ ÷ e)²", 44)
        g = txt(f"σ = {pw['sd']:.1f}% per trade,    e = {pw['edge']:.1f}% edge", 30, GREY_A)
        VGroup(f, g).arrange(DOWN, buff=0.5).move_to(UP * 1.0)
        self.play(FadeIn(head), Write(f), run_time=1.5)
        self.play(FadeIn(g, shift=UP * 0.2), run_time=0.8)
        n_t, y_t = ValueTracker(0), ValueTracker(0)
        n_num = always_redraw(lambda: txt(f"n ≈ {int(n_t.get_value()):,} trades", 40, YELLOW).move_to(DOWN * 0.6))
        y_num = always_redraw(lambda: txt(f"≈ {int(y_t.get_value())} years at this strategy's pace", 40, YELLOW).move_to(DOWN * 1.5))
        self.add(n_num)
        self.play(n_t.animate.set_value(pw["trades"]), run_time=1.3)
        self.add(y_num)
        self.play(y_t.animate.set_value(pw["years"]), run_time=1.3)
        self.say("Ten stocks and daily prices can't settle the question either way")
        self.wait(2.2)
        self.clear()

    # ---------- 9. conclusion ----------
    def conclusion(self):
        a = txt("It passed the test.", 46)
        b = txt("It isn't an edge across market conditions.", 46, YELLOW)
        c = txt("Rules before results  ·  one out-of-sample run  ·  then try to break it", 28, GREY_B)
        VGroup(a, b, c).arrange(DOWN, buff=0.5)
        self.play(Write(a), run_time=1.2)
        self.play(Write(b), run_time=1.5)
        self.play(FadeIn(c, shift=UP * 0.2), run_time=0.8)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)
