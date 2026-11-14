import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S, C = 8, 720
raw = open("/tmp/scope.bin","rb").read(); cur = np.frombuffer(raw[:4], dtype=np.int32)[0]
d = np.frombuffer(raw[4:], dtype=np.float32).reshape(S,3,C,2)
fig, ax = plt.subplots(2,1, figsize=(11,6.2), facecolor="#08030f")
x = (np.arange(C)+0.5)/C
for a, title, bass_sig, col in ((ax[0],"BASS ANTES (sem plugin) - 8 batidas sobrepostas",1,"#ff9f1c"), (ax[1],"BASS DEPOIS (com PsyPhase Lock) - 8 batidas sobrepostas",2,"#00f5d4")):
    a.set_facecolor("#05020c")
    for age in range(S-1, 0, -1):                      # oldest -> newest (skip the half-written slice 'cur')
        s = (cur - age) % S; al = 0.25 + 0.6*(1-age/S)
        for sig, c in ((0,"#ff2bd6"), (bass_sig, col)):
            mn, mx = d[s,sig,:,0], d[s,sig,:,1]; ok = mn <= mx
            v = np.where(ok, 0.5*(mn+mx), np.nan)
            a.plot(x, v, color=c, alpha=al, lw=0.9 if sig==0 else 1.1)
    for q in range(5): a.axvline(q/4, color="white", alpha=0.35 if q in (0,4) else 0.15, lw=0.8)
    a.axhline(0, color="white", alpha=0.15, lw=0.6)
    a.set_title(title, color="white", fontsize=10, loc="left"); a.set_xlim(0,1); a.set_ylim(-1,1)
    a.set_xticks([0,.25,.5,.75]); a.set_xticklabels(["1","e","&","a"], color="#b79cff"); a.set_yticks([])
    for sp in a.spines.values(): sp.set_color("#442266")
plt.tight_layout(); plt.savefig("/tmp/scope_preview.png", dpi=110, facecolor="#08030f")
