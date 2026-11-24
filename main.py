# THE WORLD TODAY — news-image-20261124
# Pure stdlib Python. Own 5x7 bitmap font, own PNG encoder.
# Renders a dense newspaper front page for Tuesday 24 November 2026.
import os, struct, zlib

W, H = 1024, 1024

# ---- canvas: 0 white, 1 black, 2 grey ----
PIX = bytearray(W * H)

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        PIX[y * W + x] = c

def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)

def hline(x, y, w, c):
    for xx in range(x, x + w):
        px(xx, y, c)

def vline(x, y, h, c):
    for yy in range(y, y + h):
        px(x, yy, c)

# ---- 5x7 bitmap font (7 rows of 5 bits, '#' = ink) ----
FONT = {}
def _g(ch, rows):
    FONT[ch] = rows

_g('A', [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"])
_g('B', ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."])
_g('C', [".####", "#....", "#....", "#....", "#....", "#....", ".####"])
_g('D', ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."])
_g('E', ["#####", "#....", "#....", "####.", "#....", "#....", "#####"])
_g('F', ["#####", "#....", "#....", "####.", "#....", "#....", "#...."])
_g('G', [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."])
_g('H', ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"])
_g('I', ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"])
_g('J', ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."])
_g('K', ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"])
_g('L', ["#....", "#....", "#....", "#....", "#....", "#....", "#####"])
_g('M', ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"])
_g('N', ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"])
_g('O', [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."])
_g('P', ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."])
_g('Q', [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"])
_g('R', ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"])
_g('S', [".####", "#....", "#....", ".###.", "....#", "....#", "####."])
_g('T', ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."])
_g('U', ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."])
_g('V', ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."])
_g('W', ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"])
_g('X', ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"])
_g('Y', ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."])
_g('Z', ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"])
_g('0', [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."])
_g('1', ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."])
_g('2', [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"])
_g('3', ["####.", "....#", "....#", ".###.", "....#", "....#", "####."])
_g('4', ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."])
_g('5', ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."])
_g('6', [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."])
_g('7', ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."])
_g('8', [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."])
_g('9', [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."])
_g(' ', [".....", ".....", ".....", ".....", ".....", ".....", "....."])
_g('.', [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."])
_g(',', [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."])
_g(':', [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."])
_g(';', [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."])
_g('!', ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."])
_g('?', [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."])
_g('-', [".....", ".....", ".....", ".###.", ".....", ".....", "....."])
_g("'", ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."])
_g('"', [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."])
_g('(', ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"])
_g(')', ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."])
_g('/', ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."])
_g('&', [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"])
_g('%', ["##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"])
_g('$', ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."])
_g('#', [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."])
_g('@', [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."])
_g('*', [".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."])
_g('+', [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."])
_g('=', [".....", ".....", "#####", ".....", "#####", ".....", "....."])
_g('<', ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."])
_g('>', [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."])
_g('_', [".....", ".....", ".....", ".....", ".....", ".....", "#####"])
_g('·', [".....", ".....", ".##..", ".##..", ".....", ".....", "....."])
_g('—', [".....", ".....", ".....", "#####", ".....", ".....", "....."])
_g('’', ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."])
_g('“', [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."])
_g('”', [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."])
_g('•', [".....", "..#..", ".###.", ".###.", ".###.", "..#..", "....."])

def text_w(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(x, y, s, scale, c, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for cc in range(5):
                if row[cc] == '#':
                    for dy in range(scale):
                        for dx in range(scale):
                            px(cx + cc * scale + dx, y + r * scale + dy, c)
                            if bold:
                                px(cx + cc * scale + dx + 1, y + r * scale + dy, c)
        cx += 6 * scale
    return cx

def wrap(s, max_w, scale):
    """Word-wrap s to lines fitting max_w pixels at scale."""
    words = s.upper().split(' ')
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if text_w(t, scale) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def para(x, y, s, max_w, scale, c, max_lines=None, leading=2, bold=False):
    """Draw wrapped paragraph; returns y just below last line."""
    lines = wrap(s, max_w, scale)
    if max_lines is not None:
        lines = lines[:max_lines]
    yy = y
    for ln in lines:
        draw_text(x, yy, ln, scale, c, bold=bold)
        yy += 7 * scale + leading
    return yy

# ---- PNG writer (8-bit greyscale, filter 0) ----
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out

def write_png(path):
    grey = bytearray(W * H)
    for i, v in enumerate(PIX):
        grey[i] = 255 if v == 0 else (0 if v == 1 else 160)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += grey[y * W:(y + 1) * W]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 0, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# ---- content: 33 stories, all first reported Tuesday 24 November 2026 ----
# (headline, summary). Verified against Reuters / AP / AFP / AAP / Arab News / wires.
LEAD = (
    "ZELENSKY: RUSSIA PLANS NEW STRIKES ON UKRAINE",
    "UKRAINIAN INTELLIGENCE WARNS OF A FRESH WAVE OF RUSSIAN AIR ATTACKS AS KYIV BRACES FOR ANOTHER WINTER UNDER FIRE, WITH CITIES ALREADY COUNTING THE COST OF NIGHTLY DRONE RAIDS.",
)
LEAD2 = (
    "MOSCOW: ESTONIA ON VERGE OF OPEN WAR",
    "RUSSIA ACCUSES ESTONIA OF HOSTILE ACTS THAT COULD TRIGGER OPEN CONFLICT, IN ITS SHARPEST WARNING YET TO A NATO ALLY ON ITS BORDER.",
)
LEAD3 = (
    "UN CHIEF: AI RISK RULES WITHIN A YEAR",
    "THE SECRETARY-GENERAL CALLS FOR A GLOBAL FRAMEWORK TO MANAGE ARTIFICIAL INTELLIGENCE RISKS BEFORE THE TECHNOLOGY OUTRUNS ITS GUARDRAILS.",
)

PANELS = [
    ("EUROPE", [
        ("US TO BLACKLIST MEGASPEED IN NVIDIA SCANDAL",
         "WASHINGTON MOVES AGAINST THE CHIP FIRM AT THE CENTRE OF THE HUANG AFFAIR AS THE SCANDAL WIDENS."),
        ("ERDOGAN: COP31 LAID BASIS FOR MORE TALKS",
         "TURKEY'S PRESIDENT INSISTS THE FAILED CLIMATE SUMMIT STILL BUILT A FOUNDATION FOR FUTURE DEALS."),
        ("UK PM: EU RETURN UNTHINKABLE WITHOUT VOTE",
         "BURNHAM SAYS REJOINING THE EU IS OFF THE TABLE UNLESS BRITAIN VOTES FOR IT IN A REFERENDUM."),
        ("FLEMISH PM SETS DEC 31 BUDGET DEADLINE",
         "DE WEVER GIVES COALITION PARTNERS UNTIL NEW YEAR'S EVE TO AGREE A BUDGET OR FACE A CRISIS."),
    ]),
    ("MIDDLE EAST", [
        ("FRANCE CONDEMNS SETTLER ATTACKS",
         "PARIS CALLS WEST BANK VIOLENCE BY SETTLERS HIGHLY CONCERNING AS TENSIONS RISE IN PALESTINIAN TOWNS."),
        ("GAZA STUDENTS BEGIN STUDIES IN IRELAND",
         "STUDENTS FROM GAZA START UNIVERSITY IN IRELAND AFTER WINNING A LONG VISA BATTLE."),
        ("OXFAM: GAZA SOIL AND WATER POISONED",
         "A NEW REPORT FINDS EXPLOSIVES AND TOXINS HAVE MADE GAZA'S AIR, SOIL AND WATER DANGEROUS FOR DECADES."),
        ("SAUDI COALITION INTERCEPTS HOUTHI DRONE",
         "A DRONE LAUNCHED TOWARD SAUDI ARABIA'S SOUTHERN REGION IS SHOT DOWN BEFORE IT CAN STRIKE."),
        ("ISRAEL FEARS UN VOTE COULD TIE ITS HANDS",
         "OFFICIALS WORRY A RESOLUTION PROTECTING MEDIATORS COULD LIMIT TARGETED KILLINGS."),
        ("EISENKOT, LIEBERMAN OPPOSE SOLO STRIKE",
         "TWO ISRAELI SECURITY HEAVYWEIGHTS REJECT THE IDEA OF AN INDEPENDENT ATTACK WITHOUT ALLIES."),
    ]),
    ("AFRICA", [
        ("KENYA, DR CONGO RENEW TIES AFTER ROW",
         "NAIROBI AND KINSHASA AGREE TO REPAIR RELATIONS AFTER A DIPLOMATIC STANDOFF."),
        ("LIBYA PARLIAMENT PUSHES UNITY GOVERNMENT",
         "LAWMAKERS LAUNCH AN INITIATIVE TO UNIFY THE COUNTRY'S SPLIT INSTITUTIONS AND CLEAR THE WAY TO VOTES."),
        ("OPERATION FINANCIAL PARIAH HITS IRAN PROXIES",
         "A NEW CAMPAIGN TARGETS THE NETWORKS FUNDING IRAN-BACKED GROUPS ACROSS THE REGION."),
        ("ZANZIBAR RESORTS ABLAZE",
         "TOWERING FLAMES DEVOUR OCEANFRONT RESORTS ON THE TANZANIAN ISLAND AS FIRE CREWS RUSH IN."),
    ]),
    ("ASIA & PACIFIC", [
        ("TOKYO REOPENS AFTER HISTORIC ROUT",
         "JAPAN'S MARKETS RESUME TRADING AFTER A HOLIDAY AND FRIDAY'S 5% NIKKEI PLUNGE, THE FIFTH WORST EVER."),
        ("NIKKEI FUTURES 1,673 ABOVE FRIDAY",
         "OFFSHORE CONTRACTS PRICED TOKYO'S BENCHMARK NEARLY 3% HIGHER WHILE THE CASH MARKET STOOD STILL."),
        ("BEIJING LIMITS DRONE PARTS USED BY RUSSIA",
         "CHINA CURBS SALES OF DRONE COMPONENTS THAT HAVE BEEN FEEDING RUSSIA'S WAR MACHINE."),
        ("ANZ: FIRST RBA CUT NOW JUNE 2027",
         "AUSTRALIA'S ANZ PULLS ITS FIRST RATE-CUT CALL FORWARD, SEEING THREE CUTS BY EARLY 2028."),
        ("TALIBAN ERASES WOMEN'S NAMES IN BALKH",
         "WOMEN'S NAMES ARE STRUCK FROM OFFICIAL DOCUMENTS IN THE NORTHERN PROVINCE AND REPLACED WITH BIBI."),
        ("SPICEJET PILOTS URGE ACTION OVER PAY",
         "INDIA'S PILOTS FEDERATION ASKS THE AVIATION MINISTRY TO STEP IN AS THE AIRLINE'S CRISIS DEEPENS."),
    ]),
    ("AMERICAS", [
        ("TRUMP PAUSES IOWA EXPLOSIVES DETONATION",
         "THE PRESIDENT HALTS THE ARMY'S PLANNED BLAST OF DEGRADED EXPLOSIVES AFTER A COURT FIGHT."),
        ("FBI DEPUTY DIRECTOR TO RETIRE IN DECEMBER",
         "CHRISTOPHER RAIA WILL LEAVE THE BUREAU NEXT MONTH, THE LATEST DEPARTURE OF THE TRUMP ERA."),
        ("FED'S WILLIAMS: INDEPENDENT BANKS DELIVER",
         "THE NEW YORK FED CHIEF DEFENDS CENTRAL BANK INDEPENDENCE AS RATE POLITICS HEATS UP."),
        ("FED WATCHDOG PROBES BOWMAN BOFA DINNER",
         "INVESTIGATORS LOOK INTO THE FED GOVERNOR'S DINNER WITH BANK OF AMERICA CLIENTS."),
        ("TRUMP: CHINA TO BUY 250 MORE BOEINGS",
         "THE PRESIDENT SAYS BEIJING WILL ORDER ANOTHER 250 PLANES AS TRADE TIES THAW."),
        ("US MARINES SEEK DOUBLE-RANGE MISSILES",
         "THE CORPS WANTS NAVAL STRIKE MISSILES WITH TWICE THE REACH FOR A PACIFIC FIGHT."),
    ]),
    ("SPORT", [
        ("SINNER SET FOR SURGERY, TO MISS MELBOURNE",
         "THE FORMER WORLD NO. 1 FACES MORE KNEE SURGERY AND WILL MISS THE AUSTRALIAN OPEN."),
        ("GUKESH DEFENDS WORLD CHESS TITLE IN GENEVA",
         "INDIA'S CHAMPION OPENS HIS TITLE DEFENCE AGAINST UZBEKISTAN'S SINDAROV TODAY."),
        ("FERRARI UNVEILS 296 CHALLENGE STRADALE",
         "MARANELLO SHOWS OFF TWO NEW 296 MODELS, THE CHALLENGE STRADALE AND THE CHALLENGE EVO."),
        ("CAS TO RULE ON SENEGAL AFCON TITLE TODAY",
         "SPORT'S TOP COURT DECIDES SENEGAL'S APPEAL AGAINST LOSING ITS AFRICA CUP OF NATIONS CROWN."),
    ]),
]

TIMELINE = "TUESDAY IN UTC · 00:05 FRANCE CONDEMNS SETTLERS · 00:32 TOKYO REOPENS · 00:52 MARINES SEEK LONGER MISSILES"
MARKETS = "MARKETS · NIKKEI FUTURES +1,673 PTS · BRENT $89.37 -3.5% · S&P 500 +5.3% MON · DOW +3.0% MON"
NUMBERS = "33 STORIES · 7 REGIONS · 89.5 HRS TOKYO SHUT · 250 BOEINGS · BEAVER SUPERMOON TONIGHT"
FOOTER = "THE WORLD TODAY · TUESDAY 24 NOVEMBER 2026 · EVERY STORY FIRST REPORTED 24 NOVEMBER 2026 · PAGE 1"

# ---- layout ----
MX = 24
CW = 976
COLW = 482
COL2X = MX + COLW + 12

def draw_panel(x, y, w, h, title, stories):
    rect(x, y, w, 22, 1)
    draw_text(x + 8, y + 7, title, 1, 0)
    yy = y + 30
    inner = w - 16
    for i, (hd, sm) in enumerate(stories):
        if i > 0:
            hline(x + 8, yy - 3, w - 16, 2)
        yy = para(x + 8, yy, hd, inner, 1, 1, max_lines=2, leading=1, bold=True)
        yy = para(x + 8, yy + 1, sm, inner, 1, 2, max_lines=2, leading=1)
        yy += 5

def main():
    # masthead
    rect(0, 0, W, 72, 1)
    t = "THE WORLD TODAY"
    draw_text((W - text_w(t, 6)) // 2, 15, t, 6, 0)
    draw_text(MX, 80, "TUESDAY 24 NOVEMBER 2026", 1, 1, bold=True)
    r = "33 STORIES · 7 REGIONS · ALL TIMES UTC"
    draw_text(MX + CW - text_w(r, 1), 80, r, 1, 1)
    hline(MX, 98, CW, 1)
    # lead
    yy = para(MX, 108, LEAD[0], CW, 3, 1, max_lines=1, bold=True)
    yy = para(MX, yy + 4, LEAD[1], CW, 1, 1, max_lines=2, leading=2)
    yy = para(MX, yy + 4, LEAD2[0], CW, 2, 1, max_lines=1, bold=True)
    yy = para(MX, yy + 3, LEAD2[1], CW, 1, 1, max_lines=2, leading=2)
    yy = para(MX, yy + 4, LEAD3[0], CW, 2, 1, max_lines=1, bold=True)
    yy = para(MX, yy + 3, LEAD3[1], CW, 1, 1, max_lines=1, leading=2)
    hline(MX, 236, CW, 1)
    # timeline strip
    draw_text(MX, 243, TIMELINE, 1, 1)
    hline(MX, 258, CW, 1)
    # panels: 3 rows x 2 cols
    rows = [(PANELS[0], PANELS[1]), (PANELS[2], PANELS[3]), (PANELS[4], PANELS[5])]
    y = 266
    for (t1, s1), (t2, s2) in rows:
        draw_panel(MX, y, COLW, 208, t1, s1)
        draw_panel(COL2X, y, COLW, 208, t2, s2)
        y += 216
    # markets strip
    rect(MX, y + 2, CW, 30, 1)
    draw_text(MX + 8, y + 11, MARKETS, 1, 0)
    # numbers band
    y2 = y + 38
    rect(MX, y2, CW, 26, 1)
    draw_text((W - text_w(NUMBERS, 1)) // 2, y2 + 9, NUMBERS, 1, 0)
    # footer
    draw_text((W - text_w(FOOTER, 1)) // 2, y2 + 34, FOOTER, 1, 1)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out, exist_ok=True)
    write_png(os.path.join(out, "entry.png"))

if __name__ == "__main__":
    main()
