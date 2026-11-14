"""Write a .cube that maps Apple Log / Rec.2020 to display Rec.709 (gamma 2.4).
Curve constants: Apple Log Profile White Paper (2023). Usage: applelog_lut.py OUT.cube [size]

The proxies in this folder come from the iPhone ProRes originals (4K, 30 fps, Apple Log):
  ffmpeg -ss IN -to OUT -i IMG.MOV -vf "scale=2560:1440:in_color_matrix=bt2020:in_range=tv,format=gbrp16le,
    lut3d=file=OUT.cube:interp=tetrahedral,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
    -c:v libx264 -crf 17 -g 30 -af "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac shot.mp4
Each proxy starts 1 s before the in-point of its shot. The look is graded in index.html (data-color-grading).
"""
import sys
R0, RT, C, BETA, GAMMA, DELTA = -0.05641088, 0.01, 47.28711236, 0.00964052, 0.08550479, 0.69336945
PT = C * (RT - R0) ** 2
M = ((1.6605, -0.5876, -0.0728), (-0.1246, 1.1329, -0.0083), (-0.0182, -0.1006, 1.1187))  # Rec.2020 -> Rec.709, linear
GAIN, WHITE = 1.25, 6.0  # 0.18 grey stays 0.18; scene value 6.0 is display white

def decode(p):
    if p >= PT: return 2 ** ((p - DELTA) / GAMMA) - BETA
    if p >= 0: return (p / C) ** 0.5 + R0
    return R0

def display(x):
    x = max(x, 0.0) * GAIN
    y = x * (1 + x / WHITE ** 2) / (1 + x)  # extended Reinhard: soft shoulder, no clip on the white fleece
    return min(y, 1.0) ** (1 / 2.4)

assert abs(decode(GAMMA * __import__("math").log2(0.18 + BETA) + DELTA) - 0.18) < 1e-6  # self-check: grey round trip
n = int(sys.argv[2]) if len(sys.argv) > 2 else 65
lin = [decode(i / (n - 1)) for i in range(n)]
with open(sys.argv[1], "w") as f:
    f.write("LUT_3D_SIZE %d\n" % n)
    for b in range(n):
        for g in range(n):
            for r in range(n):
                v = (lin[r], lin[g], lin[b])
                f.write("%.6f %.6f %.6f\n" % tuple(display(sum(m * c for m, c in zip(row, v))) for row in M))
