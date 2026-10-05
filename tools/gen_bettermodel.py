#!/usr/bin/env python3
"""BetterModel 리소스팩(assets/bettermodel)을 실제 BetterModel 로 생성해서 pack/ 에 합친다.

- Paper(버전·빌드 고정) + BetterModel(버전 고정)을 받아 잠깐 서버를 켠다.
- BetterModel 설정은 server/BetterModel/config.yml (서버에 넣는 것과 같은 파일) 에서
  pack-type 만 folder 로 바꿔서 사용 → 서버와 같은 이름·같은 내용이 나옴.
- 모델: 레포의 models/*.bbmodel
- 결과에서 assets/bettermodel/** 만 꺼내 pack/assets/bettermodel 을 통째로 교체.
  그 밖의 경로가 생기면(겹침 위험) 실패로 멈춤.

사용: python3 tools/gen_bettermodel.py [--work DIR] [--cache DIR]
필요: java 25, 인터넷 (GitHub Actions 에서 실행)
"""
import argparse, json, os, pathlib, shutil, subprocess, sys, threading, time, urllib.request

PAPER_VERSION = "26.2"
PAPER_BUILD = "129"
BETTERMODEL_VERSION = "3.5.0"

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "octoserver-resourcepack-ci (github.com/Rejecter98/octoserver-resourcepack)"}


def get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def download(urls, dest):
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[캐시] {dest.name}")
        return
    last = None
    for u in urls:
        try:
            print(f"[다운로드] {u}")
            data = get(u)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  실패: {e}")
    raise SystemExit(f"다운로드 실패: {dest.name}: {last}")


def paper_urls():
    urls = []
    try:
        j = json.loads(get(f"https://fill.papermc.io/v3/projects/paper/versions/{PAPER_VERSION}/builds/{PAPER_BUILD}"))
        urls.append(j["downloads"]["server:default"]["url"])
    except Exception as e:  # noqa: BLE001
        print(f"  fill v3 조회 실패: {e}")
    urls.append(f"https://api.papermc.io/v2/projects/paper/versions/{PAPER_VERSION}/builds/{PAPER_BUILD}"
                f"/downloads/paper-{PAPER_VERSION}-{PAPER_BUILD}.jar")
    return urls


def bettermodel_urls():
    urls = []
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    try:
        h = {"Accept": "application/vnd.github+json", **({"Authorization": f"Bearer {tok}"} if tok else {})}
        rel = json.loads(get(f"https://api.github.com/repos/toxicity188/BetterModel/releases/tags/{BETTERMODEL_VERSION}", h))
        names = [a["name"] for a in rel["assets"]]
        print("  GitHub 릴리스 파일:", names)
        for a in rel["assets"]:
            n = a["name"].lower()
            if n.endswith(".jar") and "paper" in n and "javadoc" not in n and "sources" not in n:
                urls.append(a["browser_download_url"])
    except Exception as e:  # noqa: BLE001
        print(f"  GitHub 릴리스 조회 실패: {e}")
    try:
        vs = json.loads(get('https://api.modrinth.com/v2/project/bettermodel/version?loaders=%5B%22paper%22%5D'))
        for v in vs:
            if v["version_number"] in (BETTERMODEL_VERSION, f"{BETTERMODEL_VERSION}-paper") or \
                    v["version_number"].startswith(BETTERMODEL_VERSION + "+"):
                f = next((f for f in v["files"] if f.get("primary")), v["files"][0])
                urls.append(f["url"])
                break
    except Exception as e:  # noqa: BLE001
        print(f"  Modrinth 조회 실패: {e}")
    if not urls:
        raise SystemExit(f"BetterModel {BETTERMODEL_VERSION} paper jar 를 찾지 못함")
    return urls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=str(ROOT / ".bm-work"))
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/octo-bettermodel"))
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    models = sorted((ROOT / "models").glob("*.bbmodel"))
    out = ROOT / "pack/assets/bettermodel"
    if out.exists():
        shutil.rmtree(out)
    if not models:
        print("models/*.bbmodel 없음 → bettermodel 팩 생략")
        json.dump({"models": [], "files": 0}, open(ROOT / "bettermodel_report.json", "w"))
        return

    cache = pathlib.Path(a.cache)
    paper = cache / f"paper-{PAPER_VERSION}-{PAPER_BUILD}.jar"
    bm = cache / f"BetterModel-{BETTERMODEL_VERSION}-paper.jar"
    download(paper_urls(), paper)
    download(bettermodel_urls(), bm)

    work = pathlib.Path(a.work)
    if work.exists():
        shutil.rmtree(work)
    pl = work / "plugins"
    (pl / "BetterModel/models").mkdir(parents=True)
    (pl / "BetterModel/players").mkdir(parents=True)  # 비어 있으면 기본 steve 모델을 넣지 않음
    shutil.copy(bm, pl / bm.name)
    cfg = (ROOT / "server/BetterModel/config.yml").read_text(encoding="utf-8")
    if "\npack-type: none" not in cfg or "use-obfuscation: false" not in cfg:
        raise SystemExit("server/BetterModel/config.yml 에 pack-type: none / use-obfuscation: false 가 있어야 함")
    (pl / "BetterModel/config.yml").write_text(cfg.replace("\npack-type: none", "\npack-type: folder"), encoding="utf-8")
    for m in models:
        shutil.copy(m, pl / "BetterModel/models" / m.name)
    # Paper 가 다운받는 바닐라 jar 캐시 재사용
    pcache = cache / "paper-cache"
    pcache.mkdir(parents=True, exist_ok=True)
    (work / "cache").symlink_to(pcache, target_is_directory=True)
    (work / "eula.txt").write_text("eula=true\n")
    (work / "server.properties").write_text(
        "online-mode=false\nlevel-type=minecraft\\:flat\ngenerate-structures=false\nspawn-protection=0\n"
        "max-players=1\nview-distance=2\nsimulation-distance=2\nserver-port=25599\nenable-query=false\n")

    cmd = ["java", "-Xms1G", "-Xmx3G", "-jar", str(paper), "--nogui"]
    print("[서버 시작]", " ".join(cmd))
    p = subprocess.Popen(cmd, cwd=work, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, bufsize=1)
    state = {"ok": False, "fail": None}
    log = []

    def reader():
        for line in p.stdout:
            line = line.rstrip()
            log.append(line)
            print("  |", line)
            if "Plugin is loaded." in line and not state["ok"]:
                state["ok"] = True
            if "Unable to load plugin properly" in line or "Plugin load failed" in line:
                state["fail"] = line
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    start = time.time()
    while p.poll() is None and not state["ok"] and not state["fail"] and time.time() - start < a.timeout:
        time.sleep(1)
    try:
        time.sleep(3)
        p.stdin.write("stop\n"); p.stdin.flush()
    except Exception:  # noqa: BLE001
        pass
    try:
        p.wait(timeout=120)
    except subprocess.TimeoutExpired:
        p.kill()
    t.join(timeout=5)
    if not state["ok"]:
        raise SystemExit(f"BetterModel 로딩 실패/시간 초과: {state['fail']}")
    errs = [l for l in log if "BetterModel" in l and ("ERROR" in l or "Exception" in l)]
    if errs:
        raise SystemExit("BetterModel 오류 로그:\n" + "\n".join(errs[:20]))

    build = work / "BetterModel/build"
    if not build.is_dir():
        raise SystemExit(f"생성 폴더 없음: {build}")
    files = [f for f in build.rglob("*") if f.is_file()]
    bad = [str(f.relative_to(build)) for f in files
           if not (f.relative_to(build).parts[:2] == ("assets", "bettermodel")
                   or str(f.relative_to(build)) in ("pack.mcmeta", "pack.png"))]
    if bad:
        raise SystemExit("bettermodel 네임스페이스 밖의 파일이 생성됨 (팩 경로 겹침 위험):\n" + "\n".join(bad[:50]))
    shutil.copytree(build / "assets/bettermodel", out)
    got = [str(f.relative_to(out)) for f in out.rglob("*") if f.is_file()]
    for m in models:
        if not any(m.stem in g for g in got):
            raise SystemExit(f"모델 {m.stem} 의 생성 파일을 찾지 못함")
    rep = {"paper": f"{PAPER_VERSION}-{PAPER_BUILD}", "bettermodel": BETTERMODEL_VERSION,
           "models": [m.stem for m in models], "files": len(got)}
    json.dump(rep, open(ROOT / "bettermodel_report.json", "w"), ensure_ascii=False)
    print("[완료]", rep)


if __name__ == "__main__":
    main()
