import numpy as np, subprocess, sys
FS = 44100; BPM = 175; FOCUS = 55.0
N = int(round(FS / FOCUS)); F0 = FS / N
beat = 60.0 / BPM; sixt = beat / 4
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
pattern = sys.argv[1] if len(sys.argv) > 1 else "offbeat"   # offbeat = kick + 3 bass 16ths ; together = bass on all 4 16ths
target = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
beats = 40
n = int((beats + 1) * beat * FS)

def kick(L=0.2):
    m = int(L * FS); t = np.arange(m) / FS
    f = F0 + (250 - F0) * np.exp(-t / 0.012)                   # tuned to the bass root
    y = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / 0.08) * np.clip((L - t) / 0.025, 0, 1)
    y += 0.25 * np.random.default_rng(3).standard_normal(m) * np.exp(-t / 0.002)
    y = np.tanh(1.8 * y) / np.tanh(1.8); return 0.8 * y / np.abs(y).max()

K = np.zeros(n); B = np.zeros(n); notes = []
k1 = kick()
for b in range(beats):
    t0 = int(b * beat * FS); K[t0:t0 + len(k1)] += k1[:n - t0]
    for s in ([0, 1, 2, 3] if pattern == "together" else [1, 2, 3]):
        a = int((b * beat + s * sixt) * FS); ln = int(0.075 * FS)
        t = np.arange(ln) / FS; ph = rng.uniform(0, 2 * np.pi)
        env = np.minimum(1, np.minimum(t / 0.003, (ln / FS - t) / 0.003))
        y = (0.5 * np.cos(2 * np.pi * F0 * t + ph) + 0.2 * np.cos(2 * np.pi * 2 * F0 * t + 2 * ph + 1) + 0.1 * np.cos(2 * np.pi * 3 * F0 * t + 3 * ph + 2)) * env
        B[a:a + ln] += y[:n - a]; notes.append(a)

K.astype(np.float32).tofile("/tmp/kick.f32"); B.astype(np.float32).tofile("/tmp/bass.f32")
out = subprocess.run(["./test_core", "/tmp/kick.f32", "/tmp/bass.f32", "/tmp/o_track.f32", "/tmp/o_group.f32", str(FOCUS), str(FS), str(target), sys.argv[4] if len(sys.argv) > 4 else "0"], capture_output=True, text=True)
print(out.stdout.strip())
ot = np.fromfile("/tmp/o_track.f32", dtype=np.float32).astype(float); og = np.fromfile("/tmp/o_group.f32", dtype=np.float32).astype(float)
L = int(round(0.030 * FS))

def phasor(x, a):  # one-period demod starting at sample a
    i = np.arange(N); w = 2 * np.pi * i / N
    seg = x[a:a + N]; return np.sum(seg * np.exp(-1j * w))

def wrap(d): return (d + 180) % 360 - 180
din, dout, gin, gout = [], [], [], []
for a in notes[8:]:                      # skip first notes (warm-up)
    s = a + int((float(sys.argv[5]) if len(sys.argv) > 5 else 3.0) / 1000 * FS)              # window at the START of the note (correction must already be in place)
    zk = phasor(K, s); zb = phasor(B, s)
    zbo = phasor(ot, s + L)              # output is delayed by L
    zko = phasor(np.concatenate([np.zeros(L), K]), s + L)
    din.append(np.degrees(np.angle(zb * np.conj(zk)))); dout.append(np.degrees(np.angle(zbo * np.conj(zko))))
    gin.append(abs(zk + zb)); gout.append(abs(zko + zbo))
din = np.array(din); dout = np.array(dout)
slot = np.array([ ((i + 8) % (4 if pattern=='together' else 3)) for i in range(len(din)) ])
if True:
    for sl in range(4 if pattern == 'together' else 3):
        m = slot == sl
        print(f"  slot {sl+1}: before {np.mean(np.abs(wrap(din[m]-target))):6.1f}  after {np.mean(np.abs(wrap(dout[m]-target))):6.1f} deg  (n={m.sum()})")
print(f"pattern={pattern} target={target:+.0f}deg  notes analysed: {len(din)}")
print(f"  bass-vs-kick phase BEFORE: mean |err to target| {np.mean(np.abs(wrap(din - target))):6.1f} deg   worst {np.max(np.abs(wrap(din - target))):6.1f}")
print(f"  bass-vs-kick phase AFTER : mean |err to target| {np.mean(np.abs(wrap(dout - target))):6.1f} deg   worst {np.max(np.abs(wrap(dout - target))):6.1f}")
print(f"  sub (55 Hz) sum amplitude: before min {min(gin):.1f} / mean {np.mean(gin):.1f}   after min {min(gout):.1f} / mean {np.mean(gout):.1f}")
# group mode must equal kick(delayed) + aligned bass
kd = np.concatenate([np.zeros(L), K])[:len(ot)]
print(f"  group == kick_delayed + track_out : max diff {np.max(np.abs(og - (kd + ot))):.2e}")
# gain through the engine for non-aligned content: peak of out vs in
print(f"  peak in {np.abs(K+B).max():.3f}  peak out(group) {np.abs(og).max():.3f}")

# ---- slot 3 (no kick underneath) must follow the phase of the last kick ("ghost") ----
if pattern == "offbeat":
    def ph_abs(x, a):
        i = np.arange(N); return np.sum(x[a:a+N] * np.exp(-2j*np.pi*(a+i)/N))
    errs_b, errs_a = [], []
    for j, a in enumerate(notes):
        if j % 3 != 2 or j < 9: continue
        bs = int((j // 3) * beat * FS); zk = ph_abs(K, bs + int(0.12*FS))      # kick phase (constant, f = F0)
        s0 = a + int(0.003*FS)
        errs_b.append(wrap(np.degrees(np.angle(ph_abs(B, s0)  * np.conj(zk))) - target))
        zo = ph_abs(ot, s0 + L) * np.exp(2j*np.pi*L/N)      # output index -> input-time oscillator reference
        errs_a.append(wrap(np.degrees(np.angle(zo * np.conj(zk))) - target))
    print(f"  slot 3 vs GHOST kick: before {np.mean(np.abs(errs_b)):6.1f}  after {np.mean(np.abs(errs_a)):6.1f} deg  (n={len(errs_a)})")
