# DaniSan PsyPhase Lock v1.1 — alinhador de fase kick/bass (VST3)

Plugin para o **grupo** onde kick e bass tocam juntos (darkpsy / forest, 150–200 BPM).
Mede a fase do kick e do bass na frequência do bass e gira a fase do bass (all-pass + polaridade)
para ficarem em fase no início de cada nota. Latência fixa: **30 ms** (o host compensa via PDC).

## Roteamento (importante)
Fase relativa não pode ser medida só da soma kick+bass, então o plugin usa o **sidechain** como referência do kick.

* **Modo GROUP** (padrão): plugin no grupo (kick+bass). Mande uma cópia do kick (send *pré-fader*,
  mesmo nível) para o **sidechain** do plugin. O plugin faz `bass = grupo − kick`, gira só o bass e
  deixa todo o resto como está. Se o send não for idêntico ao kick do grupo, acerte com **KICK TRIM**.
* **Modo TRACK** (GROUP desligado): plugin na faixa do bass, kick no sidechain.

## Parâmetros
| Controle | Função |
|---|---|
| FOCUS | Frequência de análise (40–100 Hz). Ajuste para a nota raiz do bass / fundamental do kick |
| TARGET | Fase desejada do bass em relação ao kick (0° = em fase) |
| AUTO | Liga o alinhamento automático por nota |
| MANUAL | Rotação manual 0–360° (só com AUTO desligado) |
| THRESHOLD | Nível a partir do qual kick/bass contam como "tocando" |
| SETTLE | Espera extra antes de medir (use 30–40 ms se o bass cai junto com o início do kick, onde o pitch ainda desce) |
| MIX | Dry/wet da correção |
| KICK TRIM | Ajuste de nível do kick do sidechain (modo GROUP) |

**Osciloscópio sincronizado no BPM do host:** mostra 1 batida (1 e & a = as 4 semicolcheias) e sobrepõe as últimas 8 batidas.
Magenta = kick (sidechain), ciano = bass depois do plugin, laranja = bass antes (botão BEFORE). Se todas as notas travam,
os traços ficam empilhados. FREEZE congela a tela. GHOST: notas de bass sem kick por baixo seguem a continuação da fase do último kick.

## Compilar
Requisitos: CMake ≥ 3.22, git, Visual Studio 2022 (Desktop C++) ou Xcode, e internet na 1ª vez (baixa o JUCE 8.0.4).
```
cmake -B build -G "Visual Studio 17 2022"
cmake --build build --config Release
```
O VST3 fica em `build/PsyPhaseLock_artefacts/Release/VST3/PsyPhase Lock.vst3`
(copie para `C:\Program Files\Common Files\VST3`). No Mac: `cmake -B build -G Xcode`.

## Teste do motor de DSP (sem JUCE)
```
cd Tests
g++ -O2 -std=c++17 test_core.cpp -o test_core
./test_core --sweep 44100 55         # precisão da rotação de fase
python3 gen_eval.py offbeat 1 0      # kick + bass em 16avos, fase aleatória por nota
```


## Repositório novo (GitHub) - passo a passo
1. github.com -> **New repository** (nome qualquer, ex.: `danisan-psyphase`, pode ser privado).
2. Na página do repositório vazio: **uploading an existing file**.
3. Extraia este zip e arraste **todo o conteúdo** para a página (CMakeLists.txt, README.md, pasta `Source`, pasta `Tests`
   e a pasta oculta `.github`). Confira se aparecem `.github/workflows/build.yml` e `Source/LogoData.h` na lista antes de commitar.
4. **Commit changes**. Aba **Actions** -> o build roda sozinho (~5 min).
5. Clique na execução verde -> **Artifacts** -> baixe `DaniSan-PsyPhaseLock-VST3-build-N`.
6. Copie a pasta `DaniSan PsyPhase Lock.vst3` para `C:\Program Files\Common Files\VST3`, **apague o `PsyPhase Lock.vst3` antigo** e reescaneie os plugins.

O plugin novo tem nome e ID diferentes do anterior (aparece como "DaniSan PsyPhase Lock"), então a DAW nunca mistura com a versão velha.
Se o canto superior direito mostrar `v1.1 | Dani San`, é o build novo.
