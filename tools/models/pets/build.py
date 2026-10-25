"""모든 펫 모델을 빌드: out/<id>.bbmodel + 미리보기 HTML"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pets import PETS

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)
only = sys.argv[2:] or list(PETS)
for pid in only:
    m = PETS[pid]()
    m.bake()
    json.dump(m.bbmodel(), open(os.path.join(OUT, m.name + '.bbmodel'), 'w'), ensure_ascii=False)
    m.image.save(os.path.join(OUT, m.name + '_tex.png'))
    views = [(25, 12), (-35, 10), (160, 15)]
    open(os.path.join(OUT, pid + '_static.html'), 'w').write(m.preview_html(views))
    pose = m.sample('walk', 0.2)
    open(os.path.join(OUT, pid + '_walk.html'), 'w').write(m.preview_html([(70, 8)], pose=pose))
    open(os.path.join(OUT, pid + '_icon.html'), 'w').write(m.preview_html([(30, 14)], scale=20, size=(512, 512), transparent=True))
    print('ok', pid)
